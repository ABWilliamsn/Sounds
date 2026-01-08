"""Config flow for Ambient Sound Synthesizer integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    ACTION_ADD,
    ACTION_EDIT,
    ACTION_FINISH,
    ACTION_REMOVE,
    ALL_DISPLAY_LABELS,
    ALL_SUBTYPES,
    CONF_ACTION,
    CONF_PROFILE_NAME,
    CONF_PROFILE_PARAMETERS,
    CONF_PROFILE_SUBTYPE,
    CONF_PROFILE_TYPE,
    CONF_PROFILES,
    CONF_SEED,
    CONF_VOLUME,
    DEFAULT_PROFILE_NAME,
    DEFAULT_VOLUME,
    DOMAIN,
    PROFILE_ROUTE,
    normalize_subtype,
)
from .noise import coerce_profile

_LOGGER = __import__("logging").getLogger(__name__)


def _subtype_label(subtype: str) -> str:
    """Return display label for a subtype."""
    return ALL_DISPLAY_LABELS.get(subtype, subtype)


def _resolve_profile_type(subtype: str) -> str:
    """Determine profile type from subtype."""
    if subtype in ["white", "pink", "brown"]:
        return "noise"
    return "ambient"


class AmbientSoundSynthesizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambient Sound Synthesizer."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._profiles: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> dict[str, Any]:
        """Handle the initial step - create initial profiles."""
        if user_input is not None:
            # Create default profile
            default_profiles = [
                {
                    CONF_PROFILE_NAME: "White Noise",
                    CONF_PROFILE_TYPE: "noise",
                    CONF_PROFILE_SUBTYPE: "white",
                    CONF_PROFILE_PARAMETERS: {
                        CONF_VOLUME: DEFAULT_VOLUME,
                    },
                },
            ]
            
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title="Ambient Sound Synthesizer",
                data={CONF_PROFILES: default_profiles},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "description": "Set up Ambient Sound Synthesizer. You can manage sound profiles after setup."
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._profiles: list[dict[str, Any]] = []
        self._edit_index: int | None = None

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> dict[str, Any]:
        """Manage the options."""
        return await self.async_step_profile_list(user_input)

    async def async_step_profile_list(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show list of profiles and actions."""
        if user_input is not None:
            action = user_input.get(CONF_ACTION)
            
            if action == ACTION_FINISH:
                return self.async_create_entry(title="", data={CONF_PROFILES: self._profiles})
            
            if action == ACTION_ADD:
                return await self.async_step_profile_edit()
            
            # Handle edit/remove for specific profile
            for idx, profile in enumerate(self._profiles):
                profile_name = profile.get(CONF_PROFILE_NAME, f"Profile {idx + 1}")
                if action == f"edit_{idx}":
                    self._edit_index = idx
                    return await self.async_step_profile_edit()
                if action == f"remove_{idx}":
                    self._profiles.pop(idx)
                    return await self.async_step_profile_list()

        # Load current profiles
        self._profiles = list(
            self.config_entry.options.get(
                CONF_PROFILES, self.config_entry.data.get(CONF_PROFILES, [])
            )
        )

        # Build profile list display
        profile_descriptions = []
        actions = {}
        
        for idx, profile in enumerate(self._profiles):
            name = profile.get(CONF_PROFILE_NAME, f"Profile {idx + 1}")
            subtype = profile.get(CONF_PROFILE_SUBTYPE, "white")
            volume = profile.get(CONF_PROFILE_PARAMETERS, {}).get(CONF_VOLUME, 0.5)
            
            profile_descriptions.append(
                f"**{name}** - {_subtype_label(subtype)} (Volume: {int(volume * 100)}%)"
            )
            actions[f"edit_{idx}"] = f"Edit {name}"
            actions[f"remove_{idx}"] = f"Remove {name}"

        if not profile_descriptions:
            profile_descriptions.append("*No profiles configured*")

        actions[ACTION_ADD] = "Add New Profile"
        actions[ACTION_FINISH] = "Finish"

        return self.async_show_form(
            step_id="profile_list",
            data_schema=vol.Schema({
                vol.Required(CONF_ACTION): vol.In(actions)
            }),
            description_placeholders={
                "profiles": "\n".join(profile_descriptions)
            },
        )

    async def async_step_profile_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Edit or create a profile."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Normalize subtype
            subtype = normalize_subtype(user_input.get(CONF_PROFILE_SUBTYPE, "white"))
            profile_type = _resolve_profile_type(subtype)
            
            profile = {
                CONF_PROFILE_NAME: user_input[CONF_PROFILE_NAME],
                CONF_PROFILE_TYPE: profile_type,
                CONF_PROFILE_SUBTYPE: subtype,
                CONF_PROFILE_PARAMETERS: {
                    CONF_VOLUME: user_input[CONF_VOLUME],
                },
            }
            
            seed = user_input.get(CONF_SEED, "").strip()
            if seed:
                profile[CONF_PROFILE_PARAMETERS][CONF_SEED] = seed
            
            # Validate and coerce
            profile = coerce_profile(profile)
            
            if self._edit_index is not None:
                self._profiles[self._edit_index] = profile
                self._edit_index = None
            else:
                self._profiles.append(profile)
            
            return await self.async_step_profile_list()

        # Get defaults for editing
        defaults = {}
        if self._edit_index is not None and self._edit_index < len(self._profiles):
            existing = self._profiles[self._edit_index]
            defaults = {
                CONF_PROFILE_NAME: existing.get(CONF_PROFILE_NAME, DEFAULT_PROFILE_NAME),
                CONF_PROFILE_SUBTYPE: existing.get(CONF_PROFILE_SUBTYPE, "white"),
                CONF_VOLUME: existing.get(CONF_PROFILE_PARAMETERS, {}).get(CONF_VOLUME, DEFAULT_VOLUME),
                CONF_SEED: existing.get(CONF_PROFILE_PARAMETERS, {}).get(CONF_SEED, ""),
            }

        # Build subtype options with labels
        subtype_options = {subtype: _subtype_label(subtype) for subtype in ALL_SUBTYPES}

        return self.async_show_form(
            step_id="profile_edit",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_PROFILE_NAME,
                    default=defaults.get(CONF_PROFILE_NAME, DEFAULT_PROFILE_NAME)
                ): str,
                vol.Required(
                    CONF_PROFILE_SUBTYPE,
                    default=defaults.get(CONF_PROFILE_SUBTYPE, "white")
                ): vol.In(subtype_options),
                vol.Required(
                    CONF_VOLUME,
                    default=defaults.get(CONF_VOLUME, DEFAULT_VOLUME)
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                vol.Optional(
                    CONF_SEED,
                    default=defaults.get(CONF_SEED, "")
                ): str,
            }),
            errors=errors,
        )
