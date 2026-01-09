"""Constants for the Ambient Sounds integration."""

DOMAIN = "ambient_sounds"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_RESULTS_PER_SEARCH = "results_per_search"

# Default values
DEFAULT_RESULTS_PER_SEARCH = 20
MAX_RESULTS_PER_SEARCH = 100

# Storage keys
STORAGE_KEY = f"{DOMAIN}_favorites"
STORAGE_VERSION = 1

# Pixabay API endpoints
PIXABAY_API_BASE = "https://pixabay.com/api/"
PIXABAY_AUDIO_ENDPOINT = f"{PIXABAY_API_BASE}?key={{api_key}}&q={{query}}&audio_type=all&per_page={{per_page}}"

