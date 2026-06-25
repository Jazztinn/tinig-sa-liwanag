# Extension subsets

Subsets kept **separate** from the headline `scripted_native` benchmark. Stored
here — not in `data/annotations/` — so they never enter the headline WER or the
standard `score.py` / `run_whisper.py` runs.

| Subset | Dir | Clips | Status |
|--------|-----|-------|--------|
| `scripted_native` extension | `scripted_native_spk2/` | 40 | Native speaker, clean WAV shape, reviewed transcript/tags, Whisper baseline generated |
| `non_native_eval` planned set | `non_native_eval/` | 20 planned | Local recording scaffold; no checked-in audio yet; robustness only |

## Speaker 2 extension

- `scripted_native_spk2/` contains a second native-speaker recording set.
- WAV files are mono 16 kHz and durations are populated.
- Transcripts come from the elicitation script.
- Per-word language tags are reviewed.
- Bundled Whisper predictions are available under
  `scripted_native_spk2/predictions/`.
- Keep this subset out of the frozen headline benchmark unless the team decides
  to publish a multi-speaker benchmark version.

## Non-native evaluation scaffold

- `non_native_eval/` contains a 20-line manifest and recording script for a
  consented non-native speaker.
- No external YouTube/podcast/vlog audio is checked in for this subset.
- Current status is planned-only: 20 prompts, 0 audio files, 0 annotations.
- Use `scripts/validate_non_native_eval.py` to check readiness.
- **Never** count `non_native_eval` toward the native headline benchmark — it is
  a robustness / stress-test subset only.
- Score only after audio is recorded, transcripts are reviewed, per-word tags are
  reviewed, and consent/provenance are documented.
