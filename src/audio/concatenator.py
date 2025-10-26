from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pydub import AudioSegment


def merge_segments(
    narration_segments: Iterable[AudioSegment], ending_path: Path
) -> AudioSegment:
    result = AudioSegment.silent(duration=0)
    for segment in narration_segments:
        result += segment

    if ending_path.exists():
        ending = AudioSegment.from_file(ending_path)
        result += ending
    return result
