# Evaluation Report

## Code-switch ASR benchmark (speech MVP)

The speech deliverable: **40 native-recorded code-switch clips** (3.0 min total),
one Hiligaynon speaker, 8 domains (market, transport, school/work, family,
health, culture, everyday, oral tradition), 4 switch types (`HIL`=11, `HIL+EN`=17,
`HIL+TL`=7, `HIL+TL+EN`=5). Reference text and per-word language tags were
reviewed by a Hiligaynon speaker.

### Headline baseline result — Whisper small, `--language tl`

| Metric | WER |
|--------|-----|
| Overall | 57.4% |
| Monolingual (pure Hiligaynon) | 65.9% |
| Switch-region (next to a language switch) | 35.8% |
| **Switch penalty** (switch − mono) | **−30.1%** |

Switch-region WER by language pair: `hil↔en` 40.0%, `hil↔tl` 24.4%, `tl↔en` 6.2%.

### Additional benchmark dimensions

The benchmark now reports more than code-switch proximity. The generated
breakdown report covers:

- speaker robustness
- domain difficulty
- switch-type difficulty (`HIL`, `HIL+EN`, `HIL+TL`, `HIL+TL+EN`)
- token-language WER for Hiligaynon, Tagalog, and English reference tokens
- switch-region WER by language pair

The frozen headline score remains the original 40 clips from `spk01`. The new
`spk02` subset is a separate second-speaker extension, not a replacement.
The `non_native_eval` subset is currently a 20-line planned recording scaffold;
it has no scored audio yet and is excluded from all WER tables.

| Dataset | Clips | Overall | Switch-region | Monolingual | Switch penalty |
|---------|------:|--------:|--------------:|------------:|---------------:|
| headline `spk01` | 40 | 57.4% | 35.8% | 65.9% | -30.1% |
| extension `spk02` | 40 | 34.4% | 28.6% | 38.8% | -10.2% |
| combined diagnostic | 80 | 46.1% | 32.0% | 53.4% | -21.4% |

Combined token-language WER: Hiligaynon 49.4%, Tagalog 27.3%, English 30.6%.
Combined domain WER ranges from 33.7% (`school_work`) to 55.8% (`health`).
Pure Hiligaynon (`HIL`) remains the hardest switch type at 63.3% combined WER.

### Interpretation — the negative penalty is the finding

An off-the-shelf Tagalog ASR model transcribes the **switch words better than the
monolingual ones**. Switch regions carry the English/Tagalog loanwords
(`traffic`, `meeting`, `grab`) the model already knows; the **Hiligaynon matrix**
is what it fails on (66% WER, no Hiligaynon training). The failure scales with
Hiligaynon involvement: `tl↔en` is near-solved (6%), `hil↔en` is worst (40%).

This quantifies the exact gap Sugidanon exists to expose: **current speech tech
catches the borrowed words and misses the Ilonggo.**

### Caveats

- Whisper **small** (not large-v3) — preliminary; a larger model lowers WER.
- Per-word tags are speaker-reviewed for the current headline benchmark.
- The headline score is single-speaker; the second native speaker is reported
  separately as an extension until a multi-speaker benchmark version is frozen.
- Non-native evaluation is scaffolded only; do not score or publish it until
  consented audio, reviewed transcripts, and reviewed token-language tags exist.

### Reproduce

```bash
python3 scripts/validate.py --kind asr --dir data/annotations
python3 scripts/run_whisper.py --model small --language tl   # optional refresh
python3 score.py --ref data/annotations --hyp data/predictions
python3 scripts/analyze_asr_breakdowns.py \
  --dataset headline:data/annotations:data/predictions \
  --dataset spk02:data/extensions/scripted_native_spk2/annotations:data/extensions/scripted_native_spk2/predictions \
  --out-json results/asr_breakdowns.json \
  --out-md results/asr_breakdowns.md
python3 scripts/validate_non_native_eval.py
```

---

## Translation benchmark

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

## Why the translation extension remains useful

The primary MVP is the code-switch ASR benchmark above. The translation files
remain useful as an extension layer because they exercise the same discipline:
schema-first data, explicit review status, baseline generation, and reproducible
scoring.

- translation schema
- seed benchmark rows
- baseline generation
- automatic scoring
- demo app extension
- clear path to human validation and later STT/translation/TTS work
