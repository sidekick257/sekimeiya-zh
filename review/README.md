# review/ 说明

只读分析产物，没有改动 `all_entries.json` 或任何 `.rpy`。

| 文件 | 内容 |
|---|---|
| `严重问题.md` | 11 条，全部是 Ren'Py 标签问题（丢 `{tip}`、多 `{tip}`、多 `{nw}`），需要人工确认 |
| `机械修正.tsv` | 173 处无歧义的统一（`A 走廊`→`A走廊`、`过去 Sekimeiya`→`过去Sekimeiya`、`『』`→`「」`、`幕布`→`遮布` 等） |
| `重复引用不一致.tsv` | 205 组「同一句英文、不同中文」，按 group 分组 |
| `make_consistency.py` | 生成上面三个文件 |
| `export_queue.py` | 按区间导出 `原文 / 现译` 分块，给审稿用 |

根目录另有：

| 文件 | 内容 |
|---|---|
| `audit_zh.py` | 术语 / 标点 / 标签 / 长度规则扫描 |
| `detect_misalign.py` | 串行检测（重复译文、长度比、人名锚点、标签） |

```bat
python audit_zh.py --md review/audit.md
python detect_misalign.py --out review/misalign.md
python review/make_consistency.py
```
