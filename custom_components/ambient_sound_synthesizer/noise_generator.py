"""Noise generator for creating various ambient sounds."""
from __future__ import annotations

import io
import logging
import math
import wave
from typing import Any

import numpy as np

_LOGGER = logging.getLogger(__name__)

# Audio configuration
SAMPLE_RATE = 44100  # CD quality
DURATION = 60  # 60 seconds of audio
BITS_PER_SAMPLE = 16


class NoiseGenerator:
    """Generate various types of ambient noises."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, duration: int = DURATION) -> None:
        """Initialize the noise generator.
        
        Args:
            sample_rate: Sample rate in Hz (default: 44100)
            duration: Duration in seconds (default: 60)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = sample_rate * duration

    def generate_white_noise(self, intensity: float = 0.5) -> bytes:
        """Generate white noise.
        
        White noise has equal energy at all frequencies.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate random samples with uniform distribution
        noise = np.random.uniform(-1, 1, self.num_samples)
        noise = noise * intensity
        return self._to_wav_bytes(noise)

    def generate_pink_noise(self, intensity: float = 0.5) -> bytes:
        """Generate pink noise (1/f noise).
        
        Pink noise has equal energy per octave, sounds more natural than white noise.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate white noise
        white = np.random.randn(self.num_samples)
        
        # Apply 1/f filter using Voss-McCartney algorithm
        num_sources = 16
        values = np.zeros(num_sources)
        max_key = 0x1F  # 31 in binary
        
        pink = np.zeros(self.num_samples)
        for i in range(self.num_samples):
            # Determine which values to update
            last_key = i % 32
            key = (i + 1) % 32
            
            # XOR to find changed bits
            diff = last_key ^ key
            
            # Update changed values
            for j in range(num_sources):
                if diff & (1 << j):
                    values[j] = np.random.randn()
            
            # Sum all values for this sample
            pink[i] = values.sum()
        
        # Normalize and scale
        pink = pink / np.abs(pink).max()
        pink = pink * intensity
        return self._to_wav_bytes(pink)

    def generate_brown_noise(self, intensity: float = 0.5) -> bytes:
        """Generate brown noise (Brownian noise).
        
        Brown noise has more energy at lower frequencies, deeper sound than pink noise.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate white noise
        white = np.random.randn(self.num_samples)
        
        # Apply integration (cumulative sum) to get brown noise
        brown = np.cumsum(white)
        
        # Normalize and scale
        brown = brown / np.abs(brown).max()
        brown = brown * intensity
        return self._to_wav_bytes(brown)

    def generate_fan_noise(self, intensity: float = 0.5) -> bytes:
        """Generate fan noise.
        
        Fan noise is a combination of low-frequency hum and filtered noise.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate time array
        t = np.linspace(0, self.duration, self.num_samples, False)
        
        # Low frequency hum (motor sound) at 60 Hz and harmonics
        hum = (
            0.3 * np.sin(2 * np.pi * 60 * t) +
            0.2 * np.sin(2 * np.pi * 120 * t) +
            0.1 * np.sin(2 * np.pi * 180 * t)
        )
        
        # Add pink noise for air movement sound
        pink = np.random.randn(self.num_samples)
        # Simple moving average filter to smooth the noise
        window_size = 100
        pink_filtered = np.convolve(pink, np.ones(window_size)/window_size, mode='same')
        
        # Combine hum and filtered noise
        fan = 0.4 * hum + 0.6 * pink_filtered
        
        # Normalize and scale
        fan = fan / np.abs(fan).max()
        fan = fan * intensity
        return self._to_wav_bytes(fan)

    def generate_rain_noise(self, intensity: float = 0.5) -> bytes:
        """Generate rain noise.
        
        Rain noise simulates rainfall with random droplets and ambient background.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Start with filtered white noise for background
        rain = np.random.randn(self.num_samples)
        
        # Apply bandpass characteristics (emphasize mid-high frequencies)
        # Simple high-pass filter
        alpha = 0.95
        rain_filtered = np.zeros_like(rain)
        for i in range(1, len(rain)):
            rain_filtered[i] = alpha * (rain_filtered[i-1] + rain[i] - rain[i-1])
        
        # Add random droplet impacts (short bursts)
        num_droplets = int(self.duration * 500)  # ~500 droplets per second
        for _ in range(num_droplets):
            pos = np.random.randint(0, self.num_samples - 100)
            # Create a short burst with exponential decay
            burst_length = np.random.randint(10, 50)
            burst = np.random.randn(burst_length) * np.exp(-np.linspace(0, 5, burst_length))
            rain_filtered[pos:pos+burst_length] += burst * 0.3
        
        # Normalize and scale
        rain_filtered = rain_filtered / np.abs(rain_filtered).max()
        rain_filtered = rain_filtered * intensity
        return self._to_wav_bytes(rain_filtered)

    def generate_ocean_noise(self, intensity: float = 0.5) -> bytes:
        """Generate ocean wave noise.
        
        Ocean noise simulates waves with slow rhythmic patterns and background ambience.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate time array
        t = np.linspace(0, self.duration, self.num_samples, False)
        
        # Create wave patterns with multiple frequencies for natural variation
        # Slow waves (0.1-0.3 Hz)
        waves = (
            0.4 * np.sin(2 * np.pi * 0.1 * t + np.random.random() * 2 * np.pi) +
            0.3 * np.sin(2 * np.pi * 0.15 * t + np.random.random() * 2 * np.pi) +
            0.2 * np.sin(2 * np.pi * 0.22 * t + np.random.random() * 2 * np.pi) +
            0.1 * np.sin(2 * np.pi * 0.28 * t + np.random.random() * 2 * np.pi)
        )
        
        # Normalize wave envelope to 0-1 range
        waves = (waves - waves.min()) / (waves.max() - waves.min())
        
        # Generate filtered noise for wave texture
        noise = np.random.randn(self.num_samples)
        # Low-pass filter for deep, rumbling sound
        window_size = 200
        noise_filtered = np.convolve(noise, np.ones(window_size)/window_size, mode='same')
        
        # Modulate noise with wave envelope
        ocean = waves * noise_filtered
        
        # Add some constant background ambience
        ocean += 0.2 * noise_filtered
        
        # Normalize and scale
        ocean = ocean / np.abs(ocean).max()
        ocean = ocean * intensity
        return self._to_wav_bytes(ocean)

    def generate_wind_noise(self, intensity: float = 0.5) -> bytes:
        """Generate wind noise.
        
        Wind noise simulates gusting wind with varying intensity.
        
        Args:
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
        """
        # Generate time array
        t = np.linspace(0, self.duration, self.num_samples, False)
        
        # Create wind gusts with slow variation
        gusts = (
            0.5 * (1 + np.sin(2 * np.pi * 0.05 * t)) +
            0.3 * (1 + np.sin(2 * np.pi * 0.12 * t + 1.5)) +
            0.2 * (1 + np.sin(2 * np.pi * 0.19 * t + 2.3))
        )
        # Normalize to 0.3-1.0 range (always some wind)
        gusts = 0.3 + 0.7 * (gusts - gusts.min()) / (gusts.max() - gusts.min())
        
        # Generate filtered noise for wind sound
        wind = np.random.randn(self.num_samples)
        
        # Apply low-pass filter for whooshing sound
        window_size = 150
        wind_filtered = np.convolve(wind, np.ones(window_size)/window_size, mode='same')
        
        # Modulate with gust envelope
        wind_modulated = gusts * wind_filtered
        
        # Add some high-frequency content for realism
        high_freq = np.random.randn(self.num_samples) * 0.1
        wind_final = wind_modulated + high_freq
        
        # Normalize and scale
        wind_final = wind_final / np.abs(wind_final).max()
        wind_final = wind_final * intensity
        return self._to_wav_bytes(wind_final)

    def _to_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """Convert numpy audio data to WAV format bytes.
        
        Args:
            audio_data: Audio data as numpy array (float, -1 to 1)
            
        Returns:
            WAV file as bytes
        """
        # Convert float audio to 16-bit PCM
        max_int16 = 2**(BITS_PER_SAMPLE - 1) - 1
        audio_int16 = np.int16(audio_data * max_int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(BITS_PER_SAMPLE // 8)  # 16-bit = 2 bytes
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        wav_buffer.seek(0)
        return wav_buffer.read()

    def generate_noise(self, noise_type: str, intensity: float = 0.5) -> bytes:
        """Generate noise of specified type.
        
        Args:
            noise_type: Type of noise (white, pink, brown, fan, rain, ocean, wind)
            intensity: Volume intensity from 0.0 to 1.0
            
        Returns:
            WAV audio data as bytes
            
        Raises:
            ValueError: If noise_type is not recognized
        """
        generators = {
            "white": self.generate_white_noise,
            "pink": self.generate_pink_noise,
            "brown": self.generate_brown_noise,
            "fan": self.generate_fan_noise,
            "rain": self.generate_rain_noise,
            "ocean": self.generate_ocean_noise,
            "wind": self.generate_wind_noise,
        }
        
        generator = generators.get(noise_type.lower())
        if generator is None:
            raise ValueError(
                f"Unknown noise type: {noise_type}. "
                f"Valid types: {', '.join(generators.keys())}"
            )
        
        _LOGGER.info("Generating %s noise with intensity %.2f", noise_type, intensity)
        return generator(intensity)
