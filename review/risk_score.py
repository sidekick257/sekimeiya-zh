#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Score each story entry by how likely its Chinese is to be problematic.

Pure surface statistics: length, connective density, clause count, long
attributives, Ren'Py tags. No model involved.

Usage:
    python review/risk_score.py                      # report percentiles of known-bad lines
    python review/risk_score.py --top 300 --out review/risk_top.md
"""
import argparse
import json
import re

CONN = ["如果", "那么", "要是", "但", "可是", "却", "而", "因为", "所以", "才", "总算",
        "毕竟", "难道", "既然", "虽然", "不过", "于是", "然后", "除非", "即使",
        "还是", "只是", "就是", "并不", "并未", "以及", "而且", "并且", "于是",
        "反而", "甚至", "然而", "因此", "假如", "万一", "否则", "哪怕"]

TAG = re.compile(r"\{[^}]*\}")


def score(e):
    zh = e.get("new") or ""
    en = e.get("text") or ""
    plain = TAG.sub("", zh)
    n = len(re.findall(r"[\u4e00-\u9fff]", plain))
    conn = sum(plain.count(c) for c in CONN)
    clauses = plain.count("，") + plain.count("；") + plain.count("——") + plain.count("……")
    de = plain.count("的")
    tags = len(TAG.findall(zh))
    words = len(re.findall(r"[A-Za-z']+", TAG.sub("", en)))
    # 长定语：连续「的」之间隔得远，粗略用 de 的数量
    s = (n * 1.0 + conn * 6 + clauses * 3 + de * 2 + tags * 4
         + max(0, n - 60) * 0.5 + max(0, words - 20) * 0.3)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    entries = [e for e in json.load(open("all_entries.json", encoding="utf-8"))["entries"]
               if e.get("group") == "story" and (e.get("new") or "").strip()]
    entries.sort(key=lambda e: int(re.search(r"_L(\d+)_", e["id"]).group(1)))
    for e in entries:
        e["_score"] = score(e)
        e["_line"] = int(re.search(r"_L(\d+)_", e["id"]).group(1))

    ranked = sorted(entries, key=lambda e: -e["_score"])
    total = len(ranked)
    pos = {e["id"]: i + 1 for i, e in enumerate(ranked)}

    known = [652, 735, 880, 959, 960, 1054, 1079, 1100, 1509, 1648, 1736, 1779,
             1813, 1828, 678, 713, 780, 786, 818, 819, 881, 904]
    print("总条数 %d\n" % total)
    print("已知问题句的排名 / 分位：")
    for e in entries:
        if e["_line"] in known:
            r = pos[e["id"]]
            print("  L%-6d  第 %5d 名  前 %.1f%%  分数 %.0f" % (e["_line"], r, 100.0 * r / total, e["_score"]))

    for pct in (0.05, 0.1, 0.2, 0.3):
        cut = int(total * pct)
        hit = sum(1 for e in entries if e["_line"] in known and pos[e["id"]] <= cut)
        print("\n前 %d%%（%d 条）覆盖了 %d/%d 条已知问题" % (pct * 100, cut, hit, len(known)))

    if args.top:
        lines = ["# 高危句（按表面风险排序，前 %d 条）\n" % args.top]
        for e in ranked[:args.top]:
            lines.append("## L%d　分数 %.0f" % (e["_line"], e["_score"]))
            lines.append("")
            lines.append(e["new"].replace("\n", " "))
            lines.append("")
        open(args.out, "w", encoding="utf-8").write("\n".join(lines))
        print("\n已写出", args.out)


if __name__ == "__main__":
    main()
