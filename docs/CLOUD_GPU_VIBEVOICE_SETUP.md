# Cloud GPU Setup for VibeVoice Integration

Since VibeVoice requires 12GB+ GPU VRAM and you're running on CPU-only laptop, this guide shows how to use cloud GPUs for high-quality mystery narration generation.

---

## Why Use Cloud GPU for VibeVoice?

**VibeVoice Advantages:**
- No token limits (64K context = ~50,000 words)
- Perfect for mystery narration (dramatic pauses, suspenseful intonation)
- Long-form coherence (up to 90 minutes)
- Natural emotional delivery
- Male voice cloning support

**Cost-Effective Approach:**
- Develop/test code locally on CPU
- Rent GPU only for final audio generation
- Pay per hour (not 247)
- Cancel after generation completes

---

## Recommended Cloud GPU Services

### Option A: RunPod (Recommended for Beginners)

**Pricing:** $0.34-0.69/hour for RTX 4090 (24GB VRAM)

**Setup Steps:**
1. Create account at https://runpod.io
2. Add $10-20 credit (enough for 20-60 hours)
3. Deploy a "PyTorch" template pod with:
   - GPU: RTX 4090 24GB (or RTX 3090)
   - Storage: 20GB
   - Template: PyTorch 2.0+

4. Connect via Jupyter or SSH
5. Clone your repository:
   ```bash
   git clone https://github.com/[your-username]/antique_mystery_podcast.git
   cd antique_mystery_podcast
   ```

6. Install dependencies:
   ```bash
   pip install git+https://github.com/vibevoice-community/VibeVoice.git
   pip install -r requirements.txt
   ```

7. Generate audio:
   ```bash
   python scripts/vibevoice_generate.py --input story.txt --output mystery.wav
   ```

8. **Download output and terminate pod** to stop charges

**Cost Example:**
- 10-minute mystery: ~60 min generation × $0.50/hr = **$0.50**
- 30-minute podcast: ~180 min generation × $0.50/hr = **$1.50**

---

### Option B: Vast.ai (Cheapest Option)

**Pricing:** $0.20-0.40/hour for RTX 3090/4090

**Setup:**
1. Browse GPU marketplace: https://vast.ai
2. Filter by:
   - GPU: RTX 3090 or RTX 4090
   - VRAM: >12GB
   - Sort by: $/hour (ascending)

3. Rent instance with PyTorch image
4. Follow same steps as RunPod

**Pros:** Often 30-50% cheaper
**Cons:** Less reliable (P2P marketplace), varying availability

---

### Option C: Google Colab Pro ($10/month)

**Pricing:** $10/month subscription (includes 100 compute units)

**Setup:**
1. Subscribe to Colab Pro: https://colab.research.google.com
2. Create new notebook
3. Change runtime to GPU (A100 or T4)
4. Install VibeVoice:
   ```python
   !git clone https://github.com/vibevoice-community/VibeVoice.git
   %cd VibeVoice
   !pip install -e .
   ```

5. Upload your story and reference audio
6. Run generation script (see `vibevoice_colab_example.ipynb`)

**Pros:** Fixed monthly cost, Google infrastructure reliability
**Cons:** Usage limits (100 units/month), slower than dedicated rentals

---

## VibeVoice Generation Workflow (Cloud GPU)

### 1. Prepare Locally (No GPU Needed)

```bash
# On your laptop - NO GPU required
cd /Users/linwang/Documents/GitHub/antique_mystery_podcast

# Prepare your mystery story
cat > input/my_mystery_story.txt << 'EOF'
[Your full mystery story text here...]
EOF

# Prepare male voice reference (5-15 seconds)
# Use existing: assets/reference_voices/training_01.mp3
# Or record new male narrator voice
```

### 2. Transfer to Cloud GPU

**Upload to RunPod/Vast.ai:**
```bash
# From laptop
scp -P [port] input/my_mystery_story.txt root@[pod-ip]:~/
scp -P [port] assets/reference_voices/training_01.mp3 root@[pod-ip]:~/
```

**Or use Google Drive (for Colab):**
```python
# In Colab notebook
from google.colab import drive
drive.mount('/content/drive')

story_path = '/content/drive/MyDrive/mystery_story.txt'
voice_path = '/content/drive/MyDrive/training_01.mp3'
```

### 3. Generate on Cloud GPU

```bash
# On cloud GPU instance
python scripts/vibevoice_generate.py \
    --input my_mystery_story.txt \
    --voice training_01.mp3 \
    --output mystery_narration.wav \
    --cfg_scale 1.3 \
    --inference_steps 5
```

**Generation Time:**
- 1 minute audio = ~6-7 minutes
- 10 minutes audio = ~60 minutes
- 30 minutes audio = ~3 hours

### 4. Download and Terminate

```bash
# Download to laptop
scp -P [port] root@[pod-ip]:~/mystery_narration.wav output/generated/

# IMPORTANT: Terminate pod to stop charges!
```

---

## Cost Comparison

| Story Length | Generation Time | RunPod Cost | Vast.ai Cost | Colab Pro |
|--------------|-----------------|-------------|--------------|-----------|
| 5 minutes    | ~30 min         | $0.25       | $0.15        | Free*     |
| 10 minutes   | ~60 min         | $0.50       | $0.30        | Free*     |
| 30 minutes   | ~3 hours        | $1.50       | $1.00        | Free*     |
| 60 minutes   | ~6 hours        | $3.00       | $2.00        | $10/mo**  |

*Within monthly compute unit limit
**Exceeds free tier, uses paid compute units

---

## Integration with Current Codebase

See `src/tts/engines/vibevoice_cloud.py` for implementation that:
1. Detects if running on CPU (local laptop)
2. Prompts user: "Generate on cloud GPU? (y/n)"
3. If yes: Guides through cloud GPU workflow
4. If no: Falls back to XTTS/F5-TTS

---

## Troubleshooting

### "CUDA out of memory"
- Try 12GB GPU instead of 24GB (cheaper)
- Reduce `inference_steps` from 20 → 5
- Split very long stories into chapters

### "Generation too slow"
- Use RTX 4090 instead of 3090 (2x faster)
- Reduce `inference_steps` to 5 (minimum)
- Consider batching multiple stories

### "Audio quality poor"
- Increase `inference_steps` to 10-20
- Improve reference audio quality
- Use `cfg_scale` 1.5-2.0 for stricter adherence

---

## When to Use Cloud GPU vs Local Engines

**Use VibeVoice (Cloud GPU) when:**
- ✅ Story >5,000 words (XTTS chunks would break flow)
- ✅ Quality is paramount (professional podcast)
- ✅ Budget allows $0.50-3.00 per episode
- ✅ Can wait 1-6 hours for generation

**Use XTTS/F5-TTS (Local CPU) when:**
- ✅ Quick iterations/testing
- ✅ Story <3,000 words
- ✅ Zero cost required
- ✅ Quality good enough (not perfect)

---

## Next Steps

1. Test VibeVoice quality with free Colab trial
2. If satisfied, set up RunPod for production
3. Integrate cloud workflow into app (Option 4)

See `scripts/vibevoice_generate.py` for ready-to-use generation script.
