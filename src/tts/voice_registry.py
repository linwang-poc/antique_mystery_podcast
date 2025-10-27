from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VoiceProfile:
    id: str
    display_name: str
    reference_mp3: Path
    params: Dict[str, Any]
    description: Optional[str] = None
    engine: str = "chatterbox"
    chunk_max_words: Optional[int] = None
    chunk_max_chars: Optional[int] = None
    reference_text: Optional[str] = None
    split_sentences: bool = False

    @property
    def safe_reference(self) -> Path:
        return self.reference_mp3.expanduser().resolve()


class VoiceRegistry:
    def __init__(self, profiles: Dict[str, VoiceProfile]) -> None:
        self._profiles = profiles

    @classmethod
    def from_directory(cls, directory: Path) -> "VoiceRegistry":
        profiles: Dict[str, VoiceProfile] = {}
        directory.mkdir(parents=True, exist_ok=True)
        for path in sorted(directory.glob("*.json")):
            profile = _load_profile(path)
            profiles[profile.id] = profile
            logger.info("Loaded voice profile '%s' from %s", profile.id, path)
        if not profiles:
            logger.warning("No voice profiles found in %s", directory)
        return cls(profiles)

    def list_profiles(self) -> Iterable[VoiceProfile]:
        return self._profiles.values()

    def get(self, profile_id: str) -> VoiceProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise ValueError(f"Voice profile '{profile_id}' not found") from exc

    def default_id(self) -> Optional[str]:
        return next(iter(self._profiles), None)


def _load_profile(path: Path) -> VoiceProfile:
    data = json.loads(path.read_text())
    profile_id = data["id"]
    reference = Path(data["reference_mp3"])
    if not reference.exists():
        alt = path.parent.parent.parent / reference
        if alt.exists():
            reference = alt
        else:
            logger.warning(
                "Reference audio %s for profile %s does not exist.", reference, profile_id
            )
    chunk_settings = data.get("chunking", {})
    chunk_max_words = _parse_optional_int(
        chunk_settings.get("max_words"), profile_id, "max_words"
    )
    chunk_max_chars = _parse_optional_int(
        chunk_settings.get("max_chars"), profile_id, "max_chars"
    )
    return VoiceProfile(
        id=profile_id,
        display_name=data.get("display_name", profile_id),
        description=data.get("description"),
        reference_mp3=reference,
        params=data.get("params", {}),
        engine=data.get("engine", "chatterbox"),
        chunk_max_words=chunk_max_words,
        chunk_max_chars=chunk_max_chars,
        reference_text=data.get("reference_text"),
        split_sentences=bool(data.get("split_sentences", False)),
    )


def _parse_optional_int(value: Optional[object], profile_id: str, field: str) -> Optional[int]:
    if value is None:
        return None
    try:
        integer = int(value)
    except (TypeError, ValueError):
        logger.warning(
            "Ignoring non-integer chunking value '%s' for %s in profile %s",
            value,
            field,
            profile_id,
        )
        return None
    if integer <= 0:
        logger.info(
            "Chunking value %s=%s in profile %s treated as unlimited.",
            field,
            value,
            profile_id,
        )
        return None
    return integer
