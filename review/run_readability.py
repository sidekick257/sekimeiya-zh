#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run the readability prompt over a range of entries (Chinese only, no English).

Usage:
    python review/run_readability.py --from 201 --to 300 --model deepseek-v4-pro \
        --key-file review/api_key.txt --out review/readability_0201_0300

Writes <out>.json and <out>.md. Never touches all_entries.json.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SPK = {
    "i": "旁白", "a": "Atsuki", "s": "Shiroya", "sa": "Naomi", "ak": "Akaro",
    "sai": "Sai", "k": "Katei", "il": "Isla", "er": "Erina", "n": "旁白",
    "aki": "Akaro", "ta": "旁白", "knn": "旁白", "c": "旁白", "il2": "Isla",
    "sai2": "Sai", "q4": "旁白", "s2": "Shiroya",
}

SYSTEM_SUFFIX = """

【本次输入格式】
一个 JSON 数组，每个元素是：
  {"n": 编号, "speaker": 说话人, "text": 这一段的中文}
按 n 的顺序往下读，前后段落就是上下文。

【本次输出格式】
只输出 JSON 对象：
{"results": [{"n": 217, "why": "哪里读着不对（30 字以内）", "new": "改好的整句"}]}
读着顺的不要放进 results；一条都没有就 {"results": []}。
"""


def load_key(args):
    if args.api_key:
        return args.api_key
    if args.key_file and os.path.exists(args.key_file):
        return open(args.key_file, encoding="utf-8").read().strip()
    for env in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        if os.environ.get(env):
            return os.environ[env]
    print("ERROR: no api key (use --key-file review/api_key.txt)")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", type=int, required=True)
    ap.add_argument("--to", dest="end", type=int, required=True)
    ap.add_argument("--model", default="deepseek-v4-pro")
    ap.add_argument("--base-url", default="https://api.deepseek.com")
    ap.add_argument("--api-key", default="")
    ap.add_argument("--key-file", default=os.path.join(HERE, "api_key.txt"))
    ap.add_argument("--prompt", default=os.path.join(ROOT, "PROOFREAD_V5.txt"))
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(HERE, "readability"))
    args = ap.parse_args()

    from openai import OpenAI

    system_prompt = open(args.prompt, encoding="utf-8").read() + SYSTEM_SUFFIX
    client = OpenAI(api_key=load_key(args), base_url=args.base_url)

    data = json.load(open(os.path.join(ROOT, "all_entries.json"), encoding="utf-8"))
    story = [e for e in data["entries"] if e.get("group") == "story"]
    story.sort(key=lambda e: int(re.search(r"_L(\d+)_", e["id"]).group(1)))
    subset = story[args.start - 1:args.end]

    results = []
    for i in range(0, len(subset), args.batch_size):
        batch = subset[i:i + args.batch_size]
        payload = []
        for j, e in enumerate(batch):
            n = args.start + i + j
            payload.append({
                "n": n,
                "speaker": SPK.get(e.get("speaker") or "", e.get("speaker") or "旁白"),
                "text": e["new"],
            })
        msg = json.dumps(payload, ensure_ascii=False, indent=1)
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": msg}],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                raw = resp.choices[0].message.content
                parsed = json.loads(raw)
                items = parsed.get("results", []) if isinstance(parsed, dict) else parsed
                results.extend(items)
                print("batch %d-%d -> %d items" % (payload[0]["n"], payload[-1]["n"], len(items)))
                break
            except Exception as exc:  # noqa: BLE001
                print("batch %d failed (%s), retry %d" % (payload[0]["n"], exc, attempt + 1))
                time.sleep(3)
        else:
            print("batch %d given up" % payload[0]["n"])

    json.dump(results, open(args.out + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# 可读性审稿（%d–%d）\n" % (args.start, args.end),
          "共 %d 条。\n" % len(results)]
    for it in results:
        n = it.get("n")
        try:
            e = story[int(n) - 1]
            cur = e["new"]
            line = int(re.search(r"_L(\d+)_", e["id"]).group(1))
        except Exception:  # noqa: BLE001
            cur, line = "", 0
        md.append("## %s. script.rpy:%s" % (n, line))
        md.append("")
        md.append("- 现译：%s" % cur.replace("\n", " "))
        md.append("- 问题：%s" % it.get("why", ""))
        md.append("- 建议：%s" % it.get("new", ""))
        md.append("")
    open(args.out + ".md", "w", encoding="utf-8").write("\n".join(md))
    print("done:", len(results), "items ->", args.out + ".md")


if __name__ == "__main__":
    main()
