#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Global consistency scan -> mechanical fix list + severe issue list.

Reads all_entries.json (read-only), writes:
    review/机械修正.tsv        unambiguous find/replace, safe to batch apply
    review/严重问题.md          misapplied lines, tag loss, length outliers
    review/重复引用不一致.tsv    same English, different Chinese

Usage: python review/make_consistency.py
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MECH = [
    ("TERM_走廊空格", re.compile(r"([ABC])\s+走廊"), lambda m: m.group(1) + "走廊",
     "A走廊 不留空格"),
    ("TERM_过去未来空格", re.compile(r"(过去|未来)\s+Sekimeiya"), lambda m: m.group(1) + "Sekimeiya",
     "过去Sekimeiya 不留空格"),
    ("QT_直角引号", re.compile(r"『"), lambda m: "「", "引号统一「」"),
    ("QT_直角引号", re.compile(r"』"), lambda m: "」", "引号统一「」"),
    ("TERM_幕布", re.compile(r"幕布"), lambda m: "遮布", "curtain 用「遮布」"),
    ("TERM_水晶室", re.compile(r"水晶(?:展厅|展览室|展示室|陈列室)"), lambda m: "水晶展室",
     "crystal room 用「水晶展室」"),
    ("TERM_芦屋塔", re.compile(r"芦屋(?:大厦|之塔|高塔)"), lambda m: "芦屋塔", "Ashiya Tower 用「芦屋塔」"),
]

def main():
    data = json.load(open(os.path.join(ROOT, "all_entries.json"), encoding="utf-8"))
    story = [e for e in data["entries"] if e.get("group") == "story"]
    story.sort(key=lambda e: int(re.search(r"_L(\d+)_", e["id"]).group(1)))

    rows = []
    for e in story:
        if not e["new"].strip():
            continue
        cur = e["new"]
        for code, pat, repl, note in MECH:
            if not pat.search(cur):
                continue
            new = pat.sub(repl, cur)
            if new != cur:
                rows.append((code, e["id"], int(re.search(r"_L(\d+)_", e["id"]).group(1)),
                             note, cur, new))
                cur = new

    with open(os.path.join(HERE, "机械修正.tsv"), "w", encoding="utf-8") as f:
        f.write("code\tid\tline\tnote\tbefore\tafter\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    print("mechanical fixes:", len(rows))

    # severe
    severe = []
    tag_re = re.compile(r"\{[^}]*\}")
    for e in story:
        en, zh = e["text"], e["new"]
        if not zh.strip():
            severe.append(("EMPTY", e, "译文为空"))
            continue
        a, b = tag_re.findall(en), tag_re.findall(zh)
        if sorted(a) != sorted(b):
            severe.append(("TAG", e, "标签不一致 原文%s / 译文%s" % (a, b)))
        w = len(re.findall(r"[A-Za-z']+", tag_re.sub("", en)))
        c = len(re.findall(r"[\u4e00-\u9fff]", zh))
        if w >= 6 and c / w > 3.2:
            severe.append(("MISAPPLY?", e, "长度比 %.1f，疑似串行" % (c / w)))
    with open(os.path.join(HERE, "严重问题.md"), "w", encoding="utf-8") as f:
        f.write("# 严重问题（错位 / 标签 / 疑似串行）\n\n")
        f.write("共 %d 条。这类问题必须人工确认，不能批量改。\n\n" % len(severe))
        for code, e, msg in severe:
            f.write("## %s  L%d  %s\n\n" % (code, int(re.search(r"_L(\d+)_", e["id"]).group(1)), e["id"]))
            f.write("- 原文：%s\n" % e["text"].replace("\n", " "))
            f.write("- 现译：%s\n" % e["new"].replace("\n", " "))
            f.write("- 说明：%s\n\n" % msg)
    print("severe:", len(severe))

    # reuse inconsistency
    groups = defaultdict(list)
    for e in story:
        if e["new"].strip():
            key = re.sub(r"\s+", " ", tag_re.sub("", e["text"]).lower()).strip()
            groups[key].append(e)
    n_group = 0
    with open(os.path.join(HERE, "重复引用不一致.tsv"), "w", encoding="utf-8") as f:
        f.write("group\tn\tid\tline\tzh\n")
        for key, g in groups.items():
            if len(g) < 2:
                continue
            d = {re.sub(r"\s+", "", tag_re.sub("", x["new"])) for x in g}
            if len(d) < 2:
                continue
            n_group += 1
            for x in g:
                f.write("%d\t%d\t%s\t%d\t%s\n" % (
                    n_group, len(d), x["id"],
                    int(re.search(r"_L(\d+)_", x["id"]).group(1)),
                    x["new"].replace("\t", " ").replace("\n", " ")))
    print("reuse groups:", n_group)

    # lobby wording
    tang = [e for e in story if "大堂" in e["new"]]
    print("大堂:", len(tang), " 大厅:", sum(1 for e in story if "大厅" in e["new"]))

if __name__ == "__main__":
    main()
