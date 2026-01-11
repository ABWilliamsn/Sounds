# GUI Navigation Flow for Noise Generator

## Media Browser Interface

When users access the Media Browser from any media player, they will see:

```
┌─────────────────────────────────────────────────────┐
│             Ambient Sounds (Root)                   │
├─────────────────────────────────────────────────────┤
│ 🎛️ Noise Generator                    [Browse >]    │
│ ⭐ Favorites                          [Browse >]    │
│ 🔍 Search Freesound                   [Browse >]    │
└─────────────────────────────────────────────────────┘
```

### Step 1: Click "🎛️ Noise Generator"

```
┌─────────────────────────────────────────────────────┐
│        🎛️ Noise Generator - Select a noise type     │
├─────────────────────────────────────────────────────┤
│ ⚪ White Noise                        [Browse >]    │
│ 🎀 Pink Noise                         [Browse >]    │
│ 🟤 Brown Noise                        [Browse >]    │
│ 🌀 Fan Noise                          [Browse >]    │
│ 🌧️ Rain                               [Browse >]    │
│ 🌊 Ocean Waves                        [Browse >]    │
│ 💨 Wind                               [Browse >]    │
└─────────────────────────────────────────────────────┘
```

### Step 2: Select a noise type (e.g., "⚪ White Noise")

```
┌─────────────────────────────────────────────────────┐
│         ⚪ White Noise - Select duration             │
├─────────────────────────────────────────────────────┤
│ ▶️ Play for 1 minute                  [Play]       │
│ ▶️ Play for 5 minutes                 [Play]       │
│ ▶️ Play for 10 minutes                [Play]       │
│ ▶️ Play for 15 minutes                [Play]       │
│ ▶️ Play for 30 minutes                [Play]       │
│ ▶️ Play for 1 hour                    [Play]       │
│ ▶️ Play for 2 hours                   [Play]       │
│ ▶️ Play for 3 hours                   [Play]       │
└─────────────────────────────────────────────────────┘
```

### Step 3: Click any duration to start playing

The noise will be generated on-demand and played on your media player!

## Features

✅ **No YAML Required** - Completely GUI-driven
✅ **Instant Playback** - Click and play
✅ **Multiple Durations** - From 1 minute to 3 hours
✅ **7 Noise Types** - White, Pink, Brown, Fan, Rain, Ocean, Wind
✅ **Works Offline** - No internet connection needed
✅ **High Quality** - 44.1kHz 16-bit audio

## Technical Details

- The noise is generated in real-time when requested
- Files are cached for 1 hour to improve performance
- Temporary files stored in `/tmp/ambient_sounds/`
- Uses NumPy for high-quality audio synthesis
