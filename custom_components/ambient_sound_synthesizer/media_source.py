"""Media Source implementation for Ambient Sounds integration."""
from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from urllib.parse import quote, unquote

from homeassistant.components.media_player import MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Default intensity for generated noise
DEFAULT_NOISE_INTENSITY = 0.5


async def async_get_media_source(hass: HomeAssistant) -> AmbientSoundsMediaSource:
    """Set up Ambient Sounds media source."""
    return AmbientSoundsMediaSource(hass)


class AmbientSoundsMediaSource(MediaSource):
    """Provide ambient sounds from Freesound as media sources."""

    name: str = "Ambient Sounds"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve media to a playable URL."""
        # identifier format: 
        # - "fav:{favorite_id}"
        # - "preview:{sound_id}:{query}:{url}"
        # - "noise:{noise_type}:{duration}"
        if not item.identifier:
            raise Unresolvable("No identifier provided")
        
        parts = item.identifier.split(":", 1)
        if len(parts) != 2:
            raise Unresolvable(f"Invalid identifier: {item.identifier}")
        
        media_type, media_data = parts
        
        if media_type == "noise":
            # Generate noise on-demand
            # Format: noise:{noise_type}:{duration}
            noise_parts = media_data.split(":", 1)
            if len(noise_parts) != 2:
                raise Unresolvable(f"Invalid noise identifier: {media_data}")
            
            noise_type, duration_str = noise_parts
            try:
                duration = int(duration_str)
            except ValueError:
                raise Unresolvable(f"Invalid duration: {duration_str}")
            
            _LOGGER.info("Generating %s noise for %d seconds", noise_type, duration)
            
            # Generate the noise
            file_path = await self._generate_noise(noise_type, duration)
            
            # Return local file path
            return PlayMedia(f"file://{file_path}", "audio/wav")
        
        elif media_type == "fav":
            # Playing a favorite
            favorite = await self._get_favorite(media_data)
            if not favorite:
                raise Unresolvable(f"Favorite not found: {media_data}")
            
            _LOGGER.info("Resolving favorite: %s", favorite["name"])
            return PlayMedia(favorite["url"], "audio/mpeg")
        
        elif media_type == "preview":
            # Preview a search result - format: preview:{sound_id}:{query}:{url}
            # Using split with maxsplit=2 to handle URLs with colons (e.g., https://)
            preview_parts = media_data.split(":", 2)
            if len(preview_parts) != 3:
                raise Unresolvable(f"Invalid preview identifier: {media_data}")
            
            sound_id, query, audio_url = preview_parts
            audio_url = unquote(audio_url)
            
            if not audio_url:
                raise Unresolvable(f"No audio URL provided for sound: {sound_id}")
            
            _LOGGER.info("Resolving preview for sound ID: %s", sound_id)
            return PlayMedia(audio_url, "audio/mpeg")
        
        else:
            raise Unresolvable(f"Unknown media type: {media_type}")

    async def async_browse_media(
        self,
        item: MediaSourceItem,
    ) -> BrowseMediaSource:
        """Browse media."""
        if not item.identifier:
            # Root level - show Favorites and Search
            return await self._browse_root()
        
        # Parse identifier - all valid identifiers must have a colon
        if ":" not in item.identifier:
            # This shouldn't happen with the new structure, but handle gracefully
            _LOGGER.warning("Invalid identifier format (no colon): %s", item.identifier)
            return await self._browse_root()
        
        parts = item.identifier.split(":", 1)
        if len(parts) != 2:
            _LOGGER.warning("Invalid identifier format: %s", item.identifier)
            return await self._browse_root()
        
        category, value = parts
        
        if category == "noise_generator":
            # Parse noise_generator identifier
            # Format: noise_generator: (root - show all noise types)
            # Format: noise_generator:{noise_type} (show duration options)
            if not value:
                return await self._browse_noise_generator()
            else:
                # Show duration options for this noise type
                return await self._browse_noise_duration(value)
        elif category == "favorites":
            return await self._browse_favorites()
        elif category == "search":
            query = unquote(value) if value else ""
            return await self._browse_search(query)
        elif category == "search_result":
            # Parse search_result identifier: search_result:{sound_id}:{query}
            result_parts = value.split(":", 1)
            if len(result_parts) == 2:
                sound_id, query = result_parts
                query = unquote(query)
                return await self._browse_search_result(sound_id, query)
            _LOGGER.warning("Invalid search result identifier: %s", value)
            return await self._browse_root()
        elif category == "info":
            # Info items are not browsable - return to root
            _LOGGER.debug("Info item clicked: %s", item.identifier)
            return await self._browse_root()
        else:
            _LOGGER.warning("Unknown category: %s", category)
            return await self._browse_root()

    async def _browse_root(self) -> BrowseMediaSource:
        """Browse root level."""
        children = [
            BrowseMediaSource(
                domain=DOMAIN,
                identifier="noise_generator:",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title="🎛️ Noise Generator",
                can_play=False,
                can_expand=True,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier="favorites:",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title="⭐ Favorites",
                can_play=False,
                can_expand=True,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier="search:",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title="🔍 Search Freesound",
                can_play=False,
                can_expand=True,
                thumbnail=None,
            ),
        ]
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="",
            media_class=MediaClass.DIRECTORY,
            media_content_type="library",
            title="Ambient Sounds",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _browse_favorites(self) -> BrowseMediaSource:
        """Browse favorites."""
        favorites = await self._get_all_favorites()
        
        children = []
        for fav_id, favorite in favorites.items():
            duration_str = ""
            if favorite.get("duration"):
                minutes = favorite["duration"] // 60
                seconds = favorite["duration"] % 60
                duration_str = f" ({minutes}:{seconds:02d})"
            
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"fav:{fav_id}",
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title=f"{favorite['name']}{duration_str}",
                    can_play=True,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        if not children:
            # Show a placeholder when no favorites
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier="info:no_favorites",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title="No favorites yet. Search Freesound to add some!",
                    can_play=False,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="favorites:",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title="⭐ Favorites",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _browse_search(self, query: str) -> BrowseMediaSource:
        """Browse search results."""
        if not query:
            # Show search categories/suggestions and custom search option
            suggestions = [
                "rain", "ocean", "forest", "wind", "thunder",
                "fire", "birds", "river", "waterfall", "cafe",
                "city", "nature", "ambient", "meditation", "relaxing"
            ]
            
            children = [
                # Add custom search option
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier="search:custom:",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title="✏️ Custom Text Search",
                    can_play=False,
                    can_expand=True,
                    thumbnail=None,
                ),
            ]
            
            for suggestion in suggestions:
                children.append(
                    BrowseMediaSource(
                        domain=DOMAIN,
                        identifier=f"search:{quote(suggestion)}",
                        media_class=MediaClass.DIRECTORY,
                        media_content_type="",
                        title=f"🔍 {suggestion.title()}",
                        can_play=False,
                        can_expand=True,
                        thumbnail=None,
                    )
                )
            
            return BrowseMediaSource(
                domain=DOMAIN,
                identifier="search:",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title="🔍 Search Freesound - Select a category or custom search",
                can_play=False,
                can_expand=True,
                children=children,
            )
        
        # Check if this is a custom search or sort request
        # Format: custom:{search_text} or {query}|sort:{name|duration}
        sort_by = None
        actual_query = query
        
        if query.startswith("custom:"):
            # Custom text search - show input prompt
            return await self._browse_custom_search()
        elif "|sort:" in query:
            # Parse sort parameter
            parts = query.split("|sort:", 1)
            actual_query = parts[0]
            sort_by = parts[1] if len(parts) > 1 else None
        
        # Perform actual search
        results = await self._search_freesound(actual_query)
        
        # Apply sorting if requested
        if sort_by == "name":
            results = sorted(results, key=lambda x: x.get("name", "").lower())
        elif sort_by == "duration":
            results = sorted(results, key=lambda x: x.get("duration", 0))
        
        # Add sorting options at the top
        children = []
        if results and not sort_by:
            # Show sorting options
            children.extend([
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"search:{quote(actual_query + '|sort:name')}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title="📊 Sort by Name (A-Z)",
                    can_play=False,
                    can_expand=True,
                    thumbnail=None,
                ),
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"search:{quote(actual_query + '|sort:duration')}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title="⏱️ Sort by Duration (Shortest First)",
                    can_play=False,
                    can_expand=True,
                    thumbnail=None,
                ),
            ])
        
        for result in results:
            sound_id = str(result["id"])
            duration = result.get("duration", 0)
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f" ({minutes}:{seconds:02d})" if duration else ""
            
            # Use name or tags for title
            title = result.get("name", result.get("tags", "Ambient Sound"))
            if len(title) > 50:
                title = title[:47] + "..."
            
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"search_result:{sound_id}:{quote(actual_query)}",
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title=f"{title}{duration_str}",
                    can_play=False,  # Can't play directly, show details first
                    can_expand=True,  # Show details and preview
                    thumbnail=None,
                )
            )
        
        if not results:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier="info:no_results",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=f"No results found for '{actual_query}'. Try another search term.",
                    can_play=False,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        # Create appropriate title based on search type
        if sort_by == "name":
            title_text = f"🔍 Results for '{actual_query}' (Sorted by Name)"
        elif sort_by == "duration":
            title_text = f"🔍 Results for '{actual_query}' (Sorted by Duration)"
        else:
            title_text = f"🔍 Results for: {actual_query}"
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=f"search:{quote(query)}",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=title_text,
            can_play=False,
            can_expand=True,
            children=children,
        )
    
    async def _browse_custom_search(self) -> BrowseMediaSource:
        """Show custom search examples."""
        # Since Media Browser doesn't support text input directly,
        # show example searches that users can click
        # For custom searches, users need to use the ambient_sounds.search service
        
        example_searches = [
            ("rain thunder", "🌧️ Rain + Thunder"),
            ("ocean waves", "🌊 Ocean Waves"),
            ("forest morning", "🌲 Forest Morning"),
            ("wind howling", "💨 Wind Howling"),
            ("city traffic", "🚗 City Traffic"),
            ("cafe ambience", "☕ Cafe Ambience"),
            ("fireplace crackling", "🔥 Fireplace"),
            ("birds chirping", "🐦 Birds Chirping"),
            ("river flowing", "🏞️ River Flowing"),
            ("thunderstorm", "⛈️ Thunderstorm"),
        ]
        
        children = []
        for search_term, display_name in example_searches:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"search:{quote(search_term)}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=display_name,
                    can_play=False,
                    can_expand=True,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="search:custom:",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title="✏️ Custom Search Examples (Click to search, or use ambient_sounds.search service)",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _browse_search_result(self, sound_id: str, query: str) -> BrowseMediaSource:
        """Browse a specific search result to show options."""
        # Get the search results again to find this specific sound
        results = await self._search_freesound(query)
        
        # Find the specific sound
        sound = None
        for result in results:
            if str(result["id"]) == sound_id:
                sound = result
                break
        
        if not sound:
            raise Unresolvable(f"Sound not found: {sound_id}")
        
        # Create a detail view showing the sound info
        duration = sound.get("duration", 0)
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}:{seconds:02d}" if duration else "Unknown"
        
        name = sound.get("name", "Unknown")
        tags = sound.get("tags", "No tags")
        username = sound.get("username", "Unknown")
        
        # Get the preview audio URL
        audio_url = sound.get("preview_url", "")
        
        # Since we can't actually add favorites from Media Browser UI,
        # we'll show instructions
        info_text = (
            f"To add this sound to your favorites, use the service:\n\n"
            f"Service: ambient_sounds.add_favorite\n"
            f"Data:\n"
            f"  sound_id: \"{sound_id}\"\n"
            f"  name: \"{name}\"\n"
            f"  url: \"{audio_url}\"\n"
            f"  duration: {duration}\n"
            f"  tags: \"{tags}\""
        )
        
        children = [
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"info:{sound_id}",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=f"📋 {name}",
                can_play=False,
                can_expand=False,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"info:{sound_id}:tags",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=f"🏷️ Tags: {tags[:50]}",
                can_play=False,
                can_expand=False,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"info:{sound_id}:duration",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=f"⏱️ Duration: {duration_str}",
                can_play=False,
                can_expand=False,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"info:{sound_id}:username",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=f"👤 By: {username}",
                can_play=False,
                can_expand=False,
                thumbnail=None,
            ),
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"info:{sound_id}:id",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=f"🔑 ID: {sound_id}",
                can_play=False,
                can_expand=False,
                thumbnail=None,
            ),
        ]
        
        if audio_url:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"preview:{sound_id}:{quote(query)}:{quote(audio_url)}",
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title="▶️ Preview",
                    can_play=True,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=f"search_result:{sound_id}:{quote(query)}",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=f"🎵 {name[:40]}",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _browse_noise_generator(self) -> BrowseMediaSource:
        """Browse noise generator options."""
        noise_types = [
            ("white", "⚪ White Noise", "Equal energy at all frequencies - great for sleep & focus"),
            ("pink", "🎀 Pink Noise", "Equal energy per octave - more natural than white noise"),
            ("brown", "🟤 Brown Noise", "Deeper, bass-heavy sound - very soothing"),
            ("fan", "🌀 Fan Noise", "Electric fan simulation with motor hum"),
            ("rain", "🌧️ Rain", "Realistic rainfall with droplet sounds"),
            ("ocean", "🌊 Ocean Waves", "Rhythmic wave patterns and surf"),
            ("wind", "💨 Wind", "Gusting wind with natural variation"),
        ]
        
        children = []
        for noise_type, title, description in noise_types:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"noise_generator:{noise_type}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=f"{title}",
                    can_play=False,
                    can_expand=True,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="noise_generator:",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title="🎛️ Noise Generator - Select a noise type",
            can_play=False,
            can_expand=True,
            children=children,
        )
    
    async def _browse_noise_duration(self, noise_type: str) -> BrowseMediaSource:
        """Browse duration options for a noise type."""
        # Define common durations in seconds
        durations = [
            (60, "1 minute"),
            (300, "5 minutes"),
            (600, "10 minutes"),
            (900, "15 minutes"),
            (1800, "30 minutes"),
            (3600, "1 hour"),
            (7200, "2 hours"),
            (10800, "3 hours"),
        ]
        
        # Get the display name for the noise type
        noise_names = {
            "white": "⚪ White Noise",
            "pink": "🎀 Pink Noise",
            "brown": "🟤 Brown Noise",
            "fan": "🌀 Fan Noise",
            "rain": "🌧️ Rain",
            "ocean": "🌊 Ocean Waves",
            "wind": "💨 Wind",
        }
        noise_name = noise_names.get(noise_type, noise_type.title())
        
        children = []
        for duration_sec, duration_label in durations:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"noise:{noise_type}:{duration_sec}",
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title=f"▶️ Play for {duration_label}",
                    can_play=True,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=f"noise_generator:{noise_type}",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=f"{noise_name} - Select duration",
            can_play=False,
            can_expand=True,
            children=children,
        )
    
    async def _generate_noise(self, noise_type: str, duration: int) -> str:
        """Generate noise and return the file path."""
        from .noise_generator import NoiseGenerator
        
        # Create temp directory for generated audio
        temp_dir = Path(tempfile.gettempdir()) / "ambient_sounds"
        temp_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        temp_file = temp_dir / f"{noise_type}_noise_{duration}s.wav"
        
        # Check if file already exists and is recent (within last hour)
        if temp_file.exists():
            file_age = time.time() - temp_file.stat().st_mtime
            if file_age < 3600:  # 1 hour
                _LOGGER.info("Using cached noise file: %s", temp_file)
                return str(temp_file)
        
        # Generate the noise
        generator = NoiseGenerator(duration=duration)
        wav_data = generator.generate_noise(noise_type, intensity=DEFAULT_NOISE_INTENSITY)
        
        # Save to file
        with open(temp_file, "wb") as f:
            f.write(wav_data)
        
        _LOGGER.info("Generated noise saved to %s", temp_file)
        return str(temp_file)

    async def _get_favorite(self, favorite_id: str) -> dict | None:
        """Get a favorite by ID."""
        favorites = await self._get_all_favorites()
        return favorites.get(favorite_id)

    async def _get_all_favorites(self) -> dict:
        """Get all favorites from all config entries."""
        all_favorites = {}
        for entry_id, entry_data in self.hass.data.get(DOMAIN, {}).items():
            favorites = entry_data.get("favorites", {})
            all_favorites.update(favorites)
        return all_favorites

    async def _search_freesound(self, query: str) -> list:
        """Search Freesound for audio."""
        # Get the first available client
        for entry_id, entry_data in self.hass.data.get(DOMAIN, {}).items():
            client = entry_data.get("client")
            results_per_search = entry_data.get("results_per_search", 20)
            if client:
                try:
                    results = await client.search_audio(query, results_per_search)
                    return results
                except Exception as err:
                    _LOGGER.error("Error searching Freesound: %s", err)
                    return []
        
        _LOGGER.warning("No Freesound client available")
        return []
