from __future__ import annotations

import logging
import os
import re
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
        self._engines: Dict[str, object] = {}

    def generate_episode(
        self,
        text: str,
        profile_id: str,
        title_hint: Optional[str] = None,
        notify: ProgressFn = None,
    ) -> Path:
        profile = self.registry.get(profile_id)
        engine_type = profile.engine.lower()
        max_words = profile.chunk_max_words
        if max_words is None and engine_type == "xtts":
            max_words = 220
        max_chars = (
            profile.chunk_max_chars
            if profile.chunk_max_chars is not None
            else 1200
        )
        chunks = list(_chunk_text(text, max_chars=max_chars, max_words=max_words))
        word_counts = [len(chunk.split()) for chunk in chunks]
        max_chunk_words = max(word_counts, default=0)
        logger.info(
            "Starting synthesis using profile '%s' (engine=%s) in %d chunk(s). Max words per chunk: %d",
            profile_id,
            engine_type,
            len(chunks),
            max_chunk_words,
        )
        for idx, chunk in enumerate(chunks, start=1):
            logger.debug("Chunk %d preview (%d words): %s", idx, len(chunk.split()), chunk)
        if notify:
            notify(0.05, f"Generating narration in {len(chunks)} chunk(s)...")

        synthesizer = self._load_engine(engine_type)

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

                    if engine_type == "xtts":
                        segment = self._synthesize_chunk_xtts(
                            engine=synthesizer,
                            profile=profile,
                            text=chunk,
                            tmpdir=tmpdir_path,
                            chunk_index=index,
                        )
                    elif engine_type == "f5tts":
                        segment = self._synthesize_chunk_f5tts(
                            engine=synthesizer,
                            profile=profile,
                            text=chunk,
                            tmpdir=tmpdir_path,
                            chunk_index=index,
                        )
                    else:
                        segment = self._synthesize_chunk_chatterbox(
                            engine=synthesizer,
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

    def _load_engine(self, engine_type: str):
        if engine_type == "xtts":
            if "xtts" not in self._engines:
                logger.info("Loading XTTS v2 engine...")
                self._engines["xtts"] = self._initialize_xtts()
            return self._engines["xtts"]

        if engine_type == "f5tts":
            if "f5tts" not in self._engines:
                logger.info("Loading F5-TTS engine...")
                self._engines["f5tts"] = self._initialize_f5tts()
            return self._engines["f5tts"]

        if "chatterbox" not in self._engines:
            logger.info("Loading Chatterbox TTS engine...")
            from chatterbox.tts import ChatterboxTTS

            self._engines["chatterbox"] = ChatterboxTTS.from_pretrained(device="cpu")
            logger.info("Chatterbox TTS loaded.")
        return self._engines["chatterbox"]

    def _initialize_xtts(self):
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
            engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            engine.to("cpu")
            if hasattr(engine, "synthesizer"):
                try:
                    engine.synthesizer.tts_model.args.num_chars = max(
                        1000, engine.synthesizer.tts_model.args.num_chars
                    )
                    logger.info(
                        "XTTS character limit raised to %s",
                        engine.synthesizer.tts_model.args.num_chars,
                    )
                except AttributeError:
                    logger.warning("Unable to adjust XTTS character limit; continuing.")
            logger.info("XTTS v2 loaded.")
            return engine
        except ImportError as exc:
            logger.error("Failed to import XTTS dependencies: %s", exc)
            raise
        finally:
            if "original_torch_load" in locals():
                torch.load = original_torch_load  # type: ignore

    def _synthesize_chunk_chatterbox(
        self,
        engine,
        profile: VoiceProfile,
        text: str,
        tmpdir: Path,
        chunk_index: int,
    ) -> AudioSegment:
        params = profile.params
        exaggeration = params.get("exaggeration", 0.85)

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

    def _synthesize_chunk_xtts(
        self,
        engine,
        profile: VoiceProfile,
        text: str,
        tmpdir: Path,
        chunk_index: int,
    ) -> AudioSegment:
        params = profile.params
        wav_path = tmpdir / f"chunk_{chunk_index:02d}.wav"

        split_sentences = (
            bool(profile.params.get("split_sentences"))
            if "split_sentences" in profile.params
            else profile.split_sentences
        )

        engine.tts_to_file(
            text=text,
            speaker_wav=str(profile.safe_reference),
            language="en",
            file_path=str(wav_path),
            temperature=params.get("temperature", 1.0),
            top_k=params.get("top_k"),
            top_p=params.get("top_p"),
            split_sentences=split_sentences,
        )

        audio = AudioSegment.from_wav(wav_path)
        speed = params.get("speed", 1.0)
        if abs(speed - 1.0) > 1e-3:
            original_rate = audio.frame_rate
            new_rate = max(1, int(original_rate * speed))
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
            audio = audio.set_frame_rate(original_rate)

        return audio

    def _initialize_f5tts(self):
        try:
            from f5_tts.api import F5TTS

            engine = F5TTS(
                model="F5TTS_Base",
                device="cpu",
            )
            logger.info("F5-TTS engine loaded.")
            return engine
        except ImportError as exc:
            logger.error("Failed to import F5-TTS dependencies: %s", exc)
            raise

    def _synthesize_chunk_f5tts(
        self,
        engine,
        profile: VoiceProfile,
        text: str,
        tmpdir: Path,
        chunk_index: int,
    ) -> AudioSegment:
        params = profile.params
        wav_path = tmpdir / f"chunk_{chunk_index:02d}.wav"

        # F5-TTS handles long text internally with automatic chunking
        # No need for external chunking - it splits at ~135 bytes per batch
        engine.infer(
            ref_file=str(profile.safe_reference),
            ref_text=profile.reference_text or "",
            gen_text=text,
            file_wave=str(wav_path),
            nfe_step=int(params.get("nfe_step", 32)),
            cfg_strength=params.get("cfg_strength", 2.0),
            sway_sampling_coef=params.get("sway_sampling_coef", -1.0),
            speed=params.get("speed", 1.0),
            remove_silence=False,
        )

        audio = AudioSegment.from_wav(wav_path)
        return audio


SENTENCE_BOUNDARY = re.compile(r"[^.!?…]+[.!?…]?")


def _split_sentences(paragraph: str) -> List[str]:
    sentences = [
        match.group().strip()
        for match in SENTENCE_BOUNDARY.finditer(paragraph)
        if match.group().strip()
    ]
    return sentences or [paragraph.strip()]


def _chunk_text(
    text: str,
    max_chars: Optional[int] = 1200,
    max_words: Optional[int] = None,
) -> Iterable[str]:
    if max_chars is not None and max_chars <= 0:
        max_chars = None
    if max_words is not None and max_words <= 0:
        max_words = None

    paragraphs = [block.strip() for block in text.split("\n\n") if block.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: List[str] = []

    for paragraph in paragraphs:
        sentences = _split_sentences(paragraph)
        current_sentences: List[str] = []
        current_words = 0

        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)
            prospective_sentences = current_sentences + [sentence]
            prospective_words = current_words + word_count
            prospective_chars = len(" ".join(prospective_sentences))

            if current_sentences and (
                (max_words is not None and prospective_words > max_words)
                or (max_chars is not None and prospective_chars > max_chars)
            ):
                chunks.append(" ".join(current_sentences).strip())
                current_sentences = []
                current_words = 0

            if (
                (max_words is not None and word_count > max_words)
                or (max_chars is not None and len(sentence) > max_chars)
            ):
                if max_words is not None:
                    step = max_words
                elif max_chars is not None:
                    step = max_chars
                else:
                    chunks.append(sentence.strip())
                    continue
                step = max(1, step)
                for start_idx in range(0, word_count, step):
                    chunk_sentence = " ".join(words[start_idx : start_idx + step])
                    chunks.append(chunk_sentence.strip())
                continue

            current_sentences.append(sentence)
            current_words += word_count

        if current_sentences:
            chunks.append(" ".join(current_sentences).strip())

    return [chunk for chunk in chunks if chunk]



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
