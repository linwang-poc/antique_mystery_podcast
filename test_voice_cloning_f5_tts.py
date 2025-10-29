#!/usr/bin/env python3
"""
F5-TTS Voice Cloning Test Script for the Antique Mystery Podcast project.

This script uses F5-TTS, which solves XTTS token limitations by:
- No 400-token hard limit (auto-chunks long text)
- Better coherence for full paragraphs
- Non-autoregressive architecture with Flow Matching

UPDATED: Now uses F5-TTS Python API instead of CLI for better stability
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# Fix PYTHONHASHSEED for F5-TTS subprocess spawning
os.environ.setdefault("PYTHONHASHSEED", "0")

BASE_DIR = Path(__file__).parent.resolve()
REFERENCE_VOICE_DIR = BASE_DIR / "assets" / "reference_voices"
OUTPUT_ROOT = BASE_DIR / "output" / "voice_tests_f5tts"


# Mystery text samples for testing (keep order deterministic for evaluation).
MYSTERY_SAMPLES: Dict[str, str] = {
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
    "03_tense_confrontation": """You're lying... he whispered, his voice barely audible over the
ticking grandfather clock. The curator's smile never wavered. Am I? she replied,
tilting her head slightly. Then explain—slowly—why your fingerprints are on the frame.
The frame that held the stolen Rembrandt. The silence stretched between them
like a taut wire, ready to snap. Finally, he spoke. You don't understand what
you're dealing with.""",
    "04_descriptive_atmosphere": """The Victorian music box sat on the mantelpiece, its silver surface
tarnished with age. Dust motes danced in the shaft of moonlight that pierced
the velvet curtains. Everything in the room was exactly as it had been fifty
years ago, frozen in time. The air itself seemed to hold its breath, waiting.
Waiting for someone to wind the key and release whatever secrets the melody
might reveal.""",
    "05_plot_twist": """But wait! The painting... was a forgery. Detective Morrison had known
it for weeks. Which meant the real artwork was still missing. And if it was
still missing, then the killer—THE killer—was still out there. Still watching.
Still waiting. He turned slowly, scanning the crowd of art collectors. Somewhere
among these faces was a murderer. A murderer who didn't know the truth. Yet.""",
}


# F5-TTS Voice parameters
# Note: F5-TTS has fewer expressive controls than Chatterbox, focusing on faithful reproduction
F5_TTS_PARAMS = {
    "nfe_step": 16,           # 16=fast (2x speed), 32=high quality (Number of Function Evaluations)
    "cfg_strength": 2.0,      # Classifier-Free Guidance strength for text adherence
    "speed": 0.95,            # Slightly slower for suspenseful pacing
    "sway_sampling_coef": -1.0,  # Sway sampling coefficient
}


def check_environment() -> tuple[List[Path], List[Path]]:
    """Ensure the project has the dependencies and assets required to run."""
    print("=" * 60)
    print("F5-TTS VOICE CLONING TEST - Environment Check")
    print("=" * 60)
    print(f"\n✓ Python version: {sys.version.split()[0]}")

    # Check for training audio files
    training_files = sorted(REFERENCE_VOICE_DIR.glob("training_*.mp3"))
    if not training_files:
        print("\n❌ ERROR: No training voice files found in assets/reference_voices/")
        print("   Please ensure training_*.mp3 files are present.")
        return [], []
    print(f"\n✓ Found {len(training_files)} training voice file(s)")
    for tf in training_files:
        print(f"  - {tf.name}")

    # Check if F5-TTS is installed
    try:
        import f5_tts  # noqa: F401
        print("✓ F5-TTS package available")
    except ImportError:
        print("\n❌ ERROR: F5-TTS is not installed.")
        print("   Install it with: pip install f5-tts")
        return [], []

    # Check for ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ ffmpeg available")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\n❌ ERROR: ffmpeg is not installed.")
        print("   Install it with: brew install ffmpeg")
        return [], []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {OUTPUT_ROOT}")

    # Prepare reference audio files (convert to 24kHz mono WAV)
    prepared_refs = prepare_reference_audio(training_files)

    print("\n" + "=" * 60)
    print("Environment check PASSED! Ready to test F5-TTS voice cloning.")
    print("=" * 60 + "\n")
    return training_files, prepared_refs


def prepare_reference_audio(training_files: List[Path]) -> List[Path]:
    """Convert training audio to F5-TTS required format (24kHz mono WAV)."""
    print("\nPreparing reference audio files for F5-TTS...")
    prepared_files = []

    for mp3_file in training_files:
        wav_file = REFERENCE_VOICE_DIR / f"{mp3_file.stem}_f5.wav"

        # Convert to 24kHz mono WAV, clipped to 10 seconds
        if not wav_file.exists():
            print(f"  Converting {mp3_file.name} to F5-TTS format...")
            try:
                subprocess.run([
                    "ffmpeg", "-i", str(mp3_file),
                    "-ac", "1",           # Mono
                    "-ar", "24000",       # 24kHz sample rate
                    "-sample_fmt", "s16", # 16-bit PCM
                    "-t", "10",           # Clip to 10 seconds
                    str(wav_file)
                ], check=True, capture_output=True)
                print(f"    ✓ Created {wav_file.name}")
            except subprocess.CalledProcessError as e:
                print(f"    ❌ Failed to convert {mp3_file.name}: {e}")
                continue
        else:
            print(f"  ✓ Using existing {wav_file.name}")

        prepared_files.append(wav_file)

    return prepared_files


def generate_sample_f5tts(
    tts_engine,
    reference_audio: Path,
    reference_text: str,
    gen_text: str,
    output_path: Path,
    params: Dict[str, float],
) -> bool:
    """Generate audio from text using F5-TTS Python API."""
    print(f"Generating: {output_path.name}")

    try:
        # Use F5-TTS Python API
        print(f"  Using reference audio: {reference_audio.name}")
        print(f"  Reference text: {reference_text[:50]}...")
        print(f"  Generation text length: {len(gen_text)} characters")

        wav, sr, spec = tts_engine.infer(
            ref_file=str(reference_audio),
            ref_text=reference_text,
            gen_text=gen_text,
            file_wave=str(output_path),
            nfe_step=params.get("nfe_step", 32),
            cfg_strength=params.get("cfg_strength", 2.0),
            sway_sampling_coef=params.get("sway_sampling_coef", -1.0),
            speed=params.get("speed", 1.0),
            remove_silence=False,
        )

        if output_path.exists():
            print(f"  ✓ Generated successfully: {output_path}")
            print(f"  Audio duration: {len(wav) / sr:.2f} seconds")
            return True
        else:
            print(f"  ❌ Output file not created")
            return False

    except Exception as error:
        print(f"  ❌ Unexpected error: {error}")
        import traceback
        traceback.print_exc()
        return False


def create_evaluation_template(output_dir: Path, generated_files: Iterable[Path]) -> None:
    """Create an evaluation template alongside the generated samples."""
    eval_file = output_dir / "EVALUATION.md"
    sample_list = list(generated_files)

    with eval_file.open("w", encoding="utf-8") as handle:
        handle.write("# F5-TTS Voice Cloning Test - Evaluation\n\n")
        handle.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Generated Files: {len(sample_list)}\n\n")

        handle.write("## F5-TTS Parameters Used\n\n")
        for param, value in F5_TTS_PARAMS.items():
            handle.write(f"- **{param}**: {value}\n")

        handle.write("\n## F5-TTS Advantages\n\n")
        handle.write("- ✅ No 400-token limit (auto-chunks long text)\n")
        handle.write("- ✅ Better coherence for full paragraphs\n")
        handle.write("- ✅ Non-autoregressive architecture\n")
        handle.write("- ✅ Supports multiple reference audio files\n")

        handle.write("\n## Sample Evaluation\n\n")
        handle.write("Rate each sample from 1-10 (1=Poor, 10=Excellent)\n\n")

        for sample_id in MYSTERY_SAMPLES:
            handle.write(f"### {sample_id.replace('_', ' ').title()}\n\n")
            handle.write("| Criteria | Rating (1-10) | Notes |\n")
            handle.write("|----------|---------------|-------|\n")
            handle.write("| Voice Quality | | |\n")
            handle.write("| Suspense/Drama | | |\n")
            handle.write("| Coherence | | |\n")
            handle.write("| Naturalness | | |\n")
            handle.write("| Pacing | | |\n")
            handle.write("| **Overall** | | **Pass/Fail** |\n\n")

        handle.write("\n## Comparison vs XTTS/Chatterbox\n\n")
        handle.write("**Voice Quality:** [ ] Better [ ] Same [ ] Worse\n\n")
        handle.write("**Coherence (long text):** [ ] Better [ ] Same [ ] Worse\n\n")
        handle.write("**Speed:** [ ] Faster [ ] Same [ ] Slower\n\n")
        handle.write("**Overall Preference:** [ ] F5-TTS [ ] XTTS [ ] Chatterbox\n\n")

        handle.write("## Overall Assessment\n\n")
        handle.write("**Decision:** [ ] PASS - Use F5-TTS for production\n")
        handle.write("            [ ] FAIL - Stick with current TTS\n")
        handle.write("            [ ] CONSIDER - Fine-tune F5-TTS model\n\n")

        handle.write("**Additional Comments:**\n\n")
        handle.write("(Describe strengths and weaknesses compared to other TTS systems)\n\n")

    print(f"✓ Evaluation template created: {eval_file}")


def load_f5tts_engine():
    """Load and initialize the F5-TTS engine using Python API."""
    print("Loading F5-TTS engine (Python API)...")
    try:
        from f5_tts.api import F5TTS

        device = "cpu"  # Use CPU for compatibility
        print(f"✓ Using device: {device}")
        print("  Loading F5TTS_Base model (first load may download ~1GB)...")

        engine = F5TTS(
            model="F5TTS_Base",
            device=device,
        )
        print("✓ F5-TTS engine loaded successfully")
        return engine
    except Exception as error:
        print(f"❌ Error loading F5-TTS: {error}")
        import traceback
        traceback.print_exc()
        return None


def run_voice_test() -> None:
    """Main entry point for the F5-TTS voice cloning test workflow."""
    training_files, prepared_refs = check_environment()
    if not training_files or not prepared_refs:
        sys.exit(1)

    # Load F5-TTS engine
    tts_engine = load_f5tts_engine()
    if not tts_engine:
        print("\n❌ Failed to load F5-TTS engine. Exiting.")
        sys.exit(1)

    # Use only the second training file for simplicity (training_02.mp3)
    if len(prepared_refs) >= 2:
        selected_ref = prepared_refs[1]  # Use second file (index 1)
        print(f"\n✓ Selected reference audio: {prepared_refs[1].name}")
    else:
        selected_ref = prepared_refs[0]  # Fallback to first file if only one exists
        print(f"\n✓ Selected reference audio: {prepared_refs[0].name}")

    # Reference text - transcription of the training audio
    # IMPORTANT: You MUST provide the actual transcription of training_02.mp3 here
    # Empty string may not work reliably for auto-transcription in all F5-TTS versions
    #
    # Example: reference_text = "The actual words spoken in training_02.mp3"
    reference_text = "strange, his light uncertain. Critics dismissed him as eccentric. Patrons ignored him. For years he stopped painting altogether"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_ROOT / f"test_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("GENERATING MYSTERY SAMPLES WITH F5-TTS")
    print("=" * 60)
    print(f"\nUsing reference audio: {selected_ref.name}")
    print()

    generated_files: List[Path] = []
    for sample_id, sample_text in MYSTERY_SAMPLES.items():
        output_path = output_dir / f"{sample_id}.wav"

        # For testing, only generate first sample
        if sample_id != '01_suspenseful_opening':
            continue

        if generate_sample_f5tts(
            tts_engine=tts_engine,
            reference_audio=selected_ref,
            reference_text=reference_text,
            gen_text=sample_text.strip(),
            output_path=output_path,
            params=F5_TTS_PARAMS,
        ):
            generated_files.append(output_path)

    print("\n" + "=" * 60)
    print("F5-TTS TEST COMPLETED!")
    print("=" * 60)
    print(f"\nGenerated {len(generated_files)} test sample(s):")
    for file_path in generated_files:
        print(f"  - {file_path}")

    print("\nF5-TTS Parameters Used:")
    for param, value in F5_TTS_PARAMS.items():
        print(f"  - {param}: {value}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Update the reference_text with actual transcription of training audio")
    print("2. Listen to the generated sample")
    print("3. Compare with XTTS and Chatterbox outputs")
    print("4. Fill out EVALUATION.md with your ratings")
    print("5. Decide if F5-TTS meets your needs or if fine-tuning is required")
    print()

    create_evaluation_template(output_dir, generated_files)


def main() -> None:
    """CLI entry point."""
    print("\n" + "=" * 60)
    print("ANTIQUE MYSTERY PODCAST - F5-TTS VOICE CLONING TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Convert training audio to F5-TTS format (24kHz mono WAV)")
    print("2. Clone voice using F5-TTS (supports multiple reference files)")
    print("3. Generate mystery narration samples WITHOUT token limits")
    print("4. Create an evaluation template for comparison\n")
    print("F5-TTS Advantages:")
    print("  ✅ No 400-token limitation (XTTS has hard limit)")
    print("  ✅ Auto-chunks long text for better coherence")
    print("  ✅ Supports multiple reference audio files")
    print("  ✅ Fine-tunable with 10-15 hours of audio\n")

    try:
        run_voice_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as error:
        print(f"\n❌ ERROR: {error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
