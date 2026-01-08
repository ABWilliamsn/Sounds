"""The Ambient Sound Synthesizer integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

SERVICE_PLAY_SOUND = "play_sound"
SERVICE_STOP_SOUND = "stop_sound"

PLAY_SOUND_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
        vol.Required("sound_type"): vol.In(
            ["rain", "ocean", "forest", "wind", "white_noise", "brown_noise"]
        ),
        vol.Optional("volume", default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional("intensity", default=50): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),
    }
)

STOP_SOUND_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambient Sound Synthesizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "active_players": {},
    }

    _LOGGER.info("Setting up Ambient Sound Synthesizer integration")

    async def handle_play_sound(call: ServiceCall) -> None:
        """Handle the play_sound service call."""
        entity_ids = call.data["entity_id"]
        sound_type = call.data["sound_type"]
        volume = call.data.get("volume", 0.5)
        intensity = call.data.get("intensity", 50)

        _LOGGER.info(
            "Playing %s sound to %s (volume: %s, intensity: %s)",
            sound_type,
            entity_ids,
            volume,
            intensity,
        )

        # Store active playback info
        for entity_id in entity_ids:
            hass.data[DOMAIN][entry.entry_id]["active_players"][entity_id] = {
                "sound_type": sound_type,
                "volume": volume,
                "intensity": intensity,
            }

        # Generate audio URL based on sound type
        # In a real implementation, this would point to actual audio files or a stream
        audio_urls = {
            "rain": "https://example.com/sounds/rain.mp3",
            "ocean": "https://example.com/sounds/ocean.mp3",
            "forest": "https://example.com/sounds/forest.mp3",
            "wind": "https://example.com/sounds/wind.mp3",
            "white_noise": "https://example.com/sounds/white_noise.mp3",
            "brown_noise": "https://example.com/sounds/brown_noise.mp3",
        }

        media_content_id = audio_urls.get(sound_type)

        # Call media_player.play_media service for each target player
        for entity_id in entity_ids:
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": entity_id,
                    "media_content_id": media_content_id,
                    "media_content_type": "music",
                },
                blocking=True,
            )

            # Set volume if specified
            await hass.services.async_call(
                "media_player",
                "volume_set",
                {
                    "entity_id": entity_id,
                    "volume_level": volume,
                },
                blocking=True,
            )

        _LOGGER.info("Successfully started playing %s", sound_type)

    async def handle_stop_sound(call: ServiceCall) -> None:
        """Handle the stop_sound service call."""
        entity_ids = call.data["entity_id"]

        _LOGGER.info("Stopping sound on %s", entity_ids)

        # Remove from active players
        for entity_id in entity_ids:
            if entity_id in hass.data[DOMAIN][entry.entry_id]["active_players"]:
                del hass.data[DOMAIN][entry.entry_id]["active_players"][entity_id]

        # Call media_player.stop service for each target player
        for entity_id in entity_ids:
            await hass.services.async_call(
                "media_player",
                "media_stop",
                {
                    "entity_id": entity_id,
                },
                blocking=True,
            )

        _LOGGER.info("Successfully stopped sound")

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_SOUND,
        handle_play_sound,
        schema=PLAY_SOUND_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_SOUND,
        handle_stop_sound,
        schema=STOP_SOUND_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister services
    hass.services.async_remove(DOMAIN, SERVICE_PLAY_SOUND)
    hass.services.async_remove(DOMAIN, SERVICE_STOP_SOUND)

    hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
