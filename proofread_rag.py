#!/usr/bin/env python3
"""Term matching and sentence retrieval used by proofread_batch.py and build_index.py.

Sentence index backends:
  - sentence-transformers (preferred, built by build_index.py)
  - BM25 (used when no vector index is present, or when build_index.py --backend bm25)

Term sources (first that exists is used, then merged with the prompt glossary):
  - optional JSON terms file (--terms)
  - 【术语】and locked names in 【必须遵守】from PROOFREAD.txt
"""

from __future__ import annotations

import json
import math
import re
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

INDEX_VERSION = 1
DEFAULT_INDEX_DIR = "proofread_index"
DEFAULT_ST_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_RAG_K = 6
DEFAULT_CONTEXT_RADIUS = 5

_SECTION_RE = re.compile(r"【([^】]+)】")
_EN_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9'’.\-]*(?:[ /]+[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9'’.\-]*)*")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_WORD_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+", re.I)
_SLASH_HEAD_RE = re.compile(
    r"\b([A-Za-z][A-Za-z0-9'’.\-]*)\s+([A-Za-z](?:/[A-Za-z])+)\b"
)
_PARENS_S_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9'’.\-]*)\(s\)", re.I)
_MODIFIED_SEKIMEDIYA_RE = re.compile(
    r"(?:赝品|灰色|fake|false|gray|grey)\s*Sekimeiya", re.I
)
_LETTER_SLASH_ZH_RE = re.compile(
    r"\b([A-Za-z](?:/[A-Za-z])+)\s*([\u4e00-\u9fff]{2,})"
)
_ZH_AFTER_EN_RE = re.compile(
    r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9'’.\- /()]*?(?:译|为)?[「 ]*([\u4e00-\u9fff]{2,})"
)
_DISCOURAGED_ZH_RE = re.compile(
    r"(?:不要用|不要写成|不要缩写成)\s*「?([\u4e00-\u9fff]+)"
)
_CONTINUE_PREFIX_RE = re.compile(r"^(作为|名称|或|或者|以及|一律|编号)")

EN_STOP = {
    "a", "an", "the", "and", "or", "of", "for", "as", "to", "in", "on", "at", "by",
    "with", "from", "into", "over", "out", "up", "be", "is", "are", "was", "were",
    "this", "that", "these", "those", "it", "its", "their", "his", "her", "not",
    "etc", "when", "if", "but", "so", "than", "then", "all", "already", "more",
    "just", "what", "have", "has", "had", "we", "you", "i", "my", "our", "your",
    "keep", "stay", "use", "used", "using", "write", "written", "also", "can",
    "found", "different", "nearby", "complete", "english", "title", "titles",
    "name", "names", "only", "once", "chosen", "same", "one", "two",
}

# Too generic as a lone English word; still used inside multi-word aliases.
EN_GENERIC = {
    "world", "worlds", "room", "rooms", "floor", "door", "key", "park", "street",
    "avenue", "energy", "gas", "family", "range", "point", "points", "find",
    "building", "event", "staff", "hidden", "security", "mechanical", "cleaning",
    "stored", "overlapping", "smoke", "rusty", "voice", "time", "copy", "travel",
    "past", "future", "spun", "town", "fake", "false", "gray", "grey", "virtual",
    "hypothetical", "proper", "symbol", "role",
}

ZH_STOP = {
    "作为", "机构", "简称", "家族", "家庭", "上面", "例子", "好例子", "全部", "保持",
    "英文", "不要", "缩写", "缩写成", "编号", "保留", "名称", "不要写成", "完整",
    "标题", "未锁定", "新造", "译法", "统一", "选定", "全文", "沿用", "以及", "或者",
    "只音译", "一经", "角色", "符号", "不同", "各种", "附近", "可以", "找到", "一律",
    "还有", "那个", "这个", "见上面", "见上面的好例子", "不要用", "不要另造",
}

SKIP_ZH_ALIASES = {"石"}  # too common (宝石, 坦桑石); Sekimeiya is matched in English


@dataclass
class Term:
    text: str
    aliases: tuple[str, ...] = field(default_factory=tuple)


def extract_section(prompt: str, title: str) -> str:
    matches = list(_SECTION_RE.finditer(prompt))
    for i, m in enumerate(matches):
        if m.group(1) == title:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(prompt)
            return prompt[start:end].strip()
    return ""


def _expand_alias_forms(alias: str) -> list[str]:
    out = []
    seen = set()

    def add(s: str):
        s = s.strip()
        if not s or s in seen:
            return
        seen.add(s)
        out.append(s)

    add(alias)
    add(alias.replace("Café", "Cafe").replace("café", "cafe"))
    add(alias.replace("’", "'"))
    for m in _PARENS_S_RE.finditer(alias):
        stem = m.group(1)
        add(_PARENS_S_RE.sub(stem, alias, count=1))
        add(_PARENS_S_RE.sub(stem + "s", alias, count=1))
    for m in _SLASH_HEAD_RE.finditer(alias):
        head, group = m.group(1), m.group(2)
        add(head)
        for part in group.split("/"):
            add(f"{head} {part}")
    # Split "Xyn / XYN" or "crystal room / crystal rooms", but not "A/B/C"
    if re.search(r"[A-Za-zÀ-ÿ]{2,}\s*/\s*[A-Za-zÀ-ÿ]{2,}", alias) and not re.search(r"\b[A-Z](?:/[A-Z])+\b", alias):
        for part in re.split(r"\s*/\s*", alias):
            add(part)
    return out


def _keep_en_alias(alias: str) -> bool:
    a = alias.strip()
    if not a:
        return False
    low = a.lower()
    if " " in a or "/" in a:
        return True
    if low in EN_STOP or low in EN_GENERIC:
        return False
    if low.isnumeric():
        return False
    if len(a) >= 4:
        return True
    # Short proper nouns: Sai, Xyn, Ina
    if len(a) >= 3 and a[0].isupper():
        return True
    return False


def aliases_from_clause(clause: str, inherited_en: tuple[str, ...] = ()) -> list[str]:
    aliases: list[str] = []
    seen = set()

    def add(s: str):
        s = (s or "").strip().strip("，。；、,;:）)")
        if not s or s in seen or s in SKIP_ZH_ALIASES or s in ZH_STOP:
            return
        # Skip instructional Chinese and slash-only tokens like A/B/C
        if re.fullmatch(r"[A-Za-z](?:/[A-Za-z])+", s):
            return
        if re.search(r"[\u4e00-\u9fff]", s) and (
            s.startswith(("不要", "保持", "以及", "一律", "编号", "作为", "一经", "未锁定", "所有", "等不", "唯一", "本人", "只音", "的"))
            or s.endswith(("译法", "标题", "符号"))
            or s in {"世界", "灰色", "为"}
        ):
            return
        seen.add(s)
        aliases.append(s)

    for quoted in re.findall(r"「([^」]+)」", clause):
        add(quoted)

    # Expand fake/false Sekimeiya and gray/grey Sekimeiya
    for m in re.finditer(r"\b([A-Za-z]+)/([A-Za-z]+)\s+(Sekimeiya)\b", clause, re.I):
        add(f"{m.group(1)} {m.group(3)}")
        add(f"{m.group(2)} {m.group(3)}")
    if "赝品" in clause and "Sekimeiya" in clause:
        add("赝品 Sekimeiya")
    if "灰色" in clause and "Sekimeiya" in clause:
        add("灰色 Sekimeiya")

    # hallway A/B/C 为 A/B/C走廊  -> A走廊, B走廊, C走廊
    for m in _LETTER_SLASH_ZH_RE.finditer(clause):
        for letter in m.group(1).split("/"):
            add(letter + m.group(2))

    # attic 阁楼 / teleport 传送 / Airun 艾伦山 — translation sitting after English
    for m in _ZH_AFTER_EN_RE.finditer(clause):
        add(m.group(1))

    for m in _DISCOURAGED_ZH_RE.finditer(clause):
        for part in re.split(r"[或及和]", m.group(1)):
            add(part)

    for raw in _EN_TOKEN_RE.findall(clause):
        raw = raw.strip().rstrip(".,;:")
        if not raw:
            continue
        for form in _expand_alias_forms(raw):
            # Do not let "赝品 Sekimeiya" add a bare Sekimeiya alias
            if form.lower() == "sekimeiya" and _MODIFIED_SEKIMEDIYA_RE.search(clause):
                continue
            if _keep_en_alias(form):
                add(form)

    if "Ψ" in clause:
        add("Ψ")

    for inh in inherited_en:
        add(inh)
    return aliases


def _bullet_lines(section: str) -> list[str]:
    lines = []
    for raw in section.splitlines():
        s = raw.strip()
        if s.startswith("-"):
            lines.append(s.lstrip("-").strip())
        elif s.startswith("•"):
            lines.append(s.lstrip("•").strip())
    return lines


def parse_terms_from_prompt(prompt: str) -> list[Term]:
    terms: list[Term] = []
    glossary = extract_section(prompt, "术语")
    for line in _bullet_lines(glossary):
        clauses = [c.strip() for c in re.split(r"[；;]", line) if c.strip()]
        inherited = []
        for i, clause in enumerate(clauses):
            local = aliases_from_clause(clause)
            local_en = tuple(a for a in local if re.search(r"[A-Za-z]", a))
            if i == 0:
                inherited = list(local_en)
            inherit = (
                i > 0
                and not local_en
                and bool(inherited)
                and bool(_CONTINUE_PREFIX_RE.search(clause))
            )
            aliases = aliases_from_clause(clause, inherited_en=tuple(inherited) if inherit else ())
            if not aliases:
                continue
            terms.append(Term(text=clause, aliases=tuple(dict.fromkeys(aliases))))

    must = extract_section(prompt, "必须遵守")
    # Locked personal names (item 1).
    name_line = ""
    for raw in must.splitlines():
        s = raw.strip()
        if "人名" in s or "Tanya" in s:
            name_line = (name_line + " " + s.lstrip("0123456789.、 ")).strip()
    if name_line:
        aliases = aliases_from_clause(name_line)
        # Also split enumerations: Sai、Atsuki、...
        for part in re.split(r"[、,，/]", name_line):
            m = re.search(r"[A-Za-z][A-Za-z0-9'’.\-]*", part)
            if m and _keep_en_alias(m.group(0)):
                aliases.append(m.group(0))
        aliases = [a for a in dict.fromkeys(aliases) if not re.search(r"[\u4e00-\u9fff]", a) or a in {"坦桑娅"}]
        if aliases:
            terms.append(Term(text=name_line, aliases=tuple(aliases)))
    return terms


def load_terms_json(path: Path) -> list[Term]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("terms") or data.get("entries") or []
    terms = []
    for item in data:
        if isinstance(item, str):
            terms.append(Term(text=item, aliases=tuple(aliases_from_clause(item))))
        elif isinstance(item, dict):
            text = (item.get("text") or item.get("rule") or "").strip()
            aliases = item.get("aliases") or []
            if not text:
                continue
            if not aliases:
                aliases = aliases_from_clause(text)
            terms.append(Term(text=text, aliases=tuple(aliases)))
    return terms


def load_terms(prompt_path: Path | None = None, terms_path: Path | None = None) -> list[Term]:
    terms: list[Term] = []
    if terms_path and terms_path.exists():
        terms.extend(load_terms_json(terms_path))
    if prompt_path and prompt_path.exists():
        terms.extend(parse_terms_from_prompt(prompt_path.read_text(encoding="utf-8")))
    # De-duplicate identical rule texts, merge aliases
    merged: dict[str, Term] = {}
    for t in terms:
        if t.text in merged:
            aliases = tuple(dict.fromkeys(merged[t.text].aliases + t.aliases))
            merged[t.text] = Term(text=t.text, aliases=aliases)
        else:
            merged[t.text] = t
    return list(merged.values())


def _en_present(haystack_lower: str, alias: str) -> bool:
    a = alias.lower()
    if " " in a or "/" in a or "-" in a:
        return a in haystack_lower
    return re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", haystack_lower) is not None


def match_terms(entry: dict, terms: list[Term]) -> list[str]:
    """Return relevant term rule strings for this entry (not the whole glossary)."""
    original = entry.get("text") or entry.get("original") or ""
    current = entry.get("new") or entry.get("current") or ""
    # Match against the sentence only, not the speaker field (or every line of
    # dialogue would pull in the personal-name rule).
    en = " ".join([original, current]).lower()
    zh = original + current
    hits = []
    seen = set()
    for term in terms:
        ok = False
        for alias in term.aliases:
            if re.search(r"[A-Za-zΨ]", alias):
                if alias == "Ψ":
                    ok = "Ψ" in original or "Ψ" in current
                else:
                    ok = _en_present(en, alias) or alias.lower() in (current or "").lower()
            else:
                ok = alias in zh
            if ok:
                break
        if ok and term.text not in seen:
            seen.add(term.text)
            hits.append(term.text)
    return hits


def tokenize(text: str) -> list[str]:
    tokens = []
    for t in _WORD_RE.findall((text or "").lower()):
        if re.fullmatch(r"[a-z0-9]+", t):
            if t not in EN_STOP:
                tokens.append(t)
        else:
            tokens.extend(t)
            tokens.extend(t[i:i + 2] for i in range(len(t) - 1))
    return tokens


def document_text(entry: dict) -> str:
    speaker = entry.get("speaker") or ""
    original = entry.get("text") or ""
    current = (entry.get("new") or "").strip()
    parts = []
    if speaker:
        parts.append(str(speaker))
    parts.append(original)
    if current:
        parts.append(current)
    return "\n".join(parts)


def usable_corpus_entries(entries: list[dict], only: str = "") -> list[dict]:
    out = []
    for e in entries:
        if not str(e.get("new") or "").strip():
            continue
        if only and only.lower() not in (str(e.get("group") or "") + str(e.get("source_file") or "")).lower():
            continue
        if not e.get("id"):
            continue
        out.append(e)
    return out


def is_useful_example(entry: dict) -> bool:
    text = (entry.get("text") or "").strip()
    if len(text) < 3 or text in {"...", "……", "…", "......", ".", "…。"}:
        return False
    return True


def format_example(entry: dict, score: float | None = None) -> dict:
    item = {
        "original": entry.get("text") or "",
        "current": (entry.get("new") or "").strip(),
    }
    speaker = entry.get("speaker")
    if speaker:
        item["speaker"] = speaker
    if score is not None:
        item["score"] = round(float(score), 4)
    return item


class SentenceRetriever:
    """Loads a prebuilt index, or builds an in-memory BM25 fallback."""

    def __init__(self):
        self.backend = "bm25"
        self.model_name = ""
        self.ids: list[str] = []
        self.docs: list[dict] = []
        self.id_to_pos: dict[str, int] = {}
        self.embeddings = None  # (N, D) float32, L2-normalized
        self._tokens: list[list[str]] = []
        self._df: dict[str, int] = {}
        self._inv: dict[str, list[tuple[int, int]]] = {}  # token -> [(doc_i, tf)]
        self._doc_len: list[int] = []
        self._avgdl = 0.0
        self._k1 = 1.5
        self._b = 0.75
        self.source = ""
        self._encode_lock = threading.Lock()

    @property
    def size(self) -> int:
        return len(self.ids)

    def _finalize_docs(self, docs: list[dict]):
        self.docs = docs
        self.ids = [d["id"] for d in docs]
        self.id_to_pos = {i: n for n, i in enumerate(self.ids)}

    def build_bm25(self, entries: list[dict]):
        self.backend = "bm25"
        self.model_name = "bm25"
        self._finalize_docs(entries)
        self._tokens = [tokenize(document_text(e)) for e in entries]
        self._df = {}
        self._inv = {}
        self._doc_len = [len(toks) for toks in self._tokens]
        self._avgdl = (sum(self._doc_len) / len(self._doc_len)) if self._doc_len else 0.0
        for i, toks in enumerate(self._tokens):
            tf: dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            for t, f in tf.items():
                self._df[t] = self._df.get(t, 0) + 1
                self._inv.setdefault(t, []).append((i, f))
        self.source = "memory"
        return self

    def build_sentence_transformers(self, entries: list[dict], model_name: str = DEFAULT_ST_MODEL, batch_size: int = 64):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Install with: pip install sentence-transformers\n"
                "CPU torch: pip install torch --index-url https://download.pytorch.org/whl/cpu"
            ) from exc
        self.backend = "sentence-transformers"
        self.model_name = model_name
        self._finalize_docs(entries)
        print(f"Encoding {len(entries)} sentences with {model_name} ...")
        model = SentenceTransformer(model_name)
        texts = [document_text(e) for e in entries]
        emb = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        self.embeddings = np.asarray(emb, dtype=np.float32)
        self.source = "memory"
        return self

    def save(self, index_dir: Path):
        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "version": INDEX_VERSION,
            "backend": self.backend,
            "model": self.model_name,
            "count": self.size,
        }
        (index_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        with (index_dir / "docs.jsonl").open("w", encoding="utf-8") as f:
            for e in self.docs:
                row = {
                    "id": e["id"],
                    "text": e.get("text") or "",
                    "new": e.get("new") or "",
                    "speaker": e.get("speaker"),
                    "source_file": e.get("source_file") or "",
                    "group": e.get("group") or "",
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        if self.backend == "sentence-transformers":
            if self.embeddings is None:
                raise RuntimeError("no embeddings to save")
            np.save(index_dir / "embeddings.npy", self.embeddings)
        elif self.backend == "bm25":
            payload = {
                "tokens": self._tokens,
                "df": self._df,
                "inv": self._inv,
                "doc_len": self._doc_len,
                "avgdl": self._avgdl,
                "k1": self._k1,
                "b": self._b,
            }
            # pickle keeps the inverted index compact enough and loads quickly
            import pickle
            (index_dir / "bm25.pkl").write_bytes(pickle.dumps(payload, protocol=4))
        # Drop files from the other backend so a rebuilt index stays consistent
        if self.backend == "sentence-transformers":
            (index_dir / "bm25.pkl").unlink(missing_ok=True)
        else:
            (index_dir / "embeddings.npy").unlink(missing_ok=True)
        return index_dir

    @classmethod
    def load(cls, index_dir: Path) -> "SentenceRetriever":
        index_dir = Path(index_dir)
        manifest = json.loads((index_dir / "manifest.json").read_text(encoding="utf-8"))
        docs = []
        with (index_dir / "docs.jsonl").open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    docs.append(json.loads(line))
        obj = cls()
        obj._finalize_docs(docs)
        obj.backend = manifest.get("backend") or "bm25"
        obj.model_name = manifest.get("model") or ""
        obj.source = str(index_dir)
        if obj.backend == "sentence-transformers":
            obj.embeddings = np.load(index_dir / "embeddings.npy")
            if obj.embeddings.shape[0] != len(docs):
                raise RuntimeError(
                    f"embeddings count {obj.embeddings.shape[0]} != docs {len(docs)}"
                )
        elif obj.backend == "bm25":
            import pickle
            payload = pickle.loads((index_dir / "bm25.pkl").read_bytes())
            obj._tokens = payload["tokens"]
            obj._df = payload["df"]
            obj._inv = payload["inv"]
            obj._doc_len = payload["doc_len"]
            obj._avgdl = payload["avgdl"]
            obj._k1 = payload.get("k1", 1.5)
            obj._b = payload.get("b", 0.75)
        else:
            raise RuntimeError(f"unknown index backend: {obj.backend}")
        return obj

    def encode_query(self, entry: dict):
        if self.backend != "sentence-transformers":
            raise RuntimeError("encode_query is only for sentence-transformers")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(self.model_name or DEFAULT_ST_MODEL)
        vec = model.encode(
            [document_text(entry)],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]
        return np.asarray(vec, dtype=np.float32)

    def _prepare_st_query_model(self):
        if self.backend != "sentence-transformers":
            return None
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(self.model_name or DEFAULT_ST_MODEL)

    def query_many(self, entries: list[dict], k: int, exclude_ids_fn=None, model=None) -> list[list[dict]]:
        """Retrieve top-k examples for each entry. exclude_ids_fn(entry) -> set of ids."""
        if k <= 0 or not self.ids:
            return [[] for _ in entries]
        if self.backend == "sentence-transformers":
            return self._query_many_st(entries, k, exclude_ids_fn, model)
        return [self._query_bm25(e, k, exclude_ids_fn(e) if exclude_ids_fn else set()) for e in entries]

    def query(self, entry: dict, k: int, exclude_ids: set[str] | None = None, model=None) -> list[dict]:
        return self.query_many([entry], k, (lambda _e: exclude_ids or set()), model)[0]

    def _query_many_st(self, entries, k, exclude_ids_fn, model):
        if model is None:
            model = self._prepare_st_query_model()
        texts = [document_text(e) for e in entries]
        with self._encode_lock:
            q = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        q = np.asarray(q, dtype=np.float32)
        # scores: (B, N)
        scores = q @ self.embeddings.T
        results = []
        # Over-fetch so exclusions still leave k hits
        pool = min(self.size, max(k + 32, k * 4))
        for i, e in enumerate(entries):
            exclude = exclude_ids_fn(e) if exclude_ids_fn else set()
            exclude.add(e.get("id") or "")
            # argpartition then sort the candidate slice
            row = scores[i]
            if pool >= self.size:
                cand = np.argsort(-row)
            else:
                part = np.argpartition(-row, pool - 1)[:pool]
                cand = part[np.argsort(-row[part])]
            hits = []
            for j in cand:
                doc = self.docs[int(j)]
                if doc["id"] in exclude or not is_useful_example(doc):
                    continue
                hits.append(format_example(doc, float(row[int(j)])))
                if len(hits) >= k:
                    break
            results.append(hits)
        return results

    def _query_bm25(self, entry: dict, k: int, exclude_ids: set[str]) -> list[dict]:
        q_tokens = tokenize(document_text(entry))
        if not q_tokens or not self._inv:
            return []
        N = self.size
        scores: dict[int, float] = {}
        tf_q: dict[str, int] = {}
        for t in q_tokens:
            tf_q[t] = tf_q.get(t, 0) + 1
        for t in tf_q:
            postings = self._inv.get(t)
            if not postings:
                continue
            n = self._df.get(t, 0)
            idf = math.log((N - n + 0.5) / (n + 0.5) + 1.0)
            for doc_i, f in postings:
                dl = self._doc_len[doc_i] or 1
                denom = f + self._k1 * (1 - self._b + self._b * dl / (self._avgdl or 1))
                scores[doc_i] = scores.get(doc_i, 0.0) + idf * (f * (self._k1 + 1)) / denom
        exclude = set(exclude_ids or ())
        exclude.add(entry.get("id") or "")
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        hits = []
        for doc_i, sc in ranked:
            doc = self.docs[doc_i]
            if doc["id"] in exclude or not is_useful_example(doc):
                continue
            hits.append(format_example(doc, sc))
            if len(hits) >= k:
                break
        return hits


def neighbor_ids(file_index: dict, entry: dict, radius: int) -> set[str]:
    """Ids of the target and its before/after window (same source_file)."""
    eid = entry.get("id")
    if not eid or eid not in file_index or radius < 0:
        return {eid} if eid else set()
    group, i = file_index[eid]
    start = max(0, i - radius)
    end = min(len(group), i + 1 + radius)
    return {e["id"] for e in group[start:end]}


def describe_retriever(retriever: SentenceRetriever | None, rag_k: int | None = None) -> str:
    if retriever is None:
        return "Sentence RAG: off"
    src = retriever.source or "memory"
    kpart = f"  k={rag_k}" if rag_k is not None else ""
    return (
        f"Sentence RAG: {retriever.backend}"
        + (f" ({retriever.model_name})" if retriever.model_name else "")
        + f"  docs={retriever.size}{kpart}  source={src}"
    )


def default_terms_path(prompt_path: Path) -> Path | None:
    """Optional standalone terms file next to the prompt or cwd."""
    candidates = [
        prompt_path.parent / "terms.json",
        Path("terms.json"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_retriever(
    index_dir: Path | None,
    entries: list[dict],
    only_for_fallback: str = "story",
) -> tuple[SentenceRetriever | None, str]:
    """Prefer a prebuilt index; otherwise build in-memory BM25 from entries with a new field."""
    if index_dir and Path(index_dir).exists() and (Path(index_dir) / "manifest.json").exists():
        try:
            ret = SentenceRetriever.load(Path(index_dir))
            if ret.backend == "sentence-transformers":
                try:
                    import sentence_transformers  # noqa: F401
                except ImportError:
                    print(
                        f"WARNING: {index_dir} is a sentence-transformers index, but the package "
                        "is not installed. Falling back to in-memory BM25."
                    )
                    print("For vector search: pip install sentence-transformers")
                    ret = None
            if ret is not None:
                return ret, f"loaded {index_dir}"
        except Exception as exc:
            print(f"WARNING: failed to load index at {index_dir}: {exc}", file=sys.stderr)
    corpus = usable_corpus_entries(entries, only="")
    if only_for_fallback:
        preferred = usable_corpus_entries(entries, only=only_for_fallback)
        if preferred:
            corpus = preferred
    if not corpus:
        return None, "no corpus"
    ret = SentenceRetriever().build_bm25(corpus)
    ret.source = "memory-bm25 (run python build_index.py for vector search)"
    return ret, "in-memory BM25 fallback"
