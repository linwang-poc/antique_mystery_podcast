# Dockerfile for VibeVoice Mystery Narrator Production Deployment
# Base: NVIDIA PyTorch with CUDA support for GPU acceleration

FROM nvcr.io/nvidia/pytorch:24.12-py3

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    HF_HOME=/models \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements_vibevoice.txt /tmp/requirements_vibevoice.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements_vibevoice.txt && \
    pip install --no-cache-dir \
        git+https://github.com/vibevoice-community/VibeVoice.git \
        soundfile>=0.12.1 \
        librosa>=0.10.0 \
        pydub>=0.25.1 && \
    rm /tmp/requirements_vibevoice.txt

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/

# Copy assets (reference voices, ending snippet)
COPY assets/ /app/assets/

# Create directories for mounted volumes
RUN mkdir -p /models /app/output

# Expose Gradio port
EXPOSE 7860

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run the application
CMD ["python", "/app/src/main_vibevoice.py"]
