"""Sound generation module for ambient sounds."""
import numpy as np
from scipy import signal
from scipy.io import wavfile
import logging

_LOGGER = logging.getLogger(__name__)

SAMPLE_RATE = 44100  # Standard CD quality


class AmbientSoundGenerator:
    """Generate various types of ambient sounds."""

    def __init__(self, sample_rate=SAMPLE_RATE):
        """Initialize the sound generator."""
        self.sample_rate = sample_rate

    def generate_white_noise(self, duration, intensity):
        """Generate white noise.
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        noise = np.random.normal(0, 1, samples)
        
        # Apply intensity scaling
        intensity_scale = {"low": 0.3, "medium": 0.6, "high": 0.9}
        noise *= intensity_scale.get(intensity, 0.6)
        
        return self._normalize_audio(noise)

    def generate_pink_noise(self, duration, intensity):
        """Generate pink noise (1/f noise) using Voss-McCartney algorithm.
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        
        # Voss-McCartney algorithm for more accurate pink noise
        pink = np.zeros(samples)
        state = np.zeros(7)
        
        for i in range(samples):
            white = np.random.uniform(-1, 1)
            state[0] = 0.99886 * state[0] + white * 0.0555179
            state[1] = 0.99332 * state[1] + white * 0.0750759
            state[2] = 0.96900 * state[2] + white * 0.1538520
            state[3] = 0.86650 * state[3] + white * 0.3104856
            state[4] = 0.55000 * state[4] + white * 0.5329522
            state[5] = -0.7616 * state[5] - white * 0.0168980
            pink[i] = (
                state[0] + state[1] + state[2] + state[3] + 
                state[4] + state[5] + state[6] + white * 0.5362
            )
            state[6] = white * 0.115926
        
        # Scale down pink noise
        pink *= 0.11
        
        # Apply intensity scaling
        intensity_scale = {"low": 0.3, "medium": 0.6, "high": 0.9}
        pink *= intensity_scale.get(intensity, 0.6)
        
        return self._normalize_audio(pink)

    def generate_brown_noise(self, duration, intensity):
        """Generate brown noise (Brownian noise, 1/f² noise).
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        
        # Generate brown noise with cumulative sum and damping
        brown = np.zeros(samples)
        value = 0.0
        
        for i in range(samples):
            white = np.random.uniform(-1, 1)
            value += white * 0.02
            # Clamp and apply damping to prevent drift
            value = np.clip(value, -1.0, 1.0) * 0.98
            brown[i] = value
        
        # Apply intensity scaling
        intensity_scale = {"low": 0.3, "medium": 0.6, "high": 0.9}
        brown *= intensity_scale.get(intensity, 0.6)
        
        return self._normalize_audio(brown)

    def generate_rain(self, duration, intensity):
        """Generate rain sound.
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        
        # Base pink noise for rain ambience
        base = self.generate_pink_noise(duration, intensity)
        
        # Add random "drops" - short bursts of high-frequency noise
        intensity_params = {
            "low": {"drop_rate": 0.5, "drop_intensity": 0.2},
            "medium": {"drop_rate": 1.0, "drop_intensity": 0.4},
            "high": {"drop_rate": 2.0, "drop_intensity": 0.6}
        }
        params = intensity_params.get(intensity, intensity_params["medium"])
        
        # Generate rain drops
        num_drops = int(duration * params["drop_rate"] * 100)
        for _ in range(num_drops):
            drop_pos = np.random.randint(0, samples - 1000)
            drop_length = np.random.randint(50, 500)
            drop = np.random.randn(drop_length) * params["drop_intensity"]
            
            # Apply envelope to drop
            envelope = np.exp(-np.linspace(0, 5, drop_length))
            drop *= envelope
            
            # Add drop to signal
            end_pos = min(drop_pos + drop_length, samples)
            base[drop_pos:end_pos] += drop[:end_pos - drop_pos]
        
        return self._normalize_audio(base)

    def generate_wind(self, duration, intensity):
        """Generate wind sound.
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        
        # Start with brown noise for low-frequency rumble
        wind = self.generate_brown_noise(duration, intensity)
        
        # Add modulation to simulate gusts
        intensity_params = {
            "low": {"mod_freq": 0.1, "mod_depth": 0.2},
            "medium": {"mod_freq": 0.2, "mod_depth": 0.4},
            "high": {"mod_freq": 0.3, "mod_depth": 0.6}
        }
        params = intensity_params.get(intensity, intensity_params["medium"])
        
        # Create modulation envelope
        t = np.linspace(0, duration, samples)
        modulation = 1 + params["mod_depth"] * np.sin(2 * np.pi * params["mod_freq"] * t)
        
        # Add random variations for gusts
        for _ in range(int(duration / 5)):
            gust_pos = np.random.randint(0, samples)
            gust_width = int(self.sample_rate * np.random.uniform(1, 3))
            gust_t = np.arange(gust_width) / self.sample_rate
            gust = 0.3 * np.sin(2 * np.pi * 0.5 * gust_t) * np.exp(-gust_t)
            
            end_pos = min(gust_pos + gust_width, samples)
            modulation[gust_pos:end_pos] += gust[:end_pos - gust_pos]
        
        wind *= modulation
        
        return self._normalize_audio(wind)

    def generate_fan(self, duration, intensity):
        """Generate fan sound.
        
        Args:
            duration: Duration in seconds
            intensity: Intensity level ('low', 'medium', 'high')
        
        Returns:
            numpy array of audio samples
        """
        samples = int(duration * self.sample_rate)
        
        # Base pink noise for fan ambience
        fan = self.generate_pink_noise(duration, intensity)
        
        # Add periodic modulation for blade rotation
        intensity_params = {
            "low": {"rotation_freq": 8, "mod_depth": 0.05},
            "medium": {"rotation_freq": 12, "mod_depth": 0.08},
            "high": {"rotation_freq": 16, "mod_depth": 0.1}
        }
        params = intensity_params.get(intensity, intensity_params["medium"])
        
        t = np.linspace(0, duration, samples)
        modulation = 1 + params["mod_depth"] * np.sin(2 * np.pi * params["rotation_freq"] * t)
        
        fan *= modulation
        
        return self._normalize_audio(fan)

    def _normalize_audio(self, audio):
        """Normalize audio to prevent clipping.
        
        Args:
            audio: numpy array of audio samples
        
        Returns:
            Normalized audio array
        """
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95  # Leave some headroom
        return audio

    def generate_and_save(self, sound_type, intensity, duration, output_path):
        """Generate and save an ambient sound to a file.
        
        Args:
            sound_type: Type of sound ('white', 'pink', 'brown', 'rain', 'wind', 'fan')
            intensity: Intensity level ('low', 'medium', 'high')
            duration: Duration in seconds
            output_path: Full path to output file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            _LOGGER.info(
                "Generating %s sound with %s intensity for %d seconds",
                sound_type, intensity, duration
            )
            
            # Generate the appropriate sound
            generators = {
                "white": self.generate_white_noise,
                "pink": self.generate_pink_noise,
                "brown": self.generate_brown_noise,
                "rain": self.generate_rain,
                "wind": self.generate_wind,
                "fan": self.generate_fan
            }
            
            generator = generators.get(sound_type)
            if not generator:
                _LOGGER.error("Unknown sound type: %s", sound_type)
                return False
            
            audio = generator(duration, intensity)
            
            # Convert to 16-bit PCM
            audio_int16 = np.int16(audio * 32767)
            
            # Save to WAV file
            wavfile.write(output_path, self.sample_rate, audio_int16)
            
            _LOGGER.info("Successfully saved audio to %s", output_path)
            return True
            
        except Exception as e:
            _LOGGER.error("Error generating sound: %s", str(e))
            return False
