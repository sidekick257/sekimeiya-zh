#!/usr/bin/env python3
"""
proofread_batch.py — second-pass proofreading for Sekimeiya localization.

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

Use --dry-run to print a sample payload without calling the API. No API key
is required for --dry-run.

Usage:
  set DEEPSEEK_API_KEY=YOUR_KEY
  python proofread_batch.py --provider deepseek --model deepseek-v4-pro --batch-size 20 --workers 4 --only story
  python proofread_batch.py --prompt PROOFREAD_READABLE.txt --provider deepseek --model deepseek-v4-pro --only story --max-entries 5

  OpenAI-compatible relay (e.g. Gemini 3.8 Flash via laozhang.ai):
  python proofread_batch.py --provider openai --model gemini-3.8-flash --base-url https://api.laozhang.ai/v1 --api-key YOUR_KEY --only story

  Same via environment variables:
  set OPENAI_API_KEY=YOUR_KEY
  set OPENAI_BASE_URL=https://api.laozhang.ai/v1
  python proofread_batch.py --provider openai --model gemini-3.8-flash --only story

  --provider gemini also uses the OpenAI-compatible relay path (not the Google SDK):
  python proofread_batch.py --provider gemini --model gemini-3.8-flash --base-url https://api.laozhang.ai/v1 --api-key YOUR_KEY --only story
"""

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

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

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
VALID_PROVIDERS = ("deepseek", "openai", "gemini")
PROVIDER_KEY_ENV = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


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


def is_gemini_model(model: str) -> bool:
    return (model or "").strip().lower().startswith("gemini")


def normalize_provider(name: str) -> str:
    return (name or "deepseek").strip().lower() or "deepseek"


def normalize_openai_base_url(url: str) -> str:
    """Strip trailing slashes; append /v1 only when the URL has no version path."""
    url = (url or "").strip()
    if not url:
        return ""
    stripped = url.rstrip("/")
    path = urlparse(stripped).path or ""
    if re.search(r"/v\d+[a-z0-9]*$", path, re.I):
        return stripped
    if path in ("", "/"):
        return stripped + "/v1"
    return stripped


def resolve_base_url(provider: str, model: str, cli_base_url: str) -> str:
    """CLI --base-url wins, then OPENAI_BASE_URL for openai/gemini (and gemini models).

    Default DeepSeek keeps the official URL and does not silently pick up
    OPENAI_BASE_URL.
    """
    cli = (cli_base_url or "").strip()
    env = (os.environ.get("OPENAI_BASE_URL") or "").strip()
    provider = normalize_provider(provider)
    gemini_like = provider == "gemini" or is_gemini_model(model)

    if cli:
        return normalize_openai_base_url(cli)
    if gemini_like or provider == "openai":
        if env:
            return normalize_openai_base_url(env)
        return ""
    return DEFAULT_DEEPSEEK_BASE_URL


def resolve_api_key(provider: str, model: str, cli_key: str):
    """Return (api_key, source_label). CLI --api-key wins over env vars."""
    if (cli_key or "").strip():
        return cli_key.strip(), "--api-key"
    provider = normalize_provider(provider)
    env_order = []
    primary = PROVIDER_KEY_ENV.get(provider)
    if primary:
        env_order.append(primary)
    if provider == "deepseek":
        env_order.append("OPENAI_API_KEY")
    elif provider == "gemini":
        env_order.append("OPENAI_API_KEY")
    if is_gemini_model(model):
        for name in ("GEMINI_API_KEY", "OPENAI_API_KEY"):
            if name not in env_order:
                env_order.append(name)
    for name in env_order:
        key = (os.environ.get(name) or "").strip()
        if key:
            return key, name
    return "", (env_order[0] if env_order else "OPENAI_API_KEY")


def should_use_json_object(provider: str, model: str, base_url: str) -> bool:
    """Keep json_object on the official DeepSeek (and official OpenAI) path.

    Relays and Gemini models often reject or ignore response_format, so those
    paths omit it and parse JSON more defensively instead.
    """
    if normalize_provider(provider) == "gemini" or is_gemini_model(model):
        return False
    if not base_url:
        return True
    host = base_url.rstrip("/")
    return host in {
        DEFAULT_DEEPSEEK_BASE_URL,
        DEFAULT_DEEPSEEK_BASE_URL + "/v1",
        "https://api.openai.com",
        "https://api.openai.com/v1",
    }


def needs_relay_base_url(provider: str, model: str, base_url: str) -> bool:
    return (normalize_provider(provider) == "gemini" or is_gemini_model(model)) and not base_url


def parse_model_json(raw) -> list:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        start_arr = text.find("[")
        end_arr = text.rfind("]") + 1
        # Prefer whichever JSON construct appears first, so a leading
        # [{...}] is not sliced down to the first object.
        candidates = []
        if start_arr >= 0 and end_arr > start_arr and (start < 0 or start_arr < start):
            candidates.append(text[start_arr:end_arr])
            if start >= 0 and end > start:
                candidates.append(text[start:end])
        else:
            if start >= 0 and end > start:
                candidates.append(text[start:end])
            if start_arr >= 0 and end_arr > start_arr:
                candidates.append(text[start_arr:end_arr])
        last_err = None
        result = None
        for cand in candidates:
            try:
                result = json.loads(cand)
                last_err = None
                break
            except json.JSONDecodeError as exc:
                last_err = exc
        if result is None:
            if last_err is not None:
                raise last_err
            raise
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("results", "entries", "data"):
            if key in result and isinstance(result[key], list):
                return result[key]
        return [{"id": k, "new": v} for k, v in result.items() if isinstance(v, str)]
    return []


def make_client(api_key: str, base_url: str):
    if OpenAI is None:
        print("Please install: pip install openai")
        sys.exit(1)
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


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


def call_chat(client, model, system_prompt, user_msg, use_json_object=True):
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
    }
    if use_json_object:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    raw = resp.choices[0].message.content
    return parse_model_json(raw)


def process_batch(args_tuple):
    (client, model, system_prompt, batch, idx, total, file_index,
     radius, terms, retriever, rag_k, use_term_rag, st_model, use_json_object) = args_tuple
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
        results = call_chat(client, model, system_prompt, user_msg, use_json_object=use_json_object)
        return idx, batch, results, None
    except Exception as ex:
        return idx, batch, None, str(ex)


def main():
    ap = argparse.ArgumentParser(
        description="Proofread all_entries.json with DeepSeek or an OpenAI-compatible relay (e.g. Gemini).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python proofread_batch.py --provider deepseek --model deepseek-v4-pro --only story\n"
            "  python proofread_batch.py --provider openai --model gemini-3.8-flash "
            "--base-url https://api.laozhang.ai/v1 --api-key YOUR_KEY --only story\n"
            "  OPENAI_API_KEY / OPENAI_BASE_URL can be used instead of --api-key / --base-url.\n"
            "  --dry-run does not need an API key.\n"
        ),
    )
    ap.add_argument(
        "--provider",
        default="deepseek",
        help="deepseek (default), openai, or gemini. gemini uses an OpenAI-compatible relay, not the Google SDK.",
    )
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument(
        "--base-url",
        default="",
        help="OpenAI-compatible API base URL (overrides OPENAI_BASE_URL). "
        "If the URL has no path, /v1 is appended. "
        "Default: official DeepSeek when --provider deepseek.",
    )
    ap.add_argument(
        "--api-key",
        default="",
        help="API key (overrides OPENAI_API_KEY / DEEPSEEK_API_KEY / GEMINI_API_KEY). Not required with --dry-run.",
    )
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--workers", type=int, default=1, help="concurrent batches")
    ap.add_argument("--limit", type=int, default=0, help="max batches to process (0=all)")
    ap.add_argument("--max-entries", type=int, default=0, help="max pending entries to process (0=all); use with --only story for a small test")
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

    provider = normalize_provider(args.provider)
    if provider not in VALID_PROVIDERS:
        print(f"ERROR: --provider must be one of: {', '.join(VALID_PROVIDERS)}")
        sys.exit(1)

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

    if args.max_entries:
        pending = pending[: args.max_entries]

    print(f"Loaded {len(entries)} entries; {len(pending)} pending.")
    if not pending:
        print("Nothing to do.")
        return

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    if args.limit:
        batches = batches[:args.limit]
    base_url = resolve_base_url(provider, args.model, args.base_url)
    use_json_object = should_use_json_object(provider, args.model, base_url)
    print(
        f"{len(batches)} batch(es) of up to {args.batch_size}. "
        f"workers={args.workers} provider={provider} model={args.model}"
    )
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

    if needs_relay_base_url(provider, args.model, base_url):
        print(
            "ERROR: Gemini models need an OpenAI-compatible --base-url or OPENAI_BASE_URL "
            "(for example https://api.laozhang.ai/v1)."
        )
        sys.exit(1)

    api_key, key_source = resolve_api_key(provider, args.model, args.api_key)
    if not api_key:
        print(
            f"ERROR: set --api-key or the {key_source} environment variable. "
            "OPENAI_API_KEY / DEEPSEEK_API_KEY / GEMINI_API_KEY are also accepted where relevant."
        )
        sys.exit(1)
    client = make_client(api_key, base_url)
    endpoint = base_url or "https://api.openai.com/v1"
    print(f"API: {endpoint}  (key from {key_source})")

    polished = 0
    tasks = [
        (
            client, args.model, system_prompt, batch, i + 1, len(batches), file_index,
            radius, terms, retriever, rag_k, use_term_rag, st_model, use_json_object,
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
