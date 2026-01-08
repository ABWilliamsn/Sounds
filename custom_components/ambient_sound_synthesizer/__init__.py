"""The Ambient Sound Synthesizer integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, SOUND_TYPES, get_sound_url

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

SERVICE_PLAY_SOUND = "play_sound"
SERVICE_STOP_SOUND = "stop_sound"

PLAY_SOUND_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
        vol.Required("sound_type"): vol.In(SOUND_TYPES),
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
    
    # Check if services are already registered - only register once per domain
    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_SOUND):
        # Register services once for the domain
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

            # Get direct audio streaming URL
            media_content_id = get_sound_url(sound_type, intensity)
            
            _LOGGER.debug("Using audio URL: %s", media_content_id)

            # Call media_player.play_media service for each target player
            for entity_id in entity_ids:
                try:
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
                except (Exception) as err:
                    _LOGGER.error("Failed to play sound on %s: %s", entity_id, err)

            _LOGGER.info("Successfully started playing %s", sound_type)

        async def handle_stop_sound(call: ServiceCall) -> None:
            """Handle the stop_sound service call."""
            entity_ids = call.data["entity_id"]

            _LOGGER.info("Stopping sound on %s", entity_ids)

            # Call media_player.stop service for each target player
            for entity_id in entity_ids:
                try:
                    await hass.services.async_call(
                        "media_player",
                        "media_stop",
                        {
                            "entity_id": entity_id,
                        },
                        blocking=True,
                    )
                except (Exception) as err:
                    _LOGGER.error("Failed to stop sound on %s: %s", entity_id, err)

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

    _LOGGER.info("Setting up Ambient Sound Synthesizer integration")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    
    # Only unregister services if this is the last entry
    if len(hass.data[DOMAIN]) == 0:
        hass.services.async_remove(DOMAIN, SERVICE_PLAY_SOUND)
        hass.services.async_remove(DOMAIN, SERVICE_STOP_SOUND)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
