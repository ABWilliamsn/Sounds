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
        # identifier format: "fav:{favorite_id}" or "search:{search_id}"
        if not item.identifier:
            raise Unresolvable("No identifier provided")
        
        parts = item.identifier.split(":", 1)
        if len(parts) != 2:
            raise Unresolvable(f"Invalid identifier: {item.identifier}")
        
        media_type, media_id = parts
        
        if media_type == "fav":
            # Playing a favorite
            favorite = await self._get_favorite(media_id)
            if not favorite:
                raise Unresolvable(f"Favorite not found: {media_id}")
            
            _LOGGER.info("Resolving favorite: %s", favorite["name"])
            return PlayMedia(favorite["url"], "audio/mpeg")
        
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
