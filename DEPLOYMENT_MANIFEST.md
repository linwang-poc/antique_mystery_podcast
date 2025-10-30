# VibeVoice Mystery Narrator - Deployment Manifest

**Purpose**: Complete file transfer guide for deploying the VibeVoice Mystery Narrator Docker container to a local server with GPU support.

**Complement to**: `DOCKER_BUILD_TEST.md` (testing guide) - this document focuses on **what to transfer and how to set up**.

---

## Pre-Deployment Server Requirements

Before transferring files, ensure the target server has:

- [ ] **Operating System**: Linux (Ubuntu 22.04+ recommended) or macOS with Apple Silicon
- [ ] **Docker Desktop**: Version 20.10+ installed and running
- [ ] **NVIDIA GPU**: 12GB+ VRAM (RTX 3090, RTX 4090, A5000, or better)
- [ ] **NVIDIA Container Toolkit**: Installed ([setup guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- [ ] **CUDA Drivers**: Version 12.1 or higher
- [ ] **Disk Space**: 30GB+ free (10GB image + 5GB models + 10GB working space)
- [ ] **Network**: Stable connection for Hugging Face model download (~5.4GB on first run)
- [ ] **Git**: Installed (for method A deployment)

**Verify GPU support before deployment:**
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```
You should see your GPU listed. If this fails, Docker GPU support is not configured.

---

## Deployment Method Decision

Choose ONE method:

### Method A: Git Clone (RECOMMENDED)
**Best for**: Servers with git access, cleanest approach, easy updates

**Pros**:
- Single command deployment
- Easy to pull updates
- Preserves git history
- No manual file tracking needed

**Cons**:
- Requires git on server
- Downloads entire repository (~50MB)

### Method B: Manual File Transfer
**Best for**: Air-gapped servers, restricted environments

**Pros**:
- No git required
- Can cherry-pick specific files
- Minimal transfer size possible

**Cons**:
- More error-prone
- Must manually track changes
- Harder to update

---

## METHOD A: Git Clone Deployment (Recommended)

### Step 1: Clone Repository on Target Server

```bash
# Navigate to deployment directory
cd /path/to/deployment/location

# Clone the repository
git clone https://github.com/yourusername/antique_mystery_podcast.git
cd antique_mystery_podcast

# Checkout the Docker deployment branch (if applicable)
git checkout main  # or specific branch/tag
```

### Step 2: Create Required Directories

```bash
# Create volume mount directories
mkdir -p models output

# Verify structure
ls -la
```

You should see:
```
Dockerfile
docker-compose.yml
.dockerignore
requirements_vibevoice.txt
src/
assets/
config/
models/     (empty, will populate on first run)
output/     (empty, will store generated audio)
```

### Step 3: Handle Untracked Files (if applicable)

**IMPORTANT**: The file `assets/reference_voices/EdisonsGhostPhone.mp3` is NOT tracked in git.

**Options**:
- **Option 1**: Skip it (use other reference voices)
- **Option 2**: Transfer manually via scp/rsync (see Manual Transfer section)
- **Option 3**: Add it to git before cloning (commit it in the source repo)

### Step 4: Proceed to Build

Skip to **"Building and Running"** section below.

---

## METHOD B: Manual File Transfer

### File Transfer Checklist

Transfer these files from source to target server:

#### Docker Configuration Files (4 files, ~5KB total)
```bash
# Transfer Docker configs
scp Dockerfile user@server:/deployment/path/
scp docker-compose.yml user@server:/deployment/path/
scp .dockerignore user@server:/deployment/path/
scp requirements_vibevoice.txt user@server:/deployment/path/
```

#### Application Source Code (~200KB)
```bash
# Transfer entire src/ directory
scp -r src/ user@server:/deployment/path/src/
```

**Critical files in src/**:
- `src/main_vibevoice.py` (entry point, 16KB)
- `src/vibevoice/generator.py` (core logic)
- `src/vibevoice/__init__.py`
- `src/ui/transcriber.py` (text formatter)
- `src/ui/__init__.py`
- `src/audio/concatenator.py` (audio processing)
- `src/audio/__init__.py`
- `src/document/parser.py` (document parsing)
- `src/document/__init__.py`

#### Configuration Files (~5KB)
```bash
# Transfer config directory
scp -r config/ user@server:/deployment/path/config/
```

**Critical file**:
- `config/config.yaml` (main application config)

**Optional** (voice profiles for legacy multi-engine TTS, not used in VibeVoice Docker):
- `config/voice_profiles/*.json`

#### Assets (~200KB + reference voices)
```bash
# Transfer assets directory
scp -r assets/ user@server:/deployment/path/assets/
```

**Critical files**:
- `assets/ending.mp3` (156KB, podcast ending snippet)
- `assets/reference_voices/*.mp3` (reference voice samples)
- `assets/reference_voices/*.wav` (F5-TTS reference voices)

**Reference voices inventory**:
- ✅ `testing_1.mp3` (tracked)
- ✅ `testing_02.mp3` (tracked)
- ✅ `testing_03.mp3` (tracked)
- ✅ `testing_04.mp3` (tracked)
- ✅ `training_01.mp3` (tracked)
- ✅ `training_02.mp3` (tracked)
- ✅ `training_01_f5.wav` (tracked)
- ✅ `training_02_f5.wav` (tracked)
- ⚠️ `EdisonsGhostPhone.mp3` (NOT tracked in git, manual transfer if needed)

#### Documentation (Optional, ~100KB)
```bash
# Transfer documentation (optional but recommended)
scp README.md user@server:/deployment/path/
scp DOCKER_BUILD_TEST.md user@server:/deployment/path/
scp DEPLOYMENT_MANIFEST.md user@server:/deployment/path/
scp CLAUDE.md user@server:/deployment/path/
```

### Create Required Directories on Server

```bash
# SSH into server
ssh user@server

# Navigate to deployment path
cd /deployment/path

# Create volume mount directories
mkdir -p models output

# Verify directory structure
ls -la
```

Expected structure:
```
/deployment/path/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements_vibevoice.txt
├── src/
│   ├── main_vibevoice.py
│   ├── vibevoice/
│   ├── ui/
│   ├── audio/
│   └── document/
├── assets/
│   ├── ending.mp3
│   └── reference_voices/
├── config/
│   └── config.yaml
├── models/         (empty)
└── output/         (empty)
```

---

## Building and Running

### Step 1: Build the Docker Image

```bash
# Navigate to deployment directory
cd /deployment/path

# Build the image (10-15 minutes on first build)
docker build -t vibevoice-app:latest .
```

**Expected output**:
```
[+] Building 842.3s (12/12) FINISHED
=> [1/7] FROM nvcr.io/nvidia/pytorch:24.12-py3
=> [2/7] WORKDIR /app
=> [3/7] RUN apt-get update && apt-get install -y ffmpeg...
=> [4/7] COPY requirements_vibevoice.txt /tmp/
=> [5/7] RUN pip install -r /tmp/requirements_vibevoice.txt...
=> [6/7] COPY src/ /app/src/
=> [7/7] COPY config/ /app/config/
=> exporting to image
=> => naming to docker.io/library/vibevoice-app:latest
```

**Build success criteria**:
- ✅ No error messages
- ✅ Image size ~9-10GB
- ✅ All layers cached for future builds

**If build fails**, check:
- Docker has 20GB+ free disk space
- Network connection stable (large downloads)
- All COPY paths exist (src/, config/, assets/)

### Step 2: Start the Container

```bash
# Start with docker-compose (recommended)
docker-compose up

# Or run in detached mode
docker-compose up -d
```

**Expected output (first run)**:
```
vibevoice-mystery-narrator | Initializing VibeVoice on cuda...
vibevoice-mystery-narrator | Loading VibeVoice processor from microsoft/VibeVoice-1.5B...
vibevoice-mystery-narrator | Downloading model weights (5.4GB)... [2-5 minutes]
vibevoice-mystery-narrator | ✓ Processor loaded
vibevoice-mystery-narrator | Loading VibeVoice-1.5B model...
vibevoice-mystery-narrator | ✓ Model loaded on cuda
vibevoice-mystery-narrator | ✓ Inference steps: 15
vibevoice-mystery-narrator | ✓ VibeVoice ready for generation!
vibevoice-mystery-narrator | Running on local URL:  http://0.0.0.0:7860
```

**First run timeline**:
- Model download: 2-5 minutes (depends on network)
- Model initialization: 1-2 minutes
- Total startup: 3-7 minutes

**Subsequent restarts**: 30-60 seconds (model cached in `./models`)

### Step 3: Verify Deployment

#### Access the UI
```bash
# Open browser
http://localhost:7860
```

**Expected**: Gradio UI with 3 tabs:
1. Format Text
2. Generate Audio
3. Help

#### Check Logs
```bash
# Real-time logs
docker logs -f vibevoice-mystery-narrator

# Last 100 lines
docker logs --tail 100 vibevoice-mystery-narrator
```

#### Check GPU Usage
```bash
# Inside container
docker exec vibevoice-mystery-narrator nvidia-smi

# From host
watch -n 1 nvidia-smi
```

#### Verify Volumes
```bash
# Models should be cached (5.4GB)
du -sh ./models
# Expected: 5.4GB after first run

# Assets mounted correctly
ls -lh ./assets/ending.mp3
# Expected: 156KB file

# Output directory writable
touch ./output/test.txt && rm ./output/test.txt
# Expected: No errors
```

---

## Post-Deployment Testing

Follow the comprehensive testing guide in **DOCKER_BUILD_TEST.md** starting from **Step 4: Test Text Formatting**.

### Quick Smoke Test

1. **Format text** (Tab 1):
   ```
   It was a dark and stormy night.

   The old mansion loomed before me.
   ```
   Click "Format for VibeVoice" → Should add `Speaker 0:` prefixes

2. **Generate short audio** (Tab 2):
   - Paste formatted text
   - Leave reference voice empty (default)
   - CFG scale: 1.3
   - Speed: 0.9
   - Check "Add Ending Snippet"
   - Click "Generate Podcast"
   - Expected: ~3-5 minutes for short test

3. **Verify output**:
   ```bash
   ls -lh ./output/*.mp3
   ```
   Should see generated MP3 file

---

## Deployment Verification Checklist

Use this checklist to confirm successful deployment:

- [ ] Docker image built successfully (9-10GB)
- [ ] Container starts without errors
- [ ] GPU detected (check `nvidia-smi` inside container)
- [ ] Model downloads on first run (5.4GB to `./models`)
- [ ] Gradio UI accessible at http://localhost:7860
- [ ] All 3 tabs visible (Format Text, Generate Audio, Help)
- [ ] Text formatter works (adds `Speaker 0:` prefixes)
- [ ] Reference voice upload works (accepts MP3/WAV files)
- [ ] Audio generation starts (check logs for progress)
- [ ] Generated MP3 file appears in `./output`
- [ ] Container restarts quickly on subsequent runs (<60s)
- [ ] Volumes persist across restarts
- [ ] Health check passes: `docker ps` shows "healthy" status

---

## File Size Reference

**Total transfer size** (Method B):
- Docker configs: ~5KB
- Source code (src/): ~200KB
- Assets: ~200KB + reference voices (~5-10MB)
- Config: ~5KB
- Documentation: ~100KB (optional)
- **Total**: ~6-11MB (excluding documentation and untracked files)

**Docker image size**: 9-10GB (after build)

**Model cache size**: 5.4GB (downloaded on first run)

**Disk space recommendation**: 30GB+ free space

---

## Common Deployment Issues

### Build Failures

**"no space left on device"**
```bash
# Clean up Docker cache
docker system prune -a
df -h  # Check available space
```

**"failed to solve with frontend dockerfile.v0"**
- Check Dockerfile syntax
- Verify all COPY paths exist before build
- Ensure requirements_vibevoice.txt is present

**"unable to find image nvcr.io/nvidia/pytorch:24.12-py3"**
- Check network connection to NVIDIA registry
- Try pulling base image manually: `docker pull nvcr.io/nvidia/pytorch:24.12-py3`

### Runtime Failures

**"could not select device driver" or "CUDA not available"**
```bash
# Test GPU access first
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Install NVIDIA Container Toolkit if not present
# See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

**"Model download failed" or "Connection timeout"**
- Check internet connection
- Hugging Face may be rate-limited (wait 15 minutes)
- Try setting HF_TOKEN environment variable if rate-limited
- Check firewall rules for outbound HTTPS

**"Container exits immediately"**
```bash
# Check logs for error details
docker logs vibevoice-mystery-narrator

# Common causes:
# - GPU memory insufficient (need 12GB+)
# - CUDA driver mismatch
# - Missing required files (check COPY paths)
```

### Volume Issues

**"Permission denied" when writing to volumes**
```bash
# Fix permissions on host
chmod 777 ./models ./output
# Or use proper user mapping in docker-compose.yml
```

**"Model re-downloads on every restart"**
- Volume mount not configured correctly
- Check `docker-compose.yml` has: `- ./models:/models`
- Verify `HF_HOME=/models` environment variable is set

---

## Updating the Deployment

### Method A (Git Clone)
```bash
cd /deployment/path
git pull origin main
docker-compose down
docker build -t vibevoice-app:latest .
docker-compose up -d
```

### Method B (Manual Transfer)
```bash
# Transfer updated files via scp
scp -r src/ user@server:/deployment/path/src/

# Rebuild and restart
ssh user@server
cd /deployment/path
docker-compose down
docker build -t vibevoice-app:latest .
docker-compose up -d
```

---

## Clean Up (if needed)

```bash
# Stop and remove container
docker-compose down

# Remove image
docker rmi vibevoice-app:latest

# Remove volumes (WARNING: Deletes model cache!)
docker volume rm antique_mystery_podcast_models
docker volume rm antique_mystery_podcast_output

# Remove all deployment files
cd /deployment/path/..
rm -rf /deployment/path
```

---

## Security Considerations

- **Port Exposure**: Gradio UI on port 7860 is exposed to localhost only by default
- **Network Access**: Container needs outbound HTTPS for model download (only on first run)
- **File Permissions**: Volume mounts use host user permissions
- **GPU Access**: Container has full GPU access via NVIDIA runtime
- **No Authentication**: Gradio UI has no built-in authentication (add reverse proxy if needed)

---

## Next Steps After Deployment

1. **Test with full story**: See `DOCKER_BUILD_TEST.md` Step 5-6
2. **Test voice cloning**: Upload custom reference audio
3. **Optimize performance**: Tune CFG scale, speed, inference steps
4. **Monitor resources**: Track GPU memory, disk usage during generation
5. **Production hardening**: Add authentication, logging, monitoring
6. **Cloud deployment**: See `docs/CLOUD_GPU_VIBEVOICE_SETUP.md` for Vast.ai/RunPod

---

## Support and Troubleshooting

**Documentation References**:
- `DOCKER_BUILD_TEST.md` - Comprehensive testing guide
- `README.md` - Project architecture and overview
- `CLAUDE.md` - Development instructions and patterns
- `docs/CLOUD_GPU_VIBEVOICE_SETUP.md` - Cloud GPU deployment

**Logs Location**:
- Container logs: `docker logs vibevoice-mystery-narrator`
- Application logs: Not currently implemented (logs to stdout only)

**Common Commands**:
```bash
# View running containers
docker ps

# Stop container
docker-compose down

# Restart container
docker-compose restart

# View GPU usage
docker exec vibevoice-mystery-narrator nvidia-smi

# Interactive shell
docker exec -it vibevoice-mystery-narrator /bin/bash
```

---

## Deployment Summary

**Fastest deployment** (if git available):
```bash
git clone https://github.com/yourusername/antique_mystery_podcast.git
cd antique_mystery_podcast
mkdir -p models output
docker build -t vibevoice-app:latest .
docker-compose up
```

**Expected timeline**:
- Clone repo: 30 seconds
- Build image: 10-15 minutes
- First startup (model download): 3-7 minutes
- **Total**: ~20 minutes to fully operational

**Success indicator**: Browser shows Gradio UI at http://localhost:7860 with "VibeVoice Mystery Narrator" title.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Tested On**: Ubuntu 22.04, Docker 24.0, NVIDIA RTX 4090
