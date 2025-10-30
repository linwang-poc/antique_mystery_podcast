# Docker Build Testing Guide

## Prerequisites

Before testing the Docker build, ensure you have:

1. **Docker Desktop** installed and running
2. **NVIDIA Container Toolkit** installed (for GPU support)
3. **NVIDIA GPU** with 12GB+ VRAM
4. **CUDA drivers** installed (12.1+)

### Verify GPU Support

```bash
# Check if NVIDIA Docker runtime is available
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

You should see your GPU listed.

---

## Step 1: Build the Docker Image

```bash
# Navigate to project root
cd /Users/linwang/Documents/GitHub/antique_mystery_podcast

# Build the image (this will take 10-15 minutes on first build)
docker build -t vibevoice-app:latest .
```

**Expected output:**
- Downloading NVIDIA PyTorch base image (~8GB)
- Installing system dependencies (ffmpeg, curl)
- Installing Python packages
- Copying application code and assets
- Image size: ~9-10GB

**If build fails**, check:
- Docker has enough disk space (20GB+ free)
- Network connection stable (large downloads)
- requirements_vibevoice.txt syntax correct

---

## Step 2: Test with Docker Compose

```bash
# Start the container with GPU support
docker-compose up

# Or run in detached mode
docker-compose up -d
```

**Expected output:**
```
vibevoice-mystery-narrator | Initializing VibeVoice on cuda...
vibevoice-mystery-narrator | Loading VibeVoice processor from microsoft/VibeVoice-1.5B...
vibevoice-mystery-narrator | ✓ Processor loaded
vibevoice-mystery-narrator | Loading VibeVoice-1.5B model (this may take 1-2 minutes)...
vibevoice-mystery-narrator | ✓ Model loaded on cuda
vibevoice-mystery-narrator | ✓ Inference steps: 15
vibevoice-mystery-narrator | ✓ VibeVoice ready for generation!
vibevoice-mystery-narrator | Running on local URL:  http://0.0.0.0:7860
```

**First run will download the 5.4GB model** (takes 2-5 minutes depending on network).

---

## Step 3: Access the UI

Open your browser and navigate to:

```
http://localhost:7860
```

You should see the **VibeVoice Mystery Narrator** UI with 3 tabs:
1. Format Text
2. Generate Audio
3. Help

---

## Step 4: Test Text Formatting

1. Go to **Tab 1: Format Text**
2. Paste this test text:

```
It was a fog-laden morning when I stumbled upon a peculiar bottle.

The bottle's antiquity was evident, but it was the unsettling aura.

This was no ordinary tonic.
```

3. Click **"Format for VibeVoice"**
4. Verify output has `Speaker 0:` prefixes

---

## Step 5: Test Audio Generation (Quick Test)

1. Go to **Tab 2: Generate Audio**
2. Paste the formatted text from Step 4
3. Leave voice reference empty (use default voice)
4. Set CFG scale: 1.3
5. Set speed: 0.9
6. Check "Add Ending Snippet"
7. Click **"Generate Podcast"**

**Expected:**
- Generation starts (check logs: `docker logs vibevoice-mystery-narrator`)
- Takes ~15-20 minutes for this short test
- Final MP3 file available for download

**If generation fails:**
- Check GPU memory: `nvidia-smi`
- Check logs: `docker logs -f vibevoice-mystery-narrator`
- Ensure 12GB+ VRAM available

---

## Step 6: Monitor Container

### View Logs
```bash
# Real-time logs
docker logs -f vibevoice-mystery-narrator

# Last 100 lines
docker logs --tail 100 vibevoice-mystery-narrator
```

### Check GPU Usage
```bash
# Inside container
docker exec vibevoice-mystery-narrator nvidia-smi

# Or from host
watch -n 1 nvidia-smi
```

### Check Disk Usage
```bash
# Model cache size
du -sh ./models

# Output files
du -sh ./output
```

---

## Step 7: Verify Volumes

Check that persistent volumes are working:

```bash
# Models should be cached
ls -lh ./models

# Outputs should be saved
ls -lh ./output
```

After first run, subsequent restarts should be fast (no model re-download).

---

## Step 8: Stop Container

```bash
# Stop gracefully
docker-compose down

# Or force stop
docker-compose down -v  # WARNING: Deletes volumes!
```

---

## Troubleshooting

### Build Issues

**Error: "no space left on device"**
```bash
# Clean up Docker cache
docker system prune -a
```

**Error: "failed to solve with frontend dockerfile.v0"**
- Check Dockerfile syntax
- Ensure all COPY paths exist

### Runtime Issues

**Error: "could not select device driver" or "CUDA not available"**
```bash
# Install NVIDIA Container Toolkit
# See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Error: "Model download failed"**
- Check internet connection
- Hugging Face may be rate-limited (wait 15 minutes)
- Try using HF_TOKEN environment variable

**Container crashes on startup**
- Check logs: `docker logs vibevoice-mystery-narrator`
- Verify GPU has 12GB+ VRAM
- Ensure CUDA drivers are up to date

---

## Success Criteria

✅ Docker image builds successfully (9-10GB)
✅ Container starts without errors
✅ Model downloads on first run (5.4GB to `./models`)
✅ Gradio UI accessible at http://localhost:7860
✅ Text formatter works (adds `Speaker 0:` prefixes)
✅ Audio generation completes (even a short test)
✅ Generated MP3 file available in `./output`
✅ Container restarts quickly (model cached)
✅ Volumes persist across restarts

---

## Next Steps After Successful Test

1. **Test with longer story** (5-10 minutes of audio)
2. **Test voice cloning** (upload reference audio)
3. **Optimize Docker image** (reduce layers if needed)
4. **Push image to registry** (GitHub Container Registry)
5. **Deploy to cloud** (Vast.ai, RunPod, etc.)

---

## Clean Up

```bash
# Stop and remove container
docker-compose down

# Remove image
docker rmi vibevoice-app:latest

# Remove volumes (WARNING: Deletes model cache!)
docker volume rm antique_mystery_podcast_models
docker volume rm antique_mystery_podcast_output
```

---

## Performance Benchmarks

**Expected timings** (RTX 4090):

| Task | Time |
|------|------|
| Docker build (first time) | 10-15 min |
| Model download (first run) | 2-5 min |
| Container startup (after model cached) | 30-60 sec |
| Generate 1 min audio | ~6 min |
| Generate 10 min audio | ~60 min |

---

## Contact

If you encounter issues not covered here, check:
- `docker logs vibevoice-mystery-narrator`
- GitHub Issues: antique_mystery_podcast
- VibeVoice community: https://github.com/vibevoice-community/VibeVoice
