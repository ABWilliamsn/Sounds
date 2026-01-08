# Ambient Sound Synthesizer

A Home Assistant custom integration to generate digital ambient sounds and play them on your media players.

## Installation

1. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for "Ambient Sound Synthesizer" and follow the configuration steps.

## Audio Files Setup

This integration plays ambient sound files on your media players. You need to provide the audio files:

1. Create a directory `config/www/ambient_sounds/` in your Home Assistant installation
2. Add your ambient sound MP3 files to this directory with names like:
   - `rain_50.mp3`, `rain_75.mp3` (different intensity levels)
   - `ocean_50.mp3`, `ocean_75.mp3`
   - `forest_50.mp3`, `wind_50.mp3`
   - `white_noise_50.mp3`, `brown_noise_50.mp3`
3. The integration will reference these files as `/local/ambient_sounds/[sound_type]_[intensity].mp3`

**Note:** You can find free ambient sound files from sources like:
- YouTube Audio Library
- Freesound.org
- BBC Sound Effects
- Your own recordings

## Usage

This integration provides services to play ambient sounds on any media player in your Home Assistant setup.

### Services

#### `ambient_sound_synthesizer.play_sound`

Play an ambient sound on one or more media players.

**Parameters:**
- `entity_id` (required): Target media player(s)
- `sound_type` (required): Type of sound - choose from: rain, ocean, forest, wind, white_noise, brown_noise
- `volume` (optional): Volume level from 0.0 to 1.0 (default: 0.5)
- `intensity` (optional): Sound intensity from 0 to 100 (default: 50) - used to select different audio files

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
```

## Configuration

You can configure default settings through the integration's options, but these can be overridden when calling the services.

## Features

- Play ambient sounds on any media player
- Six different sound types: rain, ocean, forest, wind, white noise, brown noise
- Adjustable volume and intensity
- Service-based design for maximum flexibility
- Works with any Home Assistant media player
- Use in automations and scripts

## Development

This is a Home Assistant custom integration built using the standard config flow pattern and service architecture.

## License

See LICENSE file for details. 
