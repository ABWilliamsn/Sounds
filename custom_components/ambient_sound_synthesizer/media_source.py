"""Media Source implementation for Ambient Sound Synthesizer."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import BrowseMedia, MediaClass, MediaType
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

# myNoise.net sound generator IDs and display names
SOUND_LIBRARY = {
    "rain": {
        "name": "Rain",
        "generator": "rain",
        "description": "Soothing rain sounds",
    },
    "ocean": {
        "name": "Ocean Waves",
        "generator": "ocean",
        "description": "Calming ocean waves",
    },
    "forest": {
        "name": "Forest",
        "generator": "forest",
        "description": "Peaceful forest ambience",
    },
    "wind": {
        "name": "Wind",
        "generator": "wind",
        "description": "Gentle wind sounds",
    },
    "white_noise": {
        "name": "White Noise",
        "generator": "white",
        "description": "Classic white noise",
    },
    "brown_noise": {
        "name": "Brown Noise",
        "generator": "brown",
        "description": "Deep brown noise",
    },
    "fire": {
        "name": "Fireplace",
        "generator": "fire",
        "description": "Crackling fire",
    },
    "thunder": {
        "name": "Thunder",
        "generator": "thunder",
        "description": "Distant thunder",
    },
    "river": {
        "name": "River Stream",
        "generator": "stream",
        "description": "Flowing river water",
    },
    "cafe": {
        "name": "Cafe Restaurant",
        "generator": "cafe",
        "description": "Busy cafe ambience",
    },
}


def generate_mynoise_url(generator: str, intensity: int = 50) -> str:
    """
    Generate a myNoise.net streaming URL with slider controls.
    
    Args:
        generator: The myNoise.net generator name
        intensity: Intensity level (0-100) for all sliders
    
    Returns:
        Direct streaming URL to myNoise.net audio
    """
    # Ensure intensity is within valid range
    intensity = max(0, min(100, intensity))
    
    # Create slider values based on intensity
    slider_values = ",".join([str(intensity)] * 10)
    
    # a=1 enables animation mode for more natural variation
    url = f"https://mynoise.net/NoiseMachines/{generator}NoiseGenerator.php?l={slider_values}&a=1"
    
    return url


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
        # Parse the identifier: format is "sound_id:intensity"
        # Default intensity is 50 if not specified
        parts = item.identifier.split(":")
        sound_id = parts[0]
        intensity = int(parts[1]) if len(parts) > 1 else 50

        if sound_id not in SOUND_LIBRARY:
            raise Unresolvable(f"Unknown sound: {sound_id}")

        sound = SOUND_LIBRARY[sound_id]
        url = generate_mynoise_url(sound["generator"], intensity)

        _LOGGER.info(
            "Resolving ambient sound: %s (intensity: %s) -> %s",
            sound["name"],
            intensity,
            url,
        )

        return PlayMedia(url, "audio/mpeg")

    async def async_browse_media(
        self,
        item: MediaSourceItem,
    ) -> BrowseMediaSource:
        """Browse media."""
        if item.identifier:
            # Browsing a specific sound - show intensity options
            sound_id = item.identifier
            if sound_id not in SOUND_LIBRARY:
                raise Unresolvable(f"Unknown sound: {sound_id}")

            sound = SOUND_LIBRARY[sound_id]
            
            # Create intensity level options
            children = []
            for intensity in [25, 50, 75, 100]:
                children.append(
                    BrowseMediaSource(
                        domain=DOMAIN,
                        identifier=f"{sound_id}:{intensity}",
                        media_class=MediaClass.MUSIC,
                        media_content_type=MediaType.MUSIC,
                        title=f"{sound['name']} - Intensity {intensity}%",
                        can_play=True,
                        can_expand=False,
                        thumbnail=None,
                    )
                )

            return BrowseMediaSource(
                domain=DOMAIN,
                identifier=sound_id,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=sound["name"],
                can_play=False,
                can_expand=True,
                children=children,
            )

        # Root level - show all sounds
        children = []
        for sound_id, sound in SOUND_LIBRARY.items():
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=sound_id,
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=sound["name"],
                    can_play=False,
                    can_expand=True,
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
