# Antique Mystery Podcast Generator

> AI-powered voice narration system that transforms antique mystery stories into podcast-quality audio using state-of-the-art voice cloning technology. Optimized for mystery storytelling with dramatic pauses, suspenseful intonation, and proper pacing.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Local Deployment](https://img.shields.io/badge/deployment-local-green.svg)](/)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [TTS Engine Comparison](#tts-engine-comparison)
- [Voice Parameters](#voice-parameters)
- [Development Status](#development-status)
- [Generated Files Location](#generated-files-location)
- [License](#license)

---

## Overview

The **Antique Mystery Podcast Generator** is a fully local application that converts written mystery stories into professionally narrated podcast episodes. The system uses advanced AI voice cloning technology to replicate a specific narrator voice, then applies mystery-specific audio parameters to create engaging, suspenseful audio content.

### Key Differentiators

- **Mystery-Optimized**: Unlike generic TTS systems, this app includes specialized parameters for suspense, dramatic pauses, and intonation patterns specific to mystery storytelling
- **100% Local**: All processing happens on your machine—no cloud dependencies, no API calls, complete data privacy
- **Multi-Engine Support**: Integrates three open-source TTS engines (Chatterbox, XTTS2, F5-TTS) with automatic fallback and voice quality comparison
- **Production-Ready**: Commercial-friendly MIT licensing allows future monetization of generated content
- **Two-Mode Operation**: Separate Training Mode (one-time voice setup) and Operating Mode (daily podcast generation)

### Use Cases

1. **Podcast Production**: Generate audiobook-style narrations from public domain mystery stories (Sherlock Holmes, Agatha Christie, Edgar Allan Poe)
2. **Voice Testing**: Compare voice quality across different TTS engines with standardized mystery text samples
3. **Audio Research**: Experiment with voice parameters to understand their impact on listener engagement
4. **Content Creation**: Produce consistent-quality narration for YouTube channels, audio content libraries, or educational materials

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ANTIQUE MYSTERY PODCAST GENERATOR                       │
│                         (Fully Local Application)                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                            │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Gradio Web UI (localhost:7860)                    │  │
│  │  ┌─────────────────────────────┬─────────────────────────────────┐   │  │
│  │  │      TRAINING MODE          │       OPERATING MODE            │   │  │
│  │  │  - Voice sample upload      │  - Story input (text/.docx)     │   │  │
│  │  │  - Parameter tuning UI      │  - Voice profile selection      │   │  │
│  │  │  - Test sample generation   │  - Progress tracking            │   │  │
│  │  │  - A/B comparison playback  │  - Audio preview & download     │   │  │
│  │  └─────────────────────────────┴─────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ↓                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION CORE LAYER                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        src/main.py (Entry Point)                       │  │
│  │  - Initializes VoiceRegistry from config/voice_profiles/*.json        │  │
│  │  - Creates TTSService with output directory and ending snippet        │  │
│  │  - Launches Gradio UI server on localhost                             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                    ┌───────────────┴───────────────┐                        │
│                    ↓                               ↓                        │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │    Voice Registry Manager      │  │       Document Parser            │  │
│  │  (src/tts/voice_registry.py)   │  │  (src/document/parser.py)        │  │
│  │                                 │  │                                  │  │
│  │  - Loads voice profiles         │  │  - Parses .txt/.docx files       │  │
│  │  - Validates reference audio    │  │  - Validates story length        │  │
│  │  - Manages voice parameters     │  │  - Returns clean UTF-8 text      │  │
│  │  - Returns VoiceProfile objects │  │                                  │  │
│  └────────────────────────────────┘  └──────────────────────────────────┘  │
│                    ↓                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       TTS Service Orchestrator                         │  │
│  │                    (src/tts/tts_service.py)                            │  │
│  │                                                                        │  │
│  │  1. Text chunking (respects paragraph/sentence boundaries)            │  │
│  │  2. Engine selection (Chatterbox/XTTS2/F5-TTS)                        │  │
│  │  3. Batch synthesis (process all chunks)                              │  │
│  │  4. Audio segment concatenation                                       │  │
│  │  5. Ending snippet append                                             │  │
│  │  6. MP3 export with normalization                                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TTS ENGINE INTEGRATION LAYER                        │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │   Chatterbox TTS     │  │      XTTS v2         │  │     F5-TTS       │  │
│  │  (ResembleAI)        │  │   (Coqui TTS)        │  │ (SWivid)         │  │
│  │  ──────────────      │  │  ──────────────      │  │  ──────────      │  │
│  │  License: MIT        │  │  License: Coqui      │  │  License: MIT    │  │
│  │  Quality: ⭐⭐⭐⭐⭐    │  │  Quality: ⭐⭐⭐⭐      │  │  Quality: ⭐⭐⭐⭐⭐ │  │
│  │  Speed: Fast         │  │  Speed: Medium       │  │  Speed: Very Fast│  │
│  │  Ref Audio: 5-10s    │  │  Ref Audio: 5-10s    │  │  Ref Audio: 5-10s│  │
│  │  Max Text: 1200 char │  │  Max Text: 220 words │  │  Max Text: ∞     │  │
│  │  ──────────────      │  │  ──────────────      │  │  ──────────      │  │
│  │  Best for:           │  │  Best for:           │  │  Best for:       │  │
│  │  - High quality      │  │  - Fallback option   │  │  - Long texts    │  │
│  │  - Expressiveness    │  │  - CPU-only machines │  │  - Coherence     │  │
│  │  - Commercial use    │  │  - Testing           │  │  - Speed         │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                              │
│  Each engine receives:                                                       │
│  ✓ Text chunk (auto-sized per engine limits)                                │
│  ✓ Reference audio path (from voice profile)                                │
│  ✓ Voice parameters (exaggeration, speed, temperature, etc.)                │
│  ✓ Output path (temporary WAV file)                                         │
│                                                                              │
│  Each engine returns:                                                        │
│  ✓ WAV audio tensor                                                          │
│  ✓ Sample rate (22050 Hz or 24000 Hz)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUDIO PROCESSING LAYER                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Audio Concatenator (pydub)                          │  │
│  │                 (src/audio/concatenator.py)                            │  │
│  │                                                                        │  │
│  │  1. Merge narration segments (from TTS chunks)                        │  │
│  │  2. Volume normalization (-20 dB LUFS)                                │  │
│  │  3. Sample rate conversion (24000 Hz → 22050 Hz if needed)            │  │
│  │  4. Append ending snippet (assets/ending.mp3)                         │  │
│  │  5. Add crossfade transition (0.5-1.0 seconds)                        │  │
│  │  6. Apply speed adjustment (via frame rate manipulation)              │  │
│  │  7. Export final MP3 (192 kbps bitrate)                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA STORAGE LAYER (LOCAL)                          │
│                                                                              │
│  ┌────────────────────────┐  ┌────────────────────────┐                    │
│  │   Voice Profiles       │  │   Reference Audio      │                    │
│  │  (config/voice_profiles│  │  (assets/reference_    │                    │
│  │   /*.json)             │  │   voices/*.mp3)        │                    │
│  │                        │  │                        │                    │
│  │  - Voice ID            │  │  - Training samples    │                    │
│  │  - Display name        │  │  - Testing excerpts    │                    │
│  │  - Reference path      │  │  - Reference text      │                    │
│  │  - Engine type         │  │    (for F5-TTS)        │                    │
│  │  - Parameters JSON     │  │                        │                    │
│  │  - Chunking settings   │  │  Format: MP3/WAV       │                    │
│  └────────────────────────┘  └────────────────────────┘                    │
│                                                                              │
│  ┌────────────────────────┐  ┌────────────────────────┐                    │
│  │   Ending Snippet       │  │   Generated Episodes   │                    │
│  │  (assets/ending.mp3)   │  │  (output/generated/    │                    │
│  │                        │  │   *.mp3)               │                    │
│  │  - Fixed audio file    │  │                        │                    │
│  │  - Appended to all     │  │  - Timestamped files   │                    │
│  │    episodes            │  │  - Slugified titles    │                    │
│  │  - Normalized volume   │  │  - 192 kbps MP3        │                    │
│  └────────────────────────┘  └────────────────────────┘                    │
│                                                                              │
│  All data stored locally - NO cloud storage, NO external APIs               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         TESTING & TRAINING SCRIPTS                           │
│                         (Separate CLI workflows)                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  test_voice_cloning_chatterbox.py  - Chatterbox voice quality test  │   │
│  │  test_voice_cloning_xtts.py        - XTTS2 voice quality test       │   │
│  │  test_voice_cloning_f5_tts.py      - F5-TTS voice quality test      │   │
│  │                                                                      │   │
│  │  Each script:                                                        │   │
│  │  1. Loads reference audio from assets/reference_voices/              │   │
│  │  2. Generates 5 mystery text samples (suspense, drama, atmosphere)   │   │
│  │  3. Creates evaluation template (EVALUATION.md)                      │   │
│  │  4. Outputs test audio to output/voice_tests_[engine]/              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow (Operating Mode)

```
User Story Input → Document Parser → Text Chunks → TTS Engine Selection
                                                           ↓
                                              [Chatterbox/XTTS2/F5-TTS]
                                                           ↓
                                                   Audio Segments (WAV)
                                                           ↓
                                              Audio Concatenator (pydub)
                                                           ↓
                                        Merge Segments + Ending Snippet
                                                           ↓
                                         Volume Normalize + Speed Adjust
                                                           ↓
                                              Export MP3 (192 kbps)
                                                           ↓
                                         output/generated/[timestamp]_[title].mp3
                                                           ↓
                                              User Preview & Download
```

### Component Interactions

1. **Voice Registry (`voice_registry.py`)**: Loads JSON voice profiles at startup, validates reference audio files exist, provides VoiceProfile objects to TTS Service
2. **TTS Service (`tts_service.py`)**: Orchestrates entire synthesis pipeline, manages engine lifecycle, handles chunking logic, coordinates audio merging
3. **Audio Concatenator (`concatenator.py`)**: Pure audio processing, no knowledge of TTS engines, handles all post-synthesis audio manipulation
4. **Document Parser (`parser.py`)**: Standalone text extraction, validates story length, returns clean UTF-8 text for synthesis
5. **Gradio UI (`ui/app.py`)**: Stateless UI layer, calls TTSService methods, handles progress callbacks, manages file uploads/downloads

---

## Features

### Core Capabilities

✅ **Voice Cloning**: Clone any voice from 5-15 seconds of reference audio (MP3/WAV)
✅ **Mystery-Optimized**: Special parameters for suspense, pauses, and dramatic delivery
✅ **Two Modes**:
   - **Training Mode**: Clone voice and tune parameters for perfect mystery narration
   - **Operating Mode**: Convert stories to podcast episodes with one click
✅ **Automatic Ending**: Appends predefined ending snippet to all episodes
✅ **Local & Private**: Runs entirely on your machine, no cloud dependencies
✅ **Multi-Engine Support**: Compare Chatterbox, XTTS2, and F5-TTS voice quality
✅ **Commercial-Friendly**: MIT-licensed TTS engines for future monetization
✅ **Long Text Support**: Automatic text chunking with paragraph/sentence boundary respect
✅ **Audio Quality**: 192 kbps MP3 output with volume normalization

### Advanced Features

- **Progressive Web UI**: Real-time progress tracking with stage-by-stage updates
- **A/B Testing**: Generate samples with different engines/parameters for comparison
- **Evaluation Templates**: Structured voice quality scoring system (1-10 scale)
- **Parameter Persistence**: Save voice profiles with tuned parameters for reuse
- **Error Resilience**: Automatic engine fallback if preferred TTS fails
- **Batch Processing**: Process multiple text chunks in parallel (future enhancement)

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.10+ | Core application language |
| **Deep Learning** | PyTorch | 2.0+ | Neural network inference for TTS models |
| **Audio Processing** | pydub + ffmpeg | Latest | Audio manipulation, format conversion, concatenation |
| **Web UI** | Gradio | 4.0+ | Local web interface with file upload/download |
| **Document Parsing** | python-docx | Latest | Extract text from Word documents |

### TTS Engines (Multi-Engine Architecture)

| Engine | Provider | License | Status | Voice Quality | Speed | Max Text Length |
|--------|----------|---------|--------|---------------|-------|-----------------|
| **Chatterbox** | Resemble AI | MIT | Primary | ⭐⭐⭐⭐⭐ (Best) | Fast | 1200 chars |
| **XTTS v2** | Coqui TTS | Coqui Public Model | Fallback | ⭐⭐⭐⭐ (Good) | Medium | 220 words |
| **F5-TTS** | SWivid | MIT | Alternative | ⭐⭐⭐⭐⭐ (Excellent) | Very Fast | Unlimited |

### Deployment

- **Platform**: macOS (M1/M2/M3 Apple Silicon) or Linux
- **Hosting**: 100% local (localhost:7860)
- **Storage**: Local filesystem only
- **Privacy**: No external API calls, no telemetry, no cloud dependencies

---

## Project Structure

```
antique_mystery_podcast/
├── README.md                         # This file - comprehensive documentation
├── requirements.txt                  # Python package dependencies
├── development_plan.md               # Full development roadmap and architecture
├── .env.example                      # Environment variable template
├── .gitignore                        # Git exclusion patterns
│
├── config/                           # ⚙️ CONFIGURATION FILES
│   ├── config.yaml                   # Main app configuration (TTS engine, audio settings)
│   └── voice_profiles/               # Voice profile storage
│       ├── antique_mystery_voice.json  # Default voice profile
│       ├── mystery_grandfather.json    # Example voice profile (XTTS2)
│       └── mystery_f5.json             # Example voice profile (F5-TTS)
│
├── assets/                           # 📦 USER-PROVIDED AUDIO FILES
│   ├── ending.mp3                    # ⭐ Pre-recorded ending snippet (156KB)
│   └── reference_voices/             # ⭐ Voice training samples
│       ├── training_01.mp3           # Main reference voice (5-15 seconds)
│       ├── training_02.mp3           # Additional training sample
│       ├── training_01_f5.wav        # F5-TTS format (24kHz mono WAV)
│       └── training_02_f5.wav        # Additional F5-TTS sample
│
├── src/                              # 🐍 CORE APPLICATION CODE
│   ├── __init__.py
│   ├── main.py                       # 🚀 Application entry point (run this)
│   │
│   ├── ui/                           # User Interface Layer
│   │   ├── __init__.py
│   │   └── app.py                    # Gradio web UI (Training + Operating modes)
│   │
│   ├── tts/                          # TTS Integration Layer
│   │   ├── __init__.py
│   │   ├── tts_service.py            # TTS orchestration (chunking, synthesis, merging)
│   │   └── voice_registry.py         # Voice profile management (load/validate)
│   │
│   ├── audio/                        # Audio Processing Layer
│   │   ├── __init__.py
│   │   └── concatenator.py           # Audio segment merging + ending append
│   │
│   ├── document/                     # Document Parsing Layer
│   │   ├── __init__.py
│   │   └── parser.py                 # Text/DOCX extraction and validation
│   │
│   └── modes/                        # Mode Infrastructure (reserved)
│       └── __init__.py
│
├── output/                           # 🎧 GENERATED AUDIO FILES
│   ├── generated/                    # Final podcast episodes (MP3)
│   │   └── [timestamp]_[title].mp3  # Example: 20250127_123456_the_stolen_vase.mp3
│   ├── voice_tests_chatterbox/       # Voice quality test outputs (Chatterbox)
│   ├── voice_tests_xtts/             # Voice quality test outputs (XTTS2)
│   └── voice_tests_f5tts/            # Voice quality test outputs (F5-TTS)
│
├── logs/                             # 📋 APPLICATION LOGS
│   └── app.log                       # Runtime logs (INFO, WARNING, ERROR)
│
├── docs/                             # 📚 TECHNICAL DOCUMENTATION
│   ├── TTS_IMPLEMENTATION_NOTES.md   # TTS engine integration details
│   ├── VOICE_EVALUATION_TEMPLATE.md  # Voice quality scoring template
│   └── operating_mode_plan.md        # Operating mode specification
│
├── tests/                            # 🧪 UNIT TESTS (placeholder)
│   └── __init__.py
│
└── test_voice_cloning_*.py           # 🎙️ TTS ENGINE TEST SCRIPTS
    ├── test_voice_cloning_chatterbox.py  # Chatterbox voice cloning test
    ├── test_voice_cloning_xtts.py        # XTTS2 voice cloning test
    └── test_voice_cloning_f5_tts.py      # F5-TTS voice cloning test
```

---

## Installation

### Prerequisites

- **Operating System**: macOS (M1/M2/M3) or Linux
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 5GB+ free (for TTS models)
- **Audio**: ffmpeg installed

### Step 1: Install System Dependencies

**macOS (Homebrew):**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg
brew install ffmpeg
```

**Linux (apt):**
```bash
sudo apt update
sudo apt install ffmpeg python3-pip python3-venv
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/antique_mystery_podcast.git
cd antique_mystery_podcast
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: First installation will download TTS models (~1-5GB per engine) on first run.

### Step 5: Configure Application

```bash
# Optional: Set up environment variables (for LLM preprocessing)
cp .env.example .env
nano .env  # Add your OpenAI/Claude API keys if using LLM features

# Review main configuration
nano config/config.yaml
```

### Step 6: Add Your Audio Files

**Required files:**
1. **Ending snippet**: `assets/ending.mp3` (your pre-recorded ending)
2. **Reference voice**: `assets/reference_voices/training_01.mp3` (5-15 seconds of voice to clone)

```bash
# Copy your audio files
cp ~/path/to/your/ending.mp3 assets/ending.mp3
cp ~/path/to/your/reference_voice.mp3 assets/reference_voices/training_01.mp3

# Commit to git
git add assets/
git commit -m "Add voice sample files"
```

### Step 7: Run the Application

```bash
source venv/bin/activate
python src/main.py
```

The app will launch at **http://localhost:7860**

---

## Usage

### Training Mode (One-Time Setup)

**Purpose**: Clone your reference voice and tune parameters for optimal mystery narration.

**Workflow**:

1. **Launch the app** and select **Training Mode** tab
2. **Upload reference voice** (MP3, 5-15 seconds, clean audio)
3. **Adjust mystery-specific parameters**:
   - **Speed**: 0.85-0.95 (slower for suspense)
   - **Expressiveness**: 7-9 (high for tension)
   - **Pause Duration**: 1.5-2.5 (dramatic pauses) ⭐ CRITICAL
   - **Intonation Emphasis**: 7-8 (suspense building)
   - **Pitch**: -2 to -4 (older male narrator)
4. **Generate test samples** with mystery story excerpts
5. **Listen and refine** parameters until satisfied
6. **Save voice profile** with a memorable name (e.g., "mystery_grandfather")

**Testing Scripts** (Alternative to Training Mode UI):

Run standalone test scripts to compare TTS engines:

```bash
# Test Chatterbox TTS
python test_voice_cloning_chatterbox.py

# Test XTTS2
python test_voice_cloning_xtts.py

# Test F5-TTS
python test_voice_cloning_f5_tts.py
```

Each script generates:
- 5 mystery text samples in `output/voice_tests_[engine]/test_[timestamp]/`
- `EVALUATION.md` template for scoring voice quality (1-10 scale)

### Operating Mode (Daily Podcast Generation)

**Purpose**: Convert written mystery stories into narrated podcast episodes.

**Workflow**:

1. **Select Operating Mode** tab
2. **Input your story**:
   - Paste text directly (plain text), OR
   - Upload .docx file (Word document)
3. **Select voice profile** (from saved profiles)
4. **Click "Generate Podcast"**
5. **Monitor progress**:
   - "Generating narration in N chunks..."
   - "Rendering chunk X/N"
   - "Stitching final narration..."
   - "Story ready: [filename].mp3"
6. **Preview audio** in built-in player
7. **Download MP3** to your device

**Expected Processing Time**:
- 5-minute story: ~3-10 minutes (depending on engine and hardware)
- 15-minute story: ~10-30 minutes

**Output Location**:
- Generated episodes: `output/generated/[timestamp]_[title].mp3`
- Example: `output/generated/20250127_143022_the_stolen_rembrandt.mp3`

### VibeVoice Text Formatter (Standalone Utility)

**Purpose**: Convert plain mystery story text into VibeVoice-compatible format for use in Google Colab.

**Why Use This**: VibeVoice requires text formatted with speaker labels (`Speaker 0: ...`). This utility automates the formatting process so you can quickly prepare text for the VibeVoice Colab notebook.

**How to Launch**:

```bash
# Run the transcriber utility
bash RUN_TRANSCRIBER.sh

# Or manually
source venv/bin/activate
python src/ui/transcriber.py
```

The app will launch at **http://localhost:7861**

**Workflow**:

1. **Paste your raw story text** in the input box
   - Can include multiple paragraphs
   - Can have double line breaks
   - Can have extra spaces
2. **Text is automatically formatted** in real-time (or click "Transcribe")
3. **Copy the formatted output** using the copy button
4. **Paste into VibeVoice Colab notebook** (Cell 6 - Story Input)

**What It Does**:
- Adds `Speaker 0: ` prefix to each paragraph (with space after colon)
- Removes double line breaks
- Removes extra spaces
- Preserves paragraph structure with clean `\n\n` separators

**Example**:

**Input (Plain Text)**:
```
It was a fog-laden morning when I stumbled upon a peculiar bottle.

The bottle's antiquity was evident, but it was the unsettling aura.

This was no ordinary tonic.
```

**Output (VibeVoice Format)**:
```
Speaker 0: It was a fog-laden morning when I stumbled upon a peculiar bottle.

Speaker 0: The bottle's antiquity was evident, but it was the unsettling aura.

Speaker 0: This was no ordinary tonic.
```

**Statistics Display**:
- Shows input word count and paragraph count
- Shows output word count and paragraph count
- Updates in real-time as you type

---

## TTS Engine Comparison

This application supports three TTS engines with different strengths:

| Feature | Chatterbox (Primary) | XTTS v2 (Fallback) | F5-TTS (Alternative) |
|---------|----------------------|--------------------|----------------------|
| **License** | MIT (Commercial OK) | Coqui Public Model (Non-commercial) | MIT (Commercial OK) |
| **Voice Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Expressiveness** | High (exaggeration control) | Medium | Very High (prosody) |
| **Speed** | Fast (~0.3x real-time) | Medium (~0.5x real-time) | Very Fast (~0.15x real-time) |
| **Reference Audio** | 5-10 seconds | 5-10 seconds | 5-10 seconds |
| **Max Text Length** | 1200 chars | 220 words (~400 tokens) | Unlimited (auto-chunks) |
| **Model Size** | ~1GB | ~2GB | ~1GB |
| **GPU Required** | No (CPU OK) | No (CPU OK) | No (CPU OK) |
| **Best For** | General use, commercial | CPU-only systems | Long texts, coherence |
| **Mystery Genre** | ✅ Excellent pauses/intonation | ✅ Good consistency | ✅ Best long-form coherence |

**Recommendation**: Start with **Chatterbox** for best quality and commercial licensing. Use **F5-TTS** if you need unlimited text length or very fast generation.

---

## Voice Parameters

The app includes specialized parameters optimized for mystery narration:

| Parameter | Range | Mystery Default | Purpose | Impact |
|-----------|-------|-----------------|---------|--------|
| **Speed** | 0.5-2.0x | 0.85-0.95x | Speaking rate | Slower = more suspenseful |
| **Expressiveness** | 1-10 | 7-9 | Emotional variation | Higher = more dramatic |
| **Pitch** | -12 to +12 semitones | -2 to -4 | Voice depth | Negative = deeper, older voice |
| **Emotional Intensity** | 1-10 | 6-8 | Overall energy | Higher = more tension |
| **Pause Duration** ⭐ | 0.5-3.0x | 1.5-2.5x | **Dramatic pauses** | **Critical for mystery genre** |
| **Intonation Emphasis** | 1-10 | 7-8 | Pitch variation | Higher = stronger suspense build |
| **Breath Frequency** | 1-10 | 4-7 | Natural breathing | Strategic pauses for timing |

**Mystery-Specific Guidelines**:

- **Suspenseful Opening**: Speed 0.85x, Pause 2.0x, Intonation 8
- **Dramatic Revelation**: Speed 0.75x, Pause 2.5x, Expressiveness 9
- **Tense Confrontation**: Speed 0.90x, Pitch -3, Emotional Intensity 8
- **Atmospheric Description**: Speed 0.88x, Pause 1.8x, Breath Frequency 5

---

## Development Status

**Current Phase**: Active Development (Phases 2-5 Complete)

### Completed Features ✅

- [x] Project structure and architecture
- [x] Multi-engine TTS integration (Chatterbox, XTTS2, F5-TTS)
- [x] Voice profile management system
- [x] Document parsing (text, .docx)
- [x] Audio processing pipeline
- [x] Text chunking with sentence boundary respect
- [x] Gradio web UI (Training + Operating modes)
- [x] Ending snippet integration
- [x] Voice testing scripts with evaluation templates
- [x] Configuration system (YAML + JSON)

### In Progress 🚧

- [ ] Advanced parameter tuning UI (sliders for all parameters)
- [ ] A/B testing interface (compare multiple engines)
- [ ] Batch processing (multiple stories at once)
- [ ] Real-time preview (listen while generating)

### Future Enhancements 🔮

- [ ] Multiple character voices (dialogue extraction)
- [ ] Background music integration
- [ ] Sound effects library
- [ ] Podcast RSS feed generation
- [ ] Web deployment option (Docker container)
- [ ] GPU acceleration (CUDA support)

See [development_plan.md](development_plan.md) for full roadmap.

---

## Generated Files Location

**Where to find generated podcast episodes:**

```
output/
└── generated/
    ├── 20250127_143022_the_stolen_rembrandt.mp3
    ├── 20250127_150334_antique_vase_mystery.mp3
    └── 20250127_161145_victorian_music_box.mp3
```

**File naming convention**: `[timestamp]_[slugified_title].mp3`
- Timestamp: `YYYYMMDD_HHMMSS` (sortable by creation time)
- Title: Auto-generated from story content or manual input (lowercase, underscores)

**Voice test outputs:**

```
output/
├── voice_tests_chatterbox/   # Chatterbox test outputs
│   └── test_20250127_120000/
│       ├── 01_suspenseful_opening.mp3
│       ├── 02_dramatic_revelation.mp3
│       └── EVALUATION.md
├── voice_tests_xtts/         # XTTS2 test outputs
└── voice_tests_f5tts/        # F5-TTS test outputs
```

---

## Requirements

### Hardware

- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB+ free disk space (for TTS models)
- **GPU**: Optional (will use CPU by default, GPU accelerates generation)

### Software

- **Operating System**: macOS (M1/M2/M3) or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **ffmpeg**: Latest version
- **Git**: For cloning repository

---

## License

**MIT License** - See LICENSE file for details.

This project uses MIT-licensed TTS engines (Chatterbox, F5-TTS) for commercial-friendly deployment. XTTS2 is available under Coqui Public Model License (non-commercial) and included as a fallback option.

---

## Contributing

This is currently a personal project. Contributions welcome after initial release.

**To contribute**:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## Support

For issues, questions, or feature requests:
- **GitHub Issues**: [https://github.com/yourusername/antique_mystery_podcast/issues](https://github.com/yourusername/antique_mystery_podcast/issues)
- **Documentation**: See `docs/` directory for technical details

---

## Acknowledgments

- **Resemble AI** for Chatterbox TTS (MIT License)
- **SWivid** for F5-TTS (MIT License)
- **Coqui AI** for XTTS v2 (Coqui Public Model License)
- **Gradio** for the excellent web UI framework

---

**Next Step**: Run `python src/main.py` to start generating mystery podcasts! 🎙️
