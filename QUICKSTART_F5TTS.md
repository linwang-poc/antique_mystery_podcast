# F5-TTS Quick Start Guide

## 🚀 3-Step Setup

### Step 1: Install F5-TTS
```bash
./setup_f5tts.sh
```

### Step 2: Add Transcription
Edit `test_voice_cloning_f5_tts.py` line ~237:
```python
reference_text = "Your actual training audio transcription here"
```

### Step 3: Run Test
```bash
source venv/bin/activate
python test_voice_cloning_f5_tts.py
```

---

## 📁 What Gets Created

### Input (Auto-converted):
- `assets/reference_voices/training_01_f5.wav` (24kHz mono)
- `assets/reference_voices/training_02_f5.wav` (24kHz mono)

### Output:
- `output/voice_tests_f5tts/test_YYYYMMDD_HHMMSS/01_suspenseful_opening.wav`
- `output/voice_tests_f5tts/test_YYYYMMDD_HHMMSS/EVALUATION.md`

---

## ⚙️ Parameters You Can Tune

In `test_voice_cloning_f5_tts.py`, edit `F5_TTS_PARAMS`:

```python
F5_TTS_PARAMS = {
    "nfe_step": 32,        # 16=faster, 32=better quality
    "cfg_strength": 2.0,   # Higher = stricter text following
    "speed": 0.95,         # <1.0 = slower (good for mystery)
}
```

---

## ✅ Key Features

- ✅ **Uses BOTH training files** (training_01.mp3 + training_02.mp3)
- ✅ **No 400-token limit** (XTTS has this problem!)
- ✅ **Auto-chunks** long text intelligently
- ✅ **Same mystery samples** as test_voice_cloning.py

---

## 🎯 What to Test

1. **Listen to output** - Does it sound like your narrator?
2. **Check coherence** - Does it maintain dramatic flow across paragraph?
3. **Compare to XTTS** - Better or worse for long text?
4. **Fill out EVALUATION.md** - Document findings

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `command not found: f5-tts_infer-cli` | Run `pip install f5-tts` |
| `ffmpeg not found` | Run `brew install ffmpeg` |
| Generation timeout | Lower `nfe_step` to 16 |
| Poor quality | Update `reference_text` with accurate transcription |

---

## 📊 Decision Matrix

**Use F5-TTS if:**
- ✅ Long paragraphs (>400 tokens)
- ✅ Need better coherence
- ✅ Open to fine-tuning later

**Use Chatterbox if:**
- ✅ Need expressive controls (pitch, emotion, etc.)
- ✅ Want fastest generation

**Use XTTS if:**
- ✅ Short texts (<400 tokens)
- ✅ Happy with sentence-by-sentence synthesis

---

For detailed information, see [F5_TTS_TESTING.md](F5_TTS_TESTING.md)
