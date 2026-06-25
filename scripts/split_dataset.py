#!/usr/bin/env python3
"""
split_dataset.py - Build deterministic split CSVs for the benchmark.

Sugidanon is an evaluation benchmark: by default the whole headline set is the
frozen TEST split, with no train split (see BENCHMARK.md). Development/tuning
lives on the speaker-disjoint spk02 cohort, not on a carved slice of the
headline. The --train/--val flags remain for downstream users who explicitly
want to carve their own split, but they are off by default so this tool never
contradicts the frozen benchmark.

Uses speaker-aware grouping when enough speakers exist. With one speaker, falls
back to deterministic clip-level splitting and records that limitation.
"""

import argparse
import csv
import json
import os
import random
import wave
from collections import defaultdict


def load_annotations(annotation_dir):
    rows = []
    for name in sorted(os.listdir(annotation_dir)):
        if name.startswith("hil_cs_") and name.endswith(".json"):
            with open(os.path.join(annotation_dir, name), encoding="utf-8") as f:
                rows.append(json.load(f))
    return rows


def wav_duration(audio_dir, audio_file):
    path = os.path.join(audio_dir, os.path.basename(audio_file))
    with wave.open(path) as w:
        return round(w.getnframes() / w.getframerate(), 3)


def target_counts(total, train, val):
    train_count = round(total * train)
    val_count = round(total * val)
    test_count = total - train_count - val_count
    return {"train": train_count, "validation": val_count, "test": test_count}


def split_clip_level(rows, train, val, seed):
    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    counts = target_counts(len(rows), train, val)
    train_rows = shuffled[:counts["train"]]
    val_rows = shuffled[counts["train"]:counts["train"] + counts["validation"]]
    test_rows = shuffled[counts["train"] + counts["validation"]:]
    return {"train": train_rows, "validation": val_rows, "test": test_rows}


def split_speaker_aware(rows, train, val, seed):
    by_speaker = defaultdict(list)
    for row in rows:
        speaker_id = row.get("speaker", {}).get("id") or "unknown"
        by_speaker[speaker_id].append(row)
    speakers = list(by_speaker)
    if len(speakers) < 3:
        return None

    rng = random.Random(seed)
    rng.shuffle(speakers)
    splits = {"train": [], "validation": [], "test": []}
    counts = target_counts(len(rows), train, val)
    for speaker in speakers:
        target = min(splits, key=lambda key: len(splits[key]) / max(1, counts[key]))
        splits[target].extend(by_speaker[speaker])
    return splits


def write_split_csv(rows, path, audio_dir):
    fields = [
        "clip_id", "file_name", "transcript", "domain", "switch_type",
        "speaker_id", "duration_sec", "review_status", "lang_tags_status",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: item["clip_id"]):
            speaker = row.get("speaker", {})
            duration = row.get("duration_sec")
            if duration is None:
                duration = wav_duration(audio_dir, row["audio_file"])
            writer.writerow({
                "clip_id": row["clip_id"],
                "file_name": os.path.basename(row["audio_file"]),
                "transcript": row.get("transcript", ""),
                "domain": row.get("domain", ""),
                "switch_type": row.get("switch_type", ""),
                "speaker_id": speaker.get("id", ""),
                "duration_sec": duration,
                "review_status": row.get("review_status", ""),
                "lang_tags_status": row.get("lang_tags_status", ""),
            })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotations", default="data/annotations")
    ap.add_argument("--audio", default="data/audio")
    ap.add_argument("--output-dir", default="release/dataset")
    ap.add_argument("--train", type=float, default=0.0,
                    help="train fraction; default 0.0 (eval-only benchmark, no train split)")
    ap.add_argument("--val", type=float, default=0.0,
                    help="validation fraction; default 0.0 (dev cohort is spk02, not a headline slice)")
    ap.add_argument("--test", type=float, default=1.0,
                    help="test fraction; default 1.0 (whole headline is the frozen test set)")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    if round(args.train + args.val + args.test, 6) != 1.0:
        raise SystemExit("--train + --val + --test must equal 1.0")

    rows = load_annotations(args.annotations)
    if not rows:
        raise SystemExit(f"No annotations found in {args.annotations}")

    splits = split_speaker_aware(rows, args.train, args.val, args.seed)
    strategy = "speaker_aware"
    warning = None
    if splits is None:
        splits = split_clip_level(rows, args.train, args.val, args.seed)
        strategy = "clip_level_fallback"
        warning = "Only one or two speakers found; speaker-aware split is not possible yet."

    os.makedirs(args.output_dir, exist_ok=True)
    for name, split_rows in splits.items():
        write_split_csv(split_rows, os.path.join(args.output_dir, f"{name}.csv"), args.audio)

    summary = {
        "strategy": strategy,
        "warning": warning,
        "seed": args.seed,
        "counts": {name: len(split_rows) for name, split_rows in splits.items()},
        "ratios": {"train": args.train, "validation": args.val, "test": args.test},
    }
    with open(os.path.join(args.output_dir, "split_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
