#!/usr/bin/env python3
"""
mark_done.py — Mark all story entries up to a given ID as proofread.

Usage:
  python mark_done.py script_rpy_L000919_1_b17442e2
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python mark_done.py <last_id>")
        sys.exit(1)
    last_id = sys.argv[1]

    entries_path = Path("all_entries.json")
    done_path = Path("proofread_done.txt")

    data = json.loads(entries_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    done = set()
    if done_path.exists():
        done = set(line.strip() for line in done_path.read_text(encoding="utf-8").splitlines() if line.strip())

    found = False
    marked = 0
    for e in entries:
        if "story" not in (str(e.get("group") or "") + str(e.get("source_file") or "")).lower():
            continue
        if not str(e.get("new") or "").strip():
            continue
        done.add(e["id"])
        marked += 1
        if e["id"] == last_id:
            found = True
            break

    if not found:
        print(f"WARNING: {last_id} not found. Marked {marked} entries anyway.")
    else:
        print(f"Marked {marked} entries up to {last_id}")

    done_path.write_text("\n".join(sorted(done)) + "\n", encoding="utf-8")
    print(f"Wrote {len(done)} IDs to {done_path}")


if __name__ == "__main__":
    main()
