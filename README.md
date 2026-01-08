# Ambient Sound Synthesizer

A Home Assistant custom integration that locally generates high-quality audio files of various ambient sounds. Perfect for use with media players in automations, creating a customizable noise machine directly in your Home Assistant setup.

## Features

- **Multiple Sound Types**: Generate white noise, pink noise, brown noise, rain, wind, and fan sounds
- **Intensity Levels**: Choose from low, medium, or high intensity presets for each sound
- **Customizable Duration**: Create audio files from 10 seconds to 1 hour
- **Local Generation**: All audio is generated and stored locally on your Home Assistant instance
- **Automation Ready**: Use the generated files with media players in automations
- **Easy Configuration**: Simple UI-based configuration with configurable output directory

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Ambient Sound Synthesizer" and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download this repository
2. Copy the `custom_components/ambient_sound_synthesizer` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Ambient Sound Synthesizer"
3. Configure the output directory (default: `/config/www/ambient_sounds`)
   - Files will be saved here and accessible via Home Assistant's web interface
   - Default path makes files available at `http://your-ha-instance:8123/local/ambient_sounds/`

## Usage

### Service: `ambient_sound_synthesizer.generate_sound`

Generate an ambient sound audio file with the specified parameters.

#### Parameters

| Parameter | Required | Type | Description | Options/Range |
|-----------|----------|------|-------------|---------------|
| `sound_type` | Yes | String | Type of ambient sound | `white`, `pink`, `brown`, `rain`, `wind`, `fan` |
| `intensity` | Yes | String | Intensity level | `low`, `medium`, `high` |
| `duration` | Yes | Integer | Duration in seconds | 10-3600 |
| `filename` | Yes | String | Output filename (without extension) | Any valid filename |

#### Example Service Call

```yaml
service: ambient_sound_synthesizer.generate_sound
data:
  sound_type: rain
  intensity: medium
  duration: 300
  filename: ambient_rain_5min
```

This will create a file named `ambient_rain_5min.wav` in your configured output directory.

### Sound Types Explained

- **White Noise**: Equal energy across all frequencies, sounds like static or "shh"
- **Pink Noise**: More energy in lower frequencies, often considered more pleasant than white noise
- **Brown Noise**: Even more energy in lower frequencies, deeper and more rumbling
- **Rain**: Synthesized rain sound with random droplet patterns
- **Wind**: Simulated wind with gentle gusts and variations
- **Fan**: Mechanical fan sound with periodic blade rotation

### Intensity Levels

- **Low**: Gentle, subtle sound suitable for light background ambience
- **Medium**: Moderate volume with balanced characteristics
- **High**: Strong, prominent sound with enhanced features

## Automation Examples

### Example 1: Generate and Play Rain Sound at Bedtime

```yaml
automation:
  - alias: "Bedtime Rain Sound"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      # Generate the sound
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: rain
          intensity: medium
          duration: 3600
          filename: bedtime_rain
      # Wait for file generation
      - delay: "00:00:10"
      # Play on media player
      - service: media_player.play_media
        target:
          entity_id: media_player.bedroom_speaker
        data:
          media_content_type: music
          media_content_id: "http://homeassistant.local:8123/local/ambient_sounds/bedtime_rain.wav"
```

### Example 2: Generate Multiple Sounds for Selection

```yaml
automation:
  - alias: "Generate Daily Ambient Sounds"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: white
          intensity: low
          duration: 600
          filename: white_noise_10min
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: fan
          intensity: medium
          duration: 600
          filename: fan_10min
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: wind
          intensity: low
          duration: 600
          filename: wind_10min
```

### Example 3: Input Select for Sound Choice

```yaml
input_select:
  ambient_sound_type:
    name: Ambient Sound
    options:
      - white
      - pink
      - brown
      - rain
      - wind
      - fan
    initial: rain

input_select:
  ambient_sound_intensity:
    name: Sound Intensity
    options:
      - low
      - medium
      - high
    initial: medium

script:
  generate_custom_ambient:
    sequence:
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: "{{ states('input_select.ambient_sound_type') }}"
          intensity: "{{ states('input_select.ambient_sound_intensity') }}"
          duration: 1800
          filename: "custom_ambient_{{ now().timestamp() | int }}"
```

## Technical Details

- **Audio Format**: 16-bit PCM WAV files
- **Sample Rate**: 44.1 kHz (CD quality)
- **Generation Method**: Algorithmic synthesis using NumPy and SciPy
- **File Size**: Approximately 10 MB per minute of audio
- **Dependencies**: numpy>=1.24.0, scipy>=1.10.0

## Troubleshooting

### Files not generating

1. Check Home Assistant logs for errors
2. Verify the output directory exists and is writable
3. Ensure numpy and scipy are properly installed

### Cannot play files in automations

1. Verify the file path in your media player service call
2. Check that the file was created in the output directory
3. Ensure your media player supports WAV format

### Large file sizes

Generated WAV files are uncompressed. If storage is a concern:
- Generate shorter durations
- Loop shorter files in your media player
- Use external tools to convert to compressed formats (MP3, OGG)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues) page
2. Create a new issue with detailed information about your problem
3. Include relevant log entries from Home Assistant 
