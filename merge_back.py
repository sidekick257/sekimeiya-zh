#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Map translated `new` fields back into Ren'Py files by stable id.

Reads the sidecar map plus the (now filled) all_entries.json and writes:

  output/tl/zh_cn/     official-style  translate zh_cn strings:  files
                       plus 00_hook.rpy so say/menu use that table
  output/patched/      copies of the original .rpy with Chinese
                       substituted at the exact source locations

Do not use both methods at once in the same game folder.

    python merge_back.py
    python merge_back.py --input all_entries.json --source-dir source --out output

Only entries with a non-empty `new` are written. Empty ones stay English.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_map(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "entries" in data:
        items = data["entries"]
    elif isinstance(data, list):
        items = data
    else:
        items = data.get("map") or data.get("items") or []
    return {e["id"]: e for e in items}


def load_translations_from_file(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("entries") if isinstance(data, dict) else data
    out = {}
    for e in items or []:
        new = e.get("new")
        if isinstance(new, str) and new.strip() != "":
            out[e["id"]] = new
    return out


def load_translations(input_path: Path) -> dict[str, str]:
    if input_path.is_file():
        return load_translations_from_file(input_path)
    out = {}
    for path in sorted(input_path.rglob("*.json")):
        out.update(load_translations_from_file(path))
    return out


def renpy_escape(s: str, quote: str = '"') -> str:
    """Write a Ren'Py/Python string literal (single or double quote)."""
    if quote in ('"""', "'''"):
        body = s.replace("\r\n", "\n")
        # Avoid accidentally closing the triple quote
        if quote == '"""':
            body = body.replace('"""', '\\"""')
        else:
            body = body.replace("'''", "\\'''")
        return quote + body + quote
    q = quote if quote in ('"', "'") else '"'
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == q:
            out.append("\\" + q)
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return q + "".join(out) + q


def game_comment_path(source_file: str) -> str:
    # Comments in official tl files look like: # game/script.rpy:123
    rel = source_file.replace("\\", "/")
    if not rel.startswith("game/"):
        rel = "game/" + rel
    return rel


def write_tl(out_tl: Path, mapping: dict, translations: dict[str, str]) -> tuple[int, int]:
    """Write one strings file per source, plus a hook. Dedupe by old text per file."""
    out_tl.mkdir(parents=True, exist_ok=True)
    hook = '''# Auto-generated hook: look up say/menu text in the string translation table.
# Copy the whole tl/zh_cn folder to:  <game>/game/tl/zh_cn/
#
# This covers dialogue, menu choices, and strings already wrapped in _().
# Notes, tip titles, SceneTitle, and some UI literals are NOT wrapped in _()
# in the original game — use output/patched/ for those (do not mix both methods).

init 999 python:
    config.say_menu_text_filter = _
'''
    (out_tl / "00_hook.rpy").write_text(hook.replace("\n", "\r\n"), encoding="utf-8")

    by_src = defaultdict(list)
    for eid, new in translations.items():
        rec = mapping.get(eid)
        if not rec:
            continue
        by_src[rec["source_file"]].append((rec, new))

    files = 0
    pairs = 0
    for src, items in sorted(by_src.items()):
        # Dedupe by original text; first translation wins
        seen = {}
        ordered = []
        for rec, new in sorted(items, key=lambda x: (x[0]["line"], x[0]["id"])):
            key = rec["text"]
            if key in seen:
                continue
            seen[key] = new
            ordered.append((rec, new))
        stem = Path(src).name
        # scripts/screens.rpy -> screens.rpy
        out_name = stem
        if not out_name.endswith(".rpy"):
            out_name += ".rpy"
        # prefix to keep hook first
        dest = out_tl / f"strings_{out_name}"
        lines = [
            f"# Generated from {src}. Fill results of translate_batch.py.",
            f"# Place this file in game/tl/zh_cn/ together with 00_hook.rpy.",
            "",
            "translate zh_cn strings:",
            "",
        ]
        for rec, new in ordered:
            comment = f"    # {game_comment_path(rec['source_file'])}:{rec['line']}"
            lines.append(comment)
            lines.append(f"    old {renpy_escape(rec['text'], '"')}")
            lines.append(f"    new {renpy_escape(new, '"')}")
            lines.append("")
            pairs += 1
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        files += 1
    return files, pairs


def write_patched(source_dir: Path, out_dir: Path, mapping: dict, translations: dict[str, str]) -> tuple[int, int]:
    """Replace exact source literals, file by file, from the end so offsets stay valid."""
    by_src = defaultdict(list)
    missing_src = 0
    for eid, new in translations.items():
        rec = mapping.get(eid)
        if not rec:
            continue
        by_src[rec["source_file"]].append((rec, new))

    written = 0
    replaced = 0
    for src_rel, items in sorted(by_src.items()):
        src_path = source_dir / src_rel
        if not src_path.is_file():
            print(f"  Warning: source not found, skipped: {src_path}", file=sys.stderr)
            missing_src += 1
            continue
        # Preserve original CRLF / encoding
        text = src_path.read_bytes().decode("utf-8-sig")
        # Sort by start descending; skip overlaps
        items = sorted(items, key=lambda x: x[0]["start"], reverse=True)
        used_spans = []
        for rec, new in items:
            start, end = rec["start"], rec["end"]
            original = rec.get("literal") or text[start:end]
            if text[start:end] != original:
                # Try to locate the literal nearby (in case of offset drift)
                print(
                    f"  Warning: literal mismatch {src_rel}:{rec['line']} id={rec['id']}; skipped.",
                    file=sys.stderr,
                )
                continue
            quote = rec.get("quote") or '"'
            new_lit = renpy_escape(new, quote)
            # If original triple-quoted used CRLF inside, keep CRLF in the replacement body
            if quote in ('"""', "'''") and "\r\n" in original:
                inner_start = len(quote)
                inner_end = len(new_lit) - len(quote)
                body = new_lit[inner_start:inner_end].replace("\n", "\r\n")
                new_lit = quote + body + quote
            text = text[:start] + new_lit + text[end:]
            replaced += 1
        dest = out_dir / src_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(text.encode("utf-8"))
        written += 1
    if missing_src:
        print(f"  {missing_src} source files were missing.", file=sys.stderr)
    return written, replaced


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Merge translated JSON back into Ren'Py files.")
    parser.add_argument("--input", type=Path, default=here / "all_entries.json",
                        help="Filled all_entries.json (or a directory of chunk JSON files)")
    parser.add_argument("--map", type=Path, default=here / "map" / "entries_map.json")
    parser.add_argument("--source-dir", type=Path, default=here / "source")
    parser.add_argument("--out", type=Path, default=here / "output")
    args = parser.parse_args()

    if not args.map.is_file():
        sys.exit(f"ERROR: map not found: {args.map}")
    if not args.input.exists():
        sys.exit(f"ERROR: translations not found: {args.input}")

    mapping = load_map(args.map)
    translations = load_translations(args.input)
    total_map = len(mapping)
    total_new = len(translations)
    print(f"Map entries: {total_map}. Translated (non-empty new): {total_new}.")
    if total_new == 0:
        print("No translations found. Run translate_batch.py first, then merge_back.py again.")
        # Still create empty output dirs so the path is obvious
        (args.out / "tl" / "zh_cn").mkdir(parents=True, exist_ok=True)
        (args.out / "patched").mkdir(parents=True, exist_ok=True)
        return

    unknown = [eid for eid in translations if eid not in mapping]
    if unknown:
        print(f"Warning: {len(unknown)} translated ids are not in the map (ignored).", file=sys.stderr)

    tl_dir = args.out / "tl" / "zh_cn"
    patched_dir = args.out / "patched"
    nfiles, npairs = write_tl(tl_dir, mapping, translations)
    print(f"Wrote {npairs} unique string pairs in {nfiles} files under {tl_dir}")

    if not args.source_dir.is_dir():
        print(f"Source dir not found ({args.source_dir}); skipped patched/ output.")
        print("Pass --source-dir pointing at the extracted .rpy files to build patched scripts.")
    else:
        nwritten, nrepl = write_patched(args.source_dir, patched_dir, mapping, translations)
        print(f"Wrote {nwritten} patched rpy files ({nrepl} replacements) under {patched_dir}")

    remaining = total_map - total_new
    if remaining > 0:
        print(f"Note: {remaining} entries still have empty new and were left in English.")
    print("Done.")


if __name__ == "__main__":
    main()
