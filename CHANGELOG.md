# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-08

### Changed
- **BREAKING**: Completely redesigned architecture from file-based to streaming
- Integration now streams audio on-the-fly via Home Assistant Media Source
- Profile-based configuration instead of per-generation service calls
- No more file storage—zero disk usage
- Infinite playback duration (plays until stopped)
- Removed all external dependencies (numpy, scipy)

### Added
- Media Browser integration for easy sound selection
- Profile management UI in integration configuration
- Support for multiple named profiles
- Real-time audio streaming with subprocess generation
- Volume control per profile
- Optional random seed for reproducible sounds

### Removed
- File generation service (`generate_sound`)
- Output directory configuration
- WAV file storage

## [1.0.0] - 2026-01-08

### Added
- Initial release with file-based generation
- Support for 6 sound types: white noise, pink noise, brown noise, rain, wind, and fan
- Three intensity levels: low, medium, and high
- Configurable duration from 10 seconds to 1 hour
- Custom filename support for generated audio files
- Home Assistant config flow UI for easy setup
- Service `generate_sound` for use in automations
- Comprehensive documentation and automation examples
- Local audio generation using NumPy and SciPy
- 44.1 kHz, 16-bit PCM WAV output format
