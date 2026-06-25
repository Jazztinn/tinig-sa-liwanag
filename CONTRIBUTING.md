# Contributing to Sugidanon

Thanks for contributing to an open Hiligaynon code-switch ASR benchmark.

## Quick orientation

Core benchmark tooling is **stdlib-only** (no install). Before anything else, verify the baseline reproduces on your machine:

```bash
python3 scripts/validate.py --kind asr --dir data/annotations
python3 score.py --ref data/annotations --hyp data/predictions
python3 scripts/freeze_benchmark.py --verify
python3 -m unittest discover -s tests
```

All four commands should pass cleanly.

## Adding annotation clips

1. Write or receive the elicitation sentence and draft per-word token/lang tags.
2. Record audio with `scripts/record.py --prompt N` or supply a pre-recorded WAV.
3. Run `scripts/review_annotations.py --only <clip_id>` to approve/edit lang tags in the terminal.
4. Set `"lang_tags_status": "reviewed"` and `"gold_status": "native_gold"` only after a qualified native Hiligaynon speaker has confirmed the tags — AI output must not be marked as gold.
5. Run `python3 scripts/validate.py --kind asr --dir data/annotations` to confirm schema compliance.
6. Re-run the freeze gate: `python3 scripts/freeze_benchmark.py` (writes new hashes) then commit both the new clip(s) and the updated `data/benchmark/MANIFEST.json`.
7. New extension clips (non-headline) go into `data/extensions/` and are never blended into the headline WER.

## Running / updating the ASR baseline

```bash
# requires: pip install openai-whisper torch
python3 scripts/run_whisper.py --model small --language tl
python3 score.py --ref data/annotations --hyp data/predictions --ci
```

Headline predictions live in `data/predictions/`. New baseline runs are optional additions; do not overwrite the frozen headline predictions unless intentionally cutting a new benchmark version.

## Running the web app

```bash
npm install
npm run dev   # http://localhost:3000
```

Refresh the explorer's static data after any annotation change:

```bash
python3 scripts/build_benchmark_web.py
```

## Running the full release pipeline

```bash
python3 scripts/build_release.py --overwrite
```

This validates, scores, refreshes web data, and builds a release package in `release/`.

## Conventions

- Core benchmark scripts must stay **stdlib-only** (no third-party imports in `score.py`, `validate.py`, `freeze_benchmark.py`, `build_release.py`).
- Per-word `lang` tags are `hil` / `tl` / `en` (lowercase). New tags require human review before `lang_tags_status` is set to `"reviewed"`.
- Hiligaynon references stay `seed_unverified` until a native speaker confirms them. AI output is never language gold.
- Subsets (`scripted_native`, `scripted_native_spk2`, `non_native_eval`) must never be blended into a single WER in reporting.
- Keep canonical headline numbers consistent across README, `BENCHMARK.md`, `docs/evaluation_report.md`, the Colab, and the landing page. Source of truth: `results/asr_score.txt`.
- Record provenance and license for any third-party data in `docs/source_ledger.md`.
- Never commit secrets, API keys, or audio from unconsented speakers.

## Speaker consent and ethics

Every contributor speaker must provide informed consent before recording. See the privacy section in `README.md` and `docs/licensing.md`. Consent is a prerequisite — not an afterthought.

## Code style

Python code follows standard PEP 8. No external formatters are required. Keep functions small and type-annotated where practical. Tests live in `tests/`.
