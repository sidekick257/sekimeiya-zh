"""Export all_entries.json to a readable text file (and a TSV you can open in Excel)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("entries") or []


def filtered(entries: list[dict], only: str) -> list[dict]:
    only = (only or "all").strip().lower()
    out = []
    for e in entries:
        has = bool(str(e.get("new") or "").strip())
        if only == "translated" and not has:
            continue
        if only in {"empty", "pending"} and has:
            continue
        out.append(e)
    return out


def one_block(i: int, total: int, e: dict) -> str:
    speaker = e.get("speaker") or "旁白"
    group = e.get("group") or ""
    src = e.get("source_file") or ""
    eid = e.get("id") or ""
    text = e.get("text") or ""
    new = str(e.get("new") or "").strip() or "（未译）"
    header = f"-------- {i}/{total}  {group}  {src}  {speaker}  {eid} --------"
    return f"{header}\n【原文】\n{text}\n【译文】\n{new}\n"


def write_txt(path: Path, entries: list[dict]) -> None:
    total = len(entries)
    parts = [f"共 {total} 条\n"]
    for i, e in enumerate(entries, 1):
        parts.append(one_block(i, total, e))
    path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def write_tsv(path: Path, entries: list[dict]) -> None:
    # UTF-8 BOM so Excel on Windows opens Chinese correctly.
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["序号", "id", "分组", "源文件", "说话人", "原文", "译文"])
        for i, e in enumerate(entries, 1):
            w.writerow(
                [
                    i,
                    e.get("id") or "",
                    e.get("group") or "",
                    e.get("source_file") or "",
                    e.get("speaker") or "",
                    e.get("text") or "",
                    e.get("new") or "",
                ]
            )


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="把 all_entries.json 导出成方便阅读的文本。")
    parser.add_argument("--input", type=Path, default=here / "all_entries.json")
    parser.add_argument("--output", type=Path, default=here / "readable.txt", help="可读文本，默认 readable.txt")
    parser.add_argument("--tsv", type=Path, default=here / "readable.tsv", help="表格文件，可用 Excel 打开；传空字符串则不生成")
    parser.add_argument(
        "--only",
        default="all",
        help="all（全部）、translated（只已译）、empty（只未译）",
    )
    args = parser.parse_args()
    if not args.input.is_file():
        raise SystemExit(f"ERROR: 找不到 {args.input}")

    entries = filtered(load_entries(args.input), args.only)
    write_txt(args.output, entries)
    filled = sum(1 for e in entries if str(e.get("new") or "").strip())
    print(f"Wrote {len(entries)} entries to {args.output} ({filled} translated).")

    tsv = args.tsv
    if str(tsv).strip():
        write_tsv(tsv, entries)
        print(f"Wrote {tsv} (open in Excel).")


if __name__ == "__main__":
    main()
