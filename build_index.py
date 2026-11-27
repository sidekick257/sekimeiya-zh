#!/usr/bin/env python3
"""Build a local sentence-retrieval index for proofread_batch.py.

Preferred backend is sentence-transformers (multilingual embeddings).
If it is not installed, falls back to a local BM25 index so retrieval still works.

The index directory is gitignored (embeddings can be tens of MB plus a 22k-line
docs file). Rebuild on this machine after clone:

  pip install sentence-transformers
  # if you need CPU-only torch first:
  # pip install torch --index-url https://download.pytorch.org/whl/cpu
  python build_index.py

  # force the light backend, no extra packages:
  python build_index.py --backend bm25

  python build_index.py --entries all_entries.json --out proofread_index --only story
"""

import argparse
import sys
from pathlib import Path

from proofread_rag import (
    DEFAULT_INDEX_DIR,
    DEFAULT_ST_MODEL,
    SentenceRetriever,
    usable_corpus_entries,
)


def load_entries(path: Path) -> list:
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("entries", [])


def main():
    ap = argparse.ArgumentParser(description="Build sentence RAG index for proofreading")
    ap.add_argument("--entries", default="all_entries.json")
    ap.add_argument("--out", default=DEFAULT_INDEX_DIR, help="index directory (not committed)")
    ap.add_argument(
        "--backend",
        default="auto",
        choices=["auto", "sentence-transformers", "bm25"],
        help="auto: sentence-transformers if installed, else BM25",
    )
    ap.add_argument("--model", default=DEFAULT_ST_MODEL, help="sentence-transformers model name")
    ap.add_argument("--only", default="story", help="filter corpus (substring of group/source_file); empty=all with new")
    ap.add_argument("--batch-size", type=int, default=64, help="encoding batch size")
    ap.add_argument("--force", action="store_true", help="overwrite an existing index")
    args = ap.parse_args()

    entries_path = Path(args.entries)
    if not entries_path.exists():
        print(f"ERROR: {entries_path} not found")
        sys.exit(1)

    out_dir = Path(args.out)
    if out_dir.exists() and (out_dir / "manifest.json").exists() and not args.force:
        print(f"Index already exists at {out_dir}. Use --force to rebuild.")
        sys.exit(0)

    entries = load_entries(entries_path)
    corpus = usable_corpus_entries(entries, only=args.only)
    if not corpus:
        # fall back to any non-empty new if --only was too strict
        corpus = usable_corpus_entries(entries, only="")
    if not corpus:
        print("ERROR: no entries with a non-empty new field")
        sys.exit(1)
    print(f"Corpus: {len(corpus)} sentences with translations (filter={args.only!r})")

    backend = args.backend
    if backend == "auto":
        try:
            import sentence_transformers  # noqa: F401
            backend = "sentence-transformers"
        except ImportError:
            print("sentence-transformers not installed; building BM25 index instead.")
            print("For vector search: pip install sentence-transformers")
            backend = "bm25"

    retriever = SentenceRetriever()
    if backend == "sentence-transformers":
        retriever.build_sentence_transformers(corpus, model_name=args.model, batch_size=args.batch_size)
    else:
        retriever.build_bm25(corpus)
        retriever.source = str(out_dir)

    retriever.save(out_dir)
    print(f"Wrote {out_dir}  backend={retriever.backend}  model={retriever.model_name}  docs={retriever.size}")
    print("Then run: python proofread_batch.py --dry-run --redo --only story --limit 1")


if __name__ == "__main__":
    main()
