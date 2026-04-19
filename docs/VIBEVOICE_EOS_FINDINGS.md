# VibeVoice EOS Truncation & Repetition Findings

Documented findings from extensive testing of VibeVoice audio generation, covering the EOS (End-of-Sequence) handling trade-offs and approaches explored.

---

## 1. The Truncation Problem

VibeVoice fires EOS early approximately **60% of the time** on stories of 500+ words, cutting off the ending of the generated audio. The model predicts end-of-sequence prematurely, resulting in incomplete narration. Shorter texts are less affected, but any story of meaningful length is unreliable with the default EOS behavior.

## 2. The fix-early-eos Fork

The [SanDiegoDude fork](https://github.com/SanDiegoDude/VibeVoice) delays EOS firing, which reduces truncation from ~60% down to roughly **~10%**. This is a significant improvement for completeness, but it introduces a new problem: end-of-audio repetition and garbage.

The fork uses a `pending_finish_tags` tensor to track samples that hit EOS but need to finish their current audio chunk. When EOS is detected, samples are marked as "pending finish" rather than terminated immediately. This lets audio generation complete the current chunk boundary before stopping, adding ~267ms of silence padding. A `TRIM_END_SECONDS` parameter allows trimming a fixed number of seconds from the end to remove trailing artifacts.

**vibevoice-community fork note:** PR #15 (`Force EOS token, pad audio`) was merged into the community fork. It modifies training data to explicitly append EOS tokens after speech output, and wraps audio with silence padding during training. This is a training-side fix that may improve EOS reliability in future model versions, but does not affect inference on the current `microsoft/VibeVoice-1.5B` weights.

## 3. The Repetition Problem

After delaying EOS with the fix-early-eos fork, the model sometimes **loops back and re-speaks the last sentence** in a hurried or garbled way, followed by noise or audio artifacts. This happens because the model, forced past its natural stopping point, has no new content to generate and falls into repetition.

Characteristics of the repetition artifact:
- The repeated sentence sounds rushed and lower quality than the original
- It may be followed by noise, static, or unintelligible audio
- The transition from good audio to repeated audio can be abrupt or gradual
- The artifact duration varies — sometimes 1-2 seconds, sometimes longer

## 4. Spontaneous Background Music

VibeVoice occasionally adds background music or ambient sound to generated audio. This is **not** caused by the reference voice file containing music. It is an intrinsic model behavior: certain words or phrases trigger the model to add musical elements spontaneously. The behavior is non-deterministic — the same input text may or may not produce music on different runs.

Mitigation:
- **Regenerate**: Re-running Step 6 usually produces music-free output on the next attempt.
- **Higher CFG_SCALE**: Increasing `CFG_SCALE` from 1.25 toward 1.5–2.0 enforces stricter text adherence and may reduce spontaneous creative additions.
- There is no reliable way to prevent music programmatically before generation.

## 5. Chunking Approach (Tested and Failed)

We tested splitting long texts into smaller chunks, generating audio for each chunk separately, then stitching the segments together. This approach **failed** due to multiple issues:

- **Overlapping audio**: Chunks produced audio that overlapped with adjacent segments
- **Foreign-language hallucinations**: Short chunks sometimes caused the model to hallucinate voices in other languages
- **Inter-segment garbage**: Stitched segments had audible artifacts at the boundaries
- **Inconsistent voice quality**: Voice characteristics drifted between chunks, breaking narration continuity

Chunking does not solve the fundamental EOS problem — it just creates many smaller instances of the same issue plus new stitching problems.

## 6. Automated Trim Approaches (Considered and Rejected)

Several automated approaches to detect and remove the trailing repetition/garbage were evaluated. None are reliable enough on their own:

### Energy / RMS Detection
The trailing garbage is **actual audio** (speech and noise), not silence. Energy-based thresholds cannot distinguish between legitimate narration and the garbled repetition — both have similar amplitude and spectral characteristics.

### Expected Duration Estimation / Completion Ratio
Estimating how long the audio "should" be based on word count or text length is **fundamentally unreliable**. VibeVoice generation is stochastic — speaking rate varies significantly between runs. A "short" audio could mean the voice ran slower, or it could mean EOS fired early. These two cases are indistinguishable from duration alone, so any `completion_ratio = actual / expected` logic produces false positives and false negatives. Worse, trimming a truncated audio based on word proportion makes it even shorter — cutting mid-sentence.

### Silence-Gap Detection
The repeated sentence often **overlays the original ending with minimal or no silence gap**. The model transitions directly from the legitimate final sentence into the repeated version without a clean break, so silence detection cannot reliably find the boundary.

### Spectral / Quality Analysis
While the repeated audio is lower quality, the degradation is gradual and inconsistent. Building a robust classifier for "garbled vs. legitimate" speech would require significant effort and training data, with no guarantee of reliability across different texts and voice profiles.

## 7. Current Best Recommendation

### Option A: fix-early-eos Fork + Outro Buffer + Whisper ASR Check (Recommended)

Implemented in the current notebook (`vibevoice_colab_0216_2026_ipynb.ipynb`):

**Step 1 — Buffer text (EOS protection):**
Append a short outro `BUFFER_TEXT` (Speaker 0 lines, ~40 words) after the real story. The outro is natural-sounding podcast sign-off text ("Thank you for listening…"). EOS fires near the end of text; the buffer gives it a safe zone to fire in, preserving all real story content. If the buffer is narrated, it sounds like a natural outro. `FULL_STORY = MYSTERY_STORY + BUFFER_TEXT` is used as the model input.

**Step 2 — Whisper ASR completeness check (Step 6.2):**
After generation, transcribe the last 90 seconds using `whisper` (base model, CPU). Extract 6 distinctive words (length ≥6, stopwords excluded) from the final paragraph of `MYSTERY_STORY`. Check how many appear in the transcript.

- **≥ threshold matches** from last paragraph → **COMPLETE** — apply fixed `TRIM_END_SECONDS` (default 3s) tail trim to remove repetition artifact
- Matches from second-to-last paragraph but not last → **INCOMPLETE** (final paragraph missing) — no trim, regenerate
- Neither → **TRUNCATED** — no trim, regenerate

**Why ASR beats duration estimation:** Whisper asks "was this content spoken?" rather than "was the audio long enough?" — it is immune to speaking-rate variation. Trim only activates when completeness is confirmed, so truncated audio is never made shorter.

**Combined reliability:** The buffer reduces the ~10% failure rate of the fork by pushing EOS further past the real content. Whisper catches the remaining cases and tells the user exactly what to do.

### Option B: Default VibeVoice + Re-runs
Use the community/default fork and accept occasional truncation:
- Simpler setup, no fork dependency
- Re-run generation when truncation occurs (may need 2-3 attempts)
- No repetition artifacts to deal with
- Better suited for short texts where truncation is less frequent

### Future Considerations
- Monitor VibeVoice upstream for EOS handling improvements (vibevoice-community PR #15 is a training-side fix that may improve future model weights)
- If the model receives updates to its EOS logic, re-evaluate whether the fork is still necessary
- For production workflows, build in a manual QA step after generation regardless of approach
