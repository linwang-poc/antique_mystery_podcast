# Operating Mode Implementation Plan

## Goal
Deliver a single-screen desktop web app that lets the user select a tuned narrator voice, paste or upload mystery stories, and receive a finished MP3 that appends the `assets/ending.mp3` stinger.

---

## Voice Model Persistence
- **Profile Schema**: Store profiles as `config/voice_profiles/<profile_id>.json` with fields for `id`, `display_name`, `reference_mp3`, `description`, and Chatterbox parameter overrides (`speed`, `expressiveness`, etc.).
- **Loader**: New `src/tts/voice_registry.py` reads all JSON profiles on startup, validates paths, and exposes `get_profile(profile_id)`.
- **Model Warmup**: `src/tts/tts_service.py` loads Chatterbox once (CPU) and caches the engine; generation requests pass the selected profile, reference audio path, and parameters so the result matches our tuned voice.

---

## Text Acquisition
- **UI Inputs**:
  - Gradio textarea for raw story text.
  - Gradio file uploader for `.docx` (optional).
  - Dropdown listing available voice profiles.
- **Parsing**: `src/document/parser.py` handles `.docx` → plain text via python-docx. If both text and file are provided, merge or prioritize file (decide in UX pass).
- **Validation**: Warn when character count > ~10k (~8–9 min audio) to highlight potential CPU strain on an 8 GB Air.

---

## Generation Pipeline
1. **Chunking** (optional): If paragraph count or character length suggests long runtime, split into manageable chunks (e.g., ~400 words) while preserving sentence boundaries.
2. **Synthesis**: For each chunk, call `tts_service.generate_chunk(profile, text_chunk)` which returns a WAV/MP3 in a temp directory.
3. **Intermediate Storage**: Keep chunk WAV/MP3 paths for assembly; clean up after export.

---

## Audio Finishing
- **Concatenation**: `src/audio/concatenator.py` merges generated narration with `assets/ending.mp3` using pydub; optional normalization to match loudness.
- **Export**: Save final file to `output/generated/<timestamp>_<slug>.mp3`. Store metadata (source text hash, profile id) if needed for future reference.

---

## User Feedback & Notifications
- **Progress UI**: Display status messages ("Parsing document", "Generating chunk 2/4", "Merging ending") with Gradio `StatusTracker`.
- **Warnings**: Show non-blocking warning when estimated duration may exceed hardware capabilities; suggest splitting text manually if generation fails.
- **Completion**: Surface download link plus success toast: `"The story is ready as <filename>"`.
- **Error Handling**: Catch TTS or IO errors, display helpful message, and keep temp files for debugging.

---

## Outstanding Questions
- Should we allow multiple narrator profiles and display their tuning notes to the user?
- Do we need to cache rendered episodes for quick replay?
- What level of text chunking is acceptable before pacing artifacts appear?

Tag this document whenever we refine operating mode so everyone shares the same blueprint.
