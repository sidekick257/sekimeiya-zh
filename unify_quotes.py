#!/usr/bin/env python3
"""Unify quote translations based on sekimeiya_quote_reuse_all_entries.md"""

import json
import re
from pathlib import Path

def parse_md(md_path):
    """Extract ID pairs from the markdown table."""
    text = Path(md_path).read_text(encoding="utf-8")
    pairs = []
    # Match table rows with IDs
    pattern = r"`(script_rpy_L\d+_\d+_[a-f0-9]+)`\s*\|\s*`?(script_rpy_L\d+_\d+_[a-f0-9]+)`?"
    for m in re.finditer(pattern, text):
        orig, quote = m.group(1), m.group(2)
        if orig and quote and orig != quote:
            pairs.append((orig, quote))
    return pairs

def main():
    md = Path("sekimeiya_quote_reuse_all_entries.md")
    jsn = Path("all_entries.json")
    bak = Path("all_entries.before_unify.json")

    if not md.exists():
        print(f"Missing {md}")
        return
    if not jsn.exists():
        print(f"Missing {jsn}")
        return

    # Backup
    bak.write_bytes(jsn.read_bytes())
    print(f"Backup: {bak}")

    data = json.loads(jsn.read_text(encoding="utf-8"))
    entries = {e["id"]: e for e in data["entries"]}

    pairs = parse_md(md)
    print(f"Found {len(pairs)} pairs")

    changed = 0
    for orig_id, quote_id in pairs:
        if orig_id not in entries or quote_id not in entries:
            continue
        orig_new = entries[orig_id].get("new", "").strip()
        quote_new = entries[quote_id].get("new", "").strip()
        if orig_new and orig_new != quote_new:
            entries[quote_id]["new"] = orig_new
            changed += 1

    jsn.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Unified {changed} entries")
    print("Done. Check with: python show_diff.py all_entries.before_unify.json all_entries.json")

if __name__ == "__main__":
    main()
