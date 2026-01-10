# Ambient Sounds

A Home Assistant custom integration that lets you search, discover, and play ambient sounds from Freesound's extensive audio library directly on your media players.

## Features

🔍 **Search Freesound's Audio Library**: Browse thousands of high-quality ambient sounds  
✏️ **Custom Text Search**: Search with your own keywords and phrases  
📊 **Sort Results**: Sort by name or duration  
⭐ **Favorites Management**: Save your favorite sounds for quick access  
🎵 **Media Browser Integration**: Easy browsing and playback through Home Assistant's UI  
🤖 **Automation Support**: Full service integration for automations and scripts  
☁️ **Cloud Streaming**: No local storage needed - streams directly from Freesound  
🆓 **Free API**: 5,000 requests per month on Freesound's free tier  

## Prerequisites

You'll need a free Freesound API key:

1. Go to https://freesound.org/apiv2/apply/
2. Create a free account if you don't have one
3. Copy your API key from the API documentation page

## Installation

> **Note**: For HACS installation to work, the integration files from PR #2 or #3 need to be merged to the main branch. Until then, please use Option 2 (Manual Installation from GitHub) and clone from the appropriate branch (e.g., `copilot/fix-config-flow-error`).

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ABWilliamsn&repository=Ambient-Sound-Synthesizer&category=integration)

1. Ensure [HACS](https://hacs.xyz/) is installed

2. Add this repository as a custom repository in HACS:
   - In Home Assistant, go to **HACS** → **Integrations**
   - Click the **⋮** (three dots) menu in the top right
   - Select **Custom repositories**
   - Enter the repository URL: `https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer`
   - Select category: **Integration**
   - Click **Add**

3. Install the integration:
   - Click the **+** button in HACS Integrations
   - Search for "**Ambient Sounds**"
   - Click **Download**

4. Restart Home Assistant

5. Configure the integration:
   - Go to **Settings** → **Devices & Services** → **Add Integration**
   - Search for "**Ambient Sounds**"
   - Enter your Freesound API key when prompted

### Option 2: Manual Installation from GitHub

1. Download the latest release or clone this repository from the branch with the integration files:
   ```bash
   # Clone the repository and checkout the branch with integration files
   git clone https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer.git
   cd Ambient-Sound-Synthesizer
   git checkout copilot/fix-config-flow-error  # Or the branch with the latest integration code
   ```
   
   Alternatively, download directly from GitHub:
   - Go to https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer
   - Switch to the branch with the integration files (e.g., `copilot/fix-config-flow-error`)
   - Click **Code** → **Download ZIP**
   - Extract the ZIP file

2. Copy the `custom_components/ambient_sound_synthesizer` directory to your Home Assistant's `config/custom_components/` directory:
   ```bash
   cp -r Ambient-Sound-Synthesizer/custom_components/ambient_sound_synthesizer /path/to/homeassistant/config/custom_components/
   ```
   
   Your directory structure should look like:
   ```
   config/
   └── custom_components/
       └── ambient_sound_synthesizer/
           ├── __init__.py
           ├── config_flow.py
           ├── const.py
           ├── freesound_client.py
           ├── manifest.json
           ├── media_source.py
           ├── services.yaml
           └── strings.json
   ```

3. Restart Home Assistant

4. Go to **Settings** → **Devices & Services** → **Add Integration**

5. Search for "**Ambient Sounds**"

6. Enter your Freesound API key when prompted

## Usage

### Media Browser

The primary way to use Ambient Sounds:

1. Open any media player in Home Assistant
2. Click **Browse Media**
3. Navigate to **Ambient Sounds**
4. Choose from:
   - **⭐ Favorites**: Your saved sounds for quick access
   - **🔍 Search Freesound**: Browse and search Freesound's audio catalog

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

1. **Search**: The integration uses Freesound's API to search their audio library
2. **Stream**: Audio files are streamed directly from Freesound's servers
3. **Favorites**: Your saved favorites are stored locally in Home Assistant using the Store helper
4. **Playback**: Sounds play on any compatible media player in your network

## Configuration Options

After initial setup, you can modify settings through **Options**:

- **Results per search**: Number of results to show per search (1-150, default: 20)

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

## Credits

This integration uses audio from [Freesound](https://freesound.org/), which provides high-quality royalty-free audio content. All audio is subject to Freesound's license terms.

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues

## License

See LICENSE file for details.
