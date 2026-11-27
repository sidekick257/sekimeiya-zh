# The Sekimeiya: Spun Glass 简体中文补丁

面向《The Sekimeiya: Spun Glass》(Ren'Py 7.4.4) 的简体中文补丁，采用**非侵入式**方案：不修改游戏任何原版文件。

## 目录结构

```
all_entries.json      译文总表（24,396 条，唯一的真源，改这里）
script.rpy            英文原版脚本，只读参考，不要改
patch/                可直接分发的补丁内容
  tl/zh_cn/           正文表、界面表、补充表、字体、入口脚本
  gui/                中文菜单标题图（新增，不覆盖原图）
  zz_search_all.rpy   搜索全解锁（可选，正式发布前删掉）
sync_patch.py         重新生成补丁并装进游戏
make_strings.py        从 all_entries.json 生成正文翻译表
review/               生成器与审计工具
三审须知.md            给校对人员看的说明
```

## 工作流

改完 `all_entries.json` 之后：

```bash
python sync_patch.py --install
```

会重新生成 `patch/tl/zh_cn/strings_script.rpy`、`zz_tagged_strings.rpy`，然后复制进游戏目录（路径默认 `E:\steam\steamapps\common\The Sekimeiya Spun Glass\game`，可用环境变量 `SEKIMEIYA_GAME` 覆盖）。首次启动需要重新编译，约 20–60 秒。

只生成不安装：`python sync_patch.py`。

## 补丁原理

游戏的 `script.rpy` 原样保留（在 `scripts.rpa` 里），中文全部通过 `game/tl/zh_cn/` 生效：

- `00_hook.rpy`：游戏自带的语言系统会把 `_()` 解析成恒等函数，导致翻译表失效；这里把 `_` 换成 `renpy.translate_string()`，并给 say/菜单加过滤
- `strings_script.rpy`：22,557 条正文 + 选项的英中对照
- `ui_strings.rpy`：188 条界面文本（设置、菜单、搜索、按钮）
- `zz_tagged_strings.rpy`：补充表，处理 `{time=...}` 这类会被提前渲染的标签、`{i}`/`{w}` 这类外层标签，以及多行字符串
- `00_language.rpy`：字体组——拉丁/汉字用 IBM Plex SC，数学符号（如 ∅）回落 DejaVu
- 界面里内联写死 Cabin/Acumin 字体的地方，用 `config.font_replacement_map` 在运行时重定向到中文字体

`game/` 里没有任何原版文件被修改。卸载 = 删掉 `tl/zh_cn/`、`gui/header_*.png`、`zz_search_all.rpy`。

## 当前进度

- 正文与选项：22,581 条 **全部有译文**
- 三审进行中：已细读约 1,000 条（4.4%），逐条修正
- 笔记（Notes）、Tips、第五章问答、部分存档界面文案：**未翻译**（另属别的数据表）

## 已知问题

- 中文菜单标题图是脚本生成的，字形与原版美术不完全一致（`review/make_headers.py`）
- 搜索索引在 init 阶段建立，翻译靠读取时惰性替换（`patch/tl/zh_cn/00_hook.rpy` 里有注释说明）
