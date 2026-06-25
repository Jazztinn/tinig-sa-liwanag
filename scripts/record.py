#!/usr/bin/env python3
"""
record.py — Capture a code-switch speech clip + emit a matching annotation stub.

This is the reproducible capture step of the Sugidanon speech pipeline. A
contributor records one prompted utterance; the script saves 16 kHz mono wav to
data/audio/<clip_id>.wav and writes data/annotations/<clip_id>.json pre-filled
from the prompt's known transcript. Per-word language tags start as SEED values
and must be reviewed by a qualified Hiligaynon speaker (SCHEMA.md,
AI_DISCLOSURE.md).

Recording uses the system `ffmpeg` (avfoundation on macOS, alsa/pulse on Linux).
No Python audio deps. If you already have a wav, use --from-wav to skip capture
and just register the clip.

Usage:
    # list elicitation prompts
    python3 scripts/record.py --list

    # record prompt 3 from the default mic for 8 seconds
    python3 scripts/record.py --prompt 3 --seconds 8

    # register an already-recorded wav instead of capturing
    python3 scripts/record.py --prompt 3 --from-wav /path/to/take.wav

    # macOS: find your input device index first
    ffmpeg -f avfoundation -list_devices true -i ""
    python3 scripts/record.py --prompt 3 --device ":0"
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# Reuse the same elicitation set + annotation builder so audio clip_ids line up
# with data/annotations/hil_cs_*.json and the per-word tagging stays identical.
from build_codeswitch_set import SENTENCES, make_annotation  # noqa: E402


def list_prompts():
    print("Elicitation prompts (clip_id <- prompt):")
    for n, (domain, switch_type, text) in enumerate(SENTENCES, 1):
        print(f"  hil_cs_{n:03d}  [{domain}/{switch_type}]  {text}")


def ffmpeg_input_format():
    """Return (-f format, default device) for the current OS."""
    system = platform.system()
    if system == "Darwin":
        return "avfoundation", ":0"      # default audio input
    if system == "Linux":
        return "alsa", "default"
    if system == "Windows":
        return "dshow", "audio=Microphone"
    return None, None


def record_wav(dst, seconds, device):
    fmt, default_dev = ffmpeg_input_format()
    if fmt is None:
        sys.exit(f"Unsupported OS for capture: {platform.system()}. Use --from-wav.")
    dev = device or default_dev
    cmd = ["ffmpeg", "-y", "-f", fmt, "-i", dev, "-t", str(seconds),
           "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", dst]
    print(f"Recording {seconds}s from {dev} ... speak now.")
    subprocess.run(cmd, check=True)


def convert_wav(src, dst):
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-ac", "1", "-ar", "16000",
         "-sample_fmt", "s16", dst],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def wav_duration(path):
    try:
        with wave.open(path) as w:
            return round(w.getnframes() / float(w.getframerate()), 2)
    except (wave.Error, OSError):
        return None


def write_annotation(clip_id, domain, switch_type, text, duration, ann_dir):
    ann = make_annotation(clip_id, domain, switch_type, text, duration)
    os.makedirs(ann_dir, exist_ok=True)
    path = os.path.join(ann_dir, f"{clip_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ann, f, ensure_ascii=False, indent=2)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", type=int, help="prompt number (see --list), 1-based")
    ap.add_argument("--seconds", type=int, default=8, help="capture length")
    ap.add_argument("--device", default=None, help="ffmpeg input device spec")
    ap.add_argument("--from-wav", default=None, help="register this wav instead of recording")
    ap.add_argument("--audio-dir", default=os.path.join(ROOT, "data", "audio"))
    ap.add_argument("--ann-dir", default=os.path.join(ROOT, "data", "annotations"))
    ap.add_argument("--list", action="store_true", help="list prompts and exit")
    args = ap.parse_args()

    if args.list or args.prompt is None:
        list_prompts()
        if args.prompt is None and not args.list:
            sys.exit("\nPass --prompt N to record one.")
        return

    if not (1 <= args.prompt <= len(SENTENCES)):
        sys.exit(f"--prompt must be 1..{len(SENTENCES)}")

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. Install it (brew install ffmpeg / apt install ffmpeg).")

    domain, switch_type, text = SENTENCES[args.prompt - 1]
    clip_id = f"hil_cs_{args.prompt:03d}"
    os.makedirs(args.audio_dir, exist_ok=True)
    dst_wav = os.path.join(args.audio_dir, f"{clip_id}.wav")

    print(f"Prompt [{switch_type}]: {text}")
    if args.from_wav:
        if not os.path.exists(args.from_wav):
            sys.exit(f"--from-wav not found: {args.from_wav}")
        convert_wav(args.from_wav, dst_wav)
    else:
        record_wav(dst_wav, args.seconds, args.device)

    duration = wav_duration(dst_wav)
    ann_path = write_annotation(clip_id, domain, switch_type, text, duration, args.ann_dir)
    print(f"\nSaved audio:      {os.path.relpath(dst_wav, ROOT)}  ({duration}s)")
    print(f"Wrote annotation: {os.path.relpath(ann_path, ROOT)}")
    print("Now have a Hiligaynon speaker confirm the per-word lang tags (seed_unverified).")


if __name__ == "__main__":
    main()
