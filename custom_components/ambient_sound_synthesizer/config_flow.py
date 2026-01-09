"""Config flow for Ambient Sounds integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_RESULTS_PER_SEARCH,
    DEFAULT_RESULTS_PER_SEARCH,
    DOMAIN,
    MAX_RESULTS_PER_SEARCH,
)
from .pixabay_client import PixabayClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Optional(
            CONF_RESULTS_PER_SEARCH, default=DEFAULT_RESULTS_PER_SEARCH
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_RESULTS_PER_SEARCH)),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambient Sounds."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Verify the API key
            session = async_get_clientsession(self.hass)
            client = PixabayClient(user_input[CONF_API_KEY], session)
            
            if await client.verify_api_key():
                # API key is valid
                await self.async_set_unique_id(user_input[CONF_API_KEY])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Ambient Sounds",
                    data=user_input,
                )
            else:
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Ambient Sounds."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Store config_entry in a private attribute instead of trying to set the property
        self._config_entry = config_entry

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry."""
        return self._config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_RESULTS_PER_SEARCH,
                        default=self.config_entry.options.get(
                            CONF_RESULTS_PER_SEARCH, DEFAULT_RESULTS_PER_SEARCH
                        ),
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=MAX_RESULTS_PER_SEARCH)
                    ),
                }
            ),
        )
