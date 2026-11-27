#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply the fixes recorded in 汉化笔记2.md to all_entries.json.

Usage:
    python review/apply_notes.py            # dry run, report matches only
    python review/apply_notes.py --write    # apply and save
"""
import argparse
import json
import re
import sys

NOTES = r"C:\Users\Amadeus\Desktop\汉化笔记2.md"
ENTRIES = "all_entries.json"


def norm(s):
    s = s.replace("『", "「").replace("』", "」")
    s = re.sub(r"\{[^}]*\}", "", s)          # ignore Ren'Py tags when matching
    return re.sub(r"\s+", "", s)


def parse_notes(path):
    """Return list of (current, target) blocks. Blocks are '> ' quoted lines."""
    text = open(path, encoding="utf-8").read()
    tokens = []          # ("block", text) or ("sep",)
    buf = []
    for line in text.splitlines():
        s = line.strip()
        if s == "应为":
            if buf:
                tokens.append(("block", "\n".join(buf)))
                buf = []
            tokens.append(("sep",))
            continue
        if s.startswith(">"):
            t = s[1:].strip()
            if t:
                buf.append(t)
            continue
        if buf:
            tokens.append(("block", "\n".join(buf)))
            buf = []
    if buf:
        tokens.append(("block", "\n".join(buf)))

    pairs = []
    for i, tok in enumerate(tokens):
        if tok[0] == "block" and i + 2 < len(tokens) and tokens[i + 1][0] == "sep" and tokens[i + 2][0] == "block":
            pairs.append((tok[1], tokens[i + 2][1]))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    data = json.load(open(ENTRIES, encoding="utf-8"))
    entries = data["entries"]

    by_norm = {}
    for e in entries:
        by_norm.setdefault(norm(e.get("new") or ""), []).append(e)

    pairs = parse_notes(NOTES)
    print("笔记里 %d 组\n" % len(pairs))

    applied = []
    for cur, tgt in pairs:
        # a note block may contain several paragraphs -> several entries
        cur_parts = [p for p in re.split(r"\n+", cur) if p.strip()]
        tgt_parts = [p for p in re.split(r"\n+", tgt) if p.strip()]
        if len(cur_parts) != len(tgt_parts):
            print("!! 段落数不一致，跳过：", cur[:40])
            continue
        for c, t in zip(cur_parts, tgt_parts):
            hits = by_norm.get(norm(c), [])
            hits = [h for h in hits if h.get("group") == "story"]
            if len(hits) != 1:
                print("!! 命中 %d 条：%s" % (len(hits), c[:40]))
                continue
            applied.append((hits[0], c, t))

    print("可应用 %d 条\n" % len(applied))
    for e, c, t in applied:
        print("L%s  %s" % (re.search(r"_L(\d+)_", e["id"]).group(1), e["id"]))
        print("   旧：", c[:60])
        print("   新：", t[:60])

    # term: 断路器 -> 电闸
    term_hits = [e for e in entries if "断路器" in (e.get("new") or "")]
    print("\n断路器 -> 电闸：%d 处" % len(term_hits))

    if args.write:
        import re as _re
        TAG = _re.compile(r"\{[^}]*\}")
        for e, c, t in applied:
            old_text = e["new"]
            tags = TAG.findall(old_text)
            if tags and not TAG.search(t):
                # re-insert tags at proportional positions
                positions = [m.start() for m in TAG.finditer(old_text)]
                insert = []
                for tag, pos in zip(tags, positions):
                    insert.append((int(pos / max(1, len(old_text)) * len(t)), tag))
                for pos, tag in sorted(insert, reverse=True):
                    t = t[:pos] + tag + t[pos:]
                print("   补回标签 %s -> %s" % (e["id"], tags))
            e["new"] = t
        for e in term_hits:
            e["new"] = e["new"].replace("断路器", "电闸")

        # mechanical fixes recorded by review/make_consistency.py
        mech = 0
        tsv = "review/机械修正.tsv"
        try:
            rows = open(tsv, encoding="utf-8").read().splitlines()[1:]
            by_id = {e["id"]: e for e in entries}
            for row in rows:
                parts = row.split("\t")
                if len(parts) < 6:
                    continue
                _code, eid, _line, _note, before, after = parts[:6]
                e = by_id.get(eid)
                if e and e.get("new") == before:
                    e["new"] = after
                    mech += 1
        except FileNotFoundError:
            pass

        json.dump(data, open(ENTRIES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("\n已写入。改了 %d 条 + %d 处术语 + %d 处机械修正。" % (len(applied), len(term_hits), mech))


if __name__ == "__main__":
    main()
