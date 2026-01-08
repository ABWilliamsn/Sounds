"""Noise generation utilities for streaming ambient sounds."""

from __future__ import annotations

import random
import struct
import math
from typing import Any

from .const import (
    ALL_SUBTYPES,
    CONF_PROFILE_PARAMETERS,
    CONF_PROFILE_SUBTYPE,
    CONF_PROFILE_TYPE,
    CONF_SEED,
    CONF_VOLUME,
    DEFAULT_PROFILE_SUBTYPE,
    DEFAULT_PROFILE_TYPE,
    DEFAULT_VOLUME,
    PROFILE_TYPES,
    SAMPLE_RATE,
    normalize_subtype,
)

# Voss-McCartney pink noise algorithm coefficients
PINK_NOISE_COEFFS = [
    (0.99886, 0.0555179),
    (0.99332, 0.0750759),
    (0.96900, 0.1538520),
    (0.86650, 0.3104856),
    (0.55000, 0.5329522),
    (-0.7616, -0.0168980),
]
PINK_NOISE_WHITE_COEFF = 0.5362
PINK_NOISE_FINAL_STATE_COEFF = 0.115926
PINK_NOISE_SCALE = 0.11

# Brown noise parameters
BROWN_NOISE_STEP = 0.02
BROWN_NOISE_DAMPING = 0.98


class UnknownNoiseTypeError(ValueError):
    """Error raised when an unsupported noise type is requested."""


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value between minimum and maximum."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def _normalize(value: float) -> int:
    """Normalize float sample to 16-bit PCM."""
    return int(_clamp(value, -1.0, 1.0) * 32767)


class NoiseGenerator:
    """Generate PCM frames for noise-based sounds."""

    def __init__(
        self,
        noise_subtype: str,
        volume: float,
        seed: Any | None = None,
    ) -> None:
        if noise_subtype not in ["white", "pink", "brown"]:
            raise UnknownNoiseTypeError(noise_subtype)

        self.noise_type = noise_subtype
        self.volume = _clamp(float(volume), 0.0, 1.0)
        self._rng = random.Random(seed)
        self._brown_value = 0.0
        self._pink_state = [0.0] * 7

    def _next_sample(self) -> float:
        """Generate the next audio sample."""
        if self.noise_type == "white":
            return self._rng.uniform(-1.0, 1.0)
        
        if self.noise_type == "brown":
            self._brown_value += self._rng.uniform(-1.0, 1.0) * BROWN_NOISE_STEP
            self._brown_value = _clamp(self._brown_value, -1.0, 1.0) * BROWN_NOISE_DAMPING
            return self._brown_value
        
        if self.noise_type == "pink":
            white = self._rng.uniform(-1.0, 1.0)
            # Apply pink noise filter coefficients
            for j, (decay, scale) in enumerate(PINK_NOISE_COEFFS):
                self._pink_state[j] = decay * self._pink_state[j] + white * scale
            
            pink = (
                self._pink_state[0] + self._pink_state[1] + self._pink_state[2] + 
                self._pink_state[3] + self._pink_state[4] + self._pink_state[5] + 
                self._pink_state[6] + white * PINK_NOISE_WHITE_COEFF
            )
            self._pink_state[6] = white * PINK_NOISE_FINAL_STATE_COEFF
            return _clamp(pink * PINK_NOISE_SCALE, -1.0, 1.0)

        raise UnknownNoiseTypeError(self.noise_type)

    def next_chunk(self, sample_count: int) -> bytes:
        """Return the next PCM chunk for the configured noise profile."""
        frames = bytearray()
        for _ in range(sample_count):
            sample = self._next_sample() * self.volume
            frames.extend(struct.pack("<h", _normalize(sample)))
        return bytes(frames)


class AmbientGenerator:
    """Generate PCM frames for ambient sounds (rain, wind, fan)."""

    def __init__(
        self,
        ambient_subtype: str,
        volume: float,
        seed: Any | None = None,
    ) -> None:
        if ambient_subtype not in ["rain", "wind", "fan"]:
            raise UnknownNoiseTypeError(ambient_subtype)

        self.ambient_type = ambient_subtype
        self.volume = _clamp(float(volume), 0.0, 1.0)
        self._rng = random.Random(seed)
        self._position = 0
        self._pink_state = [0.0] * 7
        self._brown_value = 0.0
        
        # Rain-specific state
        self._rain_base = []
        self._rain_drops = []
        
        # Wind-specific state
        self._wind_modulation_phase = 0.0
        
        # Fan-specific state
        self._fan_phase = 0.0

    def _generate_pink_sample(self) -> float:
        """Generate a single pink noise sample."""
        white = self._rng.uniform(-1.0, 1.0)
        for j, (decay, scale) in enumerate(PINK_NOISE_COEFFS):
            self._pink_state[j] = decay * self._pink_state[j] + white * scale
        
        pink = (
            self._pink_state[0] + self._pink_state[1] + self._pink_state[2] + 
            self._pink_state[3] + self._pink_state[4] + self._pink_state[5] + 
            self._pink_state[6] + white * PINK_NOISE_WHITE_COEFF
        )
        self._pink_state[6] = white * PINK_NOISE_FINAL_STATE_COEFF
        return _clamp(pink * PINK_NOISE_SCALE, -1.0, 1.0)

    def _generate_brown_sample(self) -> float:
        """Generate a single brown noise sample."""
        self._brown_value += self._rng.uniform(-1.0, 1.0) * BROWN_NOISE_STEP
        self._brown_value = _clamp(self._brown_value, -1.0, 1.0) * BROWN_NOISE_DAMPING
        return self._brown_value

    def _next_sample(self) -> float:
        """Generate the next audio sample."""
        if self.ambient_type == "rain":
            # Base pink noise for rain ambience
            base = self._generate_pink_sample() * 0.3
            
            # Add random drops occasionally
            if self._rng.random() < 0.01:  # 1% chance per sample
                drop_intensity = self._rng.uniform(0.1, 0.3)
                base += drop_intensity * self._rng.uniform(-1.0, 1.0)
            
            return base
        
        if self.ambient_type == "wind":
            # Brown noise base for wind
            base = self._generate_brown_sample()
            
            # Add slow modulation for gusts
            self._wind_modulation_phase += 0.1 / SAMPLE_RATE
            modulation = 1.0 + 0.3 * math.sin(2 * math.pi * self._wind_modulation_phase)
            
            # Add occasional gusts
            if self._rng.random() < 0.001:  # Rare gusts
                modulation *= 1.5
            
            return base * modulation
        
        if self.ambient_type == "fan":
            # Pink noise with periodic modulation
            base = self._generate_pink_sample()
            
            # Fan blade rotation effect (12 Hz)
            self._fan_phase += 12.0 / SAMPLE_RATE
            modulation = 1.0 + 0.08 * math.sin(2 * math.pi * self._fan_phase)
            
            return base * modulation

        raise UnknownNoiseTypeError(self.ambient_type)

    def next_chunk(self, sample_count: int) -> bytes:
        """Return the next PCM chunk for the configured ambient profile."""
        frames = bytearray()
        for _ in range(sample_count):
            sample = self._next_sample() * self.volume
            frames.extend(struct.pack("<h", _normalize(sample)))
        return bytes(frames)


def build_wav_header(sample_rate: int = SAMPLE_RATE) -> bytes:
    """Return a WAV header suitable for indefinite streaming."""
    channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    return struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        0xFFFFFFFF,
        b"WAVE",
        b"fmt ",
        16,
        1,
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        0xFFFFFFFF,
    )


def coerce_profile(raw_profile: dict[str, Any]) -> dict[str, Any]:
    """Return a serializable copy of a profile definition."""
    profile_type = raw_profile.get(CONF_PROFILE_TYPE)
    profile_subtype = raw_profile.get(CONF_PROFILE_SUBTYPE)

    if isinstance(profile_subtype, str):
        profile_subtype = normalize_subtype(profile_subtype)

    # Determine type from subtype if not specified
    if profile_type not in PROFILE_TYPES:
        if profile_subtype in ["white", "pink", "brown"]:
            profile_type = "noise"
        elif profile_subtype in ["rain", "wind", "fan"]:
            profile_type = "ambient"
        else:
            profile_type = DEFAULT_PROFILE_TYPE

    # Validate subtype
    if profile_subtype not in ALL_SUBTYPES:
        profile_subtype = DEFAULT_PROFILE_SUBTYPE

    parameters = dict(raw_profile.get(CONF_PROFILE_PARAMETERS, {}))

    volume = float(parameters.get(CONF_VOLUME, DEFAULT_VOLUME))
    volume = _clamp(volume, 0.0, 1.0)
    parameters[CONF_VOLUME] = volume

    seed = parameters.get(CONF_SEED)
    if seed in ("", None):
        parameters.pop(CONF_SEED, None)
    else:
        parameters[CONF_SEED] = seed

    return {
        CONF_PROFILE_TYPE: profile_type,
        CONF_PROFILE_SUBTYPE: profile_subtype,
        CONF_PROFILE_PARAMETERS: parameters,
    }


def create_generator(
    profile_type: str,
    subtype: str,
    volume: float,
    seed: Any | None,
    params: dict[str, Any],
) -> Any:
    """Create the appropriate generator based on profile type."""
    if profile_type == "noise":
        return NoiseGenerator(subtype, volume, seed)
    if profile_type == "ambient":
        return AmbientGenerator(subtype, volume, seed)
    raise UnknownNoiseTypeError(profile_type)
