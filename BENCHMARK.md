# Sugidanon — Benchmark Card

**Version 1.0.1** · frozen manifest: [`data/benchmark/MANIFEST.json`](data/benchmark/MANIFEST.json)
· license CC-BY-4.0 · code-switch ASR benchmark for Hiligaynon (Ilonggo).

This card is the single source of truth for the benchmark protocol. The canonical
numbers below must stay consistent with `results/asr_score.txt`, the README, the
Colab, and the landing page.

## Task and metric

- **Primary task:** code-switch automatic speech recognition with a Hiligaynon
  matrix language and borrowed English / Tagalog.
- **Primary metric:** **switch-region WER** — word error rate restricted to tokens
  within ±1 of a language-switch point, reported against **monolingual WER** so the
  *switch penalty* (switch − mono) is explicit.
- **Scorer:** [`score.py`](score.py), pure stdlib. Word-level Levenshtein;
  normalization = lowercase + strip punctuation except apostrophe/hyphen;
  switch-region window = 1. Frozen scorer hash is pinned in the manifest.

## Cohort ladder

Cohorts are **speaker-disjoint** by construction, so the test (spk01) and
development (spk02) sets never leak. Subsets are never blended into one WER.

| Cohort | Role | Speaker | Clips | Status |
|--------|------|---------|------:|--------|
| `headline` (`scripted_native`) | **test** | spk01 (Aziel Faith Agustin) | 40 | frozen |
| `scripted_native_spk2` | **development / robustness** | spk02 (Nimeesha De Guzman) | 40 | frozen |
| `non_native_eval` | **robustness** | mixed (podcast/vlog) | 0 | pending recordings |
| cross-language expansion | future | — | — | planned |

There is **no train split** — this is a low-resource evaluation benchmark; nobody
trains on it. "Development" means tuning/threshold decisions live on spk02 so the
headline test number stays untouched.

## Headline results (test = spk01, Whisper small, `--language tl`)

| Metric | WER | 95% CI |
|--------|----:|--------|
| Overall | 57.4% | [49.3%, 65.8%] |
| Monolingual (Hiligaynon) | 65.9% | [58.6%, 72.3%] |
| Switch-region | 35.8% | [26.1%, 46.4%] |
| **Switch penalty** | **−30.1%** | switch − mono |

Switch-pair WER: `hil↔en` 40.0% · `hil↔tl` 24.4% · `tl↔en` 6.2%.

The switch-region and monolingual confidence intervals do **not overlap**, so the
**negative switch penalty is statistically meaningful**, not noise: the model
transcribes the borrowed English/Tagalog words well but misses the Hiligaynon.

## Development cohort (spk02) — cross-speaker replication

| Metric | WER | 95% CI |
|--------|----:|--------|
| Overall | 34.4% | [28.9%, 40.4%] |
| Monolingual | 38.8% | [29.7%, 47.7%] |
| Switch-region | 28.6% | [22.1%, 35.3%] |
| Switch penalty | −10.2% | switch − mono |

A second speaker reproduces the **negative switch penalty** (smaller magnitude),
which strengthens the core finding rather than relying on one speaker. spk02 is
reported separately and is **never** counted toward the headline.

## Inclusion rules (frozen)

1. Headline (test) = `scripted_native`, Speaker 1 (spk01) only.
2. Cohorts are speaker-disjoint; spk02 is development, never blended into the headline WER.
3. `non_native_eval` is robustness only and never counts toward the native headline.
4. A clip is eligible only with a gold reference annotation **and** a matching prediction file.
5. Hiligaynon references stay `seed_unverified` until a native speaker confirms; AI output is never treated as gold.

## Reproducibility

The benchmark is content-addressed: every annotation and audio file is hashed in
the manifest, and the scorer is pinned by hash. Rerun anywhere and get the same
numbers, or fail loudly if the data drifted.

```bash
# 1. score the frozen headline test set (with confidence intervals)
python3 score.py --ref data/annotations --hyp data/predictions --ci

# 2. development cohort
python3 score.py \
  --ref data/extensions/scripted_native_spk2/annotations \
  --hyp data/extensions/scripted_native_spk2/predictions --ci

# 3. full slice report (speaker / domain / switch-type / token-language)
python3 scripts/analyze_asr_breakdowns.py \
  --dataset headline:data/annotations:data/predictions \
  --dataset spk2:data/extensions/scripted_native_spk2/annotations:data/extensions/scripted_native_spk2/predictions \
  --out-json results/asr_breakdowns.json --out-md results/asr_breakdowns.md

# 4. refresh / verify the frozen manifest
python3 scripts/freeze_benchmark.py            # write v1.0.1
python3 scripts/freeze_benchmark.py --verify   # CI gate: fail on any drift
```

A second baseline (`whisper-small-auto`) lives in `results/asr_baselines.md`;
forcing `tl` beats auto on every metric.

## Provenance, consent, license

- Per-source provenance and license trail: [`docs/source_ledger.md`](docs/source_ledger.md).
- Native speakers are credited as **authors**, not data sources.
- Benchmark release license: CC-BY-4.0. Third-party audio with incompatible terms
  (e.g. non-commercial corpora) is excluded from the release.

## Extending to a new language

Hiligaynon is the proof of concept; the method is the contribution. The scorer is
**language-agnostic** — `score.py` treats `lang` tags as opaque labels and derives
switch-pair buckets from the data (`pair_label`), so nothing about Hiligaynon,
Tagalog, or English is hardcoded. To stand up the same benchmark for another
underserved language (Cebuano, Waray, Aklanon, Kinaray-a, Capiznon, …) you supply:

1. **Audio** — one clip per utterance (`.wav`).
2. **Annotations** — one JSON per clip following [`SCHEMA.md`](SCHEMA.md):
   `tokens: [{text, lang}]` plus `domain`, `switch_type`, `speaker`,
   `gold_status`, `provenance`.
3. **Native-reviewed `lang` tags** — per-word language labels confirmed by a
   native speaker. AI output is never treated as gold (see ethics above).
4. **Baseline predictions** — one `{clip_id, text}` JSON per clip from any ASR model.

Then the existing tooling runs unchanged:

```bash
python3 score.py --ref <lang>/annotations --hyp <lang>/predictions --ci
python3 scripts/freeze_benchmark.py        # freeze the new cohort
```

**How many clips?** ~40 is a reasonable floor. The bootstrap CIs are the stopping
rule: if a language's switch-region and monolingual intervals still overlap,
collect more clips until they separate — at which point the switch penalty is
statistically established for that language. The benchmark reports its own
statistical readiness, so "how much data is enough" stops being a guess.

## Roadmap to a fuller benchmark

- [ ] Fill `non_native_eval` with the 20 real podcast/vlog recordings (robustness test).
- [ ] Add a natural / spontaneous native-speech cohort (rights and consent permitting).
- [ ] Cross-language expansion: Cebuano, Waray, Aklanon, Kinaray-a, Capiznon for transfer.
- [ ] Bump the manifest version when any frozen cohort changes.
