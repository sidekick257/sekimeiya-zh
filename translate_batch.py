#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch-translate Sekimeiya all_entries.json with Gemini (default) or xAI Grok.

Reads one complete JSON file and sends it to the API in batches (default 400
entries). Only fills each entry's `new` field with Simplified Chinese. Never
changes `id`, `speaker`, or `text`. Already-filled entries are skipped
(safe to resume).

Setup and run (from this folder):

    pip install -r requirements.txt
    export GEMINI_API_KEY="..."      # Windows CMD: set GEMINI_API_KEY=...
    python translate_batch.py

Defaults to DeepSeek (deepseek-v4-pro). Set DEEPSEEK_API_KEY and run:

    export DEEPSEEK_API_KEY="..."
    python translate_batch.py

To use Gemini free tier or Grok instead:

    python translate_batch.py --provider gemini
    python translate_batch.py --provider xai

The API key is read from the environment only. Do not hardcode it.
--model or DEEPSEEK_MODEL / GEMINI_MODEL / XAI_MODEL can override the default model.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

DEFAULT_PROVIDER = "deepseek"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_GEMINI_MODEL = "gemini-4-hydrogen"
DEFAULT_XAI_MODEL = "grok-4.7"
DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_BATCH = 400

MODEL_ALIASES = {
    # Official Flash id is deepseek-flash; it currently serves DeepSeek-V4.1-Flash-1017.
    "deepseek-v4.1-flash-1017": "deepseek-flash",
    "deepseek-v4.1-flash": "deepseek-flash",
    "deepseek-flash-1017": "deepseek-flash",
    "ds-fl1017": "deepseek-flash",
    "fl1017": "deepseek-flash",
}
TAG_RE = re.compile(r"\{[^{}]+\}|\{/[^{}]+\}|\[[^\[\]]+\]")
TRANSIENT_MARKERS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "timeout",
    "Timeout",
    "timed out",
    "Rate limit",
    "rate limit",
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
    "DEADLINE_EXCEEDED",
    "quota",
    "Quota",
    "Service Unavailable",
    "overloaded",
    "temporarily unavailable",
    "Too Many Requests",
    "connection reset",
    "Connection reset",
    "RemoteProtocolError",
)


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_tags(s: str) -> list[str]:
    if not s:
        return []
    return TAG_RE.findall(s)


def tags_preserved(src: str, dst: str) -> bool:
    return sorted(extract_tags(src)) == sorted(extract_tags(dst))


def parse_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def is_transient(exc: BaseException) -> bool:
    msg = str(exc)
    if any(s in msg for s in TRANSIENT_MARKERS):
        return True
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if code in (408, 429, 500, 502, 503, 504):
        return True
    name = type(exc).__name__
    return name in {
        "TimeoutError",
        "APITimeoutError",
        "RateLimitError",
        "APIConnectionError",
        "InternalServerError",
        "DeadlineExceeded",
        "ConnectError",
        "ReadTimeout",
        "WriteTimeout",
    }


def user_payload(payload: dict) -> str:
    return (
        "Translate the following entries. Return JSON only, of the form "
        '{"translations": [{"id": "...", "new": "..."}, ...]}.\n\n'
        + json.dumps(payload, ensure_ascii=False)
    )


def call_gemini(client, model: str, system_prompt: str, payload: dict) -> dict:
    from google.genai import types  # type: ignore

    resp = client.models.generate_content(
        model=model,
        contents=user_payload(payload),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    content = getattr(resp, "text", None) or ""
    if not content.strip():
        raise RuntimeError(
            "Gemini returned an empty response "
            f"(prompt_feedback={getattr(resp, 'prompt_feedback', None)!r})."
        )
    return parse_json_object(content)


def call_openai_compat(client, model: str, system_prompt: str, payload: dict) -> dict:
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload(payload)},
        ],
    )
    content = ""
    if resp.choices:
        content = resp.choices[0].message.content or ""
    if not content.strip():
        raise RuntimeError("The API returned an empty response.")
    return parse_json_object(content)


def translations_from_response(obj) -> dict[str, str]:
    items = []
    if isinstance(obj, dict):
        if "translations" in obj:
            items = obj["translations"]
        elif "entries" in obj:
            items = obj["entries"]
        else:
            items = [{"id": k, "new": v} for k, v in obj.items() if isinstance(v, str)]
    elif isinstance(obj, list):
        items = obj
    out = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        eid = it.get("id")
        new = it.get("new", it.get("translation", it.get("zh", "")))
        if eid and isinstance(new, str) and new != "":
            out[str(eid)] = new
    return out


def retry_call(call_fn, client, model, prompt, payload, retries: int, retry_wait: float):
    last = None
    wait = retry_wait
    for attempt in range(1, retries + 1):
        try:
            return call_fn(client, model, prompt, payload)
        except Exception as exc:
            last = exc
            print(f"  Attempt {attempt}/{retries} failed: {exc}", file=sys.stderr)
            if attempt >= retries or not is_transient(exc):
                break
            print(f"  Retrying in {wait:.1f}s...", file=sys.stderr)
            time.sleep(wait)
            wait = min(wait * 2, 60)
    raise last


def apply_translations(entries, mapping) -> tuple[int, int]:
    applied = 0
    warnings = 0
    by_id = {e["id"]: e for e in entries}
    for eid, new in mapping.items():
        e = by_id.get(eid)
        if not e:
            print(f"  Warning: model returned unknown id {eid}", file=sys.stderr)
            warnings += 1
            continue
        if str(e.get("new") or "").strip():
            continue
        if not tags_preserved(e.get("text") or "", new):
            print(
                f"  Warning: tags changed for {eid}. "
                f"source={extract_tags(e.get('text') or '')} new={extract_tags(new)}. Still saving.",
                file=sys.stderr,
            )
            warnings += 1
        e["new"] = new
        applied += 1
    return applied, warnings


def pending_entries(entries, only: str) -> list:
    only = (only or "").strip().lower()
    out = []
    for e in entries:
        if str(e.get("new") or "").strip():
            continue
        if only:
            group = str(e.get("group") or "").lower()
            src = str(e.get("source_file") or "").lower()
            if only not in group and only not in src:
                continue
        out.append(e)
    return out


def batched(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def save(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def make_gemini_client(api_key: str, timeout_seconds: int):
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except ImportError:
        sys.exit("ERROR: google-genai is not installed. Run: pip install -r requirements.txt")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=timeout_seconds * 1000),
    )


def make_openai_client(api_key: str, timeout_seconds: int, base_url: str):
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        sys.exit("ERROR: openai is not installed. Run: pip install -r requirements.txt")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds)


def resolve_provider(explicit: str) -> str:
    name = (explicit or "").strip().lower()
    aliases = {"grok": "xai", "dpsk": "deepseek", "ds": "deepseek"}
    name = aliases.get(name, name)
    if name in {"deepseek", "gemini", "xai"}:
        return name
    if name:
        sys.exit("ERROR: --provider must be deepseek, gemini, or xai.")
    return DEFAULT_PROVIDER


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Translate all_entries.json with DeepSeek (default), Gemini, or xAI Grok."
    )
    parser.add_argument("--input", type=Path, default=here / "all_entries.json", help="Complete JSON file")
    parser.add_argument("--output", type=Path, default=None, help="Defaults to updating --input in place")
    parser.add_argument("--prompt", type=Path, default=here / "PROMPT.txt")
    parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        help="deepseek (default), gemini, or xai",
    )
    parser.add_argument("--model", default="", help="Override the default model, e.g. deepseek-flash (V4.1-Flash-1017) or deepseek-v4-pro")
    parser.add_argument(
        "--base-url",
        default="",
        help="API base URL for DeepSeek or xAI (optional)",
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH, help="Entries per API call (default 400)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between API calls")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--retry-wait", type=float, default=2.0)
    parser.add_argument("--timeout", type=int, default=600, help="Seconds to wait for one API response")
    parser.add_argument("--limit", type=int, default=0, help="Max number of API batches this run (0 = all)")
    parser.add_argument("--only", default="", help="Only entries whose group or source_file contains this, e.g. story")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.batch_size <= 0:
        sys.exit("ERROR: --batch-size must be a positive integer.")

    provider = resolve_provider(args.provider)
    if provider == "gemini":
        default_model = os.environ.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
        env_name = "GEMINI_API_KEY"
        api_key = (os.environ.get(env_name) or "").strip()
        call_fn = call_gemini
        base_url = ""
    elif provider == "deepseek":
        default_model = os.environ.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
        env_name = "DEEPSEEK_API_KEY"
        api_key = (os.environ.get(env_name) or "").strip()
        call_fn = call_openai_compat
        base_url = (
            (args.base_url or "").strip()
            or os.environ.get("DEEPSEEK_BASE_URL")
            or DEFAULT_DEEPSEEK_BASE_URL
        )
    else:
        default_model = os.environ.get("XAI_MODEL") or DEFAULT_XAI_MODEL
        env_name = "XAI_API_KEY"
        api_key = (os.environ.get(env_name) or "").strip()
        call_fn = call_openai_compat
        base_url = (
            (args.base_url or "").strip()
            or os.environ.get("XAI_BASE_URL")
            or DEFAULT_XAI_BASE_URL
        )

    model = (args.model or "").strip() or default_model
    alias = MODEL_ALIASES.get(model.lower())
    if alias and alias != model:
        print(f"Note: '{model}' is an alias; using official model id '{alias}'.")
        model = alias
    if not args.dry_run and not api_key:
        sys.exit(f"ERROR: {env_name} is not set. Export it in your environment and try again.")
    if not args.prompt.is_file():
        sys.exit(f"ERROR: prompt file not found: {args.prompt}")
    if not args.input.is_file():
        sys.exit(f"ERROR: input file not found: {args.input}")

    prompt = load_prompt(args.prompt)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    entries = data.get("entries") or []
    pending = pending_entries(entries, args.only)
    out_path = args.output or args.input
    batches = list(batched(pending, args.batch_size))
    print(
        f"Loaded {len(entries)} entries from {args.input.name}; "
        f"{len(pending)} pending; {len(batches)} batch(es) of up to {args.batch_size}. "
        f"provider={provider} model={model}"
    )
    if args.dry_run:
        print("dry-run: no API calls.")
        return

    if provider == "gemini":
        client = make_gemini_client(api_key, args.timeout)
    else:
        client = make_openai_client(api_key, args.timeout, base_url)

    sent = 0
    total_applied = 0
    for i, batch in enumerate(batches, 1):
        if args.limit and sent >= args.limit:
            print(f"[stop] reached --limit {args.limit}")
            break
        print(f"[send] batch {i}/{len(batches)}  ({len(batch)} entries)")
        payload = {
            "entries": [
                {"id": e["id"], **({"speaker": e["speaker"]} if e.get("speaker") else {}), "text": e["text"]}
                for e in batch
            ]
        }
        obj = retry_call(call_fn, client, model, prompt, payload, args.retries, args.retry_wait)
        mapping = translations_from_response(obj)
        applied, _warnings = apply_translations(batch, mapping)
        total_applied += applied
        still = sum(1 for e in batch if not str(e.get("new") or "").strip())
        print(f"       applied={applied} still_empty={still}")
        if still:
            print(f"  Warning: {still} entries were not returned (will retry on next run).", file=sys.stderr)
        save(out_path, data)
        sent += 1
        if args.delay > 0 and i < len(batches):
            time.sleep(args.delay)

    left = sum(1 for e in pending_entries(entries, args.only) if not str(e.get("new") or "").strip())
    print(f"Done. Batches sent this run: {sent}. New translations written: {total_applied}. Still empty: {left}.")
    print("Next step: python merge_back.py")


if __name__ == "__main__":
    main()
