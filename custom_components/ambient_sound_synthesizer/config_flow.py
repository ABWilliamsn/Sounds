"""Config flow for Ambient Sound Synthesizer integration."""
import logging
import os
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ambient_sound_synthesizer"

DEFAULT_OUTPUT_DIR = "/config/www/ambient_sounds"


class AmbientSoundSynthesizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambient Sound Synthesizer."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the output directory
            output_dir = user_input.get("output_directory", DEFAULT_OUTPUT_DIR)
            
            # Check if we can create the directory
            try:
                await self.hass.async_add_executor_job(os.makedirs, output_dir, 0o755, True)
                
                # Check if only one instance is configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title="Ambient Sound Synthesizer",
                    data=user_input
                )
            except OSError as e:
                _LOGGER.error("Could not create output directory: %s", str(e))
                errors["base"] = "cannot_create_directory"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("output_directory", default=DEFAULT_OUTPUT_DIR): cv.string,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return AmbientSoundSynthesizerOptionsFlow(config_entry)


class AmbientSoundSynthesizerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Ambient Sound Synthesizer."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            output_dir = user_input.get("output_directory")
            
            # Validate the output directory
            try:
                await self.hass.async_add_executor_job(os.makedirs, output_dir, 0o755, True)
                return self.async_create_entry(title="", data=user_input)
            except OSError as e:
                _LOGGER.error("Could not create output directory: %s", str(e))
                errors["base"] = "cannot_create_directory"

        current_output_dir = self.config_entry.options.get(
            "output_directory",
            self.config_entry.data.get("output_directory", DEFAULT_OUTPUT_DIR)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("output_directory", default=current_output_dir): cv.string,
            }),
            errors=errors,
        )
