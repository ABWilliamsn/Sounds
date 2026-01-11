# Ambient Sounds

A Home Assistant custom integration that lets you search, discover, and play ambient sounds from Freesound's extensive audio library, plus generate various ambient noises on-demand directly on your media players.

## Features

🔍 **Search Freesound's Audio Library**: Browse thousands of high-quality ambient sounds  
✏️ **Custom Text Search**: Search with your own keywords and phrases  
📊 **Sort Results**: Sort by name or duration  
⭐ **Favorites Management**: Save your favorite sounds for quick access  
🎵 **Media Browser Integration**: Easy browsing and playback through Home Assistant's UI  
🤖 **Automation Support**: Full service integration for automations and scripts  
☁️ **Cloud Streaming**: No local storage needed - streams directly from Freesound  
🎛️ **Built-in Noise Generator**: Generate white, pink, brown noise, plus fan, rain, ocean, and wind sounds  
🆓 **Free API**: 5,000 requests per month on Freesound's free tier  

## Prerequisites

You'll need a free Freesound API key:

1. Go to https://freesound.org/apiv2/apply/
2. Create a free account if you don't have one
3. Copy your API key from the API documentation page

## Installation

### Option 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/ABWilliamsn/Ambient-Sounds`
6. Select category "Integration"
7. Click "Add"
8. Find "Ambient Sounds" in the list and click "Download"
9. Restart Home Assistant
10. Go to **Settings** → **Devices & Services** → **Add Integration**
11. Search for "**Ambient Sounds**"
12. Enter your Freesound API key when prompted
13. (Optional) Configure the number of results per search (default: 20)

For detailed HACS setup instructions and troubleshooting, see [HACS_SETUP.md](HACS_SETUP.md).

### Option 2: Manual Installation

1. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "**Ambient Sounds**"
5. Enter your Freesound API key when prompted
6. (Optional) Configure the number of results per search (default: 20)

## Usage

This integration offers two ways to play ambient sounds:

1. **Generated Noise** (recommended for basic noise types) - Create white, pink, brown noise, plus fan, rain, ocean, and wind sounds locally without requiring internet
2. **Freesound Library** - Search and stream thousands of ambient sounds from Freesound's cloud library

### Generated Noise (No Internet Required)

You can access the noise generator in two ways:

#### Option 1: Media Browser (GUI - No YAML needed)

The easiest way to play noise through the Home Assistant UI:

1. Open any media player in Home Assistant
2. Click **Browse Media**
3. Navigate to **Ambient Sounds** → **🎛️ Noise Generator**
4. Select a noise type:
   - ⚪ **White Noise** - Equal energy at all frequencies - great for sleep & focus
   - 🎀 **Pink Noise** - Equal energy per octave - more natural than white noise
   - 🟤 **Brown Noise** - Deeper, bass-heavy sound - very soothing
   - 🌀 **Fan Noise** - Electric fan simulation with motor hum
   - 🌧️ **Rain** - Realistic rainfall with droplet sounds
   - 🌊 **Ocean Waves** - Rhythmic wave patterns and surf
   - 💨 **Wind** - Gusting wind with natural variation
5. Choose duration (1 minute to 3 hours)
6. Click to play on your media player!

#### Option 2: Service Call (for automations and scripts)

Use the `ambient_sounds.play_noise` service in automations or scripts:

```yaml
service: ambient_sounds.play_noise
data:
  entity_id: media_player.bedroom_speaker
  noise_type: white  # white, pink, brown, fan, rain, ocean, wind
  volume: 0.3
  duration: 3600  # seconds
```

### Freesound Library (Browse & Search)

Search and stream thousands of ambient sounds:

1. Open any media player in Home Assistant
2. Click **Browse Media**
3. Navigate to **Ambient Sounds** → **🔍 Search Freesound**
4. Choose from:
   - **✏️ Custom Text Search**: See example searches or use the search service for custom queries
   - **Suggested categories** (rain, ocean, forest, wind, thunder, fire, birds, river, waterfall, cafe, city, nature, ambient, meditation, relaxing)

#### Searching for Sounds

1. Click **🔍 Search Freesound**
2. Choose from:
   - **✏️ Custom Text Search**: See example searches or use the search service for custom queries
   - **Suggested categories** (rain, ocean, forest, wind, thunder, fire, birds, river, waterfall, cafe, city, nature, ambient, meditation, relaxing)
3. Browse the results - each shows duration and descriptive tags
4. **Sort Results**: Click the sorting options at the top to sort by name (A-Z) or duration (shortest first)
5. Click on a sound to see details and preview it
6. To save it, use the `add_favorite` service with the displayed information

#### Custom Text Search

For custom searches beyond the suggested categories, use the `ambient_sounds.search` service:

```yaml
service: ambient_sounds.search
data:
  query: "rain thunder storm"
  sort_by: "duration"  # Optional: "name" or "duration"
```

Results will be logged, and you can browse them in the Media Browser by using the same search term.

### Services

Use these services for automations and to manage your library:

#### `ambient_sounds.search`

Search Freesound with custom text and optional sorting.

```yaml
service: ambient_sounds.search
data:
  query: "ocean waves beach"  # Your search keywords
  sort_by: "name"  # Optional: "name" or "duration"
```

The results are logged and available in the Media Browser under the search term.

#### `ambient_sounds.play_favorite`

Play a saved favorite sound on your media player.

```yaml
service: ambient_sounds.play_favorite
data:
  entity_id: media_player.living_room_speaker
  favorite_id: "12345"  # The Freesound sound ID
  volume: 0.7  # Optional: 0.0 to 1.0
```

#### `ambient_sounds.add_favorite`

Save a sound from your search results to favorites. Get the details from search results in Media Browser.

```yaml
service: ambient_sounds.add_favorite
data:
  sound_id: "12345"  # Freesound sound ID
  name: "Relaxing Rain"  # Your custom name
  url: "https://cdn.freesound.org/previews/..."  # Direct audio URL from Freesound
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

#### `ambient_sounds.play_noise`

Generate and play ambient noise on your media player. This service creates noise in real-time without requiring any external files or API calls.

**Available Noise Types:**
- `white` - White noise (equal energy at all frequencies)
- `pink` - Pink noise (equal energy per octave, more natural than white)
- `brown` - Brown/Brownian noise (deeper, more bass-heavy)
- `fan` - Fan noise (low hum with air movement)
- `rain` - Rain sounds (rainfall with droplet impacts)
- `ocean` - Ocean waves (rhythmic wave patterns)
- `wind` - Wind sounds (gusting wind with variation)

**Parameters:**
- `entity_id` (required): Target media player(s)
- `noise_type` (required): Type of noise to generate
- `volume` (optional): Volume level from 0.0 to 1.0 (default: 0.5)
- `intensity` (optional): Sound intensity/amplitude from 0.0 to 1.0 (default: 0.5)
- `duration` (optional): Duration in seconds, 10-3600 (default: 60)

**Example:**
```yaml
service: ambient_sounds.play_noise
data:
  entity_id: media_player.bedroom_speaker
  noise_type: pink
  volume: 0.3
  intensity: 0.6
  duration: 300  # 5 minutes
```

### Automation Examples

**Play generated white noise at bedtime:**
```yaml
automation:
  - alias: "Bedtime White Noise"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: ambient_sounds.play_noise
        data:
          entity_id: media_player.bedroom_speaker
          noise_type: white
          volume: 0.3
          intensity: 0.5
          duration: 3600  # 1 hour
```

For more automation examples, see [example_automations.yaml](example_automations.yaml).

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

**Generated Noise:**
1. **Generate**: The integration uses Python with NumPy to synthesize realistic ambient sounds in real-time
2. **Save**: Generated audio is temporarily saved as WAV files on your Home Assistant system
3. **Play**: Audio files are played on any compatible media player in your network
4. **No Internet**: Works completely offline, no API calls or external dependencies

**Freesound Library:**
1. **Search**: The integration uses Freesound's API to search their audio library
2. **Stream**: Audio files are streamed directly from Freesound's servers
3. **Favorites**: Your saved favorites are stored locally in Home Assistant using the Store helper
4. **Playback**: Sounds play on any compatible media player in your network

## Configuration Options

After initial setup, you can modify settings through **Options**:

- **Results per search**: Number of results to show per search (3-200, default: 20)

## Troubleshooting

**"Invalid API key" error during setup:**
- Double-check your API key from https://freesound.org/apiv2/apply/
- Ensure you copied the entire key without extra spaces

**No search results:**
- Check your API quota (5,000 requests/month on free tier)
- Try different search terms
- Verify your internet connection

**Sounds won't play:**
- Ensure your media player supports HTTP audio streaming
- Check that the media player is powered on and connected
- Verify the audio URL is still valid (Freesound URLs are permanent)

## API Limits

Freesound's free tier provides:
- 5,000 API requests per month
- Each search counts as one request
- No limits on playing saved favorites
- Generated noise (play_noise service) doesn't count against API limits

## Credits

This integration uses audio from [Freesound](https://freesound.org/), which provides high-quality royalty-free audio content. All audio is subject to Freesound's license terms.

Generated noise is created using Python and NumPy for real-time synthesis.

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues

## License

See LICENSE file for details.
