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
# Note: Pixabay's API primarily supports images and videos
# The free tier may have limited or no audio support
PIXABAY_API_BASE = "https://pixabay.com/api/"

