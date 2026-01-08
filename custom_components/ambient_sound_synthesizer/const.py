"""Constants for the Ambient Sound Synthesizer integration."""

from __future__ import annotations

DOMAIN = "ambient_sound_synthesizer"

# Configuration keys
CONF_PROFILES = "profiles"
CONF_PROFILE_NAME = "name"
CONF_PROFILE_TYPE = "type"
CONF_PROFILE_SUBTYPE = "subtype"
CONF_PROFILE_PARAMETERS = "parameters"

CONF_VOLUME = "volume"
CONF_SEED = "seed"

CONF_ACTION = "action"

# Default values
DEFAULT_PROFILE_NAME = "White noise"
DEFAULT_PROFILE_TYPE = "noise"
DEFAULT_PROFILE_SUBTYPE = "white"
DEFAULT_VOLUME = 0.5

# Profile types and subtypes
PROFILE_TYPES = ["noise", "ambient"]

NOISE_SUBTYPES = ["white", "pink", "brown"]
AMBIENT_SUBTYPES = ["rain", "wind", "fan"]

ALL_SUBTYPES = NOISE_SUBTYPES + AMBIENT_SUBTYPES

# Display labels for UI
NOISE_DISPLAY_LABELS = {
    "white": "White noise",
    "pink": "Pink noise",
    "brown": "Brown noise",
}

AMBIENT_DISPLAY_LABELS = {
    "rain": "Rain",
    "wind": "Wind",
    "fan": "Fan",
}

ALL_DISPLAY_LABELS = {**NOISE_DISPLAY_LABELS, **AMBIENT_DISPLAY_LABELS}

# Streaming configuration
MEDIA_MIME_TYPE = "audio/wav"
SAMPLE_RATE = 44100
STREAM_CHUNK_DURATION = 0.5  # seconds
STREAM_URL_PATH = f"/api/{DOMAIN}"
STDOUT_READ_SIZE = 32768

# Config flow actions
ACTION_ADD = "add"
ACTION_EDIT = "edit"
ACTION_REMOVE = "remove"
ACTION_FINISH = "finish"
PROFILE_ROUTE = "profile"


def normalize_subtype(value: str) -> str:
    """Return canonical subtype from UI label or raw value."""
    if not isinstance(value, str):
        return value
    
    candidate = value.strip()
    if candidate in ALL_SUBTYPES:
        return candidate
    
    # Check if it matches a display label
    lower = candidate.lower()
    for key, label in ALL_DISPLAY_LABELS.items():
        if lower == label.lower():
            return key
    
    return candidate
