# HACS Setup Instructions

This integration is compatible with HACS (Home Assistant Community Store).

## Fix for HACS Version Error

If you encounter the error: `The version f7d5ae3 for this integration can not be used with HACS`, this means HACS requires a proper semantic version tag instead of a commit hash.

### Solution

A version tag `v2.0.0` has been created for this repository to match the version in the manifest.json file. 

**Important**: The tag must be pushed to GitHub for HACS to recognize it. Run the following command:

```bash
git push origin v2.0.0
```

Or push all tags:

```bash
git push --tags
```

After the tag is pushed to GitHub, HACS will be able to use version `v2.0.0` instead of the commit hash `f7d5ae3`.

## Version Tags

HACS requires proper semantic version tags to function correctly. This repository uses version tags in the format `vX.Y.Z` that match the version specified in `custom_components/ambient_sound_synthesizer/manifest.json`.

### Current Version

- **Version**: 2.0.0
- **Tag**: v2.0.0
- **Tagged Commit**: f7d5ae3

## Installation via HACS

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/ABWilliamsn/Ambient-Sounds`
6. Select category "Integration"
7. Click "Add"
8. Find "Ambient Sounds" in the list and click "Download"
9. Restart Home Assistant

## Version History

- **v2.0.0**: Initial HACS-compatible release with proper version tagging
