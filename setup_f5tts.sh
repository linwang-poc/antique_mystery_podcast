#!/bin/bash
# Setup script for F5-TTS voice cloning

echo "=========================================="
echo "F5-TTS Setup for Antique Mystery Podcast"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing F5-TTS..."
pip install f5-tts

echo ""
echo "Checking ffmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Homebrew not found. Please install ffmpeg manually:"
        echo "   Visit: https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "✓ ffmpeg is already installed"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the F5-TTS test script:"
echo "   python test_voice_cloning_f5_tts.py"
echo ""
echo "Note: You'll need to update the reference_text in the script"
echo "      with the actual transcription of your training audio."
echo ""
