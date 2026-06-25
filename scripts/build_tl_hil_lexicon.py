#!/usr/bin/env python3
"""
Build a Tagalog -> Hiligaynon lexicon from Kaikki/Wiktionary JSONL dumps.

Method:
  1. Read Hiligaynon entries and index words by simple English gloss keys.
  2. Read Tagalog entries and map Tagalog words to Hiligaynon words that share
     the same simple English gloss key.
  3. Write a TSV lexicon consumable by the demo app.

This is a noisy bridge lexicon, not gold translation data. Human review is still
required before promoting entries into the curated lexicon.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS = {
    "hil": "https://kaikki.org/dictionary/Hiligaynon/kaikki.org-dictionary-Hiligaynon.jsonl",
    "tl": "https://kaikki.org/dictionary/Tagalog/kaikki.org-dictionary-Tagalog.jsonl",
}
BAD_GLOSS_WORDS = {
    "a",
    "an",
    "the",
    "of",
    "to",
    "for",
    "from",
    "with",
    "and",
    "or",
    "in",
    "on",
    "by",
    "someone",
    "something",
    "one",
    "person",
    "place",
}
SKIP_POS = {"character", "symbol", "punctuation", "name", "proper name"}


def download(url, path):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"Downloading {url}", file=sys.stderr)
    if shutil.which("curl"):
        subprocess.run(["curl", "-fL", url, "-o", path], check=True)
        return
    with urllib.request.urlopen(url) as response, open(path, "wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def normalize_word(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def gloss_keys(gloss):
    gloss = gloss.lower()
    gloss = re.sub(r"\([^)]*\)", " ", gloss)
    gloss = re.sub(r"[^a-z0-9;,\s'-]", " ", gloss)
    parts = re.split(r";|,|\bor\b|\band\b", gloss)
    keys = []
    for part in parts:
        part = re.sub(r"\b(to|a|an|the|of|for|from|with|in|on|by)\b", " ", part)
        part = re.sub(r"\s+", " ", part).strip()
        if not part or part in BAD_GLOSS_WORDS:
            continue
        if len(part) < 3:
            continue
        keys.append(part)
    return keys[:4]


def iter_entries(path):
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"{path}:{lineno}: skip bad JSON: {e}", file=sys.stderr)


def build_hil_index(path):
    index = defaultdict(Counter)
    for entry in iter_entries(path):
        if entry.get("pos") in SKIP_POS:
            continue
        word = normalize_word(entry.get("word", ""))
        if not word or len(word) > 40:
            continue
        for sense in entry.get("senses", []):
            for gloss in sense.get("glosses", []):
                for key in gloss_keys(gloss):
                    index[key][word] += 1
    return index


def build_pairs(tl_path, hil_index, max_entries):
    pairs = {}
    for entry in iter_entries(tl_path):
        if entry.get("pos") in SKIP_POS:
            continue
        tl_word = normalize_word(entry.get("word", ""))
        if not tl_word or len(tl_word) > 40 or " " in tl_word:
            continue

        candidates = Counter()
        for sense in entry.get("senses", []):
            for gloss in sense.get("glosses", []):
                for key in gloss_keys(gloss):
                    candidates.update(hil_index.get(key, {}))

        if candidates:
            hil_word, score = candidates.most_common(1)[0]
            if score > 0 and hil_word != tl_word:
                pairs[tl_word] = hil_word
                if max_entries and len(pairs) >= max_entries:
                    break
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=os.path.join(ROOT, "data", "external", "kaikki"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "lexicon_tl_hil_auto.tsv"))
    ap.add_argument("--max-entries", type=int, default=2500)
    ap.add_argument("--no-download", action="store_true")
    args = ap.parse_args()

    hil_path = os.path.join(args.cache_dir, "kaikki-hiligaynon.jsonl")
    tl_path = os.path.join(args.cache_dir, "kaikki-tagalog.jsonl")

    if not args.no_download:
        download(URLS["hil"], hil_path)
        download(URLS["tl"], tl_path)

    if not os.path.exists(hil_path) or not os.path.exists(tl_path):
        sys.exit("Missing Kaikki JSONL files. Run without --no-download first.")

    hil_index = build_hil_index(hil_path)
    pairs = build_pairs(tl_path, hil_index, args.max_entries)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as out:
        out.write("# Auto-generated Tagalog -> Hiligaynon bridge lexicon from Kaikki/Wiktionary gloss matching.\n")
        out.write("# Noisy: requires native-speaker review before promotion to curated data.\n")
        out.write("# source_word\thiligaynon\tsrc_lang\tsource\n")
        for tl_word in sorted(pairs):
            out.write(f"{tl_word}\t{pairs[tl_word]}\ttl\tkaikki-gloss-bridge\n")

    print(f"Wrote {len(pairs)} entries to {args.out}")


if __name__ == "__main__":
    main()
