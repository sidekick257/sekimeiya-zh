# 交接说明

## 项目状态

**已完成：**
- 脚本提取（约 24,396 条）
- 正文翻译（story 约 22,578 条）
- 一轮校对（v4-pro）
- 引用对照表生成（276 处，208 处不一致）

**未完成：**
- 写回游戏脚本（`merge_back.py` 未跑）
- 游戏内测试
- UI/笔记等非正文部分翻译

## 下一步

1. **检查统一结果**
   ```bat
   python show_diff.py all_entries.before_unify.json all_entries.json --limit 30
   ```

2. **写回游戏**
   ```bat
   python merge_back.py
   ```
   会修改游戏目录下的 `.rpy` 文件。建议先备份游戏。

3. **测试**
   启动游戏，切中文，检查：
   - 第五章复盘是否和第一章一致
   - 第三章偷听是否对得上
   - 录音笔四处是否统一
   - 有无「您」、术语是否正确

4. **补漏**
   - UI 文本（`group: ui`）
   - 笔记（`group: notes`）
   - Tips

## 已知问题

- 对照表里部分「稍作改写」类型英文本身不完全相同，中文不必强行统一
- 断续重述（偷听残句）只需关键词一致，不必补全
- 部分长句在对照表里被截断，完整译文以 JSON 为准

## 文件对应

| 游戏文件 | JSON group | 说明 |
|----------|------------|------|
| `script.rpy` | story | 主线正文 |
| `notes.rpy` | notes | 笔记/成就 |
| `tips.rpy` | tips | 提示 |
| `gui.rpy` / `options.rpy` | ui | 界面 |
| `screens_*.rpy` | ui | 界面屏幕 |

## API 配置

```bat
set DEEPSEEK_API_KEY=sk-...
```

模型选择：
- 初译：`deepseek-chat`（快）
- 校对：`deepseek-v4-pro`（质量高，慢）

## 联系

如有问题，对照 `sekimeiya_quote_reuse_all_entries.md` 里的 id 搜索 JSON。
