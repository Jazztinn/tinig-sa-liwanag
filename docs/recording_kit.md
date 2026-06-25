# Recording kit — capturing code-switch Hiligaynon clips

This is the reproducible capture step of the Sugidanon speech pipeline. It turns
prompted utterances into a code-switch-labeled speech corpus that the
switch-region WER scorer (`score.py`) can evaluate.

## What you produce

For each prompt you record:

- `data/audio/hil_cs_NNN.wav` — 16 kHz mono clip
- `data/annotations/hil_cs_NNN.json` — token-level annotation with per-word
  `hil` / `tl` / `en` / `other` tags

The annotation language tags start as **seed_unverified**. A qualified
Hiligaynon speaker must confirm or correct them before they are treated as gold
data (see `SCHEMA.md`, `AI_DISCLOSURE.md`).

## Who should record

- Native or fluent Hiligaynon (Ilonggo) speakers.
- Natural code-switching is the point: say the prompt the way you normally would
  in everyday Ilonggo-English-Tagalog speech.
- Quiet room, phone or laptop mic is fine. Aim for 16 kHz mono (the script
  resamples for you).

## Steps

1. List the prompts:

   ```bash
   python3 scripts/record.py --list
   ```

2. Record one prompt (default mic, 8 seconds):

   ```bash
   python3 scripts/record.py --prompt 1 --seconds 8
   ```

   On macOS, find your mic device first:

   ```bash
   ffmpeg -f avfoundation -list_devices true -i ""
   python3 scripts/record.py --prompt 1 --device ":0"
   ```

   Already have a take? Register it without re-recording:

   ```bash
   python3 scripts/record.py --prompt 1 --from-wav take1.wav
   ```

3. Have a Hiligaynon speaker review the per-word `lang` tags in the generated
   `data/annotations/hil_cs_NNN.json`, then mark `review_status` as `reviewed`.

4. Validate everything (with audio present):

   ```bash
   python3 scripts/validate.py --kind asr --dir data/annotations
   ```

## Run the ASR baseline + switch-region WER

Once clips exist:

```bash
# transcribe with Whisper (tl is the closest language Whisper supports)
python3 scripts/run_whisper.py --model large-v3 --language tl

# score overall / switch-region / monolingual WER + switch penalty
python3 score.py --ref data/annotations --hyp data/predictions
```

The benchmark's research value is the **switch penalty**: how much worse an ASR
model does on words next to a language switch versus monolingual words.

## Adding new prompts

Edit `SENTENCES` in `scripts/build_codeswitch_set.py` (one entry per utterance,
with best-effort per-token language tags), then regenerate the annotation stubs:

```bash
python3 scripts/build_codeswitch_set.py
```

The same list drives `scripts/record.py`, so new prompts appear automatically in
`--list`.
