# Antique Mystery Podcast Generator

An AI-powered voice narration application that converts antique mystery stories into podcast-quality audio files using voice cloning technology. Optimized for mystery storytelling with dramatic pauses, suspenseful intonation, and proper pacing.

## Features

- **Voice Cloning**: Clone any voice from 5-15 seconds of reference audio (MP3)
- **Mystery-Optimized**: Special parameters for suspense, pauses, and dramatic delivery
- **Two Modes**:
  - **Training Mode**: Clone voice and tune parameters for perfect mystery narration
  - **Operating Mode**: Convert stories to podcast episodes with one click
- **Automatic Ending**: Appends predefined ending snippet to all episodes
- **Local & Private**: Runs entirely on your Mac, no cloud dependencies
- **Commercial-Friendly**: MIT-licensed TTS engines for future monetization

## Technology Stack

- **Python 3.10+**
- **TTS Engine**: Chatterbox (primary) or GPT-SoVITS (M1 fallback)
- **Audio**: pydub + ffmpeg for MP3 processing
- **UI**: Gradio web interface
- **Platform**: macOS (M1/M2/M3) with Apple Silicon optimization

## Project Structure

```
antique_mystery_podcast/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── config.yaml              # Main configuration
│   └── voice_profiles/          # Saved voice profiles
├── assets/
│   ├── ending_snippet.mp3       # ⭐ UPLOAD YOUR ENDING HERE
│   └── reference_voices/        # ⭐ UPLOAD VOICE SAMPLES HERE
│       ├── training_*.mp3       # Training voice samples
│       └── testing_*.mp3        # Test story excerpts
├── src/
│   ├── main.py                  # Application entry point
│   ├── modes/                   # Training & Operating modes
│   ├── tts/                     # TTS engine integration
│   ├── audio/                   # Audio processing
│   ├── document/                # Document parsing
│   └── ui/                      # Gradio interfaces
├── output/
│   └── generated/               # Generated podcast files
├── tests/                       # Unit tests
└── docs/                        # Documentation
```

## Quick Start

### 1. Upload Your Voice Files ⭐ START HERE

**Before starting development, upload your audio files:**

#### Location 1: `assets/ending_snippet.mp3`
- Your pre-recorded ending that gets appended to all episodes
- MP3 format, any duration

#### Location 2: `assets/reference_voices/`
- **Training files**: `training_voice.mp3` (or similar names)
  - 5-15 seconds of the voice you want to clone
  - Clean, clear audio
- **Testing files**: `testing_story_01.mp3`, `testing_suspense.mp3` (etc.)
  - Mystery story excerpts for testing voice parameters
  - 2-3 paragraphs each

**How to upload:**
```bash
# From your Mac, in the project directory:
cp ~/Documents/voice_sample/training*.mp3 assets/reference_voices/
cp ~/Documents/voice_sample/testing*.mp3 assets/reference_voices/
cp ~/Documents/voice_sample/ending*.mp3 assets/ending_snippet.mp3

# Commit to git
git add assets/
git commit -m "Add voice sample files"
git push
```

### 2. Install Dependencies (On Your Mac)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg
brew install ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install TTS engine (will be provided after testing)
# Instructions will be added once we confirm M1 compatibility
```

### 3. Configure

```bash
# Copy environment file (optional, for LLM preprocessing)
cp .env.example .env

# Edit config if needed
nano config/config.yaml
```

### 4. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
python src/main.py

# App will open in browser at http://localhost:7860
```

## Usage

### Training Mode (One-Time Setup)

1. Launch the app and select **Training Mode**
2. Upload your reference voice MP3
3. Adjust mystery-specific parameters:
   - **Speed**: 0.85-0.95 (slower for suspense)
   - **Expressiveness**: 7-9 (high for tension)
   - **Pause Duration**: 1.5-2.5 (dramatic pauses) ⭐
   - **Intonation Emphasis**: 7-8 (suspense building)
   - **Pitch**: -2 to -4 (older male narrator)
4. Generate test samples with mystery story excerpts
5. Listen and refine parameters
6. Save voice profile

### Operating Mode (Daily Use)

1. Select **Operating Mode**
2. Input your mystery story (paste text or upload .docx)
3. Select saved voice profile
4. Click **Generate Podcast**
5. Wait for processing (< 10 minutes for 5-min story)
6. Preview and download MP3 file
7. Message appears: "The story is ready for your review as [filename]"

## Voice Parameters for Mystery Storytelling

The app includes specialized parameters optimized for mystery narration:

| Parameter | Range | Mystery Default | Purpose |
|-----------|-------|-----------------|---------|
| Speed | 0.5-2.0x | 0.90x | Slower for suspense |
| Expressiveness | 1-10 | 7 | High emotional variation |
| Pitch | -12 to +12 | -3 | Deeper, older voice |
| Emotional Intensity | 1-10 | 7 | Elevated tension |
| **Pause Duration** | 0.5-3.0x | 2.0x | **Critical for drama** |
| Intonation Emphasis | 1-10 | 7 | Suspense building |
| Breath Frequency | 1-10 | 6 | Natural rhythm |

## Development Status

**Current Phase**: Phase 0 - Environment Setup

- [x] Project structure created
- [x] Configuration files created
- [x] Documentation written
- [ ] TTS engine installation (testing M1 compatibility)
- [ ] Core implementation (Phases 1-7)

See [development_plan.md](development_plan.md) for full roadmap.

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM (16GB recommended)
- Python 3.10+
- ffmpeg
- 5GB+ free disk space (for TTS models)

## License

MIT License - See LICENSE file

## Contributing

This is currently a personal project. Contributions welcome after initial release.

## Support

For issues or questions, please open an issue on GitHub.

---

**Next Step**: Upload your voice files to `assets/` directory and commit to git!
