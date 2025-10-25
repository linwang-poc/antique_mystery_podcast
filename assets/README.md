# Assets Directory

This directory contains all audio assets for the Antique Mystery Podcast application.

## Directory Structure

```
assets/
├── ending_snippet.mp3       # Fixed ending audio (append to all episodes)
└── reference_voices/        # Voice samples for training
    ├── training_*.mp3       # Reference voice samples for cloning
    └── testing_*.mp3        # Test story excerpts for parameter tuning
```

## Files to Upload

### 1. Training Voice Sample(s)
**Location:** `assets/reference_voices/`
**Filename:** Name them `training_*.mp3` (e.g., `training_voice.mp3`, `training_voice_01.mp3`)
**Purpose:** These are the AI-generated voice samples you like. The app will clone this voice.
**Requirements:**
- MP3 format
- 5-15 seconds duration
- Clean audio, no background noise
- Demonstrates natural speaking with some emotion

### 2. Testing Story Excerpts
**Location:** `assets/reference_voices/`
**Filename:** Name them `testing_*.mp3` (e.g., `testing_story.mp3`, `testing_suspense.mp3`)
**Purpose:** Mystery story samples to test if voice parameters work well for suspense/drama
**Requirements:**
- MP3 format
- 2-3 paragraphs of mystery narration
- Include suspenseful moments, pauses, dramatic delivery

### 3. Ending Snippet
**Location:** `assets/`
**Filename:** `ending_snippet.mp3`
**Purpose:** Fixed audio that gets appended to the end of every generated podcast episode
**Requirements:**
- MP3 format
- Any duration
- Will be automatically appended to all generated stories

## Upload Instructions

1. Place your files in the correct directories as shown above
2. Commit them to git:
   ```bash
   git add assets/
   git commit -m "Add voice sample files"
   git push
   ```

## Notes

- All audio files will be automatically converted to the required format during processing
- The training voice sample is the most important - ensure it's high quality
- Testing files help tune the voice for mystery storytelling (suspense, pauses, intonation)
