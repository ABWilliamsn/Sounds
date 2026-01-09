"""Constants for the Ambient Sounds integration."""

DOMAIN = "ambient_sounds"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_RESULTS_PER_SEARCH = "results_per_search"

# Default values
# Pixabay API requires per_page to be between 3 and 200
DEFAULT_RESULTS_PER_SEARCH = 20
MIN_RESULTS_PER_SEARCH = 3
MAX_RESULTS_PER_SEARCH = 200

# Storage keys
STORAGE_KEY = f"{DOMAIN}_favorites"
STORAGE_VERSION = 1

# Pixabay API endpoints
# Note: Pixabay's API primarily supports images and videos
# The free tier may have limited or no audio support
PIXABAY_API_BASE = "https://pixabay.com/api/"

