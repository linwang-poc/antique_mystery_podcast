from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.tts.tts_service import TTSService
from src.tts.voice_registry import VoiceRegistry
from src.ui.app import create_app


def main() -> None:
    _configure_logging(PROJECT_ROOT)
    registry = VoiceRegistry.from_directory(PROJECT_ROOT / "config" / "voice_profiles")
    service = TTSService(registry)

    if registry.default_id() is None:
        raise RuntimeError(
            "No voice profiles found. Add JSON files under config/voice_profiles/."
        )

    app = create_app(registry, service)
    app.launch()


def _configure_logging(root: Path) -> None:
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("chatterbox").setLevel(logging.WARNING)


if __name__ == "__main__":
    main()
