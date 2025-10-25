# Voice Cloning Test - Setup Instructions for M1 Mac

This guide will help you set up the TTS engine on your M1 Mac and run voice cloning tests.

---

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- 5GB+ free disk space
- Homebrew installed
- Python 3.10+

---

## Step 1: Install System Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg (required for audio processing)
brew install ffmpeg

# Verify installation
ffmpeg -version
```

---

## Step 2: Clone Repository & Navigate

```bash
# Pull latest changes
cd /path/to/antique_mystery_podcast
git pull origin claude/review-specification-011CUUBDZXPrCAukQS8obm8X

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

---

## Step 3: Install Python Dependencies

### Option A: Try Chatterbox TTS First (Recommended)

```bash
# Install base dependencies
pip install numpy torch torchaudio

# Install Chatterbox TTS
pip install chatterbox-tts

# Verify installation
python -c "import chatterbox; print('Chatterbox version:', chatterbox.__version__)"
```

**If Chatterbox installation fails** (M1 compatibility issues), proceed to Option B.

---

### Option B: Use GPT-SoVITS (M1 Fallback)

```bash
# Install GPT-SoVITS wrapper
pip install gpt-sovits-python

# Verify installation
python -c "import gpt_sovits; print('GPT-SoVITS installed successfully')"
```

---

## Step 4: Verify Voice Files

```bash
# Check voice files are present
ls -lh assets/ending.mp3
ls -lh assets/reference_voices/

# You should see:
# - ending.mp3
# - training_01.mp3, training_02.mp3, training_03.mp3, training_04.mp3
# - testing_1.mp3, testing_02.mp3, testing_03.mp3, testing_04.mp3
```

---

## Step 5: Run Voice Cloning Test

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the test script
python test_voice_cloning.py
```

**Expected Output:**
1. Environment check (verifies files and packages)
2. TTS engine loading
3. Voice cloning from training_01.mp3
4. Generation of 5 mystery samples
5. Creation of evaluation template

**Generated files will be in:**
```
output/voice_tests/test_YYYYMMDD_HHMMSS/
├── 01_suspenseful_opening.mp3
├── 02_dramatic_revelation.mp3
├── 03_tense_confrontation.mp3
├── 04_descriptive_atmosphere.mp3
├── 05_plot_twist.mp3
└── EVALUATION.md
```

---

## Step 6: Evaluate Voice Quality

1. **Listen to each generated MP3 file**
2. **Open `EVALUATION.md` in the output directory**
3. **Fill out ratings for each sample** (1-10 scale)
4. **Mark overall as PASS or FAIL**
5. **Provide specific improvement suggestions**

---

## Step 7: Share Results

Once you've completed the evaluation:

```bash
# Copy the evaluation file to docs/
cp output/voice_tests/test_YYYYMMDD_HHMMSS/EVALUATION.md docs/voice_test_results.md

# Commit the results
git add docs/voice_test_results.md
git commit -m "Add voice cloning test results"
git push
```

Then share your feedback with the development team!

---

## Troubleshooting

### Issue: "No module named 'chatterbox'"

**Solution:**
- Chatterbox may not be M1 compatible
- Try installing from source:
  ```bash
  git clone https://github.com/resemble-ai/chatterbox.git
  cd chatterbox
  pip install -e .
  ```
- Or use GPT-SoVITS (Option B)

### Issue: "No module named 'torch'"

**Solution:**
```bash
pip install torch torchaudio
```

### Issue: TTS generation is very slow

**Expected behavior on M1 Mac:**
- CPU-only inference (no CUDA)
- Each 15-second sample may take 30-60 seconds to generate
- This is normal for voice cloning

### Issue: Generated audio has poor quality

**Potential causes:**
1. Reference audio quality (training_01.mp3)
2. Voice parameters need tuning
3. TTS engine not optimal for your use case

**Solution:** Fill out evaluation with specific feedback so we can adjust parameters

---

## Need Help?

If you encounter issues:

1. Check that all voice files are present
2. Verify Python version is 3.10+
3. Ensure virtual environment is activated
4. Try the alternative TTS engine
5. Share error messages with the team

---

## Next Steps After Testing

Once you've evaluated the voice:

- **If PASS:** Development team proceeds with Phase 1 implementation
- **If FAIL:** Team adjusts voice parameters based on your feedback, you re-test

Goal: Get voice quality perfect BEFORE building the full application!
