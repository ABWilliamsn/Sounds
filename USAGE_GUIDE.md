# Installation and Usage Guide

## Quick Start

1. **Install the Integration**
   - Add this repository to HACS as a custom repository
   - Search for "Ambient Sound Synthesizer" in HACS
   - Click Install
   - Restart Home Assistant

2. **Configure the Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Ambient Sound Synthesizer"
   - Set your output directory (default: `/config/www/ambient_sounds`)

3. **Generate Your First Sound**
   - Go to Developer Tools → Services
   - Select `ambient_sound_synthesizer.generate_sound`
   - Fill in the parameters:
     - Sound type: `rain`
     - Intensity: `medium`
     - Duration: `300` (5 minutes)
     - Filename: `my_first_ambient_sound`
   - Click "Call Service"

4. **Use in Automation**
   - The file will be saved as `my_first_ambient_sound.wav`
   - Access it at: `http://your-ha:8123/local/ambient_sounds/my_first_ambient_sound.wav`
   - Use with any media player in your automations

## Available Sound Types

### Noise Types

**White Noise** - Equal energy at all frequencies
- Use case: Blocking distractions, focus work
- Best intensity: Medium to High

**Pink Noise** - More bass than white noise
- Use case: Sleep, relaxation, tinnitus masking
- Best intensity: Low to Medium

**Brown Noise** - Deep, rumbling sound
- Use case: Deep sleep, meditation, concentration
- Best intensity: Low to Medium

### Nature Sounds

**Rain** - Simulated rainfall with droplets
- Use case: Sleep, relaxation, ambience
- Best intensity: Medium (light rain) to High (heavy rain)

**Wind** - Wind with gentle gusts
- Use case: Meditation, ambient background
- Best intensity: Low (gentle breeze) to High (strong wind)

**Fan** - Mechanical fan with blade rotation
- Use case: Sleep, white noise alternative
- Best intensity: Medium to High

## Intensity Levels

- **Low (30%)** - Subtle background sound
- **Medium (60%)** - Balanced, comfortable listening
- **High (90%)** - Prominent, mask other sounds

## Duration Guidelines

- **Short (10-60s)** - Notification sounds, alerts
- **Medium (1-10min)** - Focus sessions, quick relaxation
- **Long (10-60min)** - Full meditation, work sessions, power naps
- **Extra Long (60min+)** - Full sleep cycles, extended work

## File Management

Files are saved in the configured output directory with `.wav` extension.

**File Size**: Approximately 10 MB per minute at 44.1 kHz, 16-bit PCM

**Recommendations**:
- Generate multiple shorter files rather than one very long file
- Use file names that indicate the sound and purpose (e.g., `sleep_rain_30min`)
- Periodically clean up old files you no longer use
- Consider converting to MP3 if storage is limited (using external tools)

## Troubleshooting

### Service Call Fails
- Check Home Assistant logs for detailed error messages
- Verify the output directory exists and is writable
- Ensure numpy and scipy are properly installed

### File Not Created
- Check available disk space
- Verify permissions on the output directory
- Try a shorter duration first to test

### Cannot Play File
- Ensure your media player supports WAV format
- Check the file path is correct in your automation
- Verify the file was actually created in the output directory

### Poor Audio Quality
- All sounds are generated at 44.1 kHz sample rate
- Quality should be consistent across all sound types
- If audio sounds distorted, try a lower intensity level

## Advanced Usage

### Looping Sounds

Many media players support repeat/loop functionality. Generate a shorter file and loop it:

```yaml
service: media_player.play_media
target:
  entity_id: media_player.bedroom_speaker
data:
  media_content_type: music
  media_content_id: "http://homeassistant.local:8123/local/ambient_sounds/rain_5min.wav"
  repeat: "all"  # This depends on your media player
```

### Volume Control

Adjust volume after starting playback:

```yaml
service: media_player.volume_set
target:
  entity_id: media_player.bedroom_speaker
data:
  volume_level: 0.3
```

### Sleep Timer

Use a delayed action to stop playback:

```yaml
automation:
  - alias: "Sleep Sound with Timer"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: ambient_sound_synthesizer.generate_sound
        data:
          sound_type: brown
          intensity: low
          duration: 3600
          filename: sleep_sound
      - delay: "00:00:10"
      - service: media_player.play_media
        target:
          entity_id: media_player.bedroom_speaker
        data:
          media_content_type: music
          media_content_id: "http://homeassistant.local:8123/local/ambient_sounds/sleep_sound.wav"
      - delay: "01:00:00"  # Play for 1 hour
      - service: media_player.turn_off
        target:
          entity_id: media_player.bedroom_speaker
```

## Performance Notes

- Generation time is approximately real-time (5 minutes of audio takes ~5 seconds to generate)
- CPU usage is moderate during generation
- Memory usage is proportional to the duration (longer files use more RAM)
- Recommended maximum duration: 1 hour (3600 seconds)

## Privacy and Security

- All audio generation happens locally on your Home Assistant instance
- No data is sent to external services
- No internet connection required for audio generation
- Generated files are stored locally on your system
- Access to files is controlled by your Home Assistant configuration
