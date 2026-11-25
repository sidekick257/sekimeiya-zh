# Sekimeiya 汉化项目

《The Sekimeiya: Spun Glass》中文本地化项目。

## 目录结构

```
sekimeiya_translatable_scripts/
├── all_entries.json              # 主数据文件，所有条目的原文和译文
├── all_entries.before_*.json     # 各阶段备份
├── PROMPT.txt                    # 初译提示词
├── PROOFREAD.txt                 # 校对提示词
├── translate_batch.py            # 批量翻译脚本
├── proofread_batch.py            # 批量校对脚本
├── unify_quotes.py               # 引用统一脚本
├── merge_back.py                 # 写回游戏脚本
├── export_readable.py            # 导出可读文本
├── show_diff.py                  # 对比差异
├── extract_quotes.py             # 提取引用对
├── align_quotes.py               # 对齐引用（实验性）
├── mark_done.py                  # 标记已校对
├── proofread_done.txt            # 已校对 id 列表
├── sekimeiya_quote_reuse*.md     # 引用对照表
├── sekimeiya_full_story_with_choices.txt  # 中文全文本
├── readable.txt / readable.tsv   # 可读导出
├── script.rpy / notes.rpy / ...  # 游戏脚本（已提取）
├── requirements.txt              # Python 依赖
└── README.txt                    # 本文件
```

## 工作流程

### 1. 提取
从游戏 `.rpy` 文件提取可翻译文本 → `all_entries.json`

### 2. 翻译
```bat
set DEEPSEEK_API_KEY=sk-...
python translate_batch.py --provider deepseek --model deepseek-chat --only story
```

### 3. 校对
```bat
python proofread_batch.py --provider deepseek --model deepseek-v4-pro --only story
```

### 4. 统一引用
```bat
python unify_quotes.py
```

### 5. 写回游戏
```bat
python merge_back.py
```

## 关键文件说明

| 文件 | 用途 |
|------|------|
| `all_entries.json` | 核心数据。每条包含 `id`、`text`（英文）、`new`（中文）、`source_file`、`group` |
| `PROMPT.txt` | 初译系统提示词，控制翻译风格 |
| `PROOFREAD.txt` | 校对系统提示词，控制润色力度 |
| `proofread_done.txt` | 已校对条目 id，用于断点续跑 |
| `sekimeiya_quote_reuse_all_entries.md` | 引用对照表，列出同一句话在不同章节的出现位置和 id |
| `merge_back.py` | 把 `all_entries.json` 的译文写回 `.rpy` 文件 |
| `show_diff.py` | 对比两个 JSON 的差异 |

## 术语锁定

- 人名保持英文：Atsuki、Shiroya、Akaro、Naomi、Sai、Erina、Isla、Katei
- 遮布（curtain）
- 水晶展室（crystal room）
- 芦屋塔（Ashiya Tower）
- 不用「您」

## 引用统一

游戏有大量跨章节引用（第五章复盘、第三章偷听、录音笔四处出现等）。
`sekimeiya_quote_reuse_all_entries.md` 列出了 276 处引用对，其中 208 处译文不一致。
`unify_quotes.py` 会把引用处的译文统一成原句处的译文。

## 备份说明

| 文件 | 时间点 |
|------|--------|
| `all_entries.bak.json` | 最早备份 |
| `all_entries.flash.json` | flash 模型翻译后 |
| `all_entries.before_proofread.json` | 校对前 |
| `all_entries.before_align.json` | 对齐实验前 |
| `all_entries.before_unify.json` | 引用统一前 |

## 依赖

```
pip install openai
```

## 注意事项

- DeepSeek API 有并发和余额限制，v4-pro 并发上限约 49
- 校对脚本支持 `--workers` 并发，建议 8-16
- 中断后重跑会跳过 `proofread_done.txt` 中已记录的 id
- 最终写回前务必备份游戏原文件
