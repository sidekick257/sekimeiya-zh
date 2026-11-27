#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 all_entries.json 生成 Ren'Py 的 translate zh_cn strings: 表。

输出 patch/tl/zh_cn/strings_script.rpy。同一句英文只保留一条（按出现顺序取第一条译文）。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "all_entries.json")
OUT = os.path.join(HERE, "patch", "tl", "zh_cn", "strings_script.rpy")

HEADER = """\
# 自动生成，不要手改。改翻译请改 all_entries.json 后运行 sync_patch.py。

translate zh_cn strings:
"""


def esc(s):
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return '"%s"' % "".join(out)


def main():
    entries = [e for e in json.load(open(SRC, encoding="utf-8"))["entries"]
               if e.get("group") == "story" and (e.get("new") or "").strip()]
    seen = {}
    for e in entries:
        old = e["text"]
        if old in seen:
            continue
        seen[old] = e["new"]

    lines = [HEADER]
    for old, new in seen.items():
        lines.append("    old %s\n    new %s\n" % (esc(old), esc(new)))
    text = "\n".join(lines)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("Wrote %d unique string pairs to %s" % (len(seen), OUT))


if __name__ == "__main__":
    main()
