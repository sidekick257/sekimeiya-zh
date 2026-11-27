#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detect mis-aligned (串行) translations across the whole book.

Signals:
  DUP   近似的译文出现在两处，但两处英文差很多  -> 典型串行
  LEN   译文长度与英文严重不成比例
  TAG   Ren'Py 标签与原文不一致
  NUM   数字一边有一边没有
  QUOTE 引号数量不一致

Usage: python detect_misalign.py [--out review/misalign.md]
Read-only.
"""
import argparse
import json
import re
from collections import Counter, defaultdict

TAG = re.compile(r"\{[^}]*\}")
CJK = re.compile(r"[\u3400-\u9fff]")
NAMES = ["Atsuki", "Shiroya", "Akaro", "Naomi", "Sai", "Erina", "Isla", "Katei",
         "Miiya", "Tanya", "Ido", "Gan", "Lei", "Darfee", "Kyuuka", "Vaisude",
         "Maxi", "Faiten", "Jiro", "Larles", "Umi", "Amelie", "Anora", "Asfu",
         "Cevin", "Neneco", "Dote", "Stanley", "Zane"]
NAME_RE = re.compile(r"\b(" + "|".join(NAMES) + r")\b")


def norm_zh(s):
    s = TAG.sub("", s)
    return re.sub(r"[^\u3400-\u9fffA-Za-z0-9]", "", s)


def words(s):
    s = TAG.sub("", s).lower()
    return set(re.findall(r"[a-z0-9]+", s))


def grams(s, n=4):
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="all_entries.json")
    ap.add_argument("--out", default="review/misalign.md")
    args = ap.parse_args()

    data = json.load(open(args.source, encoding="utf-8"))
    story = [e for e in data["entries"] if e.get("group") == "story"]
    story.sort(key=lambda e: int(re.search(r"_L(\d+)_", e["id"]).group(1)))
    for i, e in enumerate(story, 1):
        e["_n"] = i
        e["_line"] = int(re.search(r"_L(\d+)_", e["id"]).group(1))
        e["_z"] = norm_zh(e["new"])
        e["_w"] = words(e["text"])

    cands = []

    # ---------- DUP: near-identical Chinese, different English ----------
    index = defaultdict(list)
    for i, e in enumerate(story):
        if len(e["_z"]) >= 12:
            for g in grams(e["_z"]):
                index[g].append(i)
    seen = set()
    for i, e in enumerate(story):
        z = e["_z"]
        if len(z) < 20:
            continue
        gs = grams(z)
        cnt = Counter()
        for g in gs:
            for j in index[g]:
                if j != i:
                    cnt[j] += 1
        for j, c in cnt.items():
            if j < i:
                continue
            if len(gs) > 0 and c / len(gs) < 0.6:
                continue
            key = (i, j)
            if key in seen:
                continue
            seen.add(key)
            other = story[j]
            sim = c / max(1, len(gs | grams(other["_z"])))
            if sim < 0.62:
                continue
            en_sim = len(e["_w"] & other["_w"]) / max(1, len(e["_w"] | other["_w"]))
            if en_sim > 0.45:
                continue
            cands.append({
                "code": "DUP", "sev": "高", "a": e, "b": other,
                "note": "两处译文相似度 %.0f%%，原文相似度 %.0f%%" % (sim * 100, en_sim * 100),
            })

    # ---------- LEN ----------
    for e in story:
        w = len([x for x in e["_w"] if len(x) > 1 or x.isdigit()])
        c = len(CJK.findall(TAG.sub("", e["new"])))
        if w >= 6:
            r = c / w
            if r > 3.2 or r < 0.38:
                cands.append({"code": "LEN", "sev": "中", "a": e, "b": None,
                              "note": "中英长度比 %.1f（英文 %d 词 / 中文 %d 字）" % (r, w, c)})

    # ---------- TAG ----------
    for e in story:
        a, b = Counter(TAG.findall(e["text"])), Counter(TAG.findall(e["new"]))
        if a != b:
            diff = []
            if a - b:
                diff.append("缺 " + " ".join(sorted((a - b).elements())))
            if b - a:
                diff.append("多 " + " ".join(sorted((b - a).elements())))
            cands.append({"code": "TAG", "sev": "高", "a": e, "b": None,
                          "note": "；".join(diff)})

    # ---------- NUM ----------
    def digits(s):
        s = TAG.sub("", s)
        return sorted(re.findall(r"\d+", s))
    for e in story:
        de, dz = digits(e["text"]), digits(e["new"])
        if de and not dz:
            cands.append({"code": "NUM", "sev": "低", "a": e, "b": None,
                          "note": "原文有数字 %s，译文没有" % ",".join(de)})
        elif dz and not de:
            cands.append({"code": "NUM", "sev": "低", "a": e, "b": None,
                          "note": "译文有数字 %s，原文没有" % ",".join(dz)})

    # ---------- QUOTE ----------
    for e in story:
        qe = e["text"].count('"') + e["text"].count("“")
        qz = e["new"].count("「")
        if qe and not qz:
            cands.append({"code": "QUOTE", "sev": "低", "a": e, "b": None,
                          "note": "原文是引语，译文没有「」"})

    order = {"高": 0, "中": 1, "低": 2}
    cands.sort(key=lambda c: (order.get(c["sev"], 9), c["a"]["_line"]))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# 串行 / 错位排查\n\n")
        f.write("共 %d 个候选（只读分析，未改动任何文件）。\n\n" % len(cands))
        for code in ["DUP", "LEN", "TAG", "NUM", "QUOTE"]:
            sub = [c for c in cands if c["code"] == code]
            if not sub:
                continue
            f.write("## %s（%d）\n\n" % (code, len(sub)))
            for c in sub[:60]:
                a = c["a"]
                f.write("### %s  n=%d  script.rpy:%d\n\n" % (code, a["_n"], a["_line"]))
                if c["b"] is not None:
                    b = c["b"]
                    f.write("- 对照 n=%d  script.rpy:%d\n\n" % (b["_n"], b["_line"]))
                    f.write("  - EN: %s\n" % b["text"])
                    f.write("  - ZH: %s\n\n" % b["new"])
                f.write("  - 本条 EN: %s\n" % a["text"])
                f.write("  - 本条 ZH: %s\n" % a["new"])
                f.write("  - 说明: %s\n\n" % c["note"])
            if len(sub) > 60:
                f.write("（同组还有 %d 条，见 JSON）\n\n" % (len(sub) - 60))

    json.dump([{k: v for k, v in c.items() if k not in ("a", "b")} |
               {"n": c["a"]["_n"], "line": c["a"]["_line"],
                "n2": (c["b"]["_n"] if c["b"] else None),
                "line2": (c["b"]["_line"] if c["b"] else None),
                "id": c["a"]["id"]}
               for c in cands],
              open(args.out.replace(".md", ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("candidates:", len(cands))
    print(Counter(c["code"] for c in cands))
    for c in cands[:15]:
        a = c["a"]
        print("%-6s n=%-6d L%-6d %s" % (c["code"], a["_n"], a["_line"], c["note"][:50]))


if __name__ == "__main__":
    main()
