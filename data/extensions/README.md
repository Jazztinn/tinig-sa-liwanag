# Extension subsets (robustness)

Subsets kept **separate** from the headline `scripted_native` benchmark. Stored
here — not in `data/annotations/` — so they never enter the headline WER or the
standard `score.py` / `run_whisper.py` runs.

| Subset | Dir | Clips | Status |
|--------|-----|-------|--------|
| `non_native_eval` | `non_native_eval/` | 20 | Whisper-seeded, `not_native_gold` |

## Status and rules

- These clips are **non-native** Hiligaynon speech (podcast + vlog origin).
  `gold_status: not_native_gold`, `speaker.fluency: non_native`.
- **Never** count `non_native_eval` toward the native headline benchmark — it is
  a robustness / stress-test subset only.
- Transcripts are **Whisper-seeded drafts**, not gold (`seed_unverified`).
- Per-word language tags are **not set** (`tokens[].lang = null`) — review
  required before scoring.
- Source rights: YouTube, confirmed by Team Hague. Fill exact title/URL in
  `docs/source_ledger.md`.
- Some clips (`vlog_001`, `vlog_003`, `vlog_010`) fall on music/intro and should
  be dropped on review (no-music policy, `SCHEMA.md`).
- Audio is mono 16 kHz WAV, segmented to 5-15s on silence boundaries.

`clip_id` prefixes (`podcast_`, `vlog_`) record the original source format;
the subset is `non_native_eval` for all.
