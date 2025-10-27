#!/bin/bash
# Wrapper script to run F5-TTS test with proper environment variables
# Usage: ./RUN_F5TTS_TEST.sh

export PYTHONHASHSEED=0

source venv/bin/activate
python test_voice_cloning_f5_tts.py "$@"
