#!/usr/bin/env python3
"""
proofread_batch.py — DeepSeek second-pass proofreading for Sekimeiya localization.

Supports concurrent batches for speed.

Usage:
  set DEEPSEEK_API_KEY=sk-...
  python proofread_batch.py --provider deepseek --model deepseek-v4-pro --batch-size 20 --workers 4 --only story
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Please install: pip install openai")
    sys.exit(1)


def load_prompt(path: Path) -> str:
    if not path.exists():
        print(f"ERROR: {path} not found. Put your proofreading prompt there.")
        sys.exit(1)
    return path.read_text(encoding="utf-8").strip()


def load_entries(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_entries(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_done(path: Path) -> set:
    if not path.exists():
        return set()
    return set(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def save_done(path: Path, done: set):
    path.write_text("\n".join(sorted(done)) + "\n", encoding="utf-8")


def call_deepseek(client, model, system_prompt, batch):
    user_msg = json.dumps(
        [{"id": e["id"], "original": e["text"], "current": e["new"]} for e in batch],
        ensure_ascii=False,
        indent=2,
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
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
        return [{"id": k, "new": v} for k, v in result.items() if isinstance(v, str)]
    return []


def process_batch(args_tuple):
    client, model, system_prompt, batch, idx, total = args_tuple
    print(f"[send] batch {idx}/{total}  ({len(batch)} entries)")
    try:
        results = call_deepseek(client, model, system_prompt, batch)
        return idx, batch, results, None
    except Exception as ex:
        return idx, batch, None, str(ex)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--workers", type=int, default=1, help="concurrent batches")
    ap.add_argument("--limit", type=int, default=0, help="max batches to process (0=all)")
    ap.add_argument("--only", default="", help="filter by group containing this string")
    ap.add_argument("--redo", action="store_true", help="ignore done list and re-proofread")
    ap.add_argument("--entries", default="all_entries.json")
    ap.add_argument("--done", default="proofread_done.txt", help="file tracking proofread IDs")
    ap.add_argument("--prompt", default="PROOFREAD.txt")
    args = ap.parse_args()

    entries_path = Path(args.entries)
    if not entries_path.exists():
        print(f"ERROR: {entries_path} not found")
        sys.exit(1)

    data = load_entries(entries_path)
    entries = data.get("entries", [])
    system_prompt = load_prompt(Path(args.prompt))

    done_path = Path(args.done)
    done = set() if args.redo else load_done(done_path)
    print(f"Already proofread: {len(done)}")

    pending = []
    for e in entries:
        if not str(e.get("new") or "").strip():
            continue
        if args.only and args.only.lower() not in (str(e.get("group") or "") + str(e.get("source_file") or "")).lower():
            continue
        if e["id"] in done:
            continue
        pending.append(e)

    print(f"Loaded {len(entries)} entries; {len(pending)} pending.")
    if not pending:
        print("Nothing to do.")
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: set DEEPSEEK_API_KEY environment variable")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    if args.limit:
        batches = batches[:args.limit]
    print(f"{len(batches)} batch(es) of up to {args.batch_size}. workers={args.workers} model={args.model}")

    polished = 0
    tasks = [(client, args.model, system_prompt, batch, i + 1, len(batches)) for i, batch in enumerate(batches)]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process_batch, t): t for t in tasks}
        for fut in as_completed(futures):
            idx, batch, results, err = fut.result()
            if err:
                print(f"  batch {idx} ERROR: {err}")
                continue
            id_to_new = {}
            for r in results or []:
                if isinstance(r, dict) and "id" in r and "new" in r:
                    id_to_new[r["id"]] = r["new"]
                elif isinstance(r, dict) and "id" in r and "polished" in r:
                    id_to_new[r["id"]] = r["polished"]
            applied = 0
            for e in batch:
                if e["id"] in id_to_new and str(id_to_new[e["id"]]).strip():
                    e["new"] = id_to_new[e["id"]]
                    applied += 1
                done.add(e["id"])
            polished += applied
            print(f"       batch {idx} applied={applied}")
            save_entries(entries_path, data)
            save_done(done_path, done)

    print(f"Done. Polished: {polished}. Total done: {len(done)}")
    print("Next: python export_readable.py --only translated")


if __name__ == "__main__":
    main()
