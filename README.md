# Ambient Sounds

A Home Assistant custom integration that lets you search, discover, and play ambient sounds from Pixabay's extensive audio library directly on your media players.

## Features

🔍 **Search Pixabay's Audio Library**: Browse thousands of high-quality ambient sounds  
⭐ **Favorites Management**: Save your favorite sounds for quick access  
🎵 **Media Browser Integration**: Easy browsing and playback through Home Assistant's UI  
🤖 **Automation Support**: Full service integration for automations and scripts  
☁️ **Cloud Streaming**: No local storage needed - streams directly from Pixabay  
🆓 **Free API**: 5,000 requests per month on Pixabay's free tier  

## Prerequisites

You'll need a free Pixabay API key:

1. Go to https://pixabay.com/api/docs/
2. Create a free account if you don't have one
3. Copy your API key from the API documentation page

## Installation

1. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "**Ambient Sounds**"
5. Enter your Pixabay API key when prompted
6. (Optional) Configure the number of results per search (default: 20)

## Usage

### Media Browser

The primary way to use Ambient Sounds:

1. Open any media player in Home Assistant
2. Click **Browse Media**
3. Navigate to **Ambient Sounds**
4. Choose from:
   - **⭐ Favorites**: Your saved sounds for quick access
   - **🔍 Search Pixabay**: Browse and search Pixabay's audio catalog

#### Searching for Sounds

1. Click **🔍 Search Pixabay**
2. Select a suggested category (rain, ocean, forest, etc.) or search for custom terms
3. Browse the results - each shows duration and descriptive tags
4. To play a sound:
   - First, add it to favorites using the `add_favorite` service (see below)
   - Then it will appear in your **⭐ Favorites** section for easy playback

### Services

Use these services for automations and to manage your library:

#### `ambient_sounds.play_favorite`

Play a saved favorite sound on your media player.

```yaml
service: ambient_sounds.play_favorite
data:
  entity_id: media_player.living_room_speaker
  favorite_id: "12345"  # The Pixabay sound ID
  volume: 0.7  # Optional: 0.0 to 1.0
```

#### `ambient_sounds.add_favorite`

Save a sound from your search results to favorites. Get the details from search results in Media Browser.

```yaml
service: ambient_sounds.add_favorite
data:
  sound_id: "12345"  # Pixabay sound ID
  name: "Relaxing Rain"  # Your custom name
  url: "https://cdn.pixabay.com/audio/..."  # Direct audio URL
  tags: "rain, nature, ambient"  # Optional: descriptive tags
  duration: 120  # Optional: duration in seconds
```

**Tip**: You can get these details by searching in Media Browser, then noting the sound ID and URL from the search results.

#### `ambient_sounds.remove_favorite`

Remove a sound from your favorites.

```yaml
service: ambient_sounds.remove_favorite
data:
  favorite_id: "12345"
```

#### `ambient_sounds.stop_sound`

Stop playback on a media player.

```yaml
service: ambient_sounds.stop_sound
data:
  entity_id: media_player.living_room_speaker
```

### Automation Examples

**Play rain sounds at bedtime:**
```yaml
automation:
  - alias: "Bedtime Ambient Sounds"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: ambient_sounds.play_favorite
        data:
          entity_id: media_player.bedroom_speaker
          favorite_id: "12345"  # Your favorite rain sound ID
          volume: 0.3
```

**Play nature sounds during work hours:**
```yaml
automation:
  - alias: "Work Focus Sounds"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: ambient_sounds.play_favorite
        data:
          entity_id: media_player.office_speaker
          favorite_id: "67890"  # Your favorite forest sound ID
          volume: 0.4
```

## How It Works

1. **Search**: The integration uses Pixabay's API to search their audio library
2. **Stream**: Audio files are streamed directly from Pixabay's servers
3. **Favorites**: Your saved favorites are stored locally in Home Assistant using the Store helper
4. **Playback**: Sounds play on any compatible media player in your network

## Configuration Options

After initial setup, you can modify settings through **Options**:

- **Results per search**: Number of results to show per search (3-200, default: 20)

## Troubleshooting

**"Invalid API key" error during setup:**
- Double-check your API key from https://pixabay.com/api/docs/
- Ensure you copied the entire key without extra spaces

**No search results:**
- Check your API quota (5,000 requests/month on free tier)
- Try different search terms
- Verify your internet connection

**Sounds won't play:**
- Ensure your media player supports HTTP audio streaming
- Check that the media player is powered on and connected
- Verify the audio URL is still valid (Pixabay URLs are permanent)

## API Limits

Pixabay's free tier provides:
- 5,000 API requests per month
- Each search counts as one request
- No limits on playing saved favorites

## Credits

This integration uses audio from [Pixabay](https://pixabay.com/), which provides high-quality royalty-free audio content. All audio is subject to Pixabay's license terms.

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues

## License

See LICENSE file for details.
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
