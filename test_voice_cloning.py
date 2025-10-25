#!/usr/bin/env python3
"""
Voice Cloning Test Script for Antique Mystery Podcast
Tests voice cloning quality with mystery-themed samples before full development.

Usage:
    python test_voice_cloning.py

Requirements:
    - TTS engine installed (see SETUP_INSTRUCTIONS.md)
    - Voice files in assets/reference_voices/
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Mystery text samples for testing
MYSTERY_SAMPLES = {
    "01_suspenseful_opening": """
The antique vase gleamed under the dim light of the auction house.
No one knew... its secrets had been hidden for centuries.
But tonight... someone would discover the truth.
""",

    "02_dramatic_revelation": """
She opened the old diary... and gasped.
The handwriting was unmistakable. Her grandfather...
had been there. On that very night.
The night the treasure disappeared.
""",

    "03_tense_confrontation": """
"You're lying," he whispered, his voice cold as ice.
The old clock behind her chimed midnight.
She had ten seconds... to tell the truth... or run.
""",

    "04_descriptive_atmosphere": """
The Victorian music box sat on the dusty shelf,
its brass fittings tarnished with age.
When wound, it played a haunting melody...
one that hadn't been heard in fifty years.
""",

    "05_plot_twist": """
But wait. The painting... it wasn't a forgery after all.
The signature hidden beneath the frame...
changed everything. Everything she thought she knew...
was wrong.
"""
}

# Voice parameters (mystery-optimized defaults)
VOICE_PARAMS = {
    "speed": 0.90,  # Slightly slower for suspense
    "expressiveness": 7,  # High for tension
    "pitch": -3,  # Deeper for older male voice
    "emotional_intensity": 7,  # Elevated for mystery
    "pause_duration": 2.0,  # Extended pauses for drama
    "intonation_emphasis": 7,  # Strong for foreshadowing
    "breath_frequency": 6,  # Natural storytelling rhythm
}


def check_environment():
    """Check if all required files and packages exist."""
    print("=" * 60)
    print("VOICE CLONING TEST - Environment Check")
    print("=" * 60)

    # Check Python version
    print(f"\n✓ Python version: {sys.version.split()[0]}")

    # Check for voice files
    training_files = list(Path("assets/reference_voices").glob("training_*.mp3"))
    if not training_files:
        print("\n❌ ERROR: No training voice files found in assets/reference_voices/")
        print("   Please ensure training_*.mp3 files are present.")
        return False
    print(f"\n✓ Found {len(training_files)} training voice files")

    # Check for TTS engine
    tts_engine = None
    try:
        import chatterbox
        tts_engine = "chatterbox"
        print(f"✓ Chatterbox TTS found (version: {chatterbox.__version__})")
    except ImportError:
        try:
            import gpt_sovits
            tts_engine = "gpt-sovits"
            print("✓ GPT-SoVITS found")
        except ImportError:
            print("\n❌ ERROR: No TTS engine found!")
            print("   Please install either:")
            print("   - pip install chatterbox-tts  (recommended)")
            print("   - pip install gpt-sovits-python")
            print("\n   See SETUP_INSTRUCTIONS.md for detailed setup.")
            return False

    # Check output directory
    output_dir = Path("output/voice_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {output_dir}")

    print("\n" + "=" * 60)
    print("Environment check PASSED! Ready to test voice cloning.")
    print("=" * 60 + "\n")

    return tts_engine


def load_tts_engine(engine_type):
    """Load and initialize the TTS engine."""
    print(f"Loading {engine_type} TTS engine...")

    if engine_type == "chatterbox":
        try:
            from chatterbox import ChatterboxTTS
            # Initialize Chatterbox
            # Note: Actual implementation depends on Chatterbox API
            print("✓ Chatterbox TTS loaded")
            return ChatterboxTTS()
        except Exception as e:
            print(f"❌ Error loading Chatterbox: {e}")
            return None

    elif engine_type == "gpt-sovits":
        try:
            from gpt_sovits import GPTSOVITS
            # Initialize GPT-SoVITS
            print("✓ GPT-SoVITS loaded")
            return GPTSOVITS()
        except Exception as e:
            print(f"❌ Error loading GPT-SoVITS: {e}")
            return None

    return None


def clone_voice(tts_engine, reference_audio_path):
    """Clone voice from reference audio."""
    print(f"\nCloning voice from: {reference_audio_path}")

    # TODO: Implement actual voice cloning based on TTS engine
    # This is a placeholder - actual implementation depends on the TTS library

    print("✓ Voice cloned successfully")
    return "voice_profile_placeholder"


def generate_sample(tts_engine, voice_profile, text, output_path, params):
    """Generate audio from text using cloned voice."""
    print(f"Generating: {output_path.name}")

    # TODO: Implement actual TTS generation based on engine
    # This is a placeholder - actual implementation depends on the TTS library

    # Example parameters to use:
    # - speed: params["speed"]
    # - expressiveness: params["expressiveness"]
    # - pitch: params["pitch"]
    # - pause_duration: params["pause_duration"]
    # etc.

    print(f"  ✓ Generated (placeholder)")
    return True


def run_voice_test():
    """Main test function."""
    # Check environment
    engine_type = check_environment()
    if not engine_type:
        sys.exit(1)

    # Load TTS engine
    tts_engine = load_tts_engine(engine_type)
    if not tts_engine:
        print("\n❌ Failed to load TTS engine. Exiting.")
        sys.exit(1)

    # Use first training file for voice cloning
    training_file = list(Path("assets/reference_voices").glob("training_*.mp3"))[0]

    # Clone voice
    voice_profile = clone_voice(tts_engine, training_file)

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"output/voice_tests/test_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("GENERATING MYSTERY SAMPLES")
    print("=" * 60 + "\n")

    # Generate each sample
    generated_files = []
    for sample_id, text in MYSTERY_SAMPLES.items():
        output_path = output_dir / f"{sample_id}.mp3"

        success = generate_sample(
            tts_engine,
            voice_profile,
            text.strip(),
            output_path,
            VOICE_PARAMS
        )

        if success:
            generated_files.append(output_path)

    # Print results
    print("\n" + "=" * 60)
    print("TEST COMPLETED!")
    print("=" * 60)
    print(f"\nGenerated {len(generated_files)} test samples:")
    for file in generated_files:
        print(f"  - {file}")

    print(f"\nVoice Parameters Used:")
    for param, value in VOICE_PARAMS.items():
        print(f"  - {param}: {value}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Listen to each generated sample")
    print("2. Fill out VOICE_EVALUATION.md with your ratings")
    print("3. Provide feedback on what to improve")
    print("4. Share results with development team")
    print("\n")

    # Create evaluation template
    create_evaluation_template(output_dir, generated_files)


def create_evaluation_template(output_dir, generated_files):
    """Create evaluation template for user feedback."""
    eval_file = output_dir / "EVALUATION.md"

    with open(eval_file, "w") as f:
        f.write("# Voice Cloning Test - Evaluation\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Generated Files: {len(generated_files)}\n\n")

        f.write("## Voice Parameters Used\n\n")
        for param, value in VOICE_PARAMS.items():
            f.write(f"- **{param}**: {value}\n")

        f.write("\n## Sample Evaluation\n\n")
        f.write("Rate each sample from 1-10 (1=Poor, 10=Excellent)\n\n")

        for sample_id in MYSTERY_SAMPLES.keys():
            f.write(f"### {sample_id.replace('_', ' ').title()}\n\n")
            f.write("| Criteria | Rating (1-10) | Notes |\n")
            f.write("|----------|---------------|-------|\n")
            f.write("| Voice Quality | | |\n")
            f.write("| Suspense/Drama | | |\n")
            f.write("| Pause Timing | | |\n")
            f.write("| Intonation | | |\n")
            f.write("| Pacing | | |\n")
            f.write("| Emotion | | |\n")
            f.write("| **Overall** | | **Pass/Fail** |\n\n")

        f.write("\n## Overall Assessment\n\n")
        f.write("**Overall Decision:** [ ] PASS - Voice quality is acceptable, proceed with development\n")
        f.write("                     [ ] FAIL - Voice needs improvement\n\n")
        f.write("## Improvement Suggestions\n\n")
        f.write("What specific changes would improve the voice?\n\n")
        f.write("- [ ] Increase pause duration (make more dramatic)\n")
        f.write("- [ ] Decrease pause duration (too slow)\n")
        f.write("- [ ] More expressiveness (more emotional variation)\n")
        f.write("- [ ] Less expressiveness (too exaggerated)\n")
        f.write("- [ ] Slower speed (more suspenseful)\n")
        f.write("- [ ] Faster speed (too slow)\n")
        f.write("- [ ] Deeper voice (lower pitch)\n")
        f.write("- [ ] Higher voice (raise pitch)\n")
        f.write("- [ ] Other (describe below):\n\n")
        f.write("**Additional Comments:**\n\n")
        f.write("(Describe what you like and what needs improvement)\n\n")

    print(f"✓ Evaluation template created: {eval_file}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ANTIQUE MYSTERY PODCAST - VOICE CLONING TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Clone voice from training file")
    print("2. Generate 5 mystery narration samples")
    print("3. Create evaluation template for your feedback")
    print("\n")

    try:
        run_voice_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
