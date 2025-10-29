#!/usr/bin/env python3
"""
VibeVoice Generation Script for Cloud GPU

This script runs on cloud GPU instances (RunPod, Vast.ai, Colab) to generate
high-quality mystery narration using Microsoft's VibeVoice 1.5B model.

Usage:
    python scripts/vibevoice_generate.py \
        --input story.txt \
        --voice reference_voice.mp3 \
        --output mystery_narration.wav \
        --cfg_scale 1.3 \
        --inference_steps 5

Requirements:
    - GPU with 12GB+ VRAM
    - VibeVoice installed: pip install git+https://github.com/vibevoice-community/VibeVoice.git
"""

import argparse
import sys
from pathlib import Path

try:
    import torch
    import soundfile as sf
    from vibevoice.modular.modeling_vibevoice_inference import (
        VibeVoiceForConditionalGenerationInference
    )
    from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor
except ImportError as e:
    print(f"ERROR: Required package not installed: {e}")
    print("\nInstall VibeVoice with:")
    print("  pip install git+https://github.com/vibevoice-community/VibeVoice.git")
    sys.exit(1)


def check_gpu():
    """Verify GPU availability"""
    if not torch.cuda.is_available():
        print("WARNING: CUDA not available. VibeVoice requires GPU.")
        print("Current device:", "CPU")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✓ GPU detected: {gpu_name}")
        print(f"✓ VRAM: {gpu_memory:.1f} GB")

        if gpu_memory < 12:
            print(f"WARNING: GPU has only {gpu_memory:.1f}GB VRAM. Minimum 12GB recommended.")


def load_text(input_path: Path) -> str:
    """Load story text from file"""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    if not text:
        raise ValueError("Input file is empty")

    word_count = len(text.split())
    print(f"✓ Loaded story: {word_count} words")

    if word_count > 50000:
        print(f"WARNING: Story is {word_count} words. May exceed model capacity.")

    return text


def load_voice_reference(voice_path: Path | None):
    """Load voice reference audio if provided"""
    if voice_path is None:
        print("ℹ Using default VibeVoice voice (no cloning)")
        return None

    if not voice_path.exists():
        raise FileNotFoundError(f"Voice reference not found: {voice_path}")

    try:
        import librosa
        audio, sr = librosa.load(voice_path, sr=24000, mono=True)
        duration = len(audio) / sr
        print(f"✓ Loaded voice reference: {duration:.1f} seconds")

        if duration < 3:
            print("WARNING: Reference audio <3 seconds. 5-15 seconds recommended.")
        elif duration > 30:
            print("WARNING: Reference audio >30 seconds. Will use first 15 seconds.")
            audio = audio[:int(15 * sr)]

        return audio
    except Exception as e:
        raise RuntimeError(f"Failed to load voice reference: {e}")


def generate_narration(
    text: str,
    voice_samples=None,
    cfg_scale: float = 1.3,
    inference_steps: int = 5,
    device: str = "cuda"
):
    """Generate narration using VibeVoice"""

    print("\n" + "="*60)
    print("LOADING VIBEVOICE MODEL")
    print("="*60)

    # Load processor
    print("Loading VibeVoice processor...")
    processor = VibeVoiceProcessor.from_pretrained("microsoft/VibeVoice-1.5B")
    print("✓ Processor loaded")

    # Load model
    print(f"Loading VibeVoice-1.5B model (5.4GB)...")
    model = VibeVoiceForConditionalGenerationInference.from_pretrained(
        "microsoft/VibeVoice-1.5B",
        torch_dtype=torch.bfloat16
    ).to(device)
    print(f"✓ Model loaded on {device}")

    # Set inference steps
    model.set_ddpm_inference_steps(num_steps=inference_steps)
    print(f"✓ Inference steps: {inference_steps}")

    # Prepare inputs
    print("\n" + "="*60)
    print("GENERATING AUDIO")
    print("="*60)

    voice_samples_formatted = [[voice_samples]] if voice_samples is not None else None

    inputs = processor(
        text=[text],
        voice_samples=voice_samples_formatted,
        return_tensors="pt"
    )

    # Move to GPU
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Estimate generation time
    word_count = len(text.split())
    estimated_audio_minutes = word_count / 150  # ~150 words per minute
    estimated_gen_time = estimated_audio_minutes * 6  # 0.15x RT = 6 minutes per minute

    print(f"Estimated audio length: ~{estimated_audio_minutes:.1f} minutes")
    print(f"Estimated generation time: ~{estimated_gen_time:.0f} minutes")
    print(f"CFG scale: {cfg_scale}")
    print("\nGenerating... (this will take a while)")

    # Generate
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            cfg_scale=cfg_scale,
            tokenizer=processor.tokenizer,
            generation_config={'do_sample': False},
            verbose=True
        )

    # Extract audio
    audio_tensor = outputs.speech_outputs[0]
    audio = audio_tensor.cpu().float().numpy()

    actual_duration = len(audio) / 24000 / 60
    print(f"\n✓ Generation complete!")
    print(f"✓ Audio duration: {actual_duration:.1f} minutes")

    return audio, 24000


def main():
    parser = argparse.ArgumentParser(description="Generate mystery narration with VibeVoice")
    parser.add_argument("--input", "-i", type=Path, required=True,
                        help="Input story text file")
    parser.add_argument("--voice", "-v", type=Path, default=None,
                        help="Voice reference audio (optional, 5-15 seconds)")
    parser.add_argument("--output", "-o", type=Path, required=True,
                        help="Output WAV file path")
    parser.add_argument("--cfg_scale", type=float, default=1.3,
                        help="CFG scale (1.0-2.0, higher = stricter text adherence)")
    parser.add_argument("--inference_steps", type=int, default=5,
                        help="Diffusion steps (5=fast, 20=quality)")
    parser.add_argument("--device", default="cuda",
                        help="Device (cuda/cpu)")

    args = parser.parse_args()

    # Check GPU
    check_gpu()

    # Load inputs
    print("\n" + "="*60)
    print("LOADING INPUTS")
    print("="*60)
    text = load_text(args.input)
    voice_ref = load_voice_reference(args.voice)

    # Generate
    audio, sample_rate = generate_narration(
        text,
        voice_samples=voice_ref,
        cfg_scale=args.cfg_scale,
        inference_steps=args.inference_steps,
        device=args.device
    )

    # Save
    print("\n" + "="*60)
    print("SAVING OUTPUT")
    print("="*60)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, audio, sample_rate)
    print(f"✓ Saved to: {args.output}")
    print(f"✓ File size: {args.output.stat().st_size / 1e6:.1f} MB")

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Output: {args.output.absolute()}")
    print("\nNext steps:")
    print("1. Download the audio file to your laptop")
    print("2. Terminate this cloud GPU instance to stop charges")
    print("3. Listen and evaluate the quality")


if __name__ == "__main__":
    main()
