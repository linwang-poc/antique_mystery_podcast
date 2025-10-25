# Where Are the Generated MP3 Files?

## Current Status

The voice cloning test script (`test_voice_cloning.py`) is **currently running in the background**.

It's initializing the Chatterbox TTS model and will generate voice samples. This process takes several minutes on an M1 Mac CPU.

---

## Where Files Will Be Generated

Once the test completes, you'll find the MP3 files in:

```
output/voice_tests/test_YYYYMMDD_HHMMSS/
```

The exact timestamp will be when the test started generating files.

### Expected Files:

1. `01_suspenseful_opening.mp3` - Suspenseful mystery opening
2. `02_dramatic_revelation.mp3` - Dramatic revelation scene
3. `03_tense_confrontation.mp3` - Tense dialogue confrontation
4. `04_descriptive_atmosphere.mp3` - Atmospheric description
5. `05_plot_twist.mp3` - Plot twist narration
6. `EVALUATION.md` - Template for you to fill out ratings

---

## How to Check Progress

### Option 1: Check the output directory
```bash
ls -lh output/voice_tests/
```

### Option 2: Check for test process
```bash
ps aux | grep test_voice_cloning
```

### Option 3: Check log file
```bash
tail -f test_output.log
```

---

## Expected Timeline

On an M1 Mac (CPU mode):
- **Model initialization:** 1-3 minutes
- **Voice cloning prep:** < 1 minute
- **Each sample generation:** 2-5 minutes
- **Total time:** ~15-30 minutes for 5 samples

The process is slower than GPU but will complete successfully.

---

## What to Do While Waiting

1. The script is running automatically in the background
2. You can continue working on other things
3. Check back in 15-20 minutes
4. Look for files in `output/voice_tests/test_*/`

---

## Once Files Are Generated

### Step 1: Listen to All 5 MP3 Files
Use Finder or QuickLook to play each file:
```bash
open output/voice_tests/test_*/
```

### Step 2: Fill Out Evaluation
Open `EVALUATION.md` and rate each sample:
- Voice Quality (1-10)
- Suspense/Drama (1-10)
- Pause Timing (1-10)
- Intonation (1-10)
- Pacing (1-10)
- Emotion (1-10)

### Step 3: Decide PASS or FAIL
- **PASS** → Voice quality is good, proceed with development
- **FAIL** → Need to adjust parameters and regenerate

### Step 4: Share Results
```bash
# Copy evaluation to docs/
cp output/voice_tests/test_*/EVALUATION.md docs/voice_test_results.md

# Commit and push
git add docs/voice_test_results.md
git commit -m "Add voice cloning test results"
git push
```

---

## Troubleshooting

### If the script seems stuck:
Check the log:
```bash
tail -30 test_output.log
```

### If you want to stop it:
```bash
ps aux | grep test_voice_cloning | grep -v grep | awk '{print $2}' | xargs kill
```

### If you want to run it again:
```bash
source venv/bin/activate
python test_voice_cloning.py
```

---

**Note:** The first run always takes longer because Chatterbox needs to download and initialize its weights. Subsequent runs will be faster.
