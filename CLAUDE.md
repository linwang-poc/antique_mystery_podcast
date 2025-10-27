# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Antique Mystery Podcast Generator** is a fully local AI-powered voice narration application that converts mystery stories into podcast-quality audio using voice cloning technology. The system is optimized for mystery storytelling with dramatic pauses, suspenseful intonation, and proper pacing.

**Key Architecture**: Multi-engine TTS system with three voice cloning engines (Chatterbox, XTTS2, F5-TTS), Gradio web UI, and local-only processing (no cloud dependencies).

---

## Essential Commands

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run main application (Gradio UI on localhost:7860)
python src/main.py

# Run with specific Python version
python3.10 src/main.py
```

### Voice Testing (TTS Engine Comparison)

```bash
# Test Chatterbox TTS (primary engine)
python test_voice_cloning_chatterbox.py

# Test XTTS2 (fallback engine)
python test_voice_cloning_xtts.py

# Test F5-TTS (alternative engine, requires special setup)
./RUN_F5TTS_TEST.sh
# or manually:
export PYTHONHASHSEED=0
python test_voice_cloning_f5_tts.py
```

**Test outputs**: `output/voice_tests_[engine]/test_[timestamp]/`
- Generates 5 mystery text samples with evaluation template (EVALUATION.md)

### Setup and Installation

```bash
# First-time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install ffmpeg (required for audio processing)
brew install ffmpeg  # macOS
# or: sudo apt install ffmpeg  # Linux

# F5-TTS specific setup (optional)
./setup_f5tts.sh
```

### Configuration

```bash
# Edit main application settings
nano config/config.yaml

# View/edit voice profile
nano config/voice_profiles/[profile_name].json
```

---

## Architecture Overview

### Multi-Layer Design

1. **UI Layer** (`src/ui/app.py`): Gradio web interface with Operating Mode (story → podcast generation)
2. **Application Core** (`src/main.py`): Initializes VoiceRegistry and TTSService
3. **TTS Orchestration** (`src/tts/tts_service.py`): Manages engine lifecycle, text chunking, synthesis, audio merging
4. **Voice Registry** (`src/tts/voice_registry.py`): Loads and validates voice profiles from JSON
5. **Audio Processing** (`src/audio/concatenator.py`): Merges segments, appends ending snippet
6. **Document Parsing** (`src/document/parser.py`): Extracts text from .txt/.docx files

### Critical Architecture Patterns

#### 1. Multi-Engine TTS System

Three TTS engines integrated via polymorphic interface in `tts_service.py`:

- **Chatterbox** (MIT License, primary): Best quality, expressiveness via `exaggeration` parameter
- **XTTS2** (Coqui License, fallback): 220-word limit, sentence splitting required via `split_sentences=True`
- **F5-TTS** (MIT License, alternative): Unlimited text length, requires reference transcription in `reference_text` field

**Engine Selection**: Determined by `engine` field in voice profile JSON (e.g., `"engine": "f5tts"`)

**Key Method**: `TTSService.generate_episode()` routes to:
- `_synthesize_chunk_chatterbox()` → uses `exaggeration` parameter
- `_synthesize_chunk_xtts()` → uses `temperature`, `top_k`, `top_p`, `split_sentences`
- `_synthesize_chunk_f5tts()` → uses `nfe_step`, `cfg_strength`, `sway_sampling_coef`, requires `reference_text`

#### 2. Voice Profile System

**Location**: `config/voice_profiles/*.json`

**Schema**:
```json
{
  "id": "unique_profile_id",
  "display_name": "Human Readable Name",
  "engine": "chatterbox|xtts|f5tts",
  "reference_mp3": "path/to/audio.mp3",
  "reference_text": "transcription (F5-TTS only)",
  "chunking": {
    "max_words": 220,      // XTTS2 requires ≤220 words
    "max_chars": 1200      // Chatterbox limit
  },
  "params": {
    // Engine-specific parameters
  }
}
```

**Critical**:
- XTTS2 profiles MUST set `"max_words": 220` or lower
- F5-TTS profiles MUST include `"reference_text"` (transcription of reference audio)
- Chatterbox profiles use `"exaggeration"` (0.0-1.0, default 0.85)

#### 3. Text Chunking Strategy

**Implementation**: `_chunk_text()` in `src/tts/tts_service.py`

- Splits on paragraph boundaries (`\n\n`) first
- Respects sentence boundaries (regex: `[^.!?…]+[.!?…]?`)
- Enforces per-engine limits: `max_words` (XTTS2) or `max_chars` (Chatterbox)
- F5-TTS has no limits but still chunks for progress tracking

**Why This Matters**: XTTS2 has a hard 400-token (~220 word) limit. Exceeding it causes generation failure. Always check chunk word counts in logs.

#### 4. Audio Processing Pipeline

**Flow**: WAV synthesis → pydub AudioSegment → speed adjustment → MP3 export

**Speed Adjustment**: Applied via frame rate manipulation in `_apply_voice_params()`:
```python
new_rate = int(original_rate * speed)
audio = audio._spawn(raw_data, overrides={"frame_rate": new_rate})
audio = audio.set_frame_rate(original_rate)
```

**Ending Snippet**: Appended in `merge_segments()` from `assets/ending.mp3` with 1.0s crossfade

---

## Critical Files and Their Purpose

### Core Application Files

- **`src/main.py`**: Entry point. Initializes VoiceRegistry → TTSService → Gradio UI
- **`src/tts/tts_service.py`**: TTS orchestrator. Contains ALL engine integration logic and chunking
- **`src/tts/voice_registry.py`**: Voice profile loader. Validates reference audio paths and parameters
- **`src/ui/app.py`**: Gradio interface. Single Operating Mode (no Training Mode UI yet)
- **`src/audio/concatenator.py`**: Pure audio processing. Merges segments + ending snippet

### Configuration Files

- **`config/config.yaml`**: Main app config (TTS engine defaults, audio settings, voice parameters)
- **`config/voice_profiles/*.json`**: Voice profile definitions (one per voice)

### Test Scripts (Engine Validation)

- **`test_voice_cloning_chatterbox.py`**: Tests Chatterbox with mystery text samples
- **`test_voice_cloning_xtts.py`**: Tests XTTS2 with 220-word limit awareness
- **`test_voice_cloning_f5_tts.py`**: Tests F5-TTS with unlimited text length

---

## Voice Profile Management

### Adding a New Voice Profile

1. **Prepare reference audio**:
   - Place MP3/WAV in `assets/reference_voices/`
   - 5-15 seconds of clean audio
   - For F5-TTS: Convert to 24kHz mono WAV via `ffmpeg -i input.mp3 -ac 1 -ar 24000 output.wav`

2. **Create profile JSON** in `config/voice_profiles/`:

**Chatterbox Profile**:
```json
{
  "id": "my_narrator",
  "display_name": "My Mystery Narrator",
  "engine": "chatterbox",
  "reference_mp3": "assets/reference_voices/my_voice.mp3",
  "chunking": {"max_chars": 1200},
  "params": {
    "exaggeration": 0.85,
    "speed": 0.90
  }
}
```

**XTTS2 Profile** (CRITICAL: max_words ≤ 220):
```json
{
  "id": "my_xtts_narrator",
  "engine": "xtts",
  "reference_mp3": "assets/reference_voices/my_voice.mp3",
  "chunking": {"max_words": 220},
  "split_sentences": true,
  "params": {
    "temperature": 1.0,
    "speed": 0.90
  }
}
```

**F5-TTS Profile** (CRITICAL: requires reference_text):
```json
{
  "id": "my_f5_narrator",
  "engine": "f5tts",
  "reference_mp3": "assets/reference_voices/my_voice_f5.wav",
  "reference_text": "Exact transcription of the audio file",
  "chunking": {"max_words": null},
  "params": {
    "nfe_step": 32,
    "cfg_strength": 2.0,
    "speed": 0.95
  }
}
```

3. **Restart application** to load new profile

### Voice Parameter Guidelines (Mystery-Optimized)

| Parameter | Range | Mystery Default | Engine Support |
|-----------|-------|-----------------|----------------|
| `speed` | 0.5-2.0 | 0.85-0.95 | All (post-processing) |
| `exaggeration` | 0.0-1.0 | 0.85 | Chatterbox only |
| `temperature` | 0.5-1.5 | 1.0 | XTTS2 only |
| `nfe_step` | 16-64 | 32 | F5-TTS only (16=fast, 32=quality) |
| `cfg_strength` | 1.0-3.0 | 2.0 | F5-TTS only (text adherence) |

---

## Common Development Tasks

### Testing a New TTS Engine

1. **Add engine initialization** in `TTSService._initialize_[engine]()`
2. **Add synthesis method** `_synthesize_chunk_[engine]()`
3. **Update `_load_engine()`** to route to new engine
4. **Create voice profile** with `"engine": "[engine]"`
5. **Test with**: `python test_voice_cloning_[engine].py`

### Debugging Generation Failures

**Check these in order**:

1. **Logs**: `logs/app.log` for detailed error messages
2. **Chunk sizes**: Look for "Max words per chunk" in logs. XTTS2 MUST be ≤220 words
3. **Voice profile**: Validate JSON structure and `reference_mp3` path exists
4. **Reference audio**: Ensure file is readable and correct format
5. **Engine installation**: Test engine directly via test script

**Common Issues**:
- **XTTS2 "Token limit exceeded"**: Reduce `max_words` to 200 or lower
- **F5-TTS "Reference text empty"**: Add `reference_text` field with transcription
- **Chatterbox "Model not found"**: Wait for model download on first run (~1GB)

### Adding New Voice Parameters

1. **Update voice profile JSON**: Add parameter to `params` object
2. **Update engine synthesis method**: Pass parameter to engine API
3. **Document in `config.yaml`**: Add to `voice.defaults` with description

---

## Output Structure

```
output/
├── generated/                    # Final podcast episodes
│   └── [YYYYMMDD_HHMMSS]_[title].mp3
├── voice_tests_chatterbox/       # Chatterbox test outputs
├── voice_tests_xtts/             # XTTS2 test outputs
└── voice_tests_f5tts/            # F5-TTS test outputs
```

**Filename Pattern**: `{timestamp}_{title_slug}.mp3`
- Timestamp: `20250127_143022` (sortable)
- Title slug: Sanitized from story content or user input

---

## Engine-Specific Notes

### Chatterbox (Primary Engine)

**Installation**: `pip install chatterbox-tts` (included in requirements.txt)
**Model Download**: ~1GB on first run to `models/chatterbox/`
**Key Parameter**: `exaggeration` (0.0-1.0) controls expressiveness
**Strengths**: Best voice quality, MIT license, good expressiveness control
**Limitations**: 1200 character chunk limit

### XTTS2 (Fallback Engine)

**Installation**: `pip install TTS` (Coqui TTS library)
**Critical Limitation**: 400-token (~220 word) hard limit per chunk
**Required Config**: `"split_sentences": true` in voice profile
**Required Chunking**: `"max_words": 220` or lower
**Torch Loading Fix**: Uses `weights_only=False` workaround for pickle loading
**Strengths**: Good quality, widely tested, CPU-friendly
**Limitations**: Non-commercial license (Coqui Public Model License)

### F5-TTS (Alternative Engine)

**Installation**: `pip install f5-tts`
**Setup Script**: `./setup_f5tts.sh` (automated setup)
**Critical Requirement**: `reference_text` field must contain exact transcription of reference audio
**Audio Format**: Requires 24kHz mono WAV (converts MP3 automatically in test scripts)
**Environment Variable**: Set `PYTHONHASHSEED=0` before running (use `RUN_F5TTS_TEST.sh`)
**Strengths**: Unlimited text length, very fast (0.15x real-time), excellent long-form coherence
**Limitations**: Requires reference transcription, fewer expressiveness controls

---

## Mystery Storytelling Optimization

This application is specifically tuned for mystery/suspense narration:

**Critical Parameters**:
- **Slower speed** (0.85-0.95x): Builds suspense
- **High expressiveness**: Captures tension and drama
- **Extended pauses**: Strategic silence for plot reveals
- **Intonation emphasis**: Foreshadowing through vocal inflection

**Testing Mystery Quality**:
- Use test scripts with provided mystery samples (suspenseful opening, dramatic revelation, etc.)
- Fill out `EVALUATION.md` template (1-10 scoring for suspense, pause timing, intonation)
- Compare engines side-by-side using same reference audio

---

## References

- **Full Documentation**: See `README.md` for comprehensive architecture diagrams
- **Development Plan**: See `development_plan.md` for project phases and roadmap
- **TTS Implementation**: See `docs/TTS_IMPLEMENTATION_NOTES.md` for engine integration details
- **Voice Evaluation**: See `docs/VOICE_EVALUATION_TEMPLATE.md` for quality scoring system
