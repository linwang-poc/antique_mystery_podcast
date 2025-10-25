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
   - **CRITICAL for Mystery Genre**: Voice must be refined and tuned to capture:
     - Appropriate tone for mystery storytelling (suspenseful, engaging)
     - Strategic use of pauses for dramatic effect
     - Proper intonation to build tension and suspense
     - Pacing that allows listeners to absorb plot twists
     - Emotional range suitable for mystery narratives

---

## Technical Requirements

### Technology Constraints
- **Open Source**: All components must be open source (with commercial-friendly licenses)
- **Exception**: LLM models can use frontier APIs (OpenAI or Claude)
  - API keys will be provided by user
- **Local Hosting**: REQUIRED - Application must run entirely on local machine
  - No cloud dependencies for core functionality
  - All processing done locally
  - All data stored locally

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
   - **Input Format**: MP3 files (will be converted internally as needed)
2. Use voice cloning software to extract voice characteristics
3. Fine-tune cloning parameters specifically for mystery storytelling:
   - Speaking speed (slower for suspense)
   - Expressiveness (capturing mystery tone)
   - Pitch/tone (appropriate for narrator voice)
   - Emotional range (suspense, tension, revelation)
   - Breathing/pauses (strategic pauses for dramatic effect)
   - Intonation patterns (building suspense, plot reveals)
4. Test generated samples with mystery story excerpts
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

### Selected TTS Engine: Chatterbox (Resemble AI)

**Why Chatterbox:**
- **MIT License**: Fully commercial-friendly, allowing future monetization
- **Superior Quality**: Beats ElevenLabs in blind tests (63.8% listener preference)
- **Fast Voice Cloning**: Only 5-10 seconds of reference audio required
- **Zero-Shot**: No training required for voice cloning
- **Strong Prosody**: Excellent natural emotional expression, perfect for mystery storytelling
- **Expressiveness**: Can capture suspense, tension, and dramatic pauses
- **State-of-the-Art**: 2025 cutting-edge open-source TTS technology
- **Self-Hosted**: Complete local control, no vendor lock-in
- **MP3 Support**: Can handle MP3 input files (with conversion)

**Technical Requirements:**
- Python 3.10+ environment
- PyTorch (GPU recommended for speed, CPU works but slower)
- 5-10 seconds of clean voice reference (MP3 or WAV)
- Reasonable compute resources (works on standard hardware)

**Why NOT Coqui XTTS v2:**
- **Licensing Issue**: Coqui Public Model License restricts to NON-COMMERCIAL use only
- This would prevent future commercial use/monetization
- Otherwise a solid choice technically

**Other Alternatives Considered:**
1. **F5-TTS**
   - Excellent emotional depth and very fast (0.15 real-time factor)
   - 335M parameters, great for mystery storytelling
   - Check licensing for commercial use

2. **OpenVoice v2**
   - MIT License (commercial-friendly)
   - Only 3 seconds of reference audio needed
   - Solid multilingual support

**Final Verdict**: **Chatterbox** is selected for its combination of:
- Commercial-friendly licensing
- Superior voice quality and prosody
- Excellent expressiveness for mystery genre requirements
- Fast cloning with minimal reference audio
- Local hosting capability

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
- **Audio Formats**:
  - Input: MP3 files (will be converted to WAV internally for processing)
  - Reference voice sample: MP3 format
  - Ending snippet: MP3 format (will be normalized and converted as needed)
  - Output: MP3 or WAV (user preference)
- Ending snippet should match quality/volume of generated narration
- All audio processing done locally (no cloud services)

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
- [ ] Successfully clone voice from provided MP3 sample
- [ ] Generated voice sounds natural and consistent
- [ ] Tunable parameters produce noticeable, desirable changes
- [ ] Voice captures appropriate mystery storytelling tone
- [ ] Strategic pauses and intonation work for suspense
- [ ] Voice profile saved and reusable

### Operating Mode Success
- [ ] Accept text or .docx input
- [ ] Generate narration in cloned voice with mystery-appropriate delivery
- [ ] Proper pacing, pauses, and intonation for suspense
- [ ] Successfully append ending snippet (MP3 format)
- [ ] Export combined audio file (MP3 or WAV)
- [ ] Processing time reasonable for typical story length
- [ ] Audio quality suitable for podcast distribution
- [ ] Application runs entirely on local machine

---

## Next Steps
1. Validate package choice (Coqui TTS vs alternatives)
2. Create detailed development plan
3. Set up development environment
4. Implement training mode
5. Implement operating mode
6. Testing and refinement
