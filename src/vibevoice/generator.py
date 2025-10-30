#!/usr/bin/env python3
"""
VibeVoice Generator Module

Wrapper around Microsoft's VibeVoice 1.5B model for mystery podcast generation.
Handles model loading, audio synthesis, and ending snippet concatenation.
"""

import os
import re
import torch
import soundfile as sf
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from vibevoice.modular.modeling_vibevoice_inference import (
        VibeVoiceForConditionalGenerationInference
    )
    from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor
    import librosa
    from pydub import AudioSegment
except ImportError as e:
    print(f"ERROR: Required package not installed: {e}")
    print("\nInstall VibeVoice with:")
    print("  pip install git+https://github.com/vibevoice-community/VibeVoice.git")
    raise


class VibeVoiceGenerator:
    """VibeVoice TTS generator with audio processing for mystery narration"""

    def __init__(
        self,
        model_name: str = "microsoft/VibeVoice-1.5B",
        cache_dir: str = "/models",
        device: str = "cuda",
        inference_steps: int = 15
    ):
        """
        Initialize VibeVoice generator

        Args:
            model_name: Hugging Face model ID
            cache_dir: Directory to cache model weights
            device: Device to run on ('cuda' or 'cpu')
            inference_steps: Number of diffusion steps (5=fast, 20=quality)
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.output_dir = Path("/app/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Initializing VibeVoice on {self.device}...")

        # Load processor
        print(f"Loading VibeVoice processor from {model_name}...")
        self.processor = VibeVoiceProcessor.from_pretrained(
            model_name,
            cache_dir=str(self.cache_dir)
        )
        print("✓ Processor loaded")

        # Load model
        print(f"Loading VibeVoice-1.5B model (this may take 1-2 minutes)...")
        self.model = VibeVoiceForConditionalGenerationInference.from_pretrained(
            model_name,
            cache_dir=str(self.cache_dir),
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32
        ).to(self.device)

        self.model.set_ddpm_inference_steps(num_steps=inference_steps)
        print(f"✓ Model loaded on {self.device}")
        print(f"✓ Inference steps: {inference_steps}")
        print("\n✓ VibeVoice ready for generation!\n")

    def validate_speaker_format(self, text: str) -> bool:
        """
        Validate that text uses proper 'Speaker N:' format

        Args:
            text: Input story text

        Returns:
            True if format is valid, False otherwise
        """
        speaker_pattern = r'^Speaker\s+(\d+)\s*:\s*(.*)$'
        valid_lines = []

        for line in text.split('\n'):
            if line.strip():
                if re.match(speaker_pattern, line.strip(), re.IGNORECASE):
                    valid_lines.append(line)

        return len(valid_lines) > 0

    def generate(
        self,
        text: str,
        voice_reference: Optional[str] = None,
        cfg_scale: float = 1.3,
        voice_speed_factor: float = 0.9,
        add_ending: bool = True,
        output_name: Optional[str] = None
    ) -> Path:
        """
        Generate mystery narration audio

        Args:
            text: Story text in "Speaker 0:" format
            voice_reference: Path to reference audio (5-15 seconds, MP3/WAV)
            cfg_scale: Guidance scale (1.0-2.0, higher = stricter text adherence)
            voice_speed_factor: Speed multiplier (0.5-2.0, lower = slower)
            add_ending: Whether to append ending snippet
            output_name: Output filename (without extension), auto-generated if None

        Returns:
            Path to generated audio file (MP3)
        """

        # Validate speaker format
        if not self.validate_speaker_format(text):
            raise ValueError(
                "Story text must use 'Speaker N:' format!\n"
                "Example: 'Speaker 0: Your story text here...'\n"
                "For single narrator, use 'Speaker 0:' for all paragraphs."
            )

        # Count speakers
        speakers_found = set(re.findall(r'Speaker\s+(\d+)\s*:', text, re.IGNORECASE))
        print(f"✓ Found {len(speakers_found)} speaker(s): Speaker {', Speaker '.join(sorted(speakers_found))}")

        # Load voice reference if provided
        voice_audio = None
        if voice_reference and Path(voice_reference).exists():
            voice_audio, sr = librosa.load(voice_reference, sr=24000, mono=True)
            duration = len(voice_audio) / sr
            print(f"✓ Loaded voice reference: {duration:.1f} seconds")

            if duration < 3:
                print("⚠️  WARNING: Reference audio <3 seconds. 5-15 seconds recommended.")
            elif duration > 30:
                print(f"⚠️  Trimming reference audio from {duration:.1f}s to 30s...")
                voice_audio = voice_audio[:int(30 * sr)]
        else:
            print("ℹ️  Using default VibeVoice voice (no cloning)")

        # Prepare inputs
        voice_samples = [[voice_audio]] if voice_audio is not None else None
        inputs = self.processor(
            text=[text],
            voice_samples=voice_samples,
            return_tensors="pt"
        )

        # Move to device (only move tensors)
        inputs = {
            k: v.to(self.device) if torch.is_tensor(v) else v
            for k, v in inputs.items()
        }

        # Estimate generation time
        word_count = len(re.sub(r'Speaker\s+\d+\s*:', '', text, flags=re.IGNORECASE).split())
        estimated_audio_minutes = word_count / 150
        estimated_gen_time = estimated_audio_minutes * 6

        print(f"\n{'='*60}")
        print(f"GENERATING AUDIO")
        print(f"{'='*60}")
        print(f"Word count: {word_count}")
        print(f"Estimated audio length: ~{estimated_audio_minutes:.1f} minutes")
        print(f"Estimated generation time: ~{estimated_gen_time:.0f} minutes")
        print(f"CFG scale: {cfg_scale}")
        print(f"Speed factor: {voice_speed_factor}")
        print(f"\nGenerating... (this will take a while)")
        print("☕ Go get coffee! ☕\n")

        # Generate audio
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                cfg_scale=cfg_scale,
                voice_speed_factor=voice_speed_factor,
                tokenizer=self.processor.tokenizer,
                generation_config={'do_sample': False},
                verbose=True
            )

        # Extract audio
        if not hasattr(outputs, 'speech_outputs') or len(outputs.speech_outputs) == 0:
            raise RuntimeError("Audio generation failed - no speech outputs")

        audio_tensor = outputs.speech_outputs[0]
        audio_array = audio_tensor.detach().cpu().float().numpy().ravel()
        sample_rate = 24000

        actual_duration = len(audio_array) / sample_rate / 60
        print(f"\n{'='*60}")
        print(f"✓ GENERATION COMPLETE!")
        print(f"{'='*60}")
        print(f"✓ Audio duration: {actual_duration:.1f} minutes")
        print(f"✓ Sample rate: {sample_rate} Hz")
        print(f"✓ Audio samples: {len(audio_array):,}\n")

        # Generate output filename if not provided
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"mystery_podcast_{timestamp}"

        # Save narration WAV
        narration_path = self.output_dir / f"{output_name}_narration.wav"
        sf.write(str(narration_path), audio_array, sample_rate)
        print(f"✓ Saved narration to: {narration_path}")

        # Add ending if requested
        if add_ending:
            final_path = self._add_ending(narration_path, output_name)
            return final_path
        else:
            # Convert to MP3
            final_path = self._convert_to_mp3(narration_path, output_name)
            return final_path

    def _add_ending(self, narration_path: Path, output_name: str) -> Path:
        """
        Append ending snippet to narration

        Args:
            narration_path: Path to narration WAV file
            output_name: Base output filename

        Returns:
            Path to final MP3 file
        """
        ending_path = Path("/app/assets/ending.mp3")

        if not ending_path.exists():
            print("⚠️  Ending snippet not found, skipping")
            return self._convert_to_mp3(narration_path, output_name)

        print(f"\nAdding ending snippet...")

        # Load audio segments
        narration = AudioSegment.from_wav(str(narration_path))
        ending = AudioSegment.from_file(str(ending_path))

        print(f"✓ Loaded narration: {len(narration) / 1000:.1f} seconds")
        print(f"✓ Loaded ending: {len(ending) / 1000:.1f} seconds")

        # Add 1.5s silence gap + ending
        SILENT_GAP_MS = 1500
        silent_gap = AudioSegment.silent(duration=SILENT_GAP_MS)
        combined = narration + silent_gap + ending

        total_duration = len(combined) / 1000 / 60
        print(f"✓ Combined audio: {total_duration:.2f} minutes")

        # Export as MP3
        final_path = self.output_dir / f"{output_name}_final.mp3"
        combined.export(str(final_path), format="mp3", bitrate="192k")

        print(f"✓ Saved final podcast to: {final_path}")
        print(f"✓ File size: {final_path.stat().st_size / 1e6:.1f} MB\n")

        return final_path

    def _convert_to_mp3(self, wav_path: Path, output_name: str) -> Path:
        """
        Convert WAV to MP3

        Args:
            wav_path: Path to WAV file
            output_name: Base output filename

        Returns:
            Path to MP3 file
        """
        audio = AudioSegment.from_wav(str(wav_path))
        mp3_path = self.output_dir / f"{output_name}.mp3"
        audio.export(str(mp3_path), format="mp3", bitrate="192k")
        print(f"✓ Converted to MP3: {mp3_path}")
        return mp3_path


def main():
    """Test the generator standalone"""
    generator = VibeVoiceGenerator()

    test_text = """Speaker 0: It was a fog-laden morning when I stumbled upon a peculiar bottle.

Speaker 0: This was no ordinary tonic."""

    output_path = generator.generate(
        text=test_text,
        voice_reference=None,
        cfg_scale=1.3,
        voice_speed_factor=0.9,
        add_ending=True
    )

    print(f"\n✓ Test generation complete: {output_path}")


if __name__ == "__main__":
    main()
