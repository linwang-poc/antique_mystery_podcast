from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

from docx import Document

logger = logging.getLogger(__name__)


class DocumentParser:
    def extract(self, raw_text: str, docx_path: Optional[Path]) -> Tuple[str, Optional[str]]:
        text_parts = []
        warning = None

        cleaned_raw = raw_text.strip()
        if cleaned_raw:
            text_parts.append(cleaned_raw)

        if docx_path:
            text_parts.append(self._read_docx(docx_path))
            logger.info("Loaded .docx file: %s", docx_path)

        combined = "\n\n".join(part for part in text_parts if part)
        if not combined:
            raise ValueError("No story text provided.")

        if len(combined) > 10000:
            warning = (
                "This story is quite long. Rendering on an 8GB MacBook Air may take several minutes."
            )
            logger.warning("Story length %d characters may strain memory.", len(combined))
        else:
            logger.info("Story length: %d characters.", len(combined))
        return combined, warning

    def _read_docx(self, path: Path) -> str:
        document = Document(path)
        paragraphs = [para.text.strip() for para in document.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
