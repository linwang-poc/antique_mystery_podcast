# TTS Implementation Notes

## Current Status

The `test_voice_cloning.py` script is a **framework** with placeholders for actual TTS implementation.

The following functions need actual TTS library integration:

### 1. `load_tts_engine(engine_type)`

**Current:** Returns placeholder object
**Needed:** Actual initialization of Chatterbox or GPT-SoVITS

**For Chatterbox:**
```python
# Research needed: Check Chatterbox documentation for initialization
# Example (may need adjustment):
from chatterbox import ChatterboxTTS
model = ChatterboxTTS()  # May need model path or config
```

**For GPT-SoVITS:**
```python
# Research needed: Check gpt-sovits-python documentation
# Example (may need adjustment):
from gpt_sovits import GPTSOVITS
model = GPTSOVITS()  # May need model path or config
```

---

### 2. `clone_voice(tts_engine, reference_audio_path)`

**Current:** Returns placeholder string
**Needed:** Actual voice cloning from MP3 file

**Research needed:**
- How does each TTS engine accept reference audio?
- Is it a file path or loaded audio array?
- What format does it return (voice embedding, model state, etc.)?

**Pseudocode:**
```python
# Load reference audio
audio = load_audio(reference_audio_path)  # May need audio processing

# Create voice profile/embedding
voice_profile = tts_engine.clone_voice(
    reference_audio=audio,
    # May need additional parameters
)

return voice_profile
```

---

### 3. `generate_sample(tts_engine, voice_profile, text, output_path, params)`

**Current:** Returns placeholder True
**Needed:** Actual TTS generation with parameters

**Research needed:**
- How to pass voice profile to TTS engine?
- How to set voice parameters (speed, pitch, pauses, etc.)?
- Does it directly save to file or return audio data?

**Pseudocode:**
```python
# Generate audio from text
audio = tts_engine.synthesize(
    text=text,
    voice=voice_profile,

    # Voice parameters (names may differ by engine)
    speed=params["speed"],
    pitch=params["pitch"],
    expressiveness=params["expressiveness"],
    # etc.
)

# Save to file
save_audio(audio, output_path, format="mp3")

return True
```

---

## Implementation Steps

1. **Install TTS engine on Mac** (see SETUP_INSTRUCTIONS.md)

2. **Research TTS API:**
   - Read Chatterbox or GPT-SoVITS documentation
   - Find examples of voice cloning
   - Identify correct parameter names

3. **Update test_voice_cloning.py:**
   - Replace TODOs with actual TTS calls
   - Add error handling
   - Test with one sample first

4. **Run test:**
   ```bash
   python test_voice_cloning.py
   ```

5. **Debug and iterate**

---

## Helpful Resources

### Chatterbox Documentation
- GitHub: https://github.com/resemble-ai/chatterbox
- Examples: Check `examples/` directory in repository
- API docs: Look for API reference or docstrings

### GPT-SoVITS Documentation
- PyPI: https://pypi.org/project/gpt-sovits-python/
- GitHub: https://github.com/RVC-Boss/GPT-SoVITS
- Examples: Check for inference examples

### Audio Processing
- Use `pydub` for loading/saving MP3:
  ```python
  from pydub import AudioSegment
  audio = AudioSegment.from_mp3("file.mp3")
  ```

- Or `torchaudio`:
  ```python
  import torchaudio
  waveform, sample_rate = torchaudio.load("file.mp3")
  ```

---

## Alternative Approach

If TTS implementation is complex, consider:

1. **Test with simple TTS first** (like `pyttsx3` or `gTTS`) to validate workflow
2. **Then swap in advanced TTS** once framework is working
3. **Or request help** from someone familiar with the TTS library

---

## Questions to Answer

When implementing, determine:

- [ ] Does TTS need GPU or can run on CPU?
- [ ] What audio format does TTS expect? (WAV, MP3, array)
- [ ] How long does voice cloning take?
- [ ] How long does generation take per sample?
- [ ] Are there pretrained models to download?
- [ ] Where are models cached?
- [ ] Can parameters be adjusted per-generation or only at model init?

---

## Testing Checklist

Once implemented:

- [ ] Script runs without errors
- [ ] Voice cloning completes successfully
- [ ] 5 MP3 files are generated
- [ ] Files are playable
- [ ] Voice sounds similar to reference
- [ ] Parameters affect output (test different values)
- [ ] Evaluation template is created

---

**Note:** The development team can help implement this once you share which TTS engine works on your M1 Mac and what errors/issues you encounter!
