from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional

import gradio as gr

from src.document.parser import DocumentParser
from src.tts.tts_service import TTSService
from src.tts.voice_registry import VoiceRegistry

logger = logging.getLogger(__name__)


def create_app(registry: VoiceRegistry, service: TTSService) -> gr.Blocks:
    parser = DocumentParser()
    voice_choices = [
        (profile.display_name, profile.id) for profile in registry.list_profiles()
    ]
    default_voice = registry.default_id()
    if default_voice is None and voice_choices:
        default_voice = voice_choices[0][1]

    def handle_generate(
        story_text: str,
        story_file: Optional[gr.File],
        voice_id: str,
        desired_name: str,
        progress=gr.Progress(track_tqdm=False),
    ) -> str:
        docx_path: Optional[Path] = None
        if story_file is not None and getattr(story_file, "name", None):
            docx_path = Path(story_file.name)

        active_voice = voice_id or default_voice
        if not active_voice:
            raise gr.Error("Please create a voice profile before generating audio.")

        try:
            text, warning = parser.extract(story_text or "", docx_path)

            def notifier(value: float, message: str) -> None:
                progress(value, desc=message)

            filename_hint = _sanitize_filename(desired_name)
            output_path = service.generate_episode(
                text, active_voice, title_hint=filename_hint, notify=notifier
            )
            if warning:
                progress(1.0, desc=warning)
            return str(output_path.resolve())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate narration.")
            raise gr.Error(f"Generation failed: {exc}") from exc

    with gr.Blocks(title="Antique Mystery Narrator", theme=gr.themes.Soft(primary_hue="slate").set(
        body_background_fill="*neutral_950",
        body_background_fill_dark="*neutral_950",
        background_fill_primary="*neutral_900",
        background_fill_primary_dark="*neutral_900",
        background_fill_secondary="*neutral_800",
        block_background_fill="*neutral_900",
        block_label_background_fill="*neutral_900",
        input_background_fill="*neutral_800",
        body_text_color="*neutral_50",
        body_text_color_subdued="*neutral_200",
        block_label_text_color="*neutral_100",
        input_text_color="*neutral_50",
    )) as demo:
        gr.Markdown(
            "## Antique Mystery Narrator\n"
            "Provide your story text or upload a Word document, then choose a narrator voice."
        )
        with gr.Row():
            voice = gr.Dropdown(
                choices=voice_choices,
                value=default_voice,
                label="Narrator Voice",
                scale=3,
            )
            doc_input = gr.File(
                label="Upload .docx (optional)",
                file_types=[".docx"],
                scale=1,
            )
        filename_box = gr.Textbox(
            label="Output Name (optional)",
            placeholder="e.g., Haunted_Auction_Narration",
            lines=1,
        )
        story = gr.Textbox(
            label="Story Text",
            lines=12,
            placeholder="Paste your mystery story here...",
        )
        with gr.Row():
            generate_btn = gr.Button("Generate Podcast", variant="primary")
            exit_btn = gr.Button("Exit", variant="stop")

        output_file = gr.File(label="Download Narration", interactive=False, file_count="single")

        generate_btn.click(
            handle_generate,
            inputs=[story, doc_input, voice, filename_box],
            outputs=[output_file],
        )

        def handle_exit():
            logger.info("Exit button pressed. Shutting down application.")
            os._exit(0)

        exit_btn.click(handle_exit)

    return demo


def _sanitize_filename(value: str) -> Optional[str]:
    if not value:
        return None
    cleaned = re.sub(r"[^0-9A-Za-z ]+", "", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return None
    return cleaned.replace(" ", "_")
