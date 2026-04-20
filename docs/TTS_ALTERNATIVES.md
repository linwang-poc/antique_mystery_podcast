# TTS Alternatives to VibeVoice

This document records evaluated TTS alternatives for the antique mystery podcast generator.
It exists because VibeVoice has an irreducible ~10% EOS mid-sentence truncation rate (architectural,
not fixable — Microsoft removed the source in 2025). When migrating off VibeVoice, start here.

---

## Why VibeVoice Has a Ceiling

VibeVoice uses a **single-pass encoder-decoder** architecture:
- Encoder ingests the **entire story text globally** at once
- Decoder generates audio autoregressively and can fire EOS mid-story (~10% of runs)
- The `fix-early-eos` fork (SanDiegoDude) reduced this from ~60% → ~10%, but cannot go lower
- Chunking does NOT work with VibeVoice: each chunk gets different global encoder context →
  voice drift, hallucinations, inter-segment artifacts

Modern TTS models are designed for chunked generation from the start — they maintain a
speaker embedding across chunks and stitch smoothly. EOS truncation is not a problem for them.

---

## Previously Tested (Before VibeVoice)

| Model | Notes |
|---|---|
| XTTS v2 | Tried. Configs in `config/voice_profiles/antique_mystery_voice_xtts.json` |
| F5-TTS | Tried. Configs in `config/voice_profiles/mystery_f5tts.json` |
| Chatterbox | Tried. Configs in `config/voice_profiles/mystery_grandfather_chatterbox.json` |

These were superseded by VibeVoice for quality reasons. Chatterbox has improved
significantly since testing (May 2025 release, improved since then).

---

## Primary Recommendation: Qwen3-TTS (January 2026)

**GitHub:** https://github.com/QwenLM/Qwen3-TTS  
**License:** Apache 2.0

### Why it fits this use case

- **Voice cloning from ~3 seconds** of reference audio (our `EdisonsGhostPhone.mp3` works)
- **Sentence-chunked generation by design** — EOS truncation is architecturally impossible
- **Runs on Colab free tier (T4 GPU)** — community notebooks confirm this
- **English quality** rated excellent for narration
- **Active development** — released January 2026, growing community

### Architecture (key difference from VibeVoice)

Qwen3-TTS processes text in segments (~80 words max per chunk). Each chunk:
1. Encodes the segment text with speaker embedding from reference audio
2. Generates audio for that segment
3. Stitches to previous chunk with silence at sentence/paragraph boundaries

Voice consistency across chunks is maintained by reusing the same speaker embedding.
This is how all modern long-form TTS models work.

### Ready-made Colab notebooks

| Notebook | URL | Notes |
|---|---|---|
| Voice cloning (one-click) | https://github.com/Myuniqous/qwen3-tts-voice-cloning-google-collab | Closest to our VibeVoice workflow |
| Audiobook converter | https://github.com/WhiskeyCoder/Qwen3-Audiobook-Converter | Purpose-built for long narration |
| Basic Colab | https://github.com/RedWilly/Qwen3-TTS-Colab | Simpler starting point |

### Migration plan from VibeVoice

1. **Use the same `EdisonsGhostPhone.mp3`** as voice reference (3–30 sec reference works)
2. **Text format**: Qwen3-TTS does NOT require `Speaker N:` labels. Pass plain paragraphs.
   - The `src/ui/transcriber.py` formatter adds Speaker labels — run story through it,
     then strip the `Speaker 0: ` prefixes before passing to Qwen3-TTS.
   - Or feed plain story text directly (skip the formatter entirely).
3. **Chunking**: Qwen3-TTS handles this internally. No manual chunking needed.
4. **No EOS buffer needed**: The buffer text in Cell [6] is not needed.
5. **No Whisper completeness check needed**: Chunked generation completes every segment.
6. **Ending snippet**: Step 6.5 (append `ending.mp3` via pydub) is unchanged.

### New notebook structure (when building)

| Step | Description | Change from VibeVoice |
|---|---|---|
| Step 1 | Check GPU | Same |
| Step 2 | Install Qwen3-TTS + dependencies | Replace VibeVoice pip install |
| Step 3 | Paste story text (plain paragraphs) | Remove Speaker labels, remove BUFFER_TEXT |
| Step 4 | Load voice reference | Same file (`EdisonsGhostPhone.mp3`) |
| Step 5 | Load Qwen3-TTS model | Replace VibeVoice model load |
| Step 6 | Generate (chunked automatically) | Simpler — no EOS workarounds |
| Step 6.5 | Append `ending.mp3` | Same as current |
| Step 7 | Download | Same |

### Key parameters to tune

- `max_words_per_segment`: 60–100 (lower = more consistent voice, higher = better prosody flow)
- `pause_between_segments_ms`: 300–600 (silence inserted between chunks)
- Silence at paragraph boundaries vs. sentence boundaries (configurable)

---

## Fallback Recommendation: IndexTTS-2 (September 2025)

**GitHub:** https://github.com/index-tts/index-tts  
**License:** Apache 2.0

### Why it's a strong fallback

- **Duration-controlled generation**: each segment has explicit time bounds, so EOS literally
  cannot fire at the wrong time — generation is time-gated, not token-gated
- **Extremely efficient**: 300 MB model vs VibeVoice's 5.4 GB
- **Industrial-grade reliability** (designed for production use)
- Voice cloning from 3–5 sec reference

### Limitation vs Qwen3-TTS

Less community tooling for Colab as of April 2026. ComfyUI wrappers exist
(billwuhao/ComfyUI_IndexTTS, snicolast/ComfyUI-IndexTTS2) but require more setup.

---

## Other Models (Lower Priority)

| Model | Cloning | Notes |
|---|---|---|
| **Fish Speech S2 Pro** | 10–30 sec | Best raw quality; Story Studio is cloud-dependent |
| **Chatterbox** (Resemble AI) | 5 sec | Already have configs; MIT; improved since testing |
| **Dia 1.6B** (ElevenLabs) | Yes | Apache 2.0; dialogue-focused; emotion/non-verbal sounds |
| **OuteTTS 1.0** | One-shot | DAC encoder; 150 tokens/sec; Apache 2.0 |

---

## Multi-model Tool

If evaluating multiple models, **tts-audiobook-tool** supports Qwen3-TTS, IndexTTS-2,
Chatterbox, Fish S2 Pro, and others with a unified chunking interface:
https://github.com/zeropointnine/tts-audiobook-tool

---

*Last updated: 2026-04-19*
