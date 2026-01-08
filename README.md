# Ambient Sound Synthesizer

A Home Assistant custom integration that streams high-quality ambient sounds to your media players with Media Browser support.

## Installation

1. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for "Ambient Sound Synthesizer" and follow the configuration steps.

## Overview

This integration streams ambient sounds directly to your Home Assistant media players using high-quality audio sources. No audio files needed - everything is streamed on-demand with an easy-to-use Media Browser interface.

### Features

- **High-quality ambient sounds**: Professional audio from public sources
- **Media Browser integration**: Browse and play sounds directly from Home Assistant's Media Browser UI
- **No file downloads**: Streams directly to your media players
- **Multiple sound types**: 10 different ambient sound categories
- **Service-based automation**: Full control through Home Assistant services

## Usage

### Media Browser (Recommended)

The easiest way to use this integration:

1. Open any media player in Home Assistant
2. Click the "Browse Media" button
3. Navigate to "Ambient Sound Synthesizer"
4. Browse through the 10 sound categories
5. Select a sound to play directly on your media player

This provides a simple UI-based way to control ambient sounds without writing any code!

### Services

You can also use services for automation and scripts.

#### `ambient_sound_synthesizer.play_sound`

Play an ambient sound on one or more media players.

**Parameters:**
- `entity_id` (required): Target media player(s)
- `sound_type` (required): Type of sound - choose from:
  - `rain` - Rain noise
  - `ocean` - Ocean waves
  - `forest` - Forest ambience
  - `wind` - Wind sounds
  - `white_noise` - White noise
  - `brown_noise` - Brown noise
  - `fire` - Fire crackling
  - `thunder` - Thunder sounds
  - `river` - Flowing river/stream
  - `cafe` - Cafe restaurant ambience
- `volume` (optional): Volume level from 0.0 to 1.0 (default: 0.5)
- `intensity` (optional): Sound intensity from 0 to 100 (default: 50) - for future use

**Example:**
```yaml
service: ambient_sound_synthesizer.play_sound
data:
  entity_id: media_player.living_room_speaker
  sound_type: rain
  volume: 0.7
  intensity: 50
```

#### `ambient_sound_synthesizer.stop_sound`

Stop ambient sound playback on one or more media players.

**Parameters:**
- `entity_id` (required): Target media player(s)

**Example:**
```yaml
service: ambient_sound_synthesizer.stop_sound
data:
  entity_id: media_player.living_room_speaker
```

### Using in Automations

You can use these services in automations to play ambient sounds based on triggers:

```yaml
automation:
  - alias: "Play rain sounds at bedtime"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: ambient_sound_synthesizer.play_sound
        data:
          entity_id: media_player.bedroom_speaker
          sound_type: rain
          volume: 0.3
          intensity: 60
          
  - alias: "Play cafe sounds during work hours"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: ambient_sound_synthesizer.play_sound
        data:
          entity_id: media_player.office_speaker
          sound_type: cafe
          volume: 0.4
          intensity: 50
```

## How It Works

The integration streams ambient sound audio files directly to your media players using publicly available audio sources. The sounds are high-quality looping audio files that play continuously.

## Configuration

You can configure default settings through the integration's options in the UI, but these can be overridden when calling the services.

## Features

- Stream ambient sounds to any media player
- 10 different sound types
- Adjustable volume controls
- No audio files required - everything streams on-demand
- Media Browser integration for easy UI-based control
- Service-based design for automation
- Works with any Home Assistant media player that supports HTTP streaming
- Use in automations and scripts
- Control multiple media players simultaneously

## Audio Sources

This integration uses high-quality ambient sound audio from Pixabay's royalty-free sound library. All audio files are properly licensed for use.

## Requirements

- Active internet connection to stream from myNoise.net
- Media players that support streaming from HTTP URLs
- Home Assistant 2024.1.0 or newer

## Development

This is a Home Assistant custom integration built using the standard config flow pattern and service architecture.

## License

See LICENSE file for details. 
