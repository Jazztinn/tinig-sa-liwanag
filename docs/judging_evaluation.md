# Codebase Evaluation Report

*Project: **Sugidanon** ("Tinig sa Liwanag" — ACM TechSprint Asteria, Team Hague)*
*Evaluation date: 2026-06-26 · Reviewed against the four 25% judging criteria.*

## 1. Executive Summary

Sugidanon is an open **code-switch ASR benchmark for Hiligaynon (Ilonggo)** with English/Tagalog borrowing. It is exactly the kind of artifact the challenge asks for: foundational, reusable evaluation infrastructure rather than a consumer app. The headline contribution — **switch-region WER** and the resulting *negative switch penalty* (models transcribe borrowed English/Tagalog words well but miss the Hiligaynon matrix language) — is a genuine, defensible research finding, not a wrapper around an off-the-shelf model.

The repository is unusually well-engineered for a hackathon entry. I cloned-in-place and ran the documented commands: annotation validation passes 40/40, `score.py` reproduces the canonical numbers exactly (Overall 57.4% / switch 35.8% / mono 65.9% / penalty −30.1%), the frozen-manifest drift gate reports `OK: working tree matches frozen benchmark v1.0.1`, and the test suite passes **21 tests in 0.28s**. The core tooling is **stdlib-only**, so reproduction needs no install. A content-addressed `MANIFEST.json` pins every annotation, audio file, and the scorer hash.

Biggest risks are **scale and label authority**, openly disclosed by the team: the headline benchmark is **one speaker, 40 clips**, per-word `lang` tags are reviewed by a single Hiligaynon speaker, and the `non_native_eval` cohort has **0 recordings** so far. These cap statistical power and generalizability, but the project is honest about them and structures the repo so growth is the natural next step.

**Verdict preview:** competitive. Strong on Innovation, Technical Execution, and Theme/Impact; the relatively weakest axis is Design & UX, and even that is solid.

## 2. Scorecard

| Criterion | Weight | Score / 25 | Reason |
|---|---:|---:|---|
| Innovation & Creativity | 25% | 22 | Switch-region WER + switch-penalty framing is a real, original measurement contribution for an underrepresented language; not a generic app. |
| Technical Execution | 25% | 22 | Everything runs and reproduces exactly; stdlib core, frozen manifest drift gate, 21 passing tests, bootstrap CIs. Capped by small N and single-speaker headline. |
| Design & User Experience | 25% | 19 | Excellent docs and one-command flows; hosted explorer + Colab. Some script sprawl and doc references to files I could not confirm exist. |
| Theme Relevance & Impact | 25% | 23 | Bullseye on the challenge: open, reusable Philippine-language speech infra with serious consent/provenance/licensing ethics. Impact gated by dataset size. |
| **Total** | **100%** | **86 / 100** | Competitive entry; reusable open artifact with a sharp, reproducible finding. |

## 3. Detailed Evaluation

### A. Innovation & Creativity — 22/25

**Strengths.** The central idea is meaningfully different from a generic ASR demo. Instead of reporting one blunt WER, `score.py` attributes each error to either a monolingual Hiligaynon region or a **switch region** (tokens within ±1 of a language change), then reports the **switch penalty** (switch WER − mono WER). On this data the penalty is **−30.1%**: models do *better* near switch points because they nail the borrowed English/Tagalog words and miss the Hiligaynon matrix language. That is a crisp, quantified statement of *what gets erased* — original and directly relevant to code-switch speech. The per-language-pair breakdown (`hil↔en` 40.0%, `hil↔tl` 24.4%, `tl↔en` 6.2%) adds further nuance. Naming the corpus after the *sugidanon* oral-tradition chants, and including an `oral_tradition` domain, is a thoughtful cultural-design choice.

**Weak / missing.** The finding rests on a small sample (165 switch tokens, 208 mono tokens total), so the qualitative claim is stronger than its statistical power; bootstrap CIs are provided but will be wide. Only Whisper-small is fully scored as the headline baseline (MMS/large-v3 are mentioned as roadmap/optional).

**Evidence.** `score.py:66 switch_region_flags`, `score.py:90 switch_pairs`, `results/asr_score.txt`, `BENCHMARK.md`.

**Improve before submission.** Add at least one second model's scored column (large-v3 or MMS) to turn "models" (plural claim) into demonstrated cross-model evidence.

### B. Technical Execution — 22/25

**Strengths.** It actually works, end to end, with no setup:
- `python3 scripts/validate.py --kind asr --dir data/annotations` → **40/40 passed**.
- `python3 score.py --ref data/annotations --hyp data/predictions` → reproduces canonical numbers exactly.
- `python3 scripts/freeze_benchmark.py --verify` → **`OK: working tree matches frozen benchmark v1.0.1`** (real drift gate, sha256 + scorer pin).
- `python3 -m unittest discover -s tests` → **21 tests pass** across `test_score`, `test_freeze`, `test_dataset_integrity`, `test_extension_subsets`, `test_asr_breakdowns`, `test_non_native_eval`.

Core tooling is genuinely stdlib-only (ran clean on Python 3.14). Clear input/output contract: one JSON annotation per clip with `tokens[].lang`, predictions as `{clip_id,text}`, deterministic alignment via word-level Levenshtein (`score.py:111 align`). Edge cases are handled thoughtfully: normalization keeps apostrophe/hyphen (so `Nag-grocery` survives), subsets carry `gold_status`/`subset`/`speech_style` so non-native data can never leak into the native headline, and CIs use a fixed seed for reproducibility (`score.py:224 bootstrap_ci`).

**Weak / missing.** The `scripts/` directory has ~30 files including future/extension and translation/G2P/TTS tooling — healthy ambition but some sprawl relative to the judged artifact. Headline N is small (single speaker). `non_native_eval` is scaffolding with 0 audio. I did not run `npm run build`/`next build` in this pass, so the hosted-explorer build was not independently verified here (the live Vercel URL is the team's evidence).

**Evidence.** Test run output (21 ok), `score.py`, `data/benchmark/MANIFEST.json`, `data/annotations/hil_cs_001.json`.

**Improve.** Mark or fence extension/reserved scripts (`tts_route.py`, `g2p_hil/`) more explicitly so judges don't read sprawl as incompleteness; add a one-line `make verify` / single entrypoint that runs validate+score+freeze+tests together.

### C. Design & User Experience — 19/25

**Strengths.** Documentation is a real strength: `README.md` leads with the benchmark, states the finding, gives a one-command release pipeline (`build_release.py --overwrite`), and a "minimal proof" block. `BENCHMARK.md` is a proper benchmark card (task, metric, frozen split, speaker-disjoint cohort ladder, reproducibility). A **one-click Colab** badge lowers the barrier to reproduction to near zero, and there is a hosted Next.js explorer. The canonical-numbers table in `CLAUDE.md`/`BENCHMARK.md` enforces consistency across surfaces. Output is easy to interpret (per-clip table + corpus summary + CIs). Folder names are intuitive (`data/annotations`, `data/audio`, `data/predictions`, `data/extensions`).

**Weak / missing.** The README's "Repository structure" and prose reference several paths I did not confirm in `git ls-files` in this pass — e.g. `pages/` vs the `app/` legacy demo, `data/lexicon_hil.tsv`, `g2p_hil/`, `docs/recording_kit.md` is present but some script names cited (`build_codeswitch_set.py`, `analyze_asr_breakdowns.py`) should be cross-checked against the actual `scripts/` listing for drift. (Assumption: a few doc references may be aspirational or renamed.) No top-level `CONTRIBUTING.md`. The large script count without a "start here" map can disorient a new contributor.

**Evidence.** `README.md` lines 176–227 (structure) vs `scripts/` listing; presence of both `app/` and `pages/`.

**Improve.** Add a short `CONTRIBUTING.md`; reconcile README structure block against the actual tree; add a one-paragraph "if you only run one thing, run this" callout.

### D. Theme Relevance & Impact — 23/25

**Strengths.** Direct hit on "Inclusive Speech Technology for Philippine Languages." It targets Hiligaynon (9M+ speakers, rarely measured), produces **reusable open infrastructure** (benchmark + scorer + schema + dataset card), and is explicitly designed for extension (cohort ladder, frozen manifest, split tool, HF dataset publication). Ethics are handled at a level above typical hackathon work: informed consent, minimal/anonymized speaker metadata (`spk01`), right to withdraw, provenance/licensing per item, honest fluency labeling, dual license (MIT code / CC BY 4.0 data), and a clear "AI output is never language gold" stance with `seed_unverified` flags. Native speakers are credited as authors, not data sources.

**Weak / missing.** Real-world impact is currently bounded by size (40 clips, 1 headline speaker) and by labels resting on a single reviewer — adjudication by multiple native speakers would harden the gold status. `non_native_eval` impact is promissory until clips exist.

**Evidence.** README "Why this matters" + "Data protection, privacy & ethics", `BENCHMARK.md` cohort ladder, `docs/source_ledger.md`/`licensing.md`, per-clip `provenance` block in annotations.

**Improve.** Add multi-reviewer adjudication notes (even 2-of-2 agreement on a subset) to strengthen the gold claim.

## 4. Reproducibility Check

A fresh user **can** reproduce the core benchmark with no install. Verified locally this session:

| Command | Result |
|---|---|
| `python3 scripts/validate.py --kind asr --dir data/annotations` | ✅ 40/40 passed |
| `python3 score.py --ref data/annotations --hyp data/predictions` | ✅ reproduces canonical 57.4 / 35.8 / 65.9 / −30.1 |
| `python3 scripts/freeze_benchmark.py --verify` | ✅ `working tree matches frozen benchmark v1.0.1` |
| `python3 -m unittest discover -s tests` | ✅ 21 tests OK (0.28s) |
| `score.py --ci` | ✅ documented; bootstrap CIs, fixed seed |

**Not independently run this pass:** `npm install && npm run dev/build` (web explorer), the Colab end-to-end on a clean VM, and `scripts/run_whisper.py` (needs `openai-whisper` + model download). These are documented and the live Vercel + Colab links are the team's standing evidence; I am flagging them as unverified-here rather than broken.

**Assumptions / unclear:** a few README-referenced paths (`pages/` vs `app/`, `g2p_hil/`, some script names) were not all individually confirmed against the tree in this pass; treat minor doc-vs-tree drift as possible. No environment variables are required for the core path (`.env.example` exists for the optional translation backend).

## 5. Open-Source Artifact Quality

This is a **reusable artifact**, not a throwaway demo.

- **README:** thorough, benchmark-led, with runnable commands and honest limitations. ✅
- **License:** dual — MIT (code) / CC BY 4.0 (data), explicit in `LICENSE`. ✅
- **Dataset card:** `hf_dataset/README.md` + published HF dataset (`LauelKills/sugidanon-hil-codeswitch`). ✅
- **Benchmark card:** `BENCHMARK.md` with frozen, content-addressed version. ✅ (strong, uncommon)
- **Schema:** `SCHEMA.md` documents annotation + subset schema. ✅
- **Provenance/ethics:** `docs/source_ledger.md`, `docs/licensing.md`, `AI_DISCLOSURE.md`, consent/withdrawal policy. ✅
- **Tests/validation:** unit tests + `validate.py` + drift gate. ✅
- **Contribution guide:** **no `CONTRIBUTING.md`.** ⚠️
- **Extensibility:** cohort ladder, split tool, release packager, second-speaker extension already wired. ✅

### E. Theme alignment summary
Strong open-source posture; the only conventional gap is a contribution guide. The frozen-manifest + dataset/benchmark cards put it ahead of typical hackathon repos on reusability.

## 6. Top 10 Priority Fixes

1. **Add a scored second baseline** (Whisper large-v3 or MMS) so the "models miss Hiligaynon" claim is shown across ≥2 models, not implied.
2. **Reconcile README structure vs actual tree** (`pages/` vs `app/`, `g2p_hil/`, cited script names) to remove doc-vs-code drift judges will notice.
3. **Add `CONTRIBUTING.md`** — how to add clips, run the review CLI, and pass the freeze gate before merge.
4. **Single verify entrypoint** (`make verify` or `scripts/verify.py`) running validate + score + freeze --verify + tests; cite it in README.
5. **Strengthen label authority:** document multi-reviewer adjudication (even a subset with 2-speaker agreement) to upgrade gold confidence.
6. **Surface the small-N caveat next to the headline number** everywhere, with the CI ranges, so the −30.1% is read correctly.
7. **Fence extension/reserved tooling** (`tts_route.py`, translation, G2P) visually so script sprawl doesn't read as half-finished core.
8. **Verify the web build** (`next build`) in CI or a documented step; note Node version.
9. **Land at least a few `non_native_eval` clips** or relabel that cohort clearly as "scaffold, no audio yet" in the README (it currently reads as a deliverable).
10. **Add a tiny CI workflow** (GitHub Actions) running the stdlib tests + freeze gate on push — cheap, high credibility signal.

## 7. Quick Wins Before Deadline

- Paste the actual `score.py` run output (numbers reproduce) into the README as a "verified output" block — judges love seeing it match.
- Add `CONTRIBUTING.md` (even 20 lines).
- Fix the README structure table to match `git ls-files`.
- Add one Actions YAML running `python -m unittest` + `freeze_benchmark.py --verify`.
- One sentence under the headline number stating N (40 clips / 1 speaker / 165 switch tokens) so the limitation is unmissable and reads as rigor.
- Relabel the `non_native_eval` "20-line scaffold" so 0-audio isn't mistaken for a shipped subset.

## 8. Final Judge-Style Verdict

**Competitive.** Sugidanon does the hard, unglamorous thing the challenge actually rewards: it ships reusable, open, *reproducible* evaluation infrastructure for an underrepresented Philippine language, and backs it with a genuine measurement contribution (switch-region WER and a reproducible negative switch penalty). It ran for me exactly as documented — validation, scoring, drift gate, and 21 tests all green — with no install, which is rare. Ethics, licensing, and provenance are handled seriously, and native speakers are credited as authors.

The ceiling is held down by scale (40 clips, one headline speaker, single-reviewer labels) and minor documentation-vs-tree drift, not by anything broken. Address the second-model baseline, the doc reconciliation, and a contribution guide, and this moves from "strong contender" to "front-runner." As submitted, it is a credible, honest, extensible artifact that fits "Tinig sa Liwanag" closely. **Score: 86/100.**
