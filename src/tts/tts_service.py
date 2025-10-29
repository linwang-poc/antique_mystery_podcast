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
        self._xtts_tokenizer = None

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

        # For XTTS, load engine first to get tokenizer for accurate chunking
        tokenizer = None
        if engine_type == "xtts":
            # Ensure XTTS engine (and tokenizer) is loaded before chunking
            _ = self._load_engine(engine_type)
            tokenizer = self._xtts_tokenizer

        # Chunk text with token-aware splitting for XTTS
        chunks = list(
            _chunk_text(
                text,
                max_chars=max_chars,
                max_words=max_words,
                tokenizer=tokenizer,
                max_tokens=250,  # Conservative safety margin for 400-token XTTS limit
            )
        )

        # Log chunk statistics
        word_counts = [len(chunk.split()) for chunk in chunks]
        max_chunk_words = max(word_counts, default=0)

        if tokenizer is not None:
            # Log token counts for XTTS
            token_counts = []
            for chunk in chunks:
                try:
                    token_counts.append(len(tokenizer.encode(chunk)))
                except Exception:  # noqa: BLE001
                    token_counts.append(int(len(chunk.split()) * 1.8))
            max_chunk_tokens = max(token_counts, default=0)
            logger.info(
                "Starting synthesis using profile '%s' (engine=%s) in %d chunk(s). "
                "Max tokens per chunk: %d (max words: %d)",
                profile_id,
                engine_type,
                len(chunks),
                max_chunk_tokens,
                max_chunk_words,
            )
            for idx, chunk in enumerate(chunks, start=1):
                logger.debug(
                    "Chunk %d: %d tokens, %d words - preview: %s",
                    idx,
                    token_counts[idx - 1],
                    word_counts[idx - 1],
                    chunk[:100] + "..." if len(chunk) > 100 else chunk,
                )
        else:
            # Fallback logging for non-XTTS engines
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

            # Load XTTS tokenizer for accurate token counting
            try:
                from transformers import AutoTokenizer
                self._xtts_tokenizer = AutoTokenizer.from_pretrained(
                    "coqui/XTTS-v2", use_fast=False
                )
                logger.info("XTTS tokenizer loaded for accurate token counting.")
            except Exception as tokenizer_error:  # noqa: BLE001
                logger.warning(
                    "Failed to load XTTS tokenizer: %s. Falling back to word-based chunking.",
                    tokenizer_error,
                )
                self._xtts_tokenizer = None

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

        # Pre-synthesis token verification for XTTS (400 token hard limit)
        if self._xtts_tokenizer is not None:
            try:
                token_count = len(self._xtts_tokenizer.encode(text))
                if token_count > 380:  # Safety margin before 400 limit
                    logger.error(
                        "Chunk %d exceeds safe token limit: %d tokens (max: 380). "
                        "Text preview: %s",
                        chunk_index,
                        token_count,
                        text[:200] + "..." if len(text) > 200 else text,
                    )
                    raise ValueError(
                        f"Chunk {chunk_index} has {token_count} tokens, exceeding XTTS safe limit of 380. "
                        "This indicates a chunking failure. Please report this error."
                    )
                logger.debug("Chunk %d token count verified: %d tokens", chunk_index, token_count)
            except ValueError:
                # Re-raise ValueError (our custom error)
                raise
            except Exception as e:  # noqa: BLE001
                # Tokenizer failed, log warning but proceed (chunking should have handled limits)
                logger.warning(
                    "Could not verify token count for chunk %d: %s. Proceeding with synthesis.",
                    chunk_index,
                    str(e)[:100]
                )

        # Always disable XTTS's internal sentence splitting
        # We handle all chunking externally with token-aware custom splitter
        engine.tts_to_file(
            text=text,
            speaker_wav=str(profile.safe_reference),
            language="en",
            file_path=str(wav_path),
            temperature=params.get("temperature", 1.0),
            top_k=params.get("top_k"),
            top_p=params.get("top_p"),
            split_sentences=False,
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


def _chunk_text(
    text: str,
    max_chars: Optional[int] = 1200,
    max_words: Optional[int] = None,
    tokenizer=None,
    max_tokens: int = 250,
) -> Iterable[str]:
    """
    Split text into chunks respecting natural boundaries and token limits.

    Hierarchy: Paragraphs (\\n\\n) → Lines (\\n) → Sentences (.) → Clauses (,) → Words

    Args:
        text: The text to chunk
        max_chars: Maximum characters per chunk (fallback if no tokenizer)
        max_words: Maximum words per chunk (fallback if no tokenizer)
        tokenizer: Optional tokenizer for accurate token counting (XTTS)
        max_tokens: Maximum tokens per chunk when using tokenizer (default: 250, conservative safety margin for 400 limit)
    """
    # Ensure NLTK punkt data is available for sentence tokenization
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer data...")
            nltk.download('punkt', quiet=True)
    except ImportError:
        logger.warning("NLTK not available, falling back to regex-based sentence splitting")
        nltk = None

    # Normalize limits
    if max_chars is not None and max_chars <= 0:
        max_chars = None
    if max_words is not None and max_words <= 0:
        max_words = None

    # Split into paragraphs first (\\n\\n)
    paragraphs = [block.strip() for block in text.split("\n\n") if block.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: List[str] = []

    for paragraph in paragraphs:
        # Try splitting by line breaks within paragraphs
        lines = [line.strip() for line in paragraph.split("\n") if line.strip()]

        for line in lines:
            # Split line into sentences using NLTK (handles abbreviations, etc.)
            if nltk is not None:
                try:
                    sentences = nltk.sent_tokenize(line)
                except Exception:  # noqa: BLE001
                    # Fallback to basic splitting if NLTK fails
                    sentences = _split_sentences_fallback(line)
            else:
                sentences = _split_sentences_fallback(line)

            current_parts: List[str] = []

            for sentence in sentences:
                # Check if adding this sentence would exceed limits
                prospective_text = " ".join(current_parts + [sentence])

                if tokenizer is not None:
                    # Use accurate token counting
                    try:
                        prospective_tokens = len(tokenizer.encode(prospective_text))
                    except Exception as e:  # noqa: BLE001
                        # Fallback to word counting if tokenization fails
                        logger.warning(
                            "Tokenizer encode failed (using 1.8x word estimate instead): %s",
                            str(e)[:100]
                        )
                        prospective_tokens = len(prospective_text.split()) * 1.8  # Rough estimate

                    # If current buffer exists and adding sentence exceeds limit, flush buffer
                    if current_parts and prospective_tokens > max_tokens:
                        chunk = " ".join(current_parts).strip()
                        if chunk:
                            chunks.append(chunk)
                            try:
                                actual_tokens = len(tokenizer.encode(chunk))
                            except Exception:  # noqa: BLE001
                                actual_tokens = int(len(chunk.split()) * 1.8)
                            logger.debug(
                                "Chunk created: %d tokens (%d words, %d chars)",
                                actual_tokens,
                                len(chunk.split()),
                                len(chunk),
                            )
                            if actual_tokens > max_tokens * 0.9:
                                logger.warning(
                                    "Chunk near token limit: %d/%d tokens",
                                    actual_tokens,
                                    max_tokens,
                                )
                        current_parts = []

                    # Check if single sentence is too long - need to split at clause level
                    try:
                        sentence_tokens = len(tokenizer.encode(sentence))
                    except Exception:  # noqa: BLE001
                        sentence_tokens = int(len(sentence.split()) * 1.8)
                    if sentence_tokens > max_tokens:
                        logger.debug(
                            "Sentence too long (%d tokens), splitting at clause boundaries",
                            sentence_tokens,
                        )
                        # Split long sentence at clause boundaries (commas)
                        clause_chunks = _split_at_clauses(sentence, max_tokens, tokenizer)
                        for clause_chunk in clause_chunks:
                            chunks.append(clause_chunk)
                            try:
                                clause_tokens = len(tokenizer.encode(clause_chunk))
                            except Exception:  # noqa: BLE001
                                clause_tokens = int(len(clause_chunk.split()) * 1.8)
                            logger.debug(
                                "Clause chunk: %d tokens",
                                clause_tokens,
                            )
                        continue
                else:
                    # Fallback to word/char counting
                    prospective_words = len(prospective_text.split())
                    prospective_chars = len(prospective_text)

                    if current_parts and (
                        (max_words is not None and prospective_words > max_words)
                        or (max_chars is not None and prospective_chars > max_chars)
                    ):
                        chunk = " ".join(current_parts).strip()
                        if chunk:
                            chunks.append(chunk)
                            logger.debug(
                                "Chunk created: %d words, %d chars",
                                len(chunk.split()),
                                len(chunk),
                            )
                        current_parts = []

                    # Check if single sentence exceeds limits
                    sentence_words = len(sentence.split())
                    sentence_chars = len(sentence)
                    if (
                        (max_words is not None and sentence_words > max_words)
                        or (max_chars is not None and sentence_chars > max_chars)
                    ):
                        logger.debug(
                            "Sentence too long (%d words), splitting at clause boundaries",
                            sentence_words,
                        )
                        # Split at clause boundaries
                        limit = max_words if max_words is not None else max_chars
                        clause_chunks = _split_at_clauses_fallback(sentence, limit, max_words is not None)
                        chunks.extend(clause_chunks)
                        continue

                current_parts.append(sentence)

            # Flush remaining parts
            if current_parts:
                chunk = " ".join(current_parts).strip()
                if chunk:
                    chunks.append(chunk)
                    if tokenizer is not None:
                        try:
                            actual_tokens = len(tokenizer.encode(chunk))
                        except Exception:  # noqa: BLE001
                            actual_tokens = int(len(chunk.split()) * 1.8)
                        logger.debug(
                            "Chunk created: %d tokens (%d words, %d chars)",
                            actual_tokens,
                            len(chunk.split()),
                            len(chunk),
                        )

    return [chunk for chunk in chunks if chunk]


def _split_sentences_fallback(text: str) -> List[str]:
    """Fallback regex-based sentence splitting when NLTK unavailable."""
    pattern = re.compile(r"[^.!?…]+[.!?…]?")
    sentences = [
        match.group().strip()
        for match in pattern.finditer(text)
        if match.group().strip()
    ]
    return sentences or [text.strip()]


def _split_at_clauses(sentence: str, max_tokens: int, tokenizer) -> List[str]:
    """Split a long sentence at clause boundaries (commas) respecting token limits."""
    # Split by commas
    clauses = [clause.strip() for clause in sentence.split(",") if clause.strip()]

    if len(clauses) == 1:
        # No commas, split by words as last resort
        words = sentence.split()
        chunks = []
        current_words = []
        for word in words:
            test_chunk = " ".join(current_words + [word])
            try:
                test_tokens = len(tokenizer.encode(test_chunk))
            except Exception:  # noqa: BLE001
                test_tokens = int(len(test_chunk.split()) * 1.8)
            if test_tokens > max_tokens and current_words:
                chunks.append(" ".join(current_words))
                current_words = [word]
            else:
                current_words.append(word)
        if current_words:
            chunks.append(" ".join(current_words))
        return chunks

    # Accumulate clauses respecting token limits
    chunks = []
    current_clauses = []

    for clause in clauses:
        # Add comma back except for first clause
        clause_with_punct = clause if not current_clauses else ", " + clause
        prospective = "".join(current_clauses) + clause_with_punct

        try:
            prospective_tokens = len(tokenizer.encode(prospective))
        except Exception:  # noqa: BLE001
            prospective_tokens = int(len(prospective.split()) * 1.8)

        if current_clauses and prospective_tokens > max_tokens:
            chunks.append("".join(current_clauses).strip())
            current_clauses = [clause]
        else:
            current_clauses.append(clause_with_punct)

    if current_clauses:
        chunks.append("".join(current_clauses).strip())

    return chunks


def _split_at_clauses_fallback(sentence: str, limit: int, use_words: bool) -> List[str]:
    """Split long sentence at clause boundaries for word/char fallback mode."""
    clauses = [clause.strip() for clause in sentence.split(",") if clause.strip()]

    if len(clauses) == 1:
        # Split by words
        words = sentence.split()
        chunks = []
        for start_idx in range(0, len(words), max(1, limit)):
            chunks.append(" ".join(words[start_idx : start_idx + limit]))
        return chunks

    chunks = []
    current_clauses = []

    for clause in clauses:
        clause_with_punct = clause if not current_clauses else ", " + clause
        prospective = "".join(current_clauses) + clause_with_punct

        size = len(prospective.split()) if use_words else len(prospective)
        if current_clauses and size > limit:
            chunks.append("".join(current_clauses).strip())
            current_clauses = [clause]
        else:
            current_clauses.append(clause_with_punct)

    if current_clauses:
        chunks.append("".join(current_clauses).strip())

    return chunks



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
