#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only rule audit for the Chinese translation in all_entries.json.

Usage:
    python audit_zh.py                      # whole book, markdown to stdout
    python audit_zh.py --start 1 --end 500  # first 500 story entries
    python audit_zh.py --json review/audit.json --md review/audit.md

Never writes to all_entries.json or the .rpy files.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict

TAG_RE = re.compile(r"\{[^}]*\}")
CJK_RE = re.compile(r"[\u3400-\u9fff]")

NAMES = [
    "Atsuki", "Shiroya", "Akaro", "Naomi", "Sai", "Erina", "Isla", "Katei",
    "Miiya", "Tanya", "Yomiya", "Hakutoki", "Mirana", "Cabca", "Esata",
    "Majutsu", "Moiromo", "Suripo", "Atase", "Ido", "Gan", "Lei", "Darfee",
    "Kyuuka", "Vaisude", "Maxi", "Faiten", "Jiro", "Larles", "Umi", "Amelie",
    "Anora", "Asfu", "Cevin", "Neneco", "Dote", "Stanley", "Zane",
]
NAME_SPLIT_RE = re.compile(r"(" + "|".join(sorted(NAMES, key=len, reverse=True)) + r")")

# (code, severity, regex, note)
TERM_RULES = [
    ("TERM_幕布", "高", r"幕布", "velvet curtain / 可掀起的 curtain 应为「遮布」"),
    ("TERM_水晶室", "高", r"水晶(展厅|展览室|展示室|陈列室)", "crystal room 应为「水晶展室」"),
    ("TERM_走廊空格", "中", r"[ABC]\s+走廊", "hallway A/B/C 应为 A走廊（不留空格）"),
    ("TERM_过去未来空格", "中", r"(过去|未来)\s+Sekimeiya", "应为「过去Sekimeiya」/「未来Sekimeiya」，中间不留空格"),
    ("TERM_量词", "中", r"([台块枚]\s*Sekimeiya|Sekimeiya\s*[台块枚])", "Sekimeiya 的量词统一用「个」"),
    ("TERM_您", "高", r"您", "全篇不用「您」"),
    ("TERM_Tanya", "高", r"\bTanya\b", "Tanya 应译「坦桑娅」"),
    ("TERM_芦屋塔", "中", r"(芦屋大厦|芦屋之塔|芦屋高塔)", "Ashiya Tower 应为「芦屋塔」"),
    ("TERM_展柜", "中", r"(展柜|陈列柜)", "cabinet 应为「展示柜」"),
    ("TERM_阁楼", "低", r"(顶楼|阁楼间)", "attic 应为「阁楼」"),
]

PUNCT_RULES = [
    ("PUNCT_半角逗号", "中", r"[\u4e00-\u9fff],"),
    ("PUNCT_半角句号", "中", r"[\u4e00-\u9fff]\."),
    ("PUNCT_半角问号", "中", r"[\u4e00-\u9fff]\?"),
    ("PUNCT_半角感叹", "中", r"[\u4e00-\u9fff]!"),
    ("PUNCT_三点省略", "中", r"\.\.\."),
    ("PUNCT_重复句号", "低", r"。。"),
    ("PUNCT_重复问号", "低", r"？？"),
    ("QT_直角引号", "低", r"『"),
]

# markers that usually read as translationese / stiff narration
STYLE_MARKERS = ["在我们看来", "结局"]

def zh_len(s):
    return len(CJK_RE.findall(s))

def en_words(s):
    s = TAG_RE.sub("", s)
    return len(re.findall(r"[A-Za-z']+", s))

def norm_text(s):
    s = TAG_RE.sub("", s).lower()
    return re.sub(r"\s+", " ", s).strip()

def norm_zh(s):
    s = TAG_RE.sub("", s)
    return re.sub(r"\s+", "", s)

def load(path):
    data = json.load(open(path, encoding="utf-8"))
    entries = [e for e in data["entries"] if e.get("group") == "story"]
    def line(e):
        m = re.search(r"_L(\d+)_", e["id"])
        return int(m.group(1)) if m else 0
    entries.sort(key=line)
    return entries, line

def audit(entries, line):
    issues = []
    def add(e, code, sev, msg):
        issues.append({
            "n": None, "id": e["id"], "line": line(e), "code": code,
            "sev": sev, "msg": msg, "text": e["text"], "new": e["new"],
        })

    for e in entries:
        en, zh = e["text"], e["new"]
        if not zh.strip():
            add(e, "EMPTY", "高", "译文为空")
            continue
        # tags
        a, b = Counter(TAG_RE.findall(en)), Counter(TAG_RE.findall(zh))
        if a != b:
            missing = a - b
            extra = b - a
            bits = []
            if missing:
                bits.append("缺 " + " ".join(sorted(missing.elements())))
            if extra:
                bits.append("多 " + " ".join(sorted(extra.elements())))
            add(e, "TAG", "高", "标签不一致：" + "；".join(bits))
        # terms
        for code, sev, pat, note in TERM_RULES:
            if re.search(pat, zh):
                add(e, code, sev, note)
        # punctuation
        for code, sev, pat in PUNCT_RULES:
            if re.search(pat, zh):
                add(e, code, sev, "标点")
        # style markers (low)
        hits = [m for m in STYLE_MARKERS if m in zh]
        if hits:
            add(e, "STYLE", "低", "书面腔标记：" + "、".join(hits))
        # untranslated (ignore lines that are only names / ellipsis)
        if zh_len(zh) == 0 and re.search(r"[A-Za-z]{4,}", zh):
            stripped = NAME_SPLIT_RE.sub("", TAG_RE.sub("", zh))
            stripped = re.sub(r"[\s\W\d_]+", "", stripped, flags=re.UNICODE)
            if stripped:
                add(e, "NO_ZH", "中", "译文没有中文")
        # length outlier
        w = en_words(en)
        if w >= 6:
            r = zh_len(zh) / w
            if r > 2.9:
                add(e, "LEN_LONG", "低", f"长度比 {r:.1f}（中文偏长，可能加戏或串行）")
            elif r < 0.45:
                add(e, "LEN_SHORT", "低", f"长度比 {r:.1f}（中文偏短，可能漏译）")

    # duplicates: same English, different Chinese
    by_en = defaultdict(list)
    for e in entries:
        if e["new"].strip():
            by_en[norm_text(e["text"])].append(e)
    for key, group in by_en.items():
        if len(group) < 2:
            continue
        distinct = {norm_zh(g["new"]) for g in group}
        if len(distinct) > 1:
            add(group[0], "REUSE_DIFF", "中",
                "同一句英文有 %d 种译法（%s）" % (
                    len(distinct), ", ".join(g["id"] for g in group[:6])))

    # duplicates: same Chinese, very different English (possible misapply)
    by_zh = defaultdict(list)
    for e in entries:
        if e["new"].strip():
            by_zh[norm_zh(e["new"])].append(e)
    for key, group in by_zh.items():
        if len(group) < 2:
            continue
        base = set(re.findall(r"[a-z0-9]+", norm_text(group[0]["text"])))
        for g in group[1:]:
            other = set(re.findall(r"[a-z0-9]+", norm_text(g["text"])))
            if not base or not other:
                continue
            j = len(base & other) / len(base | other)
            if j < 0.25 and abs(len(g["text"]) - len(group[0]["text"])) > 40:
                add(g, "MISAPPLY", "高",
                    "与 %s 译文完全相同但原文差异很大（jaccard %.2f）"
                    % (group[0]["id"], j))
    issues.sort(key=lambda x: x["line"])
    return issues

def render(issues, entries, start, end, out):
    counts = Counter(i["code"] for i in issues)
    out.append("# 译文规则审查报告\n")
    out.append("范围：第 %d–%d 条（script.rpy 第 %d–%d 行），共 %d 条\n" % (
        start, end, entries[start - 1]["__line"], entries[end - 1]["__line"], end - start + 1))
    out.append("问题总数：%d\n" % len(issues))
    out.append("| 代码 | 数量 |\n|---|---|")
    for code, n in counts.most_common():
        out.append("| %s | %d |" % (code, n))
    out.append("")
    for i in issues:
        out.append("### [%s] script.rpy:%d  `%s`" % (i["sev"], i["line"], i["code"]))
        out.append("- 原文：%s" % i["text"].replace("\n", " "))
        out.append("- 现译：%s" % i["new"].replace("\n", " "))
        out.append("- 说明：%s" % i["msg"])
        out.append("")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="all_entries.json")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--json", default="")
    ap.add_argument("--md", default="")
    args = ap.parse_args()

    entries, line = load(args.source)
    for e in entries:
        e["__line"] = line(e)
    end = args.end or len(entries)
    subset = entries[args.start - 1:end]
    issues = audit(subset, line)
    for idx, e in enumerate(entries, 1):
        pass
    # number issues by their position inside subset
    pos = {e["id"]: n for n, e in enumerate(entries, 1)}
    for i in issues:
        i["n"] = pos[i["id"]]

    if args.json:
        json.dump(issues, open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = []
    render(issues, entries, args.start, end, out)
    text = "\n".join(out)
    if args.md:
        open(args.md, "w", encoding="utf-8").write(text)
    if not args.md:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)

if __name__ == "__main__":
    main()
