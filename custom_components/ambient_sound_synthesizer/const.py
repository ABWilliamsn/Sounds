"""Constants for the Ambient Sounds integration."""

DOMAIN = "ambient_sounds"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_RESULTS_PER_SEARCH = "results_per_search"

# Default values
# Freesound API allows up to 150 results per page
DEFAULT_RESULTS_PER_SEARCH = 20
MIN_RESULTS_PER_SEARCH = 1
MAX_RESULTS_PER_SEARCH = 150

# Storage keys
STORAGE_KEY = f"{DOMAIN}_favorites"
STORAGE_VERSION = 1

# Freesound API endpoints
# Freesound provides direct access to audio files with a free API key
FREESOUND_API_BASE = "https://freesound.org/apiv2"

