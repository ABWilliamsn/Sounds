"""The Ambient Sound Synthesizer integration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PROFILE_NAME,
    CONF_PROFILES,
    DEFAULT_PROFILE_NAME,
    DOMAIN,
)
from .noise import coerce_profile
from .stream import SoundStreamManager, SoundStreamView


async def async_setup(hass: HomeAssistant, _: dict[str, Any]) -> bool:
    """Set up the integration via YAML (not supported)."""
    hass.data.setdefault(DOMAIN, {"entries": {}, "view": None})
    return True


def _profiles_from_entry(entry: ConfigEntry) -> list[dict[str, Any]]:
    """Return the active profiles for a config entry."""
    raw_profiles: list[dict[str, Any]]
    if CONF_PROFILES in entry.options:
        raw_profiles = entry.options[CONF_PROFILES]
    else:
        raw_profiles = entry.data.get(CONF_PROFILES, [])

    profiles: list[dict[str, Any]] = []
    for raw_profile in raw_profiles:
        name = str(raw_profile.get(CONF_PROFILE_NAME, DEFAULT_PROFILE_NAME))
        cleaned = coerce_profile(raw_profile)
        cleaned[CONF_PROFILE_NAME] = name
        profiles.append(cleaned)
    return deepcopy(profiles)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambient Sound Synthesizer from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {"entries": {}, "view": None})

    if domain_data.get("view") is None:
        view = SoundStreamView(hass)
        hass.http.register_view(view)
        domain_data["view"] = view

    profiles = _profiles_from_entry(entry)
    manager = SoundStreamManager(hass, entry.entry_id)
    manager.update_profiles(profiles)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    domain_data.setdefault("entries", {})[entry.entry_id] = {
        "title": entry.title or "Ambient Sound Synthesizer",
        "manager": manager,
    }

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Ambient Sound Synthesizer config entry."""
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return True

    entries = domain_data.get("entries", {})
    stored = entries.pop(entry.entry_id, None)
    if stored:
        manager: SoundStreamManager = stored["manager"]
        await manager.async_shutdown()
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry options updates."""
    domain_data = hass.data.get(DOMAIN, {})
    entries = domain_data.get("entries", {})
    stored = entries.get(entry.entry_id)
    if not stored:
        return

    manager: SoundStreamManager = stored["manager"]
    profiles = _profiles_from_entry(entry)
    manager.update_profiles(profiles)

    # Media source instances read directly from hass.data; nothing else needed.
