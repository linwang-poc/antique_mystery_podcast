#!/usr/bin/env python3
"""Voice Cloning Test Script for the Antique Mystery Podcast project."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


BASE_DIR = Path(__file__).parent.resolve()
REFERENCE_VOICE_DIR = BASE_DIR / "assets" / "reference_voices"
OUTPUT_ROOT = BASE_DIR / "output" / "voice_tests"


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
}


# Voice parameters (mystery-optimized defaults).
VOICE_PARAMS = {
    "speed": 0.90,  # Slightly slower for suspense
    "expressiveness": 7,  # High for tension
    "pitch": -3,  # Deeper for older male voice
    "emotional_intensity": 7,  # Elevated for mystery
    "pause_duration": 2.0,  # Extended pauses for drama
    "intonation_emphasis": 7,  # Strong for foreshadowing
    "breath_frequency": 6,  # Natural storytelling rhythm
}


def check_environment() -> List[Path]:
    """Ensure the project has the dependencies and assets required to run."""
    print("=" * 60)
    print("VOICE CLONING TEST - Environment Check")
    print("=" * 60)
    print(f"\n✓ Python version: {sys.version.split()[0]}")

    training_files = sorted(REFERENCE_VOICE_DIR.glob("training_*.mp3"))
    if not training_files:
        print("\n❌ ERROR: No training voice files found in assets/reference_voices/")
        print("   Please ensure training_*.mp3 files are present.")
        return []
    print(f"\n✓ Found {len(training_files)} training voice file(s)")

    try:
        from chatterbox.tts import ChatterboxTTS  # noqa: F401

        print("✓ Chatterbox TTS available (Resemble AI)")
    except ImportError:
        print("\n❌ ERROR: Chatterbox TTS is not installed.")
        print("   Install it with `pip install chatterbox-tts`.")
        return []

    for dependency, import_path in (
        ("torchaudio", "torchaudio"),
        ("pydub", "pydub"),
    ):
        try:
            __import__(import_path)
            print(f"✓ Dependency available: {dependency}")
        except ImportError:
            print(f"\n❌ ERROR: Missing required dependency '{dependency}'")
            print("   Install requirements with `pip install -r requirements.txt`.")
            return []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {OUTPUT_ROOT}")

    print("\n" + "=" * 60)
    print("Environment check PASSED! Ready to test voice cloning.")
    print("=" * 60 + "\n")
    return training_files


def load_tts_engine():
    """Load and initialize the Chatterbox TTS engine."""
    print("Loading Chatterbox TTS engine...")
    try:
        from chatterbox.tts import ChatterboxTTS

        device = "cpu"
        print(f"✓ Using device: {device}")
        print("  Loading Chatterbox model (first load may download ~1GB)...")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✓ Chatterbox TTS loaded successfully")
        return model
    except Exception as error:  # noqa: BLE001 - show detailed traceback
        print(f"❌ Error loading Chatterbox: {error}")
        import traceback

        traceback.print_exc()
        return None


def _prepare_wav_tensor(raw_audio, tts_engine) -> Tuple["torch.Tensor", int]:
    """Coerce engine output to a torch tensor and determine the sample rate."""
    import torch

    sample_rate = getattr(tts_engine, "sample_rate", getattr(tts_engine, "sr", 24000))
    wav = raw_audio

    if isinstance(raw_audio, tuple) and len(raw_audio) == 2:
        wav, sample_rate = raw_audio

    if not isinstance(wav, torch.Tensor):
        wav = torch.tensor(wav, dtype=torch.float32)

    wav = wav.detach().cpu()
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)

    return wav, int(sample_rate)


def _export_mp3(wav_path: Path, mp3_path: Path, speed: float) -> None:
    """Convert the intermediate WAV file to MP3 and apply speed adjustments."""
    from pydub import AudioSegment

    audio = AudioSegment.from_wav(wav_path)
    if abs(speed - 1.0) > 1e-3:
        audio = audio.speedup(playback_speed=speed)
    audio.export(mp3_path, format="mp3", bitrate="192k")
    wav_path.unlink(missing_ok=True)


def generate_sample(
    tts_engine,
    reference_audio: Path,
    text: str,
    output_path: Path,
    params: Dict[str, float],
) -> bool:
    """Generate audio from text using the Chatterbox engine."""
    print(f"Generating: {output_path.name}")
    wav_path = output_path.with_suffix(".wav")

    try:
        raw_audio = tts_engine.generate(
            text=text,
            audio_prompt_path=str(reference_audio),
            exaggeration=0.6,
        )
        wav_tensor, sample_rate = _prepare_wav_tensor(raw_audio, tts_engine)

        import torchaudio

        torchaudio.save(str(wav_path), wav_tensor, sample_rate)
        _export_mp3(wav_path, output_path, params.get("speed", 1.0))
        print(f"  ✓ Generated successfully: {output_path}")
        return True

    except Exception as error:  # noqa: BLE001
        print(f"  ❌ Error generating audio: {error}")
        import traceback

        traceback.print_exc()
        wav_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        return False


def create_evaluation_template(output_dir: Path, generated_files: Iterable[Path]) -> None:
    """Create an evaluation template alongside the generated samples."""
    eval_file = output_dir / "EVALUATION.md"
    sample_list = list(generated_files)

    with eval_file.open("w", encoding="utf-8") as handle:
        handle.write("# Voice Cloning Test - Evaluation\n\n")
        handle.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Generated Files: {len(sample_list)}\n\n")

        handle.write("## Voice Parameters Used\n\n")
        for param, value in VOICE_PARAMS.items():
            handle.write(f"- **{param}**: {value}\n")

        handle.write("\n## Sample Evaluation\n\n")
        handle.write("Rate each sample from 1-10 (1=Poor, 10=Excellent)\n\n")

        for sample_id in MYSTERY_SAMPLES:
            handle.write(f"### {sample_id.replace('_', ' ').title()}\n\n")
            handle.write("| Criteria | Rating (1-10) | Notes |\n")
            handle.write("|----------|---------------|-------|\n")
            handle.write("| Voice Quality | | |\n")
            handle.write("| Suspense/Drama | | |\n")
            handle.write("| Pause Timing | | |\n")
            handle.write("| Intonation | | |\n")
            handle.write("| Pacing | | |\n")
            handle.write("| Emotion | | |\n")
            handle.write("| **Overall** | | **Pass/Fail** |\n\n")

        handle.write("\n## Overall Assessment\n\n")
        handle.write("**Overall Decision:** [ ] PASS - Voice quality is acceptable, proceed with development\n")
        handle.write("                     [ ] FAIL - Voice needs improvement\n\n")
        handle.write("## Improvement Suggestions\n\n")
        handle.write("What specific changes would improve the voice?\n\n")
        handle.write("- [ ] Increase pause duration (make more dramatic)\n")
        handle.write("- [ ] Decrease pause duration (too slow)\n")
        handle.write("- [ ] More expressiveness (more emotional variation)\n")
        handle.write("- [ ] Less expressiveness (too exaggerated)\n")
        handle.write("- [ ] Slower speed (more suspenseful)\n")
        handle.write("- [ ] Faster speed (too slow)\n")
        handle.write("- [ ] Deeper voice (lower pitch)\n")
        handle.write("- [ ] Higher voice (raise pitch)\n")
        handle.write("- [ ] Other (describe below):\n\n")
        handle.write("**Additional Comments:**\n\n")
        handle.write("(Describe what you like and what needs improvement)\n\n")

    print(f"✓ Evaluation template created: {eval_file}")


def run_voice_test() -> None:
    """Main entry point for the voice cloning test workflow."""
    training_files = check_environment()
    if not training_files:
        sys.exit(1)

    tts_engine = load_tts_engine()
    if not tts_engine:
        print("\n❌ Failed to load TTS engine. Exiting.")
        sys.exit(1)

    reference_audio = training_files[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_ROOT / f"test_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("GENERATING MYSTERY SAMPLES")
    print("=" * 60 + "\n")

    generated_files: List[Path] = []
    for sample_id, sample_text in MYSTERY_SAMPLES.items():
        output_path = output_dir / f"{sample_id}.mp3"
        if generate_sample(
            tts_engine=tts_engine,
            reference_audio=reference_audio,
            text=sample_text.strip(),
            output_path=output_path,
            params=VOICE_PARAMS,
        ):
            generated_files.append(output_path)

    print("\n" + "=" * 60)
    print("TEST COMPLETED!")
    print("=" * 60)
    print(f"\nGenerated {len(generated_files)} test sample(s):")
    for file_path in generated_files:
        print(f"  - {file_path}")

    print("\nVoice Parameters Used:")
    for param, value in VOICE_PARAMS.items():
        print(f"  - {param}: {value}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Listen to each generated sample")
    print("2. Fill out VOICE_EVALUATION.md with your ratings")
    print("3. Provide feedback on what to improve")
    print("4. Share results with the development team")
    print()

    create_evaluation_template(output_dir, generated_files)


def main() -> None:
    """CLI entry point."""
    print("\n" + "=" * 60)
    print("ANTIQUE MYSTERY PODCAST - VOICE CLONING TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Clone voice from the first training file")
    print("2. Generate 5 mystery narration samples")
    print("3. Create an evaluation template for your feedback\n")

    try:
        run_voice_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as error:  # noqa: BLE001
        print(f"\n❌ ERROR: {error}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
