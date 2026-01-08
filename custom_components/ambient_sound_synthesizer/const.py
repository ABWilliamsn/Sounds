"""Constants for the Ambient Sound Synthesizer integration."""

DOMAIN = "ambient_sound_synthesizer"

# myNoise.net sound generator IDs and display information
SOUND_LIBRARY = {
    "rain": {
        "name": "Rain",
        "generator": "rain",
        "description": "Soothing rain sounds",
    },
    "ocean": {
        "name": "Ocean Waves",
        "generator": "ocean",
        "description": "Calming ocean waves",
    },
    "forest": {
        "name": "Forest",
        "generator": "forest",
        "description": "Peaceful forest ambience",
    },
    "wind": {
        "name": "Wind",
        "generator": "wind",
        "description": "Gentle wind sounds",
    },
    "white_noise": {
        "name": "White Noise",
        "generator": "white",
        "description": "Classic white noise",
    },
    "brown_noise": {
        "name": "Brown Noise",
        "generator": "brown",
        "description": "Deep brown noise",
    },
    "fire": {
        "name": "Fireplace",
        "generator": "fire",
        "description": "Crackling fire",
    },
    "thunder": {
        "name": "Thunder",
        "generator": "thunder",
        "description": "Distant thunder",
    },
    "river": {
        "name": "River Stream",
        "generator": "stream",
        "description": "Flowing river water",
    },
    "cafe": {
        "name": "Cafe Restaurant",
        "generator": "cafe",
        "description": "Busy cafe ambience",
    },
}

# Derived constants
MYNOISE_GENERATORS = {key: val["generator"] for key, val in SOUND_LIBRARY.items()}
SOUND_TYPES = list(SOUND_LIBRARY.keys())


def generate_mynoise_url(sound_type: str, intensity: int = 50) -> str:
    """
    Generate a myNoise.net streaming URL with slider controls.
    
    myNoise.net URL format:
    https://mynoise.net/NoiseMachines/[generator]NoiseGenerator.php?l=[sliders]&a=1
    
    where [sliders] are 10 values from 0-100 separated by commas
    We'll use the intensity parameter to control all sliders uniformly.
    
    Args:
        sound_type: The sound type (e.g., "rain", "ocean")
        intensity: Intensity level (0-100) for all sliders
    
    Returns:
        myNoise.net streaming URL
    """
    # Validate intensity range
    intensity = max(0, min(100, intensity))
    
    generator = MYNOISE_GENERATORS.get(sound_type, "white")
    
    # Create slider values based on intensity
    # myNoise uses 10 sliders for different frequency bands
    # We'll set them all to the intensity value for a balanced sound
    slider_values = ",".join([str(intensity)] * 10)
    
    # a=1 enables animation mode for more natural variation
    url = f"https://mynoise.net/NoiseMachines/{generator}NoiseGenerator.php?l={slider_values}&a=1"
    
    return url

