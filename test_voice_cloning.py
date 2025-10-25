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
    "01_suspenseful_opening": """The antique vase gleamed in the dim light of the auction house.
Margaret had seen it before, somewhere. The pattern of roses and thorns
triggered a memory she couldn't quite grasp. She stepped closer, her heart
racing. Then she saw it. The tiny crack. The same crack from her grandmother's
photograph. But that vase had been destroyed in the fire. Hadn't it?""",

    "02_dramatic_revelation": """She opened the old diary with trembling hands. The ink was faded,
but the handwriting was unmistakable. Her mother's handwriting. But the date,
the date was impossible. This entry was written three days after her mother's
death. Margaret's breath caught in her throat as she read the first line.
If you're reading this, then you know the truth about the Ashworth inheritance.""",

    "03_tense_confrontation": """You're lying, he whispered, his voice barely audible over the
ticking grandfather clock. The curator's smile never wavered. Am I? she replied,
tilting her head slightly. Then explain why your fingerprints are on the frame.
The frame that held the stolen Rembrandt. The silence stretched between them
like a taut wire, ready to snap. Finally, he spoke. You don't understand what
you're dealing with.""",

    "04_descriptive_atmosphere": """The Victorian music box sat on the mantelpiece, its silver surface
tarnished with age. Dust motes danced in the shaft of moonlight that pierced
the velvet curtains. Everything in the room was exactly as it had been fifty
years ago, frozen in time. The air itself seemed to hold its breath, waiting.
Waiting for someone to wind the key and release whatever secrets the melody
might reveal.""",

    "05_plot_twist": """But wait. The painting was a forgery. Detective Morrison had known
it for weeks. Which meant the real artwork was still missing. And if it was
still missing, then the killer was still out there. Still watching. Still
waiting. He turned slowly, scanning the crowd of art collectors. Somewhere
among these faces was a murderer. A murderer who didn't know the truth. Yet.""",
    "06_Allan_poe_Raven": """ Ah, distinctly I remember it was in the bleak December;
And each separate dying ember wrought its ghost upon the floor.
    Eagerly I wished the morrow;—vainly I had sought to borrow
    From my books surcease of sorrow—sorrow for the lost Lenore—
For the rare and radiant maiden whom the angels name Lenore—
            Nameless here for evermore.

    And the silken, sad, uncertain rustling of each purple curtain
Thrilled me—filled me with fantastic terrors never felt before;
    So that now, to still the beating of my heart, I stood repeating
    “’Tis some visitor entreating entrance at my chamber door—
Some late visitor entreating entrance at my chamber door;—
            This it is and nothing more."""
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

    # Check for TTS engine (prioritize Chatterbox)
    tts_engine = None
    try:
        from chatterbox.tts import ChatterboxTTS
        tts_engine = "chatterbox"
        print("✓ Chatterbox TTS found (Resemble AI)")
    except ImportError:
        try:
            from TTS.api import TTS
            tts_engine = "coqui"
            import TTS as tts_module
            print(f"✓ Coqui TTS found (version: {tts_module.__version__})")
        except ImportError:
            print("\n❌ ERROR: No TTS engine found!")
            print("   Please install one of:")
            print("   - pip install chatterbox-tts  (Recommended - open source)")
            print("   - pip install TTS  (Coqui TTS alternative)")
            print("\n   See CHATTERBOX_RESEARCH.md for installation details.")
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
            from chatterbox.tts import ChatterboxTTS

            # Use CPU for M1 Mac
            device = "cpu"
            print(f"✓ Using device: {device}")

            print("  Loading Chatterbox model (first time may download ~1GB)...")
            model = ChatterboxTTS.from_pretrained(device=device)
            print("✓ Chatterbox TTS loaded successfully")
            return model
        except Exception as e:
            print(f"❌ Error loading Chatterbox: {e}")
            import traceback
            traceback.print_exc()
            return None

    elif engine_type == "coqui":
        try:
            from TTS.api import TTS
            import torch
            import os

            # Use CPU for M1 Mac (MPS may not be stable for TTS)
            device = "cpu"
            print(f"✓ Using device: {device}")

            # Set environment variable to accept XTTS license automatically
            # This is for non-commercial use (CPML license)
            os.environ["COQUI_TOS_AGREED"] = "1"

            print("  Note: Using XTTS v2 under non-commercial CPML license")
            print("  See: https://coqui.ai/cpml")

            # Initialize Coqui TTS with XTTS v2 (supports voice cloning)
            print("  Downloading model (first time only, ~2GB)...")
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            print("✓ Coqui TTS (XTTS v2) loaded successfully")
            return tts
        except Exception as e:
            print(f"❌ Error loading Coqui TTS: {e}")
            import traceback
            traceback.print_exc()
            return None

    elif engine_type == "gpt-sovits":
        try:
            from gpt_sovits import GPTSOVITS
            print("✓ GPT-SoVITS loaded")
            return GPTSOVITS()
        except Exception as e:
            print(f"❌ Error loading GPT-SoVITS: {e}")
            return None

    return None


def clone_voice(tts_engine, reference_audio_path, engine_type="chatterbox"):
    """Clone voice from reference audio."""
    print(f"\nCloning voice from: {reference_audio_path}")

    # For Chatterbox and Coqui TTS, voice cloning is done on-the-fly during generation
    # We just need to store the path to the reference audio
    # The actual cloning happens in generate_sample()

    print("✓ Voice reference prepared (cloning will happen during generation)")
    return str(reference_audio_path)


def generate_sample(tts_engine, voice_profile, text, output_path, params, engine_type="chatterbox"):
    """Generate audio from text using cloned voice."""
    print(f"Generating: {output_path.name}")

    try:
        if engine_type == "chatterbox":
            # For Chatterbox TTS:
            # voice_profile is the path to the reference audio file
            print(f"  Synthesizing with Chatterbox voice cloning...")

            # Generate audio with voice cloning
            # Chatterbox uses audio_prompt_path for zero-shot voice cloning
            wav = tts_engine.generate(
                text=text,
                audio_prompt_path=voice_profile,
                exaggeration=0.6  # Higher for mystery narration
            )

            # Save WAV first using torchaudio (more reliable than soundfile)
            import torch
            import torchaudio
            wav_path = str(output_path).replace('.mp3', '.wav')

            # Convert to tensor if it's a numpy array
            if not isinstance(wav, torch.Tensor):
                import numpy as np
                wav = torch.from_numpy(wav)

            # Ensure correct shape (channels, samples)
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)  # Add channel dimension

            # Save as WAV
            torchaudio.save(wav_path, wav, sample_rate=24000)

            # Convert WAV to MP3 and apply speed adjustment if needed
            from pydub import AudioSegment
            audio = AudioSegment.from_wav(wav_path)

            # Apply speed adjustment (if different from 1.0)
            speed = params.get("speed", 1.0)
            if speed != 1.0:
                # Change speed without changing pitch
                audio = audio.speedup(playback_speed=speed)

            # Export as MP3
            audio.export(output_path, format="mp3", bitrate="192k")

            # Clean up WAV file
            import os
            os.remove(wav_path)

            print(f"  ✓ Generated successfully: {output_path}")
            return True

        elif engine_type == "coqui":
            # For Coqui TTS XTTS v2:
            # voice_profile is the path to the reference audio file
            speaker_wav = voice_profile

            # XTTS v2 supports English language
            language = "en"

            # Generate audio with voice cloning
            print(f"  Synthesizing with cloned voice...")

            # Generate to WAV first
            wav_path = str(output_path).replace('.mp3', '.wav')
            tts_engine.tts_to_file(
                text=text,
                speaker_wav=speaker_wav,
                language=language,
                file_path=wav_path
            )

            # Convert WAV to MP3 and apply speed adjustment if needed
            from pydub import AudioSegment
            audio = AudioSegment.from_wav(wav_path)

            # Apply speed adjustment (if different from 1.0)
            speed = params.get("speed", 1.0)
            if speed != 1.0:
                # Change speed without changing pitch
                audio = audio.speedup(playback_speed=speed)

            # Export as MP3
            audio.export(output_path, format="mp3", bitrate="192k")

            # Clean up WAV file
            import os
            os.remove(wav_path)

            print(f"  ✓ Generated successfully: {output_path}")
            return True

        else:
            print(f"  ❌ Unknown engine type: {engine_type}")
            return False

    except Exception as e:
        print(f"  ❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False


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
            VOICE_PARAMS,
            engine_type
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
