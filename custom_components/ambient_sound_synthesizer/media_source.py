"""Media Source implementation for Ambient Sound Synthesizer."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import BrowseMedia, MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SOUND_LIBRARY, get_sound_url

_LOGGER = logging.getLogger(__name__)


async def async_get_media_source(hass: HomeAssistant) -> AmbientSoundMediaSource:
    """Set up Ambient Sound media source."""
    return AmbientSoundMediaSource(hass)


class AmbientSoundMediaSource(MediaSource):
    """Provide ambient sounds from myNoise.net as media sources."""

    name: str = "Ambient Sound Synthesizer"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve media to a playable URL."""
        sound_id = item.identifier

        if sound_id not in SOUND_LIBRARY:
            raise Unresolvable(f"Unknown sound: {sound_id}")

        sound = SOUND_LIBRARY[sound_id]
        url = get_sound_url(sound_id)

        _LOGGER.info(
            "Resolving ambient sound: %s -> %s",
            sound["name"],
            url,
        )

        return PlayMedia(url, "audio/mpeg")

    async def async_browse_media(
        self,
        item: MediaSourceItem,
    ) -> BrowseMediaSource:
        """Browse media."""
        # Root level - show all sounds
        children = []
        for sound_id, sound in SOUND_LIBRARY.items():
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=sound_id,
                    media_class=MediaClass.MUSIC,
                    media_content_type=MediaType.MUSIC,
                    title=sound["name"],
                    can_play=True,
                    can_expand=False,
                    thumbnail=None,
                )
            )

        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="",
            media_class=MediaClass.DIRECTORY,
            media_content_type="library",
            title="Ambient Sound Synthesizer",
            can_play=False,
            can_expand=True,
            children=children,
        )
