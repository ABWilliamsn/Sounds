# Ambient Sound Synthesizer

A Home Assistant custom integration that streams high-quality ambient sounds from myNoise.net to your media players with full intensity control.

## Installation

1. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for "Ambient Sound Synthesizer" and follow the configuration steps.

## Overview

This integration leverages myNoise.net's professional sound generators to stream ambient sounds directly to your Home Assistant media players. No audio files needed - everything is streamed on-demand from myNoise.net with customizable intensity controls.

### Features from myNoise.net

- **High-quality sound generation**: Professional ambient sound generators
- **Intensity sliders**: Control sound characteristics with the intensity parameter (0-100)
- **Animation mode**: Natural variation in the sounds for more realistic experience
- **No file downloads**: Streams directly from myNoise.net
- **Multiple sound types**: 10 different ambient sound generators

## Usage

This integration provides services to play ambient sounds on any media player in your Home Assistant setup.

### Services

#### `ambient_sound_synthesizer.play_sound`

Play an ambient sound from myNoise.net on one or more media players.

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
- `intensity` (optional): Sound intensity from 0 to 100 (default: 50) - controls myNoise.net's slider levels

**Example:**
```yaml
service: ambient_sound_synthesizer.play_sound
data:
  entity_id: media_player.living_room_speaker
  sound_type: rain
  volume: 0.7
  intensity: 75
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

The integration generates myNoise.net streaming URLs with customized slider settings based on your intensity parameter. These URLs point to myNoise.net's sound generators, which:

1. Generate ambient sounds in real-time
2. Stream them continuously to your media player
3. Include animation mode for natural sound variation
4. Adjust intensity based on your settings

### Intensity Parameter

The `intensity` parameter (0-100) controls all 10 frequency band sliders on myNoise.net:
- **0-30**: Subtle, background ambience
- **30-70**: Moderate, noticeable presence
- **70-100**: Strong, prominent sound

## Configuration

You can configure default settings through the integration's options in the UI, but these can be overridden when calling the services.

## Features

- Stream ambient sounds from myNoise.net on any media player
- 10 different sound types from professional sound generators
- Adjustable volume and intensity controls
- No audio files required - everything streams on-demand
- Service-based design for maximum flexibility
- Works with any Home Assistant media player
- Use in automations and scripts
- Control multiple media players simultaneously

## Credits

This integration uses sound generators from [myNoise.net](https://mynoise.net/), created by Stéphane Pigeon. myNoise.net provides high-quality ambient sound generators with sophisticated algorithms.

## Requirements

- Active internet connection to stream from myNoise.net
- Media players that support streaming from HTTP URLs
- Home Assistant 2024.1.0 or newer

## Development

This is a Home Assistant custom integration built using the standard config flow pattern and service architecture.

## License

See LICENSE file for details. 
