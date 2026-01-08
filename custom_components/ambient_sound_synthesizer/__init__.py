"""The Ambient Sound Synthesizer integration."""
import logging
import os
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .sound_generator import AmbientSoundGenerator

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ambient_sound_synthesizer"

SERVICE_GENERATE_SOUND = "generate_sound"

ATTR_SOUND_TYPE = "sound_type"
ATTR_INTENSITY = "intensity"
ATTR_DURATION = "duration"
ATTR_FILENAME = "filename"

SOUND_TYPES = ["white", "pink", "brown", "rain", "wind", "fan"]
INTENSITIES = ["low", "medium", "high"]

SERVICE_GENERATE_SOUND_SCHEMA = vol.Schema({
    vol.Required(ATTR_SOUND_TYPE): vol.In(SOUND_TYPES),
    vol.Required(ATTR_INTENSITY): vol.In(INTENSITIES),
    vol.Required(ATTR_DURATION): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
    vol.Required(ATTR_FILENAME): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambient Sound Synthesizer from a config entry."""
    
    # Store the configuration
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "output_directory": entry.options.get(
            "output_directory",
            entry.data.get("output_directory", "/config/www/ambient_sounds")
        )
    }
    
    # Initialize the sound generator
    generator = AmbientSoundGenerator()
    
    async def handle_generate_sound(call: ServiceCall):
        """Handle the generate_sound service call."""
        sound_type = call.data[ATTR_SOUND_TYPE]
        intensity = call.data[ATTR_INTENSITY]
        duration = call.data[ATTR_DURATION]
        filename = call.data[ATTR_FILENAME]
        
        # Get the output directory from the first config entry
        output_dir = None
        for entry_id, data in hass.data[DOMAIN].items():
            if isinstance(data, dict) and "output_directory" in data:
                output_dir = data["output_directory"]
                break
        
        if not output_dir:
            _LOGGER.error("No output directory configured")
            return
        
        # Ensure the output directory exists
        try:
            await hass.async_add_executor_job(os.makedirs, output_dir, 0o755, True)
        except OSError as e:
            _LOGGER.error("Could not create output directory: %s", str(e))
            return
        
        # Add .wav extension if not present
        if not filename.endswith(".wav"):
            filename = f"{filename}.wav"
        
        output_path = os.path.join(output_dir, filename)
        
        _LOGGER.info(
            "Generating %s sound with %s intensity for %d seconds, saving to %s",
            sound_type, intensity, duration, output_path
        )
        
        # Generate the sound in an executor (blocking operation)
        success = await hass.async_add_executor_job(
            generator.generate_and_save,
            sound_type,
            intensity,
            duration,
            output_path
        )
        
        if success:
            _LOGGER.info("Successfully generated ambient sound: %s", output_path)
        else:
            _LOGGER.error("Failed to generate ambient sound")
    
    # Register the service
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_SOUND,
        handle_generate_sound,
        schema=SERVICE_GENERATE_SOUND_SCHEMA,
    )
    
    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the service if this is the last config entry
    if len(hass.data[DOMAIN]) == 1:
        hass.services.async_remove(DOMAIN, SERVICE_GENERATE_SOUND)
    
    # Remove the config entry data
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    # Update the stored configuration
    hass.data[DOMAIN][entry.entry_id] = {
        "output_directory": entry.options.get(
            "output_directory",
            entry.data.get("output_directory", "/config/www/ambient_sounds")
        )
    }
