# Antique Mystery Podcast - Development Plan

## Executive Summary

This plan outlines the development of a voice narration application that converts antique mystery stories into podcast-quality audio files using AI voice cloning technology. The application will have two modes: Training Mode (one-time setup) and Operating Mode (production use).

**Recommended TTS Engine:** Chatterbox (MIT License) or F5-TTS
**Alternative:** Coqui XTTS v2 (non-commercial use only)

---

## Technology Stack

### Core Components

**Backend:**
- Python 3.10+
- FastAPI (web framework for API endpoints)
- PyTorch (deep learning framework)
- TTS Engine: Chatterbox or F5-TTS
- pydub (audio processing and concatenation)
- python-docx (Word document parsing)

**Frontend:**
- Gradio (simple, fast Python-based UI) OR
- Streamlit (alternative simple UI framework)
- HTML/CSS/JavaScript (if custom UI needed)

**Storage:**
- Local filesystem for voice profiles
- Local filesystem for audio assets (ending snippet, generated files)
- SQLite or JSON for configuration/metadata (optional)

**Optional LLM Integration:**
- OpenAI API (if text preprocessing needed)
- Anthropic Claude API (alternative)

---

## Project Structure

```
antique_mystery_podcast/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── config.yaml           # Application configuration
│   └── voice_profiles.json   # Saved voice profile metadata
├── assets/
│   ├── ending_snippet.wav    # Fixed ending audio file
│   └── reference_voices/     # Reference audio samples
├── src/
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── config.py             # Configuration management
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── training_mode.py  # Training mode logic
│   │   └── operating_mode.py # Operating mode logic
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── tts_engine.py     # TTS engine wrapper
│   │   └── voice_cloner.py   # Voice cloning logic
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── processor.py      # Audio processing utilities
│   │   └── concatenator.py   # Audio file combination
│   ├── document/
│   │   ├── __init__.py
│   │   └── parser.py         # Document parsing (txt, docx)
│   └── ui/
│       ├── __init__.py
│       ├── training_ui.py    # Training mode interface
│       └── operating_ui.py   # Operating mode interface
├── output/
│   └── generated/            # Generated audio files
├── tests/
│   ├── __init__.py
│   ├── test_tts.py
│   ├── test_audio.py
│   └── test_document.py
└── docs/
    ├── development_sketch.md
    ├── development_plan.md
    └── user_guide.md
```

---

## Development Phases

### Phase 0: Environment Setup (Est. 2-3 hours)

**Tasks:**
1. Set up Python virtual environment
2. Install base dependencies (Python 3.10+, PyTorch)
3. Install TTS engine (Chatterbox or F5-TTS)
4. Test TTS engine installation with basic example
5. Create project structure (directories, init files)
6. Set up git repository and .gitignore
7. Create requirements.txt

**Deliverables:**
- Working Python environment
- Project structure in place
- TTS engine functional and tested
- requirements.txt with all dependencies

**Acceptance Criteria:**
- Can import TTS library without errors
- Can generate a simple "Hello World" audio file
- Project structure matches plan

---

### Phase 1: Core Audio Processing (Est. 4-5 hours)

**Tasks:**
1. **Document Parser Module** (`src/document/parser.py`)
   - Implement text file reader
   - Implement .docx parser using python-docx
   - Text cleaning and preprocessing
   - Handle encoding issues

2. **Audio Processing Module** (`src/audio/processor.py`)
   - Load audio files (WAV, MP3)
   - Audio normalization (volume leveling)
   - Format conversion utilities
   - Audio metadata extraction

3. **Audio Concatenation Module** (`src/audio/concatenator.py`)
   - Combine multiple audio files
   - Handle sample rate matching
   - Add crossfade/smooth transitions (optional)
   - Export to WAV/MP3

**Deliverables:**
- Document parser that handles .txt and .docx
- Audio processing utilities
- Audio concatenation function
- Unit tests for each module

**Acceptance Criteria:**
- Can extract text from Word documents
- Can load and process audio files
- Can concatenate two audio files successfully
- All tests pass

---

### Phase 2: TTS Engine Integration (Est. 6-8 hours)

**Tasks:**
1. **TTS Engine Wrapper** (`src/tts/tts_engine.py`)
   - Create abstraction layer for TTS engine
   - Implement text-to-speech generation
   - Handle long text chunking (if needed)
   - Implement streaming/batch processing
   - Error handling and retries

2. **Voice Cloning Module** (`src/tts/voice_cloner.py`)
   - Implement reference audio loading
   - Voice profile creation from sample
   - Parameter tuning interface:
     - Speed/pace adjustment
     - Expressiveness control
     - Pitch/tone modification
     - Emotional range settings
   - Voice profile serialization/deserialization
   - Voice profile storage

3. **Configuration Management** (`src/config.py`)
   - Load configuration from YAML
   - Manage voice profile metadata
   - Environment variable handling
   - Default settings

**Deliverables:**
- TTS engine wrapper with clean API
- Voice cloning functionality
- Configuration management system
- Voice profile storage system

**Acceptance Criteria:**
- Can generate speech from text using default voice
- Can clone voice from reference audio sample
- Can adjust voice parameters (speed, pitch, etc.)
- Can save and load voice profiles
- Configuration loads correctly

---

### Phase 3: Training Mode Implementation (Est. 5-6 hours)

**Tasks:**
1. **Training Mode Logic** (`src/modes/training_mode.py`)
   - Voice sample ingestion
   - Voice cloning workflow
   - Parameter tuning interface
   - Sample generation for testing
   - Voice profile saving

2. **Training UI** (`src/ui/training_ui.py`)
   - Audio file upload component
   - Parameter adjustment sliders/inputs:
     - Speed (0.5x - 2.0x)
     - Expressiveness (1-10 scale)
     - Pitch adjustment (-12 to +12 semitones)
     - Emotional intensity (1-10 scale)
   - "Generate Test Sample" button
   - Audio playback for comparison
   - "Save Voice Profile" button
   - Status messages and progress bars

3. **Sample Testing Workflow**
   - Generate multiple test samples with different settings
   - Side-by-side comparison with reference
   - Iteration support until satisfied

**Deliverables:**
- Complete training mode backend
- Functional training UI
- Voice profile creation workflow
- Testing and comparison tools

**Acceptance Criteria:**
- Can upload reference voice sample
- Can adjust voice parameters via UI
- Can generate test samples and play them back
- Can compare generated voice with reference
- Can save finalized voice profile
- UI provides clear feedback and status

---

### Phase 4: Operating Mode Implementation (Est. 5-6 hours)

**Tasks:**
1. **Operating Mode Logic** (`src/modes/operating_mode.py`)
   - Document input handling (text or .docx)
   - Text-to-speech generation using saved profile
   - Load ending snippet
   - Combine narration + ending snippet
   - File export with naming convention
   - Progress tracking

2. **Operating UI** (`src/ui/operating_ui.py`)
   - Text input textarea OR file upload
   - Voice profile selection dropdown
   - "Generate Podcast" button
   - Progress bar with stages:
     - "Parsing document..."
     - "Generating narration..."
     - "Adding ending..."
     - "Exporting file..."
   - Success message with filename
   - Audio playback component
   - Download button

3. **File Management**
   - Automatic filename generation (timestamp-based)
   - Output directory management
   - Cleanup old files (optional)

**Deliverables:**
- Complete operating mode backend
- Functional operating UI
- End-to-end story-to-audio pipeline
- File management system

**Acceptance Criteria:**
- Can input text or upload .docx file
- Can select saved voice profile
- Generates complete narration in cloned voice
- Successfully appends ending snippet
- Exports final audio file
- Displays success message with filename
- User can play and download result

---

### Phase 5: Main Application & Integration (Est. 3-4 hours)

**Tasks:**
1. **Main Application** (`src/main.py`)
   - Mode selection (Training vs Operating)
   - Application initialization
   - Routing between modes
   - Global error handling
   - Logging setup

2. **UI Integration**
   - Create unified interface with mode tabs
   - Consistent styling
   - Navigation between modes
   - Help text and instructions

3. **Configuration**
   - Create default config.yaml
   - Set up .env.example for API keys
   - Document all configuration options

**Deliverables:**
- Complete main application
- Unified UI with both modes
- Configuration files
- Logging system

**Acceptance Criteria:**
- Application launches successfully
- Can switch between Training and Operating modes
- Both modes function correctly
- Configuration loads properly
- Errors are logged and displayed appropriately

---

### Phase 6: Testing & Refinement (Est. 4-5 hours)

**Tasks:**
1. **Unit Testing**
   - Write tests for document parser
   - Write tests for audio processing
   - Write tests for TTS integration
   - Write tests for file operations

2. **Integration Testing**
   - Test complete training workflow
   - Test complete operating workflow
   - Test edge cases (very long texts, special characters)
   - Test error scenarios

3. **User Acceptance Testing**
   - Test with real antique mystery story
   - Verify audio quality
   - Check voice consistency
   - Validate ending snippet integration
   - Test with different document formats

4. **Refinement**
   - Fix bugs found during testing
   - Optimize performance
   - Improve error messages
   - Enhance UI/UX based on testing

**Deliverables:**
- Comprehensive test suite
- Bug fixes
- Performance optimizations
- Polished user experience

**Acceptance Criteria:**
- All unit tests pass
- Integration tests pass
- Can successfully process real story end-to-end
- Audio quality meets expectations
- No critical bugs
- UI is intuitive and responsive

---

### Phase 7: Documentation & Deployment (Est. 2-3 hours)

**Tasks:**
1. **User Documentation**
   - Installation guide
   - Training mode tutorial
   - Operating mode tutorial
   - Troubleshooting section
   - FAQ

2. **Developer Documentation**
   - Code documentation (docstrings)
   - Architecture overview
   - API documentation
   - Contributing guide

3. **Deployment Preparation**
   - Create requirements.txt
   - Document system requirements
   - Create setup script (optional)
   - Package application (optional)

**Deliverables:**
- Complete user guide
- Developer documentation
- Deployment instructions
- README.md

**Acceptance Criteria:**
- User can follow docs to install and use application
- All code is documented
- README provides clear project overview
- Installation process is documented

---

## Detailed Implementation Notes

### TTS Engine Selection & Setup

**Option 1: Chatterbox (Recommended)**
```bash
pip install torch torchaudio
pip install chatterbox-tts  # hypothetical package name
```

Advantages:
- MIT License (commercial-friendly)
- High quality, beats commercial TTS
- 5-10 seconds for cloning
- Strong prosody for storytelling

Setup considerations:
- May require model download on first run
- GPU recommended but not required
- Check official docs for exact installation

**Option 2: F5-TTS**
```bash
pip install torch torchaudio
pip install f5-tts
```

Advantages:
- Excellent emotional depth
- Very fast (0.15 real-time factor)
- 10 seconds for cloning
- 335M parameters

**Option 3: Coqui XTTS v2 (if non-commercial is acceptable)**
```bash
pip install TTS
```

Advantages:
- Well-documented
- Proven in production
- Easy HTTP API via xtts-api-server
- 6-10 seconds for cloning

Licensing caveat:
- Non-commercial use only

### Voice Cloning Parameters

The training UI should expose these parameters:

1. **Speed (0.5x - 2.0x)**
   - Slower speed for thoughtful, deliberate narration
   - Recommended for "grandpa storyteller": 0.9x - 1.0x

2. **Expressiveness (1-10)**
   - Higher = more emotional variation
   - Recommended for storytelling: 6-8

3. **Pitch Adjustment (-12 to +12 semitones)**
   - Negative values for deeper, older voice
   - Recommended: -2 to -4 for older male voice

4. **Emotional Intensity (1-10)**
   - Controls overall emotional energy
   - Recommended for mystery stories: 5-7

5. **Pause Duration Multiplier (0.5x - 2.0x)**
   - Longer pauses for dramatic effect
   - Recommended: 1.2x - 1.5x

### Audio Processing Specifications

**Input Audio (Reference Voice):**
- Format: WAV (preferred) or MP3
- Sample Rate: 22050 Hz or 44100 Hz
- Channels: Mono (stereo will be converted)
- Duration: 6-10 seconds minimum
- Quality: Clean, no background noise

**Output Audio:**
- Format: WAV (for quality) or MP3 (for size)
- Sample Rate: 22050 Hz (standard for speech)
- Channels: Mono
- Bit Depth: 16-bit
- Compression: None (WAV) or 192kbps (MP3)

**Ending Snippet:**
- Should match output specifications
- Volume-normalized to -20 dB LUFS
- Crossfade duration: 0.5-1.0 seconds (optional)

### Text Processing Considerations

1. **Text Cleaning:**
   - Remove formatting artifacts from Word docs
   - Normalize whitespace
   - Handle special characters appropriately
   - Preserve paragraph breaks (for natural pauses)

2. **Chunking for Long Texts:**
   - TTS engines may have max text length
   - Split on paragraph or sentence boundaries
   - Typical chunk size: 500-1000 characters
   - Preserve context across chunks

3. **LLM Preprocessing (Optional):**
   - If needed, use Claude/OpenAI to:
     - Fix formatting issues
     - Add pronunciation hints
     - Identify dialogue vs narration
     - Suggest emphasis points

### Error Handling

**Critical Error Scenarios:**
1. TTS engine fails to initialize
2. Reference audio file corrupted/missing
3. Document parsing fails
4. Audio concatenation fails
5. Insufficient disk space
6. GPU out of memory

**Error Handling Strategy:**
- Graceful degradation (CPU fallback)
- Clear error messages to user
- Detailed logging for debugging
- Retry logic for transient failures
- Input validation before processing

### Performance Optimization

**GPU Usage:**
- Enable CUDA if available
- Batch processing for multiple chunks
- Model caching to avoid reloading

**Memory Management:**
- Stream large audio files
- Clear cache between generations
- Limit concurrent operations

**Speed Improvements:**
- Pre-load models at startup
- Cache voice profiles in memory
- Use faster audio codecs

---

## Testing Strategy

### Unit Tests

**Document Parser:**
- Test text file parsing
- Test .docx parsing
- Test encoding handling
- Test malformed file handling

**Audio Processing:**
- Test audio loading (WAV, MP3)
- Test volume normalization
- Test sample rate conversion
- Test format conversion

**Audio Concatenation:**
- Test combining two files
- Test sample rate mismatch handling
- Test crossfade functionality

**TTS Engine:**
- Test text-to-speech generation
- Test voice cloning
- Test parameter adjustment
- Test error handling

### Integration Tests

**Training Mode:**
- Complete workflow: upload → tune → save
- Test parameter variations
- Test voice profile persistence

**Operating Mode:**
- Complete workflow: input → generate → export
- Test with various document sizes
- Test with special characters
- Test ending snippet concatenation

### User Acceptance Tests

**Real-World Scenarios:**
1. Clone voice from provided sample
2. Generate 5-minute narration from story
3. Verify voice consistency throughout
4. Verify ending snippet integration
5. Verify output file playability

**Quality Checks:**
- Voice sounds natural
- Pacing is appropriate
- No artifacts or glitches
- Volume levels consistent
- Ending transition smooth

---

## Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] PyTorch installed (with CUDA if GPU available)
- [ ] TTS engine installed and tested
- [ ] All dependencies in requirements.txt
- [ ] Configuration files created (.env, config.yaml)
- [ ] Reference voice sample prepared
- [ ] Ending snippet audio file prepared
- [ ] Output directory created
- [ ] All tests passing
- [ ] Documentation complete
- [ ] User guide available

---

## Timeline Estimate

**Total Development Time: 30-35 hours**

| Phase | Description | Est. Hours |
|-------|-------------|------------|
| Phase 0 | Environment Setup | 2-3 |
| Phase 1 | Core Audio Processing | 4-5 |
| Phase 2 | TTS Engine Integration | 6-8 |
| Phase 3 | Training Mode | 5-6 |
| Phase 4 | Operating Mode | 5-6 |
| Phase 5 | Integration | 3-4 |
| Phase 6 | Testing & Refinement | 4-5 |
| Phase 7 | Documentation | 2-3 |

**Development Schedule (Part-time):**
- Week 1: Phases 0-1 (Setup + Audio Processing)
- Week 2: Phase 2 (TTS Integration)
- Week 3: Phases 3-4 (Training + Operating Modes)
- Week 4: Phases 5-7 (Integration, Testing, Docs)

**Development Schedule (Full-time):**
- Days 1-2: Phases 0-2
- Days 3-4: Phases 3-4
- Day 5: Phases 5-7

---

## Risk Assessment

### Technical Risks

**Risk 1: TTS Engine Performance**
- Impact: High
- Likelihood: Medium
- Mitigation: Test early with long texts, have CPU fallback

**Risk 2: Voice Cloning Quality**
- Impact: High
- Likelihood: Medium
- Mitigation: Extensive testing in training mode, parameter tuning

**Risk 3: Audio Quality Issues**
- Impact: Medium
- Likelihood: Low
- Mitigation: Use established audio libraries, test thoroughly

**Risk 4: Dependency Conflicts**
- Impact: Medium
- Likelihood: Medium
- Mitigation: Use virtual environment, pin versions in requirements.txt

### Non-Technical Risks

**Risk 1: Voice Cloning Ethics/Legal**
- Impact: High
- Likelihood: Low (if using AI-generated reference)
- Mitigation: Document voice origin, add usage disclaimer

**Risk 2: Scope Creep**
- Impact: Medium
- Likelihood: Medium
- Mitigation: Stick to MVP features, document future enhancements

---

## Future Enhancements (Post-MVP)

1. **Multiple Voice Profiles**
   - Support different narrators
   - Character voices for dialogue

2. **Advanced Audio Effects**
   - Background music
   - Sound effects
   - Reverb/ambiance

3. **Batch Processing**
   - Process multiple stories at once
   - Queue management

4. **Web Interface**
   - Deploy as web application
   - Multi-user support
   - Cloud storage

5. **LLM Integration**
   - Story enhancement
   - Automatic chapter detection
   - Dialogue extraction

6. **Export Formats**
   - MP3 with metadata (ID3 tags)
   - Podcast RSS feed generation
   - Direct upload to podcast platforms

7. **Voice Mixing**
   - Blend multiple voice characteristics
   - Create custom voice profiles

8. **Real-time Preview**
   - Live text-to-speech as you type
   - Instant parameter changes

---

## Success Metrics

**Training Mode Success:**
- Voice cloning time < 2 minutes
- User satisfaction with cloned voice quality
- Successful voice profile save/load

**Operating Mode Success:**
- Processing time < 2x story duration
- Audio quality rating > 8/10
- No critical errors in 10 consecutive runs
- Smooth ending snippet integration

**Overall Success:**
- Complete story-to-podcast in < 10 minutes
- Output suitable for podcast distribution
- User can operate without technical assistance
- Application runs on standard hardware

---

## Approval & Sign-off

This development plan requires approval before implementation begins.

**Stakeholder Review:**
- [ ] Business requirements validated
- [ ] Technical approach approved
- [ ] Timeline acceptable
- [ ] Resource requirements confirmed

**Ready to Proceed:**
- [ ] TTS engine choice finalized
- [ ] Reference voice sample available
- [ ] Ending snippet prepared
- [ ] Development environment ready

---

**Next Steps After Approval:**
1. Finalize TTS engine choice (Chatterbox vs F5-TTS vs Coqui)
2. Set up development environment
3. Begin Phase 0: Environment Setup
4. Regular progress updates after each phase
