#!/usr/bin/env python3
"""
review_annotations.py - Terminal review for token language tags.

Actions:
  a = approve current token tags
  e = edit one token language
  s = skip
  q = quit
"""

import argparse
import json
import os


VALID_LANGS = {"hil", "tl", "en", "other"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def annotation_paths(annotation_dir, only):
    wanted = set(only or [])
    for name in sorted(os.listdir(annotation_dir)):
        if not (name.startswith("hil_cs_") and name.endswith(".json")):
            continue
        clip_id = name[:-5]
        if wanted and clip_id not in wanted:
            continue
        yield os.path.join(annotation_dir, name)


def print_annotation(data):
    print()
    print(f"{data['clip_id']}  {data.get('domain')}  {data.get('switch_type')}")
    print(data.get("transcript", ""))
    for token in data.get("tokens", []):
        print(f"  {token['idx']:>2}: {token['text']:<18} {token['lang']}")
    print(f"lang_tags_status: {data.get('lang_tags_status')}")


def review(path):
    data = load(path)
    while True:
        print_annotation(data)
        action = input("[a]pprove [e]dit [s]kip [q]uit: ").strip().lower()
        if action == "a":
            data["lang_tags_status"] = "reviewed"
            save(path, data)
            print(f"saved {data['clip_id']}: lang_tags_status=reviewed")
            return "approved"
        if action == "e":
            raw_idx = input("token idx: ").strip()
            if not raw_idx.isdigit():
                print("bad idx")
                continue
            idx = int(raw_idx)
            if idx < 0 or idx >= len(data.get("tokens", [])):
                print("idx out of range")
                continue
            lang = input("lang (hil/tl/en/other): ").strip()
            if lang not in VALID_LANGS:
                print("bad lang")
                continue
            data["tokens"][idx]["lang"] = lang
            data["lang_tags_status"] = "seed_unverified"
            save(path, data)
            print(f"saved {data['clip_id']} token {idx}={lang}")
            continue
        if action == "s":
            return "skipped"
        if action == "q":
            return "quit"
        print("bad action")


def summarize(annotation_dir):
    counts = {}
    for path in annotation_paths(annotation_dir, None):
        status = load(path).get("lang_tags_status", "missing")
        counts[status] = counts.get(status, 0) + 1
    print(json.dumps(counts, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotations", default="data/annotations")
    ap.add_argument("--only", nargs="*", help="clip ids, e.g. hil_cs_001 hil_cs_002")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    if args.summary:
        summarize(args.annotations)
        return

    for path in annotation_paths(args.annotations, args.only):
        result = review(path)
        if result == "quit":
            break


if __name__ == "__main__":
    main()
