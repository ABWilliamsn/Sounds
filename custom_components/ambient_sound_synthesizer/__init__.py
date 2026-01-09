"""The Ambient Sounds integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
import voluptuous as vol

from .const import (
    CONF_API_KEY,
    CONF_RESULTS_PER_SEARCH,
    DEFAULT_RESULTS_PER_SEARCH,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .freesound_client import FreesoundClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

SERVICE_PLAY_FAVORITE = "play_favorite"
SERVICE_STOP_SOUND = "stop_sound"
SERVICE_ADD_FAVORITE = "add_favorite"
SERVICE_REMOVE_FAVORITE = "remove_favorite"

PLAY_FAVORITE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
        vol.Required("favorite_id"): str,
        vol.Optional("volume", default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

STOP_SOUND_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
    }
)

ADD_FAVORITE_SCHEMA = vol.Schema(
    {
        vol.Required("sound_id"): str,
        vol.Required("name"): str,
        vol.Required("url"): str,
        vol.Optional("tags"): str,
        vol.Optional("duration"): int,
    }
)

REMOVE_FAVORITE_SCHEMA = vol.Schema(
    {
        vol.Required("favorite_id"): str,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambient Sounds from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Get API key and settings from config entry
    api_key = entry.data[CONF_API_KEY]
    results_per_search = entry.options.get(
        CONF_RESULTS_PER_SEARCH,
        entry.data.get(CONF_RESULTS_PER_SEARCH, DEFAULT_RESULTS_PER_SEARCH),
    )
    
    # Create Freesound client
    session = async_get_clientsession(hass)
    client = FreesoundClient(api_key, session)
    
    # Create favorites storage
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    favorites_data = await store.async_load() or {"favorites": {}}
    
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "store": store,
        "favorites": favorites_data.get("favorites", {}),
        "results_per_search": results_per_search,
    }
    
    # Register services (only once per domain)
    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_FAVORITE):
        
        async def handle_play_favorite(call: ServiceCall) -> None:
            """Handle the play_favorite service call."""
            entity_ids = call.data["entity_id"]
            favorite_id = call.data["favorite_id"]
            volume = call.data.get("volume", 0.5)
            
            # Find the favorite
            favorite = None
            for entry_id, entry_data in hass.data[DOMAIN].items():
                if favorite_id in entry_data.get("favorites", {}):
                    favorite = entry_data["favorites"][favorite_id]
                    break
            
            if not favorite:
                _LOGGER.error("Favorite %s not found", favorite_id)
                return
            
            _LOGGER.info("Playing favorite '%s' to %s", favorite["name"], entity_ids)
            
            # Play the audio
            for entity_id in entity_ids:
                try:
                    await hass.services.async_call(
                        "media_player",
                        "play_media",
                        {
                            "entity_id": entity_id,
                            "media_content_id": favorite["url"],
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
                except Exception as err:
                    _LOGGER.error("Failed to play favorite on %s: %s", entity_id, err)
        
        async def handle_stop_sound(call: ServiceCall) -> None:
            """Handle the stop_sound service call."""
            entity_ids = call.data["entity_id"]
            
            _LOGGER.info("Stopping sound on %s", entity_ids)
            
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
                except Exception as err:
                    _LOGGER.error("Failed to stop sound on %s: %s", entity_id, err)
        
        async def handle_add_favorite(call: ServiceCall) -> None:
            """Handle the add_favorite service call."""
            sound_id = call.data["sound_id"]
            name = call.data["name"]
            url = call.data["url"]
            tags = call.data.get("tags", "")
            duration = call.data.get("duration", 0)
            
            # Add to all config entries (in case there are multiple)
            for entry_id, entry_data in hass.data[DOMAIN].items():
                favorites = entry_data.get("favorites", {})
                favorites[sound_id] = {
                    "id": sound_id,
                    "name": name,
                    "url": url,
                    "tags": tags,
                    "duration": duration,
                }
                entry_data["favorites"] = favorites
                
                # Save to storage
                store = entry_data["store"]
                await store.async_save({"favorites": favorites})
            
            _LOGGER.info("Added favorite: %s", name)
        
        async def handle_remove_favorite(call: ServiceCall) -> None:
            """Handle the remove_favorite service call."""
            favorite_id = call.data["favorite_id"]
            
            # Remove from all config entries
            for entry_id, entry_data in hass.data[DOMAIN].items():
                favorites = entry_data.get("favorites", {})
                if favorite_id in favorites:
                    del favorites[favorite_id]
                    entry_data["favorites"] = favorites
                    
                    # Save to storage
                    store = entry_data["store"]
                    await store.async_save({"favorites": favorites})
            
            _LOGGER.info("Removed favorite: %s", favorite_id)
        
        # Register services
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_FAVORITE,
            handle_play_favorite,
            schema=PLAY_FAVORITE_SCHEMA,
        )
        
        hass.services.async_register(
            DOMAIN,
            SERVICE_STOP_SOUND,
            handle_stop_sound,
            schema=STOP_SOUND_SCHEMA,
        )
        
        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_FAVORITE,
            handle_add_favorite,
            schema=ADD_FAVORITE_SCHEMA,
        )
        
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_FAVORITE,
            handle_remove_favorite,
            schema=REMOVE_FAVORITE_SCHEMA,
        )
    
    _LOGGER.info("Setting up Ambient Sounds integration")
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    
    # Only unregister services if this is the last entry
    if len(hass.data[DOMAIN]) == 0:
        hass.services.async_remove(DOMAIN, SERVICE_PLAY_FAVORITE)
        hass.services.async_remove(DOMAIN, SERVICE_STOP_SOUND)
        hass.services.async_remove(DOMAIN, SERVICE_ADD_FAVORITE)
        hass.services.async_remove(DOMAIN, SERVICE_REMOVE_FAVORITE)
    
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
