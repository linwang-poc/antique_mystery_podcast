from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

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
        progress=gr.Progress(track_tqdm=False),
    ) -> Tuple[Optional[Path], str]:
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

            output_path = service.generate_episode(text, active_voice, notify=notifier)
            if warning:
                progress(1.0, desc=warning)
            return (str(output_path.resolve()),)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate narration.")
            raise gr.Error(f"Generation failed: {exc}") from exc

    with gr.Blocks(title="Antique Mystery Narrator") as demo:
        gr.Markdown(
            "## Antique Mystery Narrator\n"
            "Provide your story text or upload a Word document, then choose a narrator voice."
        )
        with gr.Row():
            voice = gr.Dropdown(
                choices=voice_choices,
                value=default_voice,
                label="Narrator Voice",
            )
            doc_input = gr.File(
                label="Upload .docx (optional)",
                file_types=[".docx"],
            )
        story = gr.Textbox(
            label="Story Text",
            lines=12,
            placeholder="Paste your mystery story here...",
        )
        generate_btn = gr.Button("Generate Podcast")

        output_file = gr.File(label="Download Narration", interactive=False, file_count="single")

        generate_btn.click(
            handle_generate,
            inputs=[story, doc_input, voice],
            outputs=[output_file],
        )

    return demo
