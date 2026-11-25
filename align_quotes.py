#!/usr/bin/env python3
"""
align_quotes.py — Align referenced passages in Sekimeiya translation.

Reads sekimeiya_quote_reuse.md and all_entries.json, sends pairs to DeepSeek
to check/unify translations, writes changes back.

Usage:
  set DEEPSEEK_API_KEY=sk-...
  python align_quotes.py --limit 5
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Please install: pip install openai")
    sys.exit(1)


PROMPT = """你是中文校对编辑。下面是同一句话或同一场戏在不同章节的出现。

请检查译文是否一致。如果不一致，给出统一后的译文。

【规则】
1. 逐字重复的句子，译文必须完全一致。
2. 断续/残句（偷听、闪回片段）不要强行补全，只保证能对上的部分和前文一致。
3. 人名保持英文。
4. 保留标签如 {w}、{time=9}。
5. 不要用「您」。

【输入】
我会给你多组成对的句子，每组包含：
- 原句处（较早出现）
- 引用处（较晚出现）
- 类型（逐字重复 / 稍作改写 / 断续重述）

【输出】
JSON 数组，每项包含：
- id: 引用处的 id
- new: 统一后的译文（如果不用改，就原样返回）
- changed: true/false

例如：[{"id": "xxx", "new": "统一后的译文", "changed": true}]
"""


def load_entries(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_entries(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_quote_file(path: Path) -> list:
    """Parse sekimeiya_quote_reuse.md and extract pairs."""
    text = path.read_text(encoding="utf-8")
    pairs = []
    # Simple table row parser
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "引用处" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 5:
            continue
        ref_loc, ref_text, orig_loc, orig_text, typ = cols[:5]
        if not ref_text or not orig_text:
            continue
        pairs.append({
            "ref_loc": ref_loc,
            "ref_text": ref_text,
            "orig_loc": orig_loc,
            "orig_text": orig_text,
            "type": typ,
        })
    return pairs


def find_entry(entries: list, text: str) -> dict | None:
    """Find entry by matching text against 'new' (Chinese translation)."""
    text_clean = re.sub(r"[｜|].*", "", text).strip()
    if not text_clean:
        return None
    for e in entries:
        new = str(e.get("new") or "").strip()
        if not new:
            continue
        if text_clean in new or new in text_clean:
            return e
    return None


def call_deepseek(client, model, pairs_batch):
    user_msg = json.dumps(pairs_batch, ensure_ascii=False, indent=2)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            result = json.loads(raw[start:end])
        else:
            raise
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("results", "entries", "data"):
            if key in result and isinstance(result[key], list):
                return result[key]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=5)
    ap.add_argument("--entries", default="all_entries.json")
    ap.add_argument("--quotes", default="sekimeiya_quote_reuse.md")
    args = ap.parse_args()

    entries_path = Path(args.entries)
    quotes_path = Path(args.quotes)
    if not entries_path.exists() or not quotes_path.exists():
        print("ERROR: missing all_entries.json or sekimeiya_quote_reuse.md")
        sys.exit(1)

    data = load_entries(entries_path)
    entries = data.get("entries", [])
    pairs = parse_quote_file(quotes_path)
    print(f"Parsed {len(pairs)} quote pairs from {quotes_path}")

    # match to entries
    matched = []
    for p in pairs:
        ref_e = find_entry(entries, p["ref_text"])
        orig_e = find_entry(entries, p["orig_text"])
        if ref_e and orig_e and ref_e.get("new") and orig_e.get("new"):
            matched.append({
                "ref_id": ref_e["id"],
                "ref_text": ref_e["text"],
                "ref_new": ref_e["new"],
                "orig_id": orig_e["id"],
                "orig_text": orig_e["text"],
                "orig_new": orig_e["new"],
                "type": p["type"],
            })
    print(f"Matched {len(matched)} pairs with translations")

    if args.limit:
        matched = matched[:args.limit]

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: set DEEPSEEK_API_KEY")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    id_to_entry = {e["id"]: e for e in entries}
    changed = 0
    for i in range(0, len(matched), args.batch_size):
        batch = matched[i:i + args.batch_size]
        print(f"[send] pairs {i+1}-{i+len(batch)}")
        try:
            results = call_deepseek(client, args.model, batch)
        except Exception as ex:
            print(f"  ERROR: {ex}")
            time.sleep(3)
            continue
        for r in results:
            if not isinstance(r, dict):
                continue
            eid = r.get("id")
            new = r.get("new")
            if eid and new and eid in id_to_entry:
                if id_to_entry[eid]["new"] != new:
                    id_to_entry[eid]["new"] = new
                    changed += 1
        save_entries(entries_path, data)
        time.sleep(0.5)

    print(f"Done. Changed: {changed}")


if __name__ == "__main__":
    main()
