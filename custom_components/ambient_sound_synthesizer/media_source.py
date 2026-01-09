"""Media Source implementation for Ambient Sounds integration."""
from __future__ import annotations

import logging
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


async def async_get_media_source(hass: HomeAssistant) -> AmbientSoundsMediaSource:
    """Set up Ambient Sounds media source."""
    return AmbientSoundsMediaSource(hass)


class AmbientSoundsMediaSource(MediaSource):
    """Provide ambient sounds from Pixabay as media sources."""

    name: str = "Ambient Sounds"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve media to a playable URL."""
        # identifier format: "fav:{favorite_id}" or "preview:{sound_id}:{query}:{url}"
        if not item.identifier:
            raise Unresolvable("No identifier provided")
        
        parts = item.identifier.split(":", 1)
        if len(parts) != 2:
            raise Unresolvable(f"Invalid identifier: {item.identifier}")
        
        media_type, media_data = parts
        
        if media_type == "fav":
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
        
        # Parse identifier
        parts = item.identifier.split(":", 1)
        if len(parts) != 2:
            raise Unresolvable(f"Invalid identifier: {item.identifier}")
        
        category, value = parts
        
        if category == "favorites":
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
            raise Unresolvable(f"Invalid search result identifier: {value}")
        else:
            raise Unresolvable(f"Unknown category: {category}")

    async def _browse_root(self) -> BrowseMediaSource:
        """Browse root level."""
        children = [
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
                title="🔍 Search Pixabay",
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
                    identifier="empty",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title="No favorites yet. Search Pixabay to add some!",
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
            # Show search categories/suggestions
            suggestions = [
                "rain", "ocean", "forest", "wind", "thunder",
                "fire", "birds", "river", "waterfall", "cafe",
                "city", "nature", "ambient", "meditation", "relaxing"
            ]
            
            children = []
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
                title="🔍 Search Pixabay - Select a category",
                can_play=False,
                can_expand=True,
                children=children,
            )
        
        # Perform actual search
        results = await self._search_pixabay(query)
        
        children = []
        for result in results:
            sound_id = str(result["id"])
            duration = result.get("duration", 0)
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f" ({minutes}:{seconds:02d})" if duration else ""
            
            # Create a descriptive title
            title = result.get("tags", "Ambient Sound").replace(",", " •")
            if len(title) > 50:
                title = title[:47] + "..."
            
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"search_result:{sound_id}:{quote(query)}",
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title=f"{title}{duration_str}",
                    can_play=False,  # Can't play directly, must favorite first
                    can_expand=True,  # Show options to favorite
                    thumbnail=result.get("picture_id"),
                )
            )
        
        if not children:
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier="no_results",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=f"No results found for '{query}'. Try another search term.",
                    can_play=False,
                    can_expand=False,
                    thumbnail=None,
                )
            )
        
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=f"search:{quote(query)}",
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=f"🔍 Results for: {query}",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _browse_search_result(self, sound_id: str, query: str) -> BrowseMediaSource:
        """Browse a specific search result to show options."""
        # Get the search results again to find this specific sound
        results = await self._search_pixabay(query)
        
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
        
        tags = sound.get("tags", "No tags")
        
        # Get the audio URL
        audio_url = None
        for key in ["previewURL", "pageURL"]:
            if key in sound:
                audio_url = sound[key]
                break
        
        # Since we can't actually add favorites from Media Browser UI,
        # we'll show instructions
        info_text = (
            f"To add this sound to your favorites, use the service:\n\n"
            f"Service: ambient_sounds.add_favorite\n"
            f"Data:\n"
            f"  sound_id: \"{sound_id}\"\n"
            f"  name: \"{tags[:30]}\"\n"
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
                title=f"📋 Tags: {tags[:50]}",
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
                    title="▶️ Preview (if supported by player)",
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
            title=f"🎵 {tags[:40]}",
            can_play=False,
            can_expand=True,
            children=children,
        )

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

    async def _search_pixabay(self, query: str) -> list:
        """Search Pixabay for audio."""
        # Get the first available client
        for entry_id, entry_data in self.hass.data.get(DOMAIN, {}).items():
            client = entry_data.get("client")
            results_per_search = entry_data.get("results_per_search", 20)
            if client:
                try:
                    results = await client.search_audio(query, results_per_search)
                    return results
                except Exception as err:
                    _LOGGER.error("Error searching Pixabay: %s", err)
                    return []
        
        _LOGGER.warning("No Pixabay client available")
        return []
