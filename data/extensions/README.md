# Extension subsets

Subsets kept **separate** from the headline `scripted_native` benchmark. Stored
here — not in `data/annotations/` — so they never enter the headline WER or the
standard `score.py` / `run_whisper.py` runs.

| Subset | Dir | Clips | Status |
|--------|-----|-------|--------|
| `scripted_native` candidate | `scripted_native_spk2/` | 40 | Native speaker, clean WAV shape, transcript and token tags reviewed |

## Speaker 2 candidate

- `scripted_native_spk2/` contains a second native-speaker recording set.
- WAV files are mono 16 kHz and durations are populated.
- Transcripts come from the elicitation script.
- Per-word language tags are reviewed.
- Keep this subset out of the headline benchmark until baseline predictions are
  generated and a multi-speaker reporting decision is made.

## Non-native candidate rules

- Non-native, podcast, vlog, or other external-source clips are not checked in
  here unless redistribution rights are fully documented.
- **Never** count `non_native_eval` toward the native headline benchmark — it is
  a robustness / stress-test subset only.
- Source rights and redistribution status are not release-ready. Fill exact
  title, URL, license/permission, and redistribution terms in
  `docs/source_ledger.md` before publishing or packaging this subset.
- Per-word language tags and transcripts must be reviewed before scoring.
- Clip IDs should record the source format (`podcast_`, `vlog_`, etc.), while
  `subset` should remain `non_native_eval`.
