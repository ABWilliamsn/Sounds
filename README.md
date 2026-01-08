# Ambient Sound Synthesizer

A Home Assistant custom integration that generates high-quality ambient audio **on-the-fly** and streams it directly through your media players. No files to manage, instant playback, infinite duration.

## Features

- **Real-time Audio Generation**: Streams synthesized audio continuously without file storage
- **Multiple Sound Types**: White noise, pink noise, brown noise, rain, wind, and fan sounds
- **Media Browser Integration**: Browse and play sounds directly from Home Assistant's Media Browser
- **Profile Management**: Create and manage multiple sound profiles with custom names and volumes
- **Zero Disk Usage**: No audio files stored—everything generated on-demand
- **Pure Python**: No external dependencies, all synthesis done locally
- **Infinite Playback**: Sounds play continuously until you stop them

## Sound Types

### Noise Types
- **White Noise**: Equal energy at all frequencies, like static or "shh"
- **Pink Noise**: More energy in lower frequencies, often more pleasant than white noise
- **Brown Noise**: Deep, rumbling sound with even more low-frequency energy

### Ambient Sounds
- **Rain**: Synthesized rainfall with random droplet patterns
- **Wind**: Wind ambience with gentle variations
- **Fan**: Mechanical fan sound with periodic blade rotation

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

## Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Ambient Sound Synthesizer"
3. Complete the setup (a default white noise profile will be created)
4. Go to the integration and click **Configure** to manage profiles

## Managing Profiles

### Add a Profile

1. Go to **Settings** → **Devices & Services** → **Ambient Sound Synthesizer** → **Configure**
2. Select "Add New Profile"
3. Enter:
   - **Profile Name**: Descriptive name (e.g., "Bedtime Rain")
   - **Sound Type**: Choose from white/pink/brown noise, rain, wind, or fan
   - **Volume**: 0.0 to 1.0 (0.5 is 50%)
   - **Random Seed** (optional): For reproducible randomness
4. Save and repeat for more profiles

### Edit or Remove Profiles

1. Go to **Configure** in the integration settings
2. Select "Edit [Profile Name]" or "Remove [Profile Name]"
3. Make changes and save

## Usage

### Method 1: Media Browser

1. Open **Media** or click "Browse media" on any media player
2. Select **Ambient Sound Synthesizer**
3. Choose a sound profile
4. Select your target media player
5. Sound starts playing immediately

### Method 2: Automations

```yaml
service: media_player.play_media
target:
  entity_id: media_player.bedroom_speaker
data:
  media_content_type: music
  media_content_id: media-source://ambient_sound_synthesizer/white-noise
```

To find the exact `media_content_id`:
1. Browse to the profile in Media Browser
2. Click the three dots
3. Select "Show code snippet"
4. Copy the `media_content_id`

## Example Automations

### Bedtime Rain Sound

```yaml
automation:
  - alias: "Play Rain at Bedtime"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.bedroom_speaker
        data:
          media_content_type: music
          media_content_id: media-source://ambient_sound_synthesizer/bedtime-rain
      - service: media_player.volume_set
        target:
          entity_id: media_player.bedroom_speaker
        data:
          volume_level: 0.3
```

### Stop Sound After 1 Hour

```yaml
automation:
  - alias: "Sleep Sound Timer"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.bedroom_speaker
        data:
          media_content_type: music
          media_content_id: media-source://ambient_sound_synthesizer/brown-noise
      - delay: "01:00:00"
      - service: media_player.turn_off
        target:
          entity_id: media_player.bedroom_speaker
```

### Focus Mode with Fan Sound

```yaml
script:
  focus_mode:
    alias: "Start Focus Mode"
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.office
        data:
          brightness: 200
      - service: media_player.play_media
        target:
          entity_id: media_player.office_speaker
        data:
          media_content_type: music
          media_content_id: media-source://ambient_sound_synthesizer/fan-sound
      - service: media_player.volume_set
        target:
          entity_id: media_player.office_speaker
        data:
          volume_level: 0.4
```

## Technical Details

- **Audio Format**: 16-bit PCM WAV, mono channel
- **Sample Rate**: 44.1 kHz (CD quality)
- **Generation Method**: Real-time algorithmic synthesis using pure Python
- **Streaming**: Audio generated in subprocess and streamed via HTTP
- **CPU Usage**: Minimal (a few percent per active stream)
- **Dependencies**: None (pure Python, no numpy/scipy required)

## Advantages Over File-Based Approaches

✅ **No Disk Space**: Zero storage required
✅ **Instant Playback**: No generation delay, start immediately  
✅ **Infinite Duration**: Plays continuously, no looping artifacts
✅ **Easy Management**: Add/edit profiles through UI
✅ **Integrated**: Works with Home Assistant's Media Browser
✅ **Lightweight**: No external dependencies

## Volume Guidelines

- **0.1-0.3**: Subtle background ambience
- **0.3-0.5**: Comfortable listening level
- **0.5-0.7**: Moderate masking of external sounds
- **0.7-1.0**: Strong ambient sound

You can also adjust volume using your media player's volume control.

## Troubleshooting

### Sound Not Playing

- Verify your media player supports WAV/audio streaming
- Check Home Assistant logs for errors
- Ensure the integration is properly configured with at least one profile

### Audio Cuts Out

- Check CPU usage—high load may affect streaming
- Verify network connectivity between Home Assistant and media player
- Try reducing the number of simultaneous streams

### Profile Not Appearing

- Refresh the Media Browser
- Restart Home Assistant
- Check the profile was saved correctly in the integration settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was inspired by the [Noise Generator](https://github.com/nirnachmani/noise-generator) integration by nirnachmani. The streaming architecture and Media Source integration patterns are based on that excellent work, adapted here for ambient sound synthesis.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues) page
2. Create a new issue with detailed information about your problem
3. Include relevant log entries from Home Assistant
