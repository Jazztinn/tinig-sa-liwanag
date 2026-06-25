# Evaluation Report

## Current status

This hackathon version evaluates a **dictionary baseline** on a 30-row seed
benchmark for English, Filipino, and code-switched text into Hiligaynon.

The benchmark rows are marked `seed_unverified`. They are useful for showing the
workflow and failure modes, but they are not gold data until reviewed by native
Hiligaynon speakers.

## Reproduce

```bash
python3 scripts/validate.py --kind translation --dir data/benchmark
python3 scripts/generate_baseline_predictions.py
python3 scripts/evaluate_translation.py \
  --refs data/benchmark/hil_translation_v1.jsonl \
  --preds data/predictions/translation_baseline_dict.jsonl
```

## What is evaluated

The current evaluator reports:

- coverage
- exact match after normalization
- token F1
- chrF-style character n-gram F-score
- per-domain averages

These metrics are only a scaffold. Hiligaynon translation quality still needs
human review for adequacy, fluency, context preservation, and terminology.

## Baseline being tested

`dict-baseline` uses `scripts/translate_hil.py` with the local Hiligaynon
lexicon. It translates known words and marks unknown terms with `*word*`.

This is intentionally weak. Its purpose is to prove that word-level translation
is insufficient for context-aware Hiligaynon translation.

## Current generated result

Latest local run:

| Model | References | Predictions | Coverage | Exact match | Token F1 | chrF |
|-------|------------|-------------|----------|-------------|----------|------|
| dict-baseline | 30 | 30 | 100.0% | 0.0% | 30.9% | 34.7% |

The result is useful because it makes the failure visible: even with complete
prediction coverage, the baseline does not produce exact contextual translations.

## Expected failure modes

- unknown words are copied as `*word*`
- grammar and word order are not repaired
- context is ignored
- pronoun references are not resolved
- tense/aspect is not handled reliably
- idioms and local expressions are not translated naturally
- code-switched sentences remain fragmented
- public-service, education, and health terminology need reviewer decisions

## Human review needed

Before this can become a real benchmark:

1. A native Hiligaynon reviewer should edit or reject each `reference_translation`.
2. A second reviewer should check a subset for agreement.
3. Rows should move from `seed_unverified` to `reviewed`.
4. Disagreements should be adjudicated and marked `adjudicated`.
5. The final test split should be frozen before model tuning.

## Why this is still a valid MVP

In a two-hour hackathon, the team cannot honestly claim a production model or a
gold Hiligaynon dataset without speaker validation. The MVP instead delivers the
reproducible infrastructure:

- benchmark schema
- seed benchmark rows
- baseline generation
- automatic scoring
- demo app
- clear path to human validation and later STT/TTS work
