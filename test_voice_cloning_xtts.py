#!/usr/bin/env python3
"""
Voice Cloning Test Script (XTTS v2 Alternative)

This script mirrors `test_voice_cloning.py` but uses the open-source
Coqui XTTS v2 model instead of Chatterbox. XTTS is licensed under the
Coqui Public Model License (non-commercial). Use this script when you
need a fully open-source fallback.
"""

from __future__ import annotations

import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

# Suppress the attention mask warning from transformers. We now rely on
# XTTS's sentence splitter to stay under the 400-token limit, so the model
# reuses attention masks internally without bubbling up the warning.
warnings.filterwarnings("ignore", message=".*attention mask.*pad token.*eos token.*")


BASE_DIR = Path(__file__).parent.resolve()
REFERENCE_VOICE_DIR = BASE_DIR / "assets" / "reference_voices"
OUTPUT_ROOT = BASE_DIR / "output" / "voice_tests_xtts"


MYSTERY_SAMPLES = {
    "01_suspenseful_opening": """The antique vase gleamed in the dim light of the auction house.
Margaret had seen it before, somewhere. The pattern of roses and thorns
triggered a memory she couldn't quite grasp. She stepped closer, her heart
racing. Then she saw it. The tiny crack. The same crack from her grandmother's
photograph. But that vase had been destroyed in the fire. Hadn't it?""",
}


VOICE_PARAMS = {
    "speed": 0.90,
    "expressiveness": 8,
    "pitch": 1,
    "pause_duration": 2.2,
    "exaggeration": 0.6,  # Document purposes; XTTS does not expose this knob.
    "split_sentences": False,  # Disabled - we handle chunking externally with custom token-aware splitter
}


def check_environment() -> List[Path]:
    print("=" * 60)
    print("VOICE CLONING TEST (XTTS) - Environment Check")
    print("=" * 60)
    print(f"\n✓ Python version: {sys.version.split()[0]}")

    training_files = sorted(REFERENCE_VOICE_DIR.glob("training_*.mp3"))
    if not training_files:
        print("\n❌ ERROR: No training voice files found in assets/reference_voices/")
        return []
    print(f"\n✓ Found {len(training_files)} training voice file(s)")

    try:
        import torchaudio  # noqa: F401
        print("✓ torchaudio available")
    except ImportError:
        print("\n❌ ERROR: torchaudio is required. Install via pip.")
        return []

    try:
        from TTS.api import TTS  # noqa: F401
        import TTS as tts_module
        print(f"✓ Coqui TTS library found (version: {tts_module.__version__})")
    except ImportError:
        print("\n❌ ERROR: Coqui TTS library not installed.")
        print("   Install with: pip install TTS")
        return []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {OUTPUT_ROOT}")

    print("\n" + "=" * 60)
    print("Environment check PASSED! Ready to test voice cloning (XTTS).")
    print("=" * 60 + "\n")
    return training_files


def load_xtts_engine():
    print("Loading Coqui XTTS v2 engine...")
    try:
        import torch
        from torch.serialization import add_safe_globals
        from TTS.tts.configs.xtts_config import XttsConfig, XttsAudioConfig
        from TTS.config.shared_configs import BaseDatasetConfig
        from TTS.tts.models.xtts import XttsArgs

        add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

        original_torch_load = torch.load

        def trusted_torch_load(*args, **kwargs):
            kwargs.setdefault("weights_only", False)
            return original_torch_load(*args, **kwargs)

        torch.load = trusted_torch_load  # type: ignore

        from TTS.api import TTS

        os.environ.setdefault("COQUI_TOS_AGREED", "1")
        device = "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        tts.to(device)
        print("✓ XTTS v2 loaded successfully")
        return tts
    except Exception as error:  # noqa: BLE001
        print(f"❌ Error loading XTTS v2: {error}")
        import traceback

        traceback.print_exc()
        return None
    finally:
        if "original_torch_load" in locals() and "torch" in locals():
            torch.load = original_torch_load  # type: ignore


def generate_sample_xtts(
    tts_engine,
    reference_audio: Path,
    text: str,
    output_path: Path,
    params: Dict[str, float],
) -> bool:
    from pydub import AudioSegment

    print(f"Generating: {output_path.name}")
    wav_path = output_path.with_suffix(".wav")
    try:
        tts_engine.tts_to_file(
            text=text,
            speaker_wav=str(reference_audio),
            language="en",
            file_path=str(wav_path),
            split_sentences=bool(params.get("split_sentences", True)),
        )

        audio = AudioSegment.from_wav(wav_path)
        speed = params.get("speed", 1.0)
        if abs(speed - 1.0) > 1e-3:
            original_rate = audio.frame_rate
            new_rate = max(1, int(original_rate * speed))
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
            audio = audio.set_frame_rate(original_rate)

        audio.export(output_path, format="mp3", bitrate="192k")
        wav_path.unlink(missing_ok=True)
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
    eval_file = output_dir / "EVALUATION.md"
    with eval_file.open("w", encoding="utf-8") as handle:
        handle.write("# Voice Cloning Test (XTTS) - Evaluation\n\n")
        handle.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Generated Files: {len(list(generated_files))}\n\n")
        handle.write("## Voice Parameters Used\n\n")
        for param, value in VOICE_PARAMS.items():
            handle.write(f"- **{param}**: {value}\n")

        handle.write("\n## Notes\n\n")
        handle.write(
            "XTTS v2 exposes fewer expressive controls than Chatterbox. Most parameters above are"
            " informational and implemented via post-processing (speed) or left for future tuning.\n"
        )


def run_voice_test_xtts(single_sample_only: bool = True) -> None:
    training_files = check_environment()
    if not training_files:
        sys.exit(1)

    tts_engine = load_xtts_engine()
    if not tts_engine:
        sys.exit(1)

    reference_audio = training_files[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_ROOT / f"test_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []
    for sample_id, sample_text in MYSTERY_SAMPLES.items():
        if single_sample_only and sample_id != "01_suspenseful_opening":
            continue
        output_path = output_dir / f"{sample_id}.mp3"
        if generate_sample_xtts(
            tts_engine=tts_engine,
            reference_audio=reference_audio,
            text=sample_text.strip(),
            output_path=output_path,
            params=VOICE_PARAMS,
        ):
            generated_files.append(output_path)

    create_evaluation_template(output_dir, generated_files)
    print("\n" + "=" * 60)
    print("XTTS TEST COMPLETED!")
    print("=" * 60)
    for file_path in generated_files:
        print(f"  - {file_path}")
    print("\nEvaluation template saved alongside outputs.")


def main() -> None:
    print("\n" + "=" * 60)
    print("ANTIQUE MYSTERY PODCAST - XTTS VOICE CLONING TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Clone voice from the first training file using XTTS v2")
    print("2. Generate a suspenseful opening sample")
    print("3. Create a lightweight evaluation template\n")

    try:
        run_voice_test_xtts(single_sample_only=True)
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
