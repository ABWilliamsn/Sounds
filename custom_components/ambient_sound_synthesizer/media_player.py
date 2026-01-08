"""Media player platform for Ambient Sound Synthesizer integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ambient Sound Synthesizer media player."""
    async_add_entities([AmbientSoundSynthesizerMediaPlayer(entry)], True)


class AmbientSoundSynthesizerMediaPlayer(MediaPlayerEntity):
    """Representation of an Ambient Sound Synthesizer media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the media player."""
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Ambient Sound Synthesizer",
            "model": "Virtual Sound Generator",
        }
        self._state = MediaPlayerState.OFF
        self._volume = entry.options.get("volume", 50) / 100.0
        self._sound_type = entry.options.get("sound_type", "rain")
        self._intensity = entry.options.get("intensity", 50)

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the media player."""
        return self._state

    @property
    def volume_level(self) -> float:
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode."""
        return self._sound_type

    @property
    def sound_mode_list(self) -> list[str] | None:
        """Return the list of available sound modes."""
        return ["rain", "ocean", "forest", "wind", "white_noise", "brown_noise"]

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
        _LOGGER.info("Ambient Sound Synthesizer turned on")

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        self._state = MediaPlayerState.OFF
        self.async_write_ha_state()
        _LOGGER.info("Ambient Sound Synthesizer turned off")

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        self._volume = volume
        self.async_write_ha_state()
        _LOGGER.info("Volume set to %s", volume)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select sound mode."""
        if self.sound_mode_list and sound_mode in self.sound_mode_list:
            self._sound_type = sound_mode
            self.async_write_ha_state()
            _LOGGER.info("Sound mode set to %s", sound_mode)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "sound_type": self._sound_type,
            "intensity": self._intensity,
        }

    async def async_update(self) -> None:
        """Update the entity."""
        # Update from config entry options
        self._volume = self._entry.options.get("volume", 50) / 100.0
        self._sound_type = self._entry.options.get("sound_type", "rain")
        self._intensity = self._entry.options.get("intensity", 50)
