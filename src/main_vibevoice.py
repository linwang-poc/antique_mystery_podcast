#!/usr/bin/env python3
"""
VibeVoice Mystery Narrator - Combined UI

Production Gradio application combining text formatter and VibeVoice generator
in a single interface for mystery podcast production.
"""

import os
import sys
import gradio as gr
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules
from ui.transcriber import format_for_vibevoice
from vibevoice.generator import VibeVoiceGenerator


def create_combined_app():
    """Create multi-tab Gradio app with Transcriber + VibeVoice Generator"""

    # Initialize VibeVoice generator (loads model on startup)
    print("\n" + "="*60)
    print("INITIALIZING VIBEVOICE MYSTERY NARRATOR")
    print("="*60 + "\n")

    try:
        generator = VibeVoiceGenerator(
            model_name="microsoft/VibeVoice-1.5B",
            cache_dir="/models",
            device="cuda",
            inference_steps=15
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize VibeVoice generator: {e}")
        print("\nStarting UI anyway (generator will be unavailable)")
        generator = None

    with gr.Blocks(
        title="VibeVoice Mystery Narrator",
        theme=gr.themes.Soft()
    ) as app:

        gr.Markdown("""
        # 🎙️ VibeVoice Mystery Narrator - Production System

        **Convert mystery stories into professional podcast narration using AI voice cloning**
        """)

        with gr.Tabs():
            # ========================================
            # Tab 1: Text Formatter (Transcriber)
            # ========================================
            with gr.Tab("📝 1. Format Text"):
                gr.Markdown("""
                ## Step 1: Prepare Your Story Text

                Convert plain mystery story text into VibeVoice-compatible format.

                **VibeVoice requires `Speaker 0:` format for all text!**
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

                        format_btn = gr.Button(
                            "🔄 Format for VibeVoice",
                            variant="primary",
                            size="lg"
                        )

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
                        formatted_text = gr.Textbox(
                            label="Formatted Text (Copy this for Step 2)",
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
                    """Format text and return statistics"""
                    import re

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
                format_btn.click(
                    fn=format_and_stats,
                    inputs=[input_text],
                    outputs=[formatted_text, input_stats, output_stats]
                )

                # Live preview on text change
                input_text.change(
                    fn=format_and_stats,
                    inputs=[input_text],
                    outputs=[formatted_text, input_stats, output_stats]
                )

            # ========================================
            # Tab 2: VibeVoice Generator
            # ========================================
            with gr.Tab("🎧 2. Generate Audio"):
                if generator is None:
                    gr.Markdown("""
                    ## ⚠️ Generator Unavailable

                    The VibeVoice generator failed to initialize. Check logs for details.
                    """)
                else:
                    gr.Markdown("""
                    ## Step 2: Generate Mystery Narration

                    Provide formatted text (from Step 1) and optional voice reference to generate podcast audio.
                    """)

                    with gr.Row():
                        story_text = gr.Textbox(
                            label="Story Text (Must use 'Speaker 0:' format from Step 1)",
                            placeholder="Speaker 0: It was a dark and stormy night...\n\nSpeaker 0: The fog rolled in from the harbor...",
                            lines=12,
                            max_lines=25
                        )

                    with gr.Row():
                        with gr.Column():
                            voice_file = gr.Audio(
                                label="Voice Reference (Optional, 5-15 seconds, MP3/WAV)",
                                type="filepath"
                            )

                            gr.Markdown("""
                            **Voice Cloning Tips:**
                            - 5-15 seconds of clean audio
                            - No background noise
                            - Natural speaking tone
                            - Leave empty for default voice
                            """)

                        with gr.Column():
                            cfg_scale = gr.Slider(
                                minimum=1.0,
                                maximum=2.0,
                                value=1.3,
                                step=0.1,
                                label="CFG Scale (1.0=creative, 2.0=strict)"
                            )

                            speed_factor = gr.Slider(
                                minimum=0.5,
                                maximum=1.5,
                                value=0.9,
                                step=0.05,
                                label="Speed Factor (0.5=slow, 1.5=fast)"
                            )

                            add_ending = gr.Checkbox(
                                label="Add Ending Snippet",
                                value=True,
                                info="Append ending.mp3 with 1.5s silence gap"
                            )

                    with gr.Row():
                        output_name = gr.Textbox(
                            label="Output Filename (optional, auto-generated if empty)",
                            placeholder="my_mystery_podcast",
                            value=""
                        )

                        generate_btn = gr.Button(
                            "🎬 Generate Podcast",
                            variant="primary",
                            size="lg"
                        )

                    with gr.Row():
                        progress_text = gr.Textbox(
                            label="Generation Progress",
                            lines=8,
                            interactive=False,
                            show_label=True
                        )

                    with gr.Row():
                        output_audio = gr.Audio(
                            label="Generated Narration (Download below)",
                            type="filepath",
                            show_download_button=True
                        )

                    def handle_generate(text, voice_path, cfg, speed, add_end, name):
                        """Generate audio and return file path with progress updates"""
                        try:
                            if not text or not text.strip():
                                return None, "❌ Error: Please provide story text"

                            # Validate speaker format
                            if "Speaker 0:" not in text and "speaker 0:" not in text:
                                return None, "❌ Error: Text must use 'Speaker 0:' format!\n\nUse Step 1 (Format Text tab) to format your text first."

                            progress_msg = "⏳ Starting generation...\n"
                            progress_msg += f"Text length: {len(text)} characters\n"
                            progress_msg += f"Word count: {len(text.split())} words\n"
                            progress_msg += f"CFG scale: {cfg}\n"
                            progress_msg += f"Speed factor: {speed}\n"
                            progress_msg += f"Voice reference: {'Yes' if voice_path else 'Default voice'}\n"
                            progress_msg += f"Add ending: {'Yes' if add_end else 'No'}\n\n"
                            progress_msg += "🎬 Generating audio... (this may take several minutes)\n"
                            progress_msg += "Progress will be shown in container logs.\n"

                            output_path = generator.generate(
                                text=text,
                                voice_reference=voice_path,
                                cfg_scale=cfg,
                                voice_speed_factor=speed,
                                add_ending=add_end,
                                output_name=name if name else None
                            )

                            success_msg = progress_msg + "\n" + "="*60 + "\n"
                            success_msg += "✅ GENERATION COMPLETE!\n"
                            success_msg += "="*60 + "\n"
                            success_msg += f"✓ Output file: {output_path.name}\n"
                            success_msg += f"✓ File size: {output_path.stat().st_size / 1e6:.1f} MB\n"
                            success_msg += f"✓ Location: {output_path}\n\n"
                            success_msg += "🎧 Play audio above or download using the button.\n"

                            return str(output_path), success_msg

                        except ValueError as e:
                            # Format validation errors
                            error_msg = f"❌ Validation Error:\n\n{str(e)}\n\n"
                            error_msg += "💡 Tip: Use Step 1 (Format Text tab) to properly format your text."
                            return None, error_msg

                        except Exception as e:
                            error_msg = f"❌ Generation Error:\n\n{str(e)}\n\n"
                            error_msg += "Check container logs for detailed error information."
                            return None, error_msg

                    generate_btn.click(
                        fn=handle_generate,
                        inputs=[story_text, voice_file, cfg_scale, speed_factor, add_ending, output_name],
                        outputs=[output_audio, progress_text]
                    )

            # ========================================
            # Tab 3: Help & Documentation
            # ========================================
            with gr.Tab("📖 Help"):
                gr.Markdown("""
                ## How to Use This Application

                ### Workflow

                1. **Format Text (Tab 1)**
                   - Paste your raw mystery story text
                   - Click "Format for VibeVoice"
                   - Copy the formatted output

                2. **Generate Audio (Tab 2)**
                   - Paste formatted text from Step 1
                   - (Optional) Upload voice reference for cloning
                   - Adjust CFG scale and speed
                   - Click "Generate Podcast"
                   - Wait for generation (6 minutes per minute of audio)
                   - Download the final MP3

                ### Text Format Requirements

                **VibeVoice requires `Speaker N:` format!**

                ✅ **Correct:**
                ```
                Speaker 0: It was a dark and stormy night.

                Speaker 0: The detective entered the room.
                ```

                ❌ **Incorrect:**
                ```
                It was a dark and stormy night.

                NARRATOR: The detective entered the room.
                ```

                ### Voice Reference Guidelines

                - **Length**: 5-15 seconds ideal
                - **Quality**: Clean audio, no background noise
                - **Content**: Natural speaking, not shouting/whispering
                - **Format**: MP3 or WAV
                - **Optional**: Leave empty to use default VibeVoice voice

                ### Generation Parameters

                - **CFG Scale**: 1.0=more creative, 2.0=stricter text adherence (default: 1.3)
                - **Speed Factor**: 0.5=very slow, 1.5=very fast (default: 0.9 for mystery pacing)
                - **Add Ending**: Appends `ending.mp3` with 1.5 second silence gap

                ### Estimated Generation Time

                - 5-minute story: ~30 minutes
                - 10-minute story: ~60 minutes
                - 20-minute story: ~2 hours

                **Performance**: ~0.15x real-time (6 minutes to generate 1 minute of audio)

                ### System Requirements

                - GPU with 12GB+ VRAM (RTX 3090, RTX 4090, A100)
                - CUDA 12.1+
                - Docker with NVIDIA Container Toolkit

                ### Troubleshooting

                **"No valid speaker lines found"**
                - Use Step 1 to format your text first
                - Ensure all paragraphs start with `Speaker 0:`

                **"Generation taking too long"**
                - This is normal! Be patient.
                - Check container logs: `docker logs vibevoice-mystery-narrator`

                **"GPU out of memory"**
                - Reduce inference steps (5 instead of 15)
                - Split very long stories into chapters

                ### Support

                For issues, check:
                - Container logs: `docker logs vibevoice-mystery-narrator`
                - GitHub repository: antique_mystery_podcast
                - VibeVoice documentation: https://github.com/vibevoice-community/VibeVoice
                """)

        return app


def main():
    """Launch the combined Gradio application"""
    app = create_combined_app()

    # Launch configuration
    app.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,        # Standard Gradio port
        share=False,             # Don't create public link
        inbrowser=False,         # Don't auto-open browser (containerized)
        show_error=True          # Show errors in UI
    )


if __name__ == "__main__":
    main()
