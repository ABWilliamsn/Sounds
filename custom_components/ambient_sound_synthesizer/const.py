"""Constants for the Ambient Sound Synthesizer integration."""

DOMAIN = "ambient_sound_synthesizer"

# Ambient sound streaming URLs from public sources
# These are long-form looping audio streams that work with media players
SOUND_LIBRARY = {
    "rain": {
        "name": "Rain",
        "description": "Soothing rain sounds",
        "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",  # Rain sound loop
    },
    "ocean": {
        "name": "Ocean Waves",
        "description": "Calming ocean waves",
        "url": "https://cdn.pixabay.com/download/audio/2022/06/07/audio_b9bd4170e4.mp3",  # Ocean waves
    },
    "forest": {
        "name": "Forest",
        "description": "Peaceful forest ambience",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_4a668c6c21.mp3",  # Birds and forest
    },
    "wind": {
        "name": "Wind",
        "description": "Gentle wind sounds",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/24/audio_15234dd5c2.mp3",  # Wind ambience
    },
    "white_noise": {
        "name": "White Noise",
        "description": "Classic white noise",
        "url": "https://cdn.pixabay.com/download/audio/2021/08/09/audio_c49bd8c20a.mp3",  # White noise
    },
    "brown_noise": {
        "name": "Brown Noise",
        "description": "Deep brown noise",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_2702bc6ea2.mp3",  # Brown noise
    },
    "fire": {
        "name": "Fireplace",
        "description": "Crackling fire",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_7193938e79.mp3",  # Fire crackling
    },
    "thunder": {
        "name": "Thunder",
        "description": "Distant thunder",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/20/audio_13619db5d9.mp3",  # Thunder and rain
    },
    "river": {
        "name": "River Stream",
        "description": "Flowing river water",
        "url": "https://cdn.pixabay.com/download/audio/2022/05/13/audio_c610d02d41.mp3",  # River stream
    },
    "cafe": {
        "name": "Cafe Restaurant",
        "description": "Busy cafe ambience",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_805ef08a54.mp3",  # Restaurant ambience
    },
}

SOUND_TYPES = list(SOUND_LIBRARY.keys())


def get_sound_url(sound_type: str, intensity: int = 50) -> str:
    """
    Get the streaming URL for a sound type.
    
    Note: The intensity parameter is kept for API compatibility but doesn't
    affect the output since we're using pre-recorded loops. In a future version,
    this could be used to select different variations or adjust volume.
    
    Args:
        sound_type: The sound type (e.g., "rain", "ocean")
        intensity: Intensity level (0-100) - currently not used
    
    Returns:
        Direct audio streaming URL
    """
    if sound_type not in SOUND_LIBRARY:
        # Default to rain if unknown type
        sound_type = "rain"
    
    return SOUND_LIBRARY[sound_type]["url"]

