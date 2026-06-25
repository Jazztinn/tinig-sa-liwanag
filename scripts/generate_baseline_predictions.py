#!/usr/bin/env python3
"""
Generate baseline Hiligaynon translation predictions for a benchmark JSONL file.

Default backend is the local dictionary translator. This keeps the hackathon
artifact reproducible without network access or model downloads.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import translate_hil  # noqa: E402


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", default=os.path.join(ROOT, "data", "benchmark", "hil_translation_v1.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "predictions", "translation_baseline_dict.jsonl"))
    ap.add_argument("--backend", choices=["dict", "hf"], default="dict")
    ap.add_argument("--model", default="welyjesch/lfm25-sft-hiligaynon")
    ap.add_argument("--lexicon", default=os.path.join(ROOT, "data", "lexicon_hil.tsv"))
    args = ap.parse_args()

    if args.backend == "dict":
        auto = os.path.join(os.path.dirname(args.lexicon), "lexicon_hil_auto.tsv")
        translate_hil.load_lexicon_file(auto)
        translate_hil.load_lexicon_file(args.lexicon)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    count = 0
    with open(args.out, "w", encoding="utf-8") as out:
        for row in read_jsonl(args.refs):
            source = row["source_text"]
            if args.backend == "hf":
                prediction = translate_hil.translate_hf(source, args.model)
                model = args.model
            else:
                prediction = translate_hil.translate_dict(source)
                model = "dict-baseline"
            out.write(json.dumps({
                "id": row["id"],
                "model": model,
                "prediction": prediction,
            }, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} predictions to {args.out}")


if __name__ == "__main__":
    main()
