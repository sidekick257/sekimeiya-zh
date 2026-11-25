#!/usr/bin/env python3
"""
show_diff.py — Compare before/after proofreading.

Usage:
  python show_diff.py all_entries.before_proofread.json all_entries.json
  python show_diff.py all_entries.before_proofread.json all_entries.json --limit 50
"""

import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before", help="backup JSON (before proofreading)")
    ap.add_argument("after", help="current JSON (after proofreading)")
    ap.add_argument("--limit", type=int, default=30, help="max diffs to show")
    ap.add_argument("--only", default="", help="filter by group/source containing this")
    args = ap.parse_args()

    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))

    before_map = {e["id"]: e for e in before.get("entries", [])}
    after_map = {e["id"]: e for e in after.get("entries", [])}

    diffs = []
    for eid, e_after in after_map.items():
        e_before = before_map.get(eid)
        if not e_before:
            continue
        old = str(e_before.get("new") or "").strip()
        new = str(e_after.get("new") or "").strip()
        if old and new and old != new:
            if args.only:
                key = (str(e_after.get("group") or "") + str(e_after.get("source_file") or "")).lower()
                if args.only.lower() not in key:
                    continue
            diffs.append({
                "id": eid,
                "text": e_after.get("text", ""),
                "old": old,
                "new": new,
                "group": e_after.get("group", ""),
                "source": e_after.get("source_file", ""),
            })

    print(f"Found {len(diffs)} changed entries.")
    if not diffs:
        return

    show = diffs[:args.limit]
    for i, d in enumerate(show, 1):
        print(f"\n-------- {i}/{len(diffs)}  {d['group']}  {d['source']}  {d['id']} --------")
        print(f"【原文】\n{d['text']}")
        print(f"【改前】\n{d['old']}")
        print(f"【改后】\n{d['new']}")

    if len(diffs) > args.limit:
        print(f"\n... and {len(diffs) - args.limit} more. Use --limit to see more.")


if __name__ == "__main__":
    main()
