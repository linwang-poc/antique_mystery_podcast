from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import torch
import torchaudio
from pydub import AudioSegment

from src.audio.concatenator import merge_segments
from src.tts.voice_registry import VoiceProfile, VoiceRegistry

logger = logging.getLogger(__name__)

ProgressFn = Optional[Callable[[float, str], None]]


class TTSService:
    def __init__(
        self,
        registry: VoiceRegistry,
        output_dir: Path = Path("output/generated"),
        ending_path: Path = Path("assets/ending.mp3"),
    ) -> None:
        self.registry = registry
        self.output_dir = output_dir
        self.ending_path = ending_path
        self._engine = None

    def generate_episode(
        self,
        text: str,
        profile_id: str,
        title_hint: Optional[str] = None,
        notify: ProgressFn = None,
    ) -> Path:
        profile = self.registry.get(profile_id)
        engine = self._load_engine()

        chunks = list(_chunk_text(text))
        logger.info(
            "Starting synthesis using profile '%s' in %d chunk(s).",
            profile_id,
            len(chunks),
        )
        if notify:
            notify(0.05, f"Generating narration in {len(chunks)} chunk(s)...")

        try:
            with TemporaryDirectory(prefix="mystery_chunks_") as tmpdir:
                tmpdir_path = Path(tmpdir)
                segments: List[AudioSegment] = []

                for index, chunk in enumerate(chunks, start=1):
                    if notify:
                        notify(
                            0.05 + 0.7 * (index / max(len(chunks), 1)),
                            f"Rendering chunk {index}/{len(chunks)}",
                        )
                    logger.debug(
                        "Rendering chunk %d/%d (%d chars).", index, len(chunks), len(chunk)
                    )
                    segment = self._synthesize_chunk(
                        engine=engine,
                        profile=profile,
                        text=chunk,
                        tmpdir=tmpdir_path,
                        chunk_index=index,
                    )
                    segments.append(segment)
        except Exception:
            logger.exception("Error during synthesis")
            raise

        logger.info("Merging narration with ending snippet.")
        narration = merge_segments(segments, self.ending_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _slugify(title_hint or "mystery_story")
        output_path = self.output_dir / f"{timestamp}_{slug}.mp3"

        if notify:
            notify(0.85, "Stitching final narration...")
        narration.export(output_path, format="mp3", bitrate="192k")

        logger.info("Narration exported to %s", output_path)
        if notify:
            notify(1.0, f"Story ready: {output_path.name}")
        return output_path

    def _load_engine(self):
        if self._engine is None:
            logger.info("Loading Chatterbox TTS engine...")
            from chatterbox.tts import ChatterboxTTS

            self._engine = ChatterboxTTS.from_pretrained(device="cpu")
            logger.info("Chatterbox TTS loaded.")
        return self._engine

    def _synthesize_chunk(
        self,
        engine,
        profile: VoiceProfile,
        text: str,
        tmpdir: Path,
        chunk_index: int,
    ) -> AudioSegment:
        params = profile.params
        exaggeration = params.get("exaggeration", 0.6)

        raw_audio = engine.generate(
            text=text,
            audio_prompt_path=str(profile.safe_reference),
            exaggeration=exaggeration,
        )
        wav_tensor, sample_rate = _prepare_wav_tensor(raw_audio, engine)

        wav_path = tmpdir / f"chunk_{chunk_index:02d}.wav"
        torchaudio.save(str(wav_path), wav_tensor, sample_rate)

        audio = AudioSegment.from_wav(wav_path)
        audio = _apply_voice_params(audio, params)
        return audio


def _chunk_text(text: str, max_chars: int = 1200) -> Iterable[str]:
    paragraphs = [block.strip() for block in text.split("\n\n") if block.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    current = []
    current_len = 0
    for paragraph in paragraphs:
        if current_len + len(paragraph) <= max_chars:
            current.append(paragraph)
            current_len += len(paragraph) + 2
        else:
            sentences = paragraph.split(". ")
            for sentence in sentences:
                sent = sentence.strip()
                if not sent:
                    continue
                if current_len + len(sent) <= max_chars:
                    current.append(sent)
                    current_len += len(sent) + 1
                else:
                    if current:
                        yield " ".join(current)
                    current = [sent]
                    current_len = len(sent)
    if current:
        yield " ".join(current)


def _prepare_wav_tensor(raw_audio, engine) -> Tuple[torch.Tensor, int]:
    sample_rate = getattr(engine, "sample_rate", getattr(engine, "sr", 24000))
    wav = raw_audio
    if isinstance(raw_audio, tuple) and len(raw_audio) == 2:
        wav, sample_rate = raw_audio

    if not isinstance(wav, torch.Tensor):
        wav = torch.tensor(wav, dtype=torch.float32)

    wav = wav.detach().cpu()
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    return wav, int(sample_rate)


def _apply_voice_params(audio: AudioSegment, params: Dict[str, float]) -> AudioSegment:
    speed = params.get("speed", 1.0)
    if abs(speed - 1.0) > 1e-3:
        original_rate = audio.frame_rate
        new_rate = max(1, int(original_rate * speed))
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        audio = audio.set_frame_rate(original_rate)
    return audio


def _slugify(value: str) -> str:
    allowed = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.lower())
    cleaned = "_".join(filter(None, allowed.split("_")))
    return cleaned[:40] or "story"
