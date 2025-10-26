from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VoiceProfile:
    id: str
    display_name: str
    reference_mp3: Path
    params: Dict[str, float]
    description: Optional[str] = None

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
    reference = Path(data["reference_mp3"])
    if not reference.exists():
        alt = path.parent.parent.parent / reference
        if alt.exists():
            reference = alt
        else:
            logger.warning(
                "Reference audio %s for profile %s does not exist.", reference, data["id"]
            )
    return VoiceProfile(
        id=data["id"],
        display_name=data.get("display_name", data["id"]),
        description=data.get("description"),
        reference_mp3=reference,
        params=data.get("params", {}),
    )
