#!/usr/bin/env python3
"""
VibeVoice Text Formatter - Standalone Utility

This utility converts plain text into VibeVoice-compatible format by:
1. Adding "Speaker 0: " prefix to each paragraph
2. Normalizing line breaks (removing double breaks)
3. Removing extra spaces

Usage:
    python src/ui/transcriber.py
"""

import re
import gradio as gr


def format_for_vibevoice(raw_text: str) -> str:
    """
    Convert plain text into VibeVoice format with Speaker 0: prefixes.

    Args:
        raw_text: Raw story text with multiple paragraphs

    Returns:
        Formatted text with "Speaker 0: " prefixes and normalized spacing
    """
    if not raw_text or not raw_text.strip():
        return ""

    # Split into paragraphs (split on one or more newlines)
    paragraphs = re.split(r'\n+', raw_text)

    # Process each paragraph
    formatted_paragraphs = []
    for para in paragraphs:
        # Remove extra spaces (replace multiple spaces with single space)
        para = re.sub(r'\s+', ' ', para.strip())

        # Skip empty paragraphs
        if not para:
            continue

        # Add "Speaker 0: " prefix (with space after colon)
        formatted_para = f"Speaker 0: {para}"
        formatted_paragraphs.append(formatted_para)

    # Join with double newline for readability
    return "\n\n".join(formatted_paragraphs)


def create_ui():
    """Create Gradio interface for the text formatter."""

    with gr.Blocks(title="VibeVoice Text Formatter") as app:
        gr.Markdown("""
        # VibeVoice Text Formatter

        Convert plain mystery story text into VibeVoice-compatible format.

        ## How to use:
        1. Paste your raw story text in the input box below
        2. Click "Transcribe" to format the text
        3. Copy the formatted output to use in Google Colab

        ## What it does:
        - Adds `Speaker 0: ` prefix to each paragraph
        - Removes double line breaks
        - Removes extra spaces
        - Ensures proper formatting for VibeVoice processor
        """)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input (Plain Text)")
                input_text = gr.Textbox(
                    label="Raw Story Text",
                    placeholder="Paste your mystery story here...\n\nIt can have multiple paragraphs.\n\nWith double line breaks.",
                    lines=15,
                    max_lines=30
                )

                transcribe_btn = gr.Button("Transcribe", variant="primary", size="lg")

                gr.Markdown("""
                **Example input:**
                ```
                It was a fog-laden morning when I stumbled upon a peculiar bottle.


                The bottle's antiquity was evident, but it was the unsettling aura.

                This was no ordinary tonic.
                ```
                """)

            with gr.Column():
                gr.Markdown("### Output (VibeVoice Format)")
                output_text = gr.Textbox(
                    label="Formatted Text (Copy this to Colab)",
                    lines=15,
                    max_lines=30,
                    interactive=False,
                    show_copy_button=True
                )

                gr.Markdown("""
                **Formatted output:**
                ```
                Speaker 0: It was a fog-laden morning when I stumbled upon a peculiar bottle.

                Speaker 0: The bottle's antiquity was evident, but it was the unsettling aura.

                Speaker 0: This was no ordinary tonic.
                ```
                """)

        # Statistics display
        with gr.Row():
            input_stats = gr.Markdown("**Input:** 0 words, 0 paragraphs")
            output_stats = gr.Markdown("**Output:** 0 words, 0 paragraphs")

        def format_and_stats(text):
            """Format text and return statistics."""
            formatted = format_for_vibevoice(text)

            # Calculate statistics
            input_words = len(text.split()) if text else 0
            input_paras = len([p for p in re.split(r'\n+', text) if p.strip()]) if text else 0

            output_words = len(formatted.replace("Speaker 0:", "").split()) if formatted else 0
            output_paras = formatted.count("Speaker 0:") if formatted else 0

            input_stat_text = f"**Input:** {input_words:,} words, {input_paras} paragraph(s)"
            output_stat_text = f"**Output:** {output_words:,} words, {output_paras} paragraph(s)"

            return formatted, input_stat_text, output_stat_text

        # Connect button to formatting function
        transcribe_btn.click(
            fn=format_and_stats,
            inputs=[input_text],
            outputs=[output_text, input_stats, output_stats]
        )

        # Also format on text change (live preview)
        input_text.change(
            fn=format_and_stats,
            inputs=[input_text],
            outputs=[output_text, input_stats, output_stats]
        )

    return app


def main():
    """Launch the transcriber UI."""
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,  # Different port from main app (7860)
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
