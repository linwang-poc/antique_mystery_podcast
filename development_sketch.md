# Antique Mystery Podcast - Development Sketch

## Project Overview
An application that converts antique mystery stories into voice-narrated podcast episodes with a consistent narrator voice, using AI voice cloning technology.

---

## Business Requirements

### Core Functionality
1. **Document-to-Voice Conversion**
   - Input: Mystery story document (text or Word format) focused on antiques
   - Output: Voice narration file with specific voice characteristics
   - Target voice: Older male narrator (e.g., "grandpa" or "grandfather" voice)

2. **Episode Finale**
   - Append a predefined voice snippet at the end of each story
   - The snippet is a fixed audio file (same for all episodes)
   - Combine story narration + ending snippet into single audio file

3. **Voice Cloning & Style Transfer**
   - Use existing AI-generated voice sample as reference
   - Clone voice characteristics: timbre, pace, intonation, style
   - Maintain consistency across all generated episodes

---

## Technical Requirements

### Technology Constraints
- **Open Source**: All components must be open source
- **Exception**: LLM models can use frontier APIs (OpenAI or Claude)
  - API keys will be provided by user
- **Local Hosting**: Prefer self-hosted solutions when possible

### Operating Modes

#### 1. Operating Mode (Production)
Primary mode for converting new stories to voice files.

**Workflow:**
1. User provides input via simple UI:
   - Raw text input (paste), OR
   - Path to Word document (.docx)
2. App processes text and generates voice narration using pre-cloned voice
3. App appends predefined ending snippet to narration
4. App exports combined audio file
5. User receives confirmation: "The story is ready for your review as [filename]"

**Features:**
- Simple, user-friendly interface
- Access to stored cloned voice profile
- Access to fixed ending snippet audio file
- Audio file combination/concatenation
- File export with clear naming

#### 2. Training Mode (One-Time Setup)
Initial setup to create the cloned voice profile.

**Workflow:**
1. Ingest sample voice file (AI-generated voice user likes)
2. Use voice cloning software to extract voice characteristics
3. Fine-tune cloning parameters:
   - Speaking speed
   - Expressiveness
   - Pitch/tone
   - Emotional range
   - Breathing/pauses
4. Test generated samples
5. Save final cloned voice profile for Operating Mode

**Features:**
- Voice sample ingestion
- Parameter tuning interface
- Sample generation for testing
- Profile persistence/storage

---

## Technical Architecture (Preliminary)

### Components

1. **Frontend/UI Layer**
   - Simple web interface or desktop GUI
   - Text input or file upload
   - Progress indication
   - Audio playback for review

2. **Backend/Processing Layer**
   - Text extraction (from .docx if needed)
   - LLM integration (optional - for text preprocessing/enhancement)
   - TTS engine integration
   - Audio processing (concatenation, normalization)

3. **Voice Cloning Engine**
   - Voice cloning model/service
   - Parameter storage
   - Voice profile management

4. **Storage Layer**
   - Voice profile storage
   - Ending snippet storage
   - Generated audio files
   - Configuration/settings

---

## Package Research & Recommendations

### Primary Candidate: Coqui TTS (XTTS v2)

**Why Coqui TTS / XTTS v2:**
- **Voice Cloning**: Can clone target speaker with 6-10 seconds of reference audio
- **Style Transfer**: Transfers intonation, emotion, pacing from reference
- **Multilingual**: Supports multiple languages if needed
- **Expressive**: Captures emotional tone (warm, storytelling, serious)
- **Flexibility**: Can achieve various "grandpa" styles (wise, tired, grumpy)
- **API Available**: `xtts-api-server` provides HTTP endpoint
  - Default: localhost:8020
  - POST text + voice profile → get WAV audio
  - Supports streaming
- **Self-Hosted**: No vendor lock-in, no per-character billing
- **Open Source**: Permissive license (MPL/MIT-style)

**Technical Requirements:**
- Python 3.10+ environment
- PyTorch (GPU recommended for speed, CPU works but slower)
- 6-10 seconds clean voice reference (mono WAV, ~22kHz)
- Reasonable compute resources

**Alternative Candidates:**
1. **Chatterbox (Resemble AI)**
   - Newer, high-quality TTS
   - MIT-style license
   - Strong natural prosody
   - Would need additional prompting for "old man" tone
   - Less established than Coqui for voice cloning

**Verdict**: Coqui TTS/XTTS v2 is the recommended choice for this project.

---

## Key Considerations

### Voice Cloning Ethics & Legal
- Ensure AI-generated reference voice was created ethically
- Do NOT clone real person's voice without explicit consent
- Voice likeness is part of personal identity (similar to face likeness)
- For commercial use, verify all rights and permissions

### Audio Quality
- Input text quality affects narration quality
- Reference audio should be clean, clear, minimal background noise
- Ending snippet should match quality/volume of generated narration

### Performance
- GPU recommended for faster generation (important for longer stories)
- CPU-only mode viable for occasional use or shorter texts
- Consider batch processing for multiple stories

### Scalability
- Single-user application initially
- Could expand to multi-user with voice profile management
- Could add multiple narrator voices (different character voices)

---

## Success Criteria

### Training Mode Success
- [ ] Successfully clone voice from provided sample
- [ ] Generated voice sounds natural and consistent
- [ ] Tunable parameters produce noticeable, desirable changes
- [ ] Voice profile saved and reusable

### Operating Mode Success
- [ ] Accept text or .docx input
- [ ] Generate narration in cloned voice
- [ ] Successfully append ending snippet
- [ ] Export combined audio file
- [ ] Processing time reasonable for typical story length
- [ ] Audio quality suitable for podcast distribution

---

## Next Steps
1. Validate package choice (Coqui TTS vs alternatives)
2. Create detailed development plan
3. Set up development environment
4. Implement training mode
5. Implement operating mode
6. Testing and refinement
