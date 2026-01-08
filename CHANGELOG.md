# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-08

### Added
- Initial release of Ambient Sound Synthesizer integration
- Support for 6 sound types: white noise, pink noise, brown noise, rain, wind, and fan
- Three intensity levels: low, medium, and high
- Configurable duration from 10 seconds to 1 hour
- Custom filename support for generated audio files
- Home Assistant config flow UI for easy setup
- Service `generate_sound` for use in automations
- Comprehensive documentation and automation examples
- Local audio generation using NumPy and SciPy
- 44.1 kHz, 16-bit PCM WAV output format
