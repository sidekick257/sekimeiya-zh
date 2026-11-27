#!/usr/bin/env python3
import json
from pathlib import Path

SRC = Path("all_entries.json")
OUT_DIR = Path("output/tl/zh_cn")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "script.rpy"

data = json.loads(SRC.read_text(encoding="utf-8"))
entries = data.get("entries", [])

story = [
    e for e in entries
    if "story" in (str(e.get("group") or "") + str(e.get("source_file") or "")).lower()
    and str(e.get("new") or "").strip()
]

lines = ["# Dialogue translations", ""]
count = 0
for e in story:
    eid = e.get("id", "")
    old = str(e.get("text") or "").replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    new = str(e.get("new") or "").replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    if not old or not new:
        continue
    lines.append(f'translate zh_cn {eid}:')
    lines.append(f'    # "{old}"')
    lines.append(f'    "{new}"')
    lines.append("")
    count += 1

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {count} dialogue blocks")