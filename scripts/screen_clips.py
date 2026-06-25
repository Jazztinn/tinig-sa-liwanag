#!/usr/bin/env python3
"""
screen_clips.py — Flag phrase clips that may be mis-cut, so you ear-check fewer.

After scripts/split_claps.py, this scans each data/audio/hil_cs_*.wav for two
clap-split failure modes:

  CLIPPED  loud energy in the first/last window  -> a word may be cut off, or
           the clip starts/ends mid-speech.
  CLAP     a near-peak spike inside the edge windows -> leftover clap blip.

Clips with no flag are very likely clean. Pure standard library.

Usage:
    python3 scripts/screen_clips.py
    python3 scripts/screen_clips.py --edge 0.2 --clip-ratio 0.5
"""

import argparse
import audioop
import glob
import os
import wave

WIN = 0.02  # 20ms sub-window for peak scan


def analyze(path, edge, clip_ratio, clap_ratio):
    w = wave.open(path)
    sr, n = w.getframerate(), w.getnframes()
    data = w.readframes(n)
    w.close()
    bw = 2
    total = len(data)
    edge_b = int(edge * sr) * bw
    # body RMS (excluding edges) as the speech reference
    body = data[edge_b:total - edge_b] or data
    body_rms = audioop.rms(body, bw) or 1
    gpeak = audioop.max(data, bw) or 1

    head, tail = data[:edge_b], data[total - edge_b:]
    flags = []
    for name, seg in (("head", head), ("tail", tail)):
        if not seg:
            continue
        seg_rms = audioop.rms(seg, bw)
        seg_peak = audioop.max(seg, bw)
        if seg_rms > clip_ratio * body_rms:
            flags.append(f"CLIPPED-{name}")
        elif seg_peak > clap_ratio * gpeak:
            flags.append(f"CLAP-{name}")
    return flags, round(n / sr, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/audio")
    ap.add_argument("--edge", type=float, default=0.15, help="edge window (s)")
    ap.add_argument("--clip-ratio", type=float, default=0.6,
                    help="edge RMS > this x body RMS -> possible clipped word")
    ap.add_argument("--clap-ratio", type=float, default=0.85,
                    help="edge peak > this x global peak -> possible leftover clap")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "hil_cs_*.wav")))
    if not files:
        raise SystemExit(f"No clips in {args.dir}")
    flagged = []
    for f in files:
        flags, dur = analyze(f, args.edge, args.clip_ratio, args.clap_ratio)
        cid = os.path.basename(f)[:-4]
        if flags:
            flagged.append(cid)
            print(f"  {cid}  {dur:5.2f}s  {', '.join(flags)}")
    print("-" * 40)
    if flagged:
        print(f"{len(flagged)}/{len(files)} clips to ear-check:")
        print("  " + " ".join(flagged))
        print("Listen, then re-split tight ones: "
              "python3 scripts/split_claps.py --src <folder> --only N --guard 0.25")
    else:
        print(f"All {len(files)} clips clean by the edge heuristic. Spot-check a few anyway.")


if __name__ == "__main__":
    main()
