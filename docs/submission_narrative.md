# Submission Narrative

## One-line pitch

Sugidanon is a reproducible benchmark scaffold and demo for
context-aware Hiligaynon translation, designed as the language foundation for
future Philippine STT/TTS systems.

## Problem

Many Philippine languages remain underrepresented in open language and speech
technology. Hiligaynon speakers need systems that understand meaning in context,
not tools that only replace isolated words.

## Original plan

The team first considered building a full Hiligaynon STT/TTS demo. During
scoping, we narrowed the MVP because speech synthesis and recognition depend on
a language layer that can already preserve meaning.

## MVP delivered

This repository now provides:

- a JSONL schema for context-aware Hiligaynon translation examples
- a 30-row seed benchmark across daily life, health, education, public service,
  emergency, workplace, agriculture, and code-switching
- a reproducible dictionary baseline generator
- an automatic evaluator with coverage, exact match, token F1, chrF, and
  per-domain summaries
- a local demo app with benchmark seed prompts
- documentation for human review and future speech extension

## Honest limitation

The current Hiligaynon references are marked `seed_unverified`. Because the
team did not have access to native Hiligaynon reviewers during the two-hour
hackathon, we do not claim this is gold data or a production-quality model.

## Why the baseline matters

The dictionary baseline exposes exactly why the project is needed. It can
translate some known words, but it fails on context, grammar, code-switching,
and domain-specific meaning. That gives future model work a clear target.

## Next step

The immediate next step is native-speaker validation:

1. Review each seed translation.
2. Edit or reject inaccurate references.
3. Add human scores for adequacy, fluency, context, and terminology.
4. Freeze a test split.
5. Compare dictionary, neural, and fine-tuned baselines.

## Future speech path

Once text translation is measurable, the project can reconnect to speech:

```text
STT -> Hiligaynon translation -> TTS
```

The existing G2P, ASR, and TTS utilities in the repository remain as future
infrastructure, but they are not the MVP claim.
