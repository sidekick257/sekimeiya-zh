#!/usr/bin/env python3
"""
proofread_batch.py — DeepSeek second-pass proofreading for Sekimeiya localization.

Supports concurrent batches for speed.

Each item sent to the model includes:
  - before / after: the preceding and following sentences from the same
    source file (default: 5 on each side; fewer at edges; never crosses files)
  - retrieved_terms: glossary entries that match this sentence (keyword RAG)
  - retrieved_examples: semantically similar translations (vector index if
    present, otherwise BM25), so wording stays consistent

Build a vector index first when you can:

  python build_index.py
  python build_index.py --backend bm25          # no sentence-transformers

Use --dry-run to print a sample payload without calling the API.

Usage:
  set DEEPSEEK_API_KEY=sk-...
  python proofread_batch.py --provider deepseek --model deepseek-v4-pro --batch-size 20 --workers 4 --only story
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from proofread_rag import (
    DEFAULT_CONTEXT_RADIUS,
    DEFAULT_INDEX_DIR,
    DEFAULT_RAG_K,
    default_terms_path,
    describe_retriever,
    load_retriever,
    load_terms,
    match_terms,
    neighbor_ids,
)


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


def build_file_index(entries):
    """Map entry id -> (same-file entry list, index). Context never crosses source_file."""
    by_file = {}
    for e in entries:
        by_file.setdefault(e.get("source_file") or "", []).append(e)
    index = {}
    for group in by_file.values():
        for i, e in enumerate(group):
            index[e["id"]] = (group, i)
    return index


def format_context_line(e):
    item = {
        "original": e.get("text") or "",
        "current": (e.get("new") or "").strip() or "（尚无译文）",
    }
    speaker = e.get("speaker")
    if speaker:
        item["speaker"] = speaker
    return item


def neighbors(index, entry, radius=DEFAULT_CONTEXT_RADIUS):
    group, i = index[entry["id"]]
    before = [format_context_line(e) for e in group[max(0, i - radius):i]]
    after = [format_context_line(e) for e in group[i + 1:i + 1 + radius]]
    return before, after


def build_payload(
    batch,
    index,
    radius=DEFAULT_CONTEXT_RADIUS,
    terms=None,
    retriever=None,
    rag_k=DEFAULT_RAG_K,
    use_term_rag=True,
    retrieved_map=None,
):
    """Build the JSON list sent to the model. Does not mutate entry dicts.

    retrieved_map: optional precomputed {id: [examples]} so a batch can be
    encoded once instead of loading the embedding model per sentence.
    """
    items = []
    for e in batch:
        item = {
            "id": e["id"],
            "original": e["text"],
            "current": e["new"],
        }
        if radius > 0 and e["id"] in index:
            before, after = neighbors(index, e, radius)
            item["before"] = before
            item["after"] = after
        if use_term_rag and terms:
            hits = match_terms(e, terms)
            if hits:
                item["retrieved_terms"] = hits
        examples = None
        if retrieved_map is not None:
            examples = retrieved_map.get(e["id"])
        elif retriever is not None and rag_k > 0:
            exclude = neighbor_ids(index, e, radius)
            examples = retriever.query(e, rag_k, exclude_ids=exclude)
        if examples:
            item["retrieved_examples"] = examples
        items.append(item)
    return items


def retrieve_for_batch(batch, index, retriever, rag_k, radius, st_model=None):
    if retriever is None or rag_k <= 0 or not batch:
        return {}
    examples_list = retriever.query_many(
        batch,
        rag_k,
        exclude_ids_fn=lambda e: neighbor_ids(index, e, radius),
        model=st_model,
    )
    return {e["id"]: ex for e, ex in zip(batch, examples_list)}


def call_deepseek(client, model, system_prompt, user_msg):
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
    (client, model, system_prompt, batch, idx, total, file_index,
     radius, terms, retriever, rag_k, use_term_rag, st_model) = args_tuple
    print(f"[send] batch {idx}/{total}  ({len(batch)} entries)")
    try:
        retrieved_map = retrieve_for_batch(batch, file_index, retriever, rag_k, radius, st_model)
        payload = build_payload(
            batch,
            file_index,
            radius=radius,
            terms=terms,
            rag_k=rag_k,
            use_term_rag=use_term_rag,
            retrieved_map=retrieved_map,
        )
        user_msg = json.dumps(payload, ensure_ascii=False, indent=2)
        results = call_deepseek(client, model, system_prompt, user_msg)
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
    ap.add_argument("--dry-run", action="store_true", help="print a sample payload and exit, no API call")
    ap.add_argument(
        "--context-radius",
        type=int,
        default=DEFAULT_CONTEXT_RADIUS,
        help="sentences of same-file context before and after each entry (default 5)",
    )
    ap.add_argument(
        "--index",
        default=DEFAULT_INDEX_DIR,
        help="directory written by build_index.py (default proofread_index)",
    )
    ap.add_argument(
        "--terms",
        default="",
        help="optional terms JSON; otherwise terms are read from PROOFREAD.txt 【术语】",
    )
    ap.add_argument("--rag-k", type=int, default=DEFAULT_RAG_K, help="similar sentences to retrieve (default 6)")
    ap.add_argument("--no-sentence-rag", action="store_true", help="disable similar-sentence retrieval")
    ap.add_argument("--no-term-rag", action="store_true", help="disable term keyword retrieval")
    args = ap.parse_args()

    entries_path = Path(args.entries)
    if not entries_path.exists():
        print(f"ERROR: {entries_path} not found")
        sys.exit(1)

    data = load_entries(entries_path)
    entries = data.get("entries", [])
    prompt_path = Path(args.prompt)
    system_prompt = load_prompt(prompt_path)
    file_index = build_file_index(entries)
    radius = max(0, args.context_radius)
    rag_k = 0 if args.no_sentence_rag else max(0, args.rag_k)
    use_term_rag = not args.no_term_rag

    terms = []
    if use_term_rag:
        terms_path = Path(args.terms) if args.terms else default_terms_path(prompt_path)
        terms = load_terms(prompt_path, terms_path)
        src = str(terms_path) if terms_path else str(prompt_path)
        print(f"Term RAG: {len(terms)} entries from {src}")
    else:
        print("Term RAG: off")

    retriever = None
    st_model = None
    if rag_k > 0:
        retriever, note = load_retriever(Path(args.index), entries, only_for_fallback="story")
        if retriever is None:
            print("WARNING: sentence RAG requested but no corpus/index was available; continuing without it.")
            rag_k = 0
        else:
            print(describe_retriever(retriever, rag_k) + f"  ({note})")
            if retriever.backend == "sentence-transformers":
                # Load the query encoder once, share across workers.
                st_model = retriever._prepare_st_query_model()
    else:
        print("Sentence RAG: off")

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

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    if args.limit:
        batches = batches[:args.limit]
    print(f"{len(batches)} batch(es) of up to {args.batch_size}. workers={args.workers} model={args.model}")
    print(f"Context: {radius} sentence(s) before and after each entry (same source_file).")

    if args.dry_run:
        sample_batch = batches[0][:3]
        retrieved_map = retrieve_for_batch(sample_batch, file_index, retriever, rag_k, radius, st_model)
        sample = build_payload(
            sample_batch,
            file_index,
            radius=radius,
            terms=terms,
            rag_k=rag_k,
            use_term_rag=use_term_rag,
            retrieved_map=retrieved_map,
        )
        print("Dry-run sample payload (first 3 items of batch 1):")
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        return

    if OpenAI is None:
        print("Please install: pip install openai")
        sys.exit(1)
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: set DEEPSEEK_API_KEY environment variable")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    polished = 0
    tasks = [
        (
            client, args.model, system_prompt, batch, i + 1, len(batches), file_index,
            radius, terms, retriever, rag_k, use_term_rag, st_model,
        )
        for i, batch in enumerate(batches)
    ]

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
            batch_ids = {e["id"] for e in batch}
            for e in batch:
                if e["id"] in id_to_new and str(id_to_new[e["id"]]).strip():
                    e["new"] = id_to_new[e["id"]]
                    applied += 1
                done.add(e["id"])
            extras = [eid for eid in id_to_new if eid not in batch_ids]
            if extras:
                print(f"       batch {idx} ignored {len(extras)} id(s) not in this batch")
            polished += applied
            print(f"       batch {idx} applied={applied}")
            save_entries(entries_path, data)
            save_done(done_path, done)

    print(f"Done. Polished: {polished}. Total done: {len(done)}")
    print("Next: python export_readable.py --only translated")


if __name__ == "__main__":
    main()
