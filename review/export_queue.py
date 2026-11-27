#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export a range of story entries to review/queue/ch_XXXX_YYYY.txt.

Usage:
    python review/export_queue.py --from 1 --to 500 --size 100
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int, default=500)
    ap.add_argument("--size", type=int, default=100)
    args = ap.parse_args()

    data = json.load(open(os.path.join(ROOT, "all_entries.json"), encoding="utf-8"))
    story = [e for e in data["entries"] if e.get("group") == "story"]

    def line(e):
        return int(re.search(r"_L(\d+)_", e["id"]).group(1))

    story.sort(key=line)
    # global position index (1-based) so numbering stays stable across batches
    pos = {e["id"]: i for i, e in enumerate(story, 1)}

    outdir = os.path.join(HERE, "queue")
    os.makedirs(outdir, exist_ok=True)
    for start in range(args.start - 1, args.end, args.size):
        chunk = story[start:start + args.size]
        if not chunk:
            break
        path = os.path.join(outdir, "ch_%04d_%04d.txt" % (start + 1, start + len(chunk)))
        with open(path, "w", encoding="utf-8") as f:
            f.write("# 共 %d 条，编号为全书序号\n\n" % len(chunk))
            for e in chunk:
                f.write("[%d] script.rpy:%d id=%s speaker=%s\n" % (
                    pos[e["id"]], line(e), e["id"], e.get("speaker") or "-"))
                f.write("EN: " + e["text"].replace("\n", " ") + "\n")
                f.write("ZH: " + e["new"].replace("\n", " ") + "\n\n")
        print(path, len(chunk))


if __name__ == "__main__":
    main()
