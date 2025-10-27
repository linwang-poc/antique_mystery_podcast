# F5-TTS Voice Cloning Test Guide

## Overview

This guide helps you test **F5-TTS** as an alternative to XTTS for the Antique Mystery Podcast project. F5-TTS solves the major limitation of XTTS's 400-token restriction.

## Why F5-TTS?

### Advantages over XTTS:
- ✅ **No 400-token limit** - Handles full paragraphs without manual chunking
- ✅ **Better coherence** - Processes entire paragraphs maintaining thematic flow
- ✅ **Multiple reference files** - Can use both training_01.mp3 and training_02.mp3
- ✅ **Auto-chunking** - Automatically handles long text (>30s) intelligently
- ✅ **Fine-tunable** - Can be customized with just 10-15 hours of audio

### Trade-offs:
- ⚠️ **Fewer expressive controls** - No exaggeration, pitch, or emotion parameters
- ⚠️ **~50% slower** than XTTS (but Fast F5-TTS variant is 4x faster)
- ⚠️ **Requires transcription** - Need reference text for training audio

---

## Quick Start

### Step 1: Install F5-TTS

```bash
# Option A: Use the setup script
./setup_f5tts.sh

# Option B: Manual installation
source venv/bin/activate
pip install f5-tts
```

### Step 2: Prepare Reference Transcription

**IMPORTANT:** Before running the test, you need to transcribe your training audio files.

Open `test_voice_cloning_f5_tts.py` and update line ~237:

```python
# Replace this placeholder:
reference_text = "This is a reference transcription..."

# With actual transcription of training_01.mp3 and training_02.mp3:
reference_text = "The actual spoken words in your training audio files."
```

**Tip:** You can use an ASR tool to auto-transcribe, or F5-TTS can do it automatically (uses extra GPU memory).

### Step 3: Run the Test

```bash
source venv/bin/activate
python test_voice_cloning_f5_tts.py
```

### Step 4: Evaluate Results

Check the output in `output/voice_tests_f5tts/test_YYYYMMDD_HHMMSS/`:
- Listen to generated audio samples
- Fill out `EVALUATION.md`
- Compare with XTTS and Chatterbox outputs

---

## F5-TTS Parameters Explained

The script uses these F5-TTS parameters (in `F5_TTS_PARAMS`):

| Parameter | Default | Description | Options |
|-----------|---------|-------------|---------|
| `nfe_step` | 32 | Quality vs Speed | 16=fast, 32=high quality, 7=very fast |
| `cfg_strength` | 2.0 | Text adherence strength | Higher = stricter following |
| `speed` | 0.95 | Playback speed | <1.0 = slower (better for suspense) |
| `ode_method` | "euler" | ODE solver | Usually keep default |
| `sway_sampling_coef` | -1.0 | Sampling quality | Usually keep default |

### What F5-TTS Does NOT Support:
- ❌ No `exaggeration` parameter (like Chatterbox)
- ❌ No `expressiveness` control
- ❌ No `pitch` adjustment
- ❌ No `emotional_intensity`

F5-TTS focuses on **faithful voice reproduction** rather than expressive manipulation.

---

## File Structure

```
test_voice_cloning_f5_tts.py    # Main F5-TTS test script
setup_f5tts.sh                  # Installation helper
F5_TTS_TESTING.md              # This guide

assets/reference_voices/
├── training_01.mp3             # Original training audio
├── training_02.mp3             # Original training audio
├── training_01_f5.wav         # Auto-generated 24kHz mono (F5-TTS format)
└── training_02_f5.wav         # Auto-generated 24kHz mono (F5-TTS format)

output/voice_tests_f5tts/
└── test_YYYYMMDD_HHMMSS/
    ├── 01_suspenseful_opening.wav
    └── EVALUATION.md
```

---

## Comparison: F5-TTS vs XTTS vs Chatterbox

| Feature | Chatterbox | XTTS | F5-TTS |
|---------|------------|------|--------|
| **Token Limit** | None | ❌ 400 tokens | ✅ None (auto-chunks) |
| **Expressive Controls** | ✅✅✅ Many | ❌ Few | ❌ Few |
| **Speed** | Fast | Fast | Slower (~50%) |
| **Voice Quality** | Excellent | Excellent | Excellent |
| **Coherence** | Good | Poor (breaks) | ✅ Excellent |
| **Fine-tuning** | ❌ No | ❌ No | ✅ Yes (10-15h) |
| **Multi-ref Audio** | ❌ No | ❌ No | ✅ Yes |

---

## Troubleshooting

### Error: "f5-tts_infer-cli: command not found"
**Solution:** Install F5-TTS:
```bash
pip install f5-tts
```

### Error: "ffmpeg not found"
**Solution:** Install ffmpeg:
```bash
brew install ffmpeg
```

### Error: "Output file not created"
**Possible causes:**
1. Invalid reference_text transcription
2. Insufficient GPU/CPU memory
3. Audio file format issues

**Solution:** Check logs in terminal output for specific error messages.

### Warning: "Generation timed out"
**Solution:** This can happen for very long text. Try:
1. Reduce `nfe_step` to 16 for faster generation
2. Split into smaller samples
3. Increase timeout in the script (line ~181)

---

## Next Steps After Testing

### If F5-TTS Quality is Good:
✅ Use zero-shot F5-TTS for production (no training needed!)

### If F5-TTS Quality Needs Improvement:
Consider **fine-tuning** F5-TTS:
1. Collect 10-15 hours of narrator audio
2. Transcribe all audio files
3. Follow F5-TTS fine-tuning guide
4. Train custom model for your specific voice

### If F5-TTS Doesn't Meet Needs:
- Stick with Chatterbox (has best expressive controls)
- Or use XTTS with manual text chunking

---

## Advanced: Fine-Tuning F5-TTS

If you want a custom model trained on your narrator's voice:

### Requirements:
- **10-15 hours** of clean audio
- All audio transcribed
- GPU recommended (CPU works but slower)

### Process:
```bash
# Clone F5-TTS repository
git clone https://github.com/SWivid/F5-TTS.git
cd F5-TTS

# Prepare dataset
# - Convert all audio to 24kHz mono WAV
# - Create metadata.csv with: filename, transcription

# Run fine-tuning (Gradio interface)
f5-tts_finetune-gradio

# Or command line
accelerate config
accelerate launch train.py
```

**Training time:** 1-2 days on GPU

---

## Support & Resources

- **F5-TTS GitHub:** https://github.com/SWivid/F5-TTS
- **F5-TTS Paper:** https://arxiv.org/abs/2410.06885
- **Discussion:** https://github.com/SWivid/F5-TTS/discussions

---

## Summary

**Test F5-TTS if you:**
- ✅ Need to process full paragraphs (>400 tokens)
- ✅ Want better thematic coherence
- ✅ Are willing to sacrifice some expressive controls
- ✅ May want to fine-tune in the future

**Stick with current TTS if you:**
- ❌ Need fine-grained expressive controls (Chatterbox)
- ❌ Can work within 400-token chunks (XTTS)
- ❌ Need maximum speed

---

*Last updated: 2025-10-26*
