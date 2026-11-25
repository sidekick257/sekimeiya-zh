#!/usr/bin/env python3
"""
extract_quotes.py — Extract matched quote pairs by sequential order.

Full story line N corresponds to the Nth story entry in all_entries.json.

Usage:
  python extract_quotes.py --limit 20
"""

import argparse
import json
import re
from pathlib import Path


def load_story_lines(path: Path) -> list:
    """Return list of (line_num, text) for dialogue lines."""
    result = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "|" in line and not line.startswith("#") and not line.startswith("="):
            text = line.split("|", 1)[1].strip()
            if text:
                result.append((i, text))
    return result


def parse_quote_file(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    pairs = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "引用处" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 5:
            continue
        ref_loc, ref_text, orig_loc, orig_text, typ = cols[:5]
        ref_lines = re.findall(r"L(\d+)", ref_loc)
        orig_lines = re.findall(r"L(\d+)", orig_loc)
        if not ref_lines or not orig_lines:
            continue
        pairs.append({
            "ref_loc": ref_loc,
            "ref_line": int(ref_lines[0]),
            "orig_loc": orig_loc,
            "orig_line": int(orig_lines[0]),
            "type": typ,
        })
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--entries", default="all_entries.json")
    ap.add_argument("--quotes", default="sekimeiya_quote_reuse.md")
    ap.add_argument("--story", default="sekimeiya_full_story_with_choices.txt")
    args = ap.parse_args()

    for p in (Path(args.entries), Path(args.quotes), Path(args.story)):
        if not p.exists():
            print(f"ERROR: missing {p}")
            return

    data = json.loads(Path(args.entries).read_text(encoding="utf-8"))
    story_entries = [e for e in data.get("entries", []) if "story" in (str(e.get("group") or "") + str(e.get("source_file") or "")).lower()]
    story_lines = load_story_lines(Path(args.story))
    pairs = parse_quote_file(Path(args.quotes))

    print(f"story entries: {len(story_entries)}, story lines: {len(story_lines)}, pairs: {len(pairs)}")

    # build line_num -> index mapping
    line_to_idx = {ln: i for i, (ln, _) in enumerate(story_lines)}

    matched = []
    for p in pairs:
        orig_idx = line_to_idx.get(p["orig_line"])
        ref_idx = line_to_idx.get(p["ref_line"])
        if orig_idx is None or ref_idx is None:
            continue
        if orig_idx >= len(story_entries) or ref_idx >= len(story_entries):
            continue
        orig_e = story_entries[orig_idx]
        ref_e = story_entries[ref_idx]
        matched.append({
            "type": p["type"],
            "orig_loc": p["orig_loc"],
            "orig_en": orig_e.get("text", "")[:60],
            "orig_zh": orig_e.get("new", "")[:60],
            "ref_loc": p["ref_loc"],
            "ref_en": ref_e.get("text", "")[:60],
            "ref_zh": ref_e.get("new", "")[:60],
        })

    print(f"Matched {len(matched)} pairs\n")
    for i, m in enumerate(matched[:args.limit], 1):
        print(f"-------- {i}  {m['type']} --------")
        print(f"【原句处】{m['orig_loc']}")
        print(f"  英文: {m['orig_en']}...")
        print(f"  译文: {m['orig_zh']}...")
        print(f"【引用处】{m['ref_loc']}")
        print(f"  英文: {m['ref_en']}...")
        print(f"  译文: {m['ref_zh']}...")
        print()


if __name__ == "__main__":
    main()
