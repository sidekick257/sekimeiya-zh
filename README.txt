《The Sekimeiya: Spun Glass》简体中文翻译包
==========================================

本包只负责「提取纯文本」和「把译文填回脚本」，不包含任何译文。
all_entries.json 里每条的 new 字段都是空的。用脚本调用 API 自动翻译即可，不需要在网页里一条条手翻。

文件说明
--------
  all_entries.json       全部 24,396 条待译文本（一份完整总表）
  map/entries_map.json   回填对照表（翻译时不用改）
  source/                原始 .rpy 副本，供回填使用
  PROMPT.txt             系统提示词（含专有名词；要求输出简体中文）
  translate_batch.py     读取总表，按批次调用 API（默认 DeepSeek，也可切到 Gemini / Grok）
  merge_back.py          把译文填回 Ren'Py
  requirements.txt       Python 依赖（openai、google-genai）

工作流程是：纯文本提取（已完成，在 all_entries.json）→ 脚本自动翻译 → merge_back 合并回游戏。
分批是脚本在调用 API 时自己切的，你不需要手动拆文件。进度会写回 all_entries.json，已经填好的 new 会被跳过，所以中断后重新运行即可续传。

虽然模型上下文可以很长，也不建议一次把两万多条全部塞进同一次请求：输出有长度上限，容易被截断或格式坏掉；失败就要整包重来。脚本默认每次发送 400 条，可用 --batch-size 修改。

推荐做法：用 DeepSeek
---------------------
1. 打开 https://platform.deepseek.com/api_keys ，注册或登录后创建 API Key。
2. 在平台里充值后再调用（按 token 计费）。不要把密钥粘贴到聊天里，也不要写进脚本，只放到环境变量 DEEPSEEK_API_KEY。
3. 安装依赖并运行：

  pip install -r requirements.txt

  # Linux / macOS / Git Bash
  export DEEPSEEK_API_KEY="你的密钥"

  # Windows CMD
  set DEEPSEEK_API_KEY=你的密钥

  # Windows PowerShell
  $env:DEEPSEEK_API_KEY="你的密钥"

  python translate_batch.py
  python merge_back.py

默认模型是 deepseek-v4-pro（截至 2026 年 11 月，DeepSeek API 目前质量最好的型号；旧的 deepseek-chat / deepseek-reasoner 已下线）。要换更快、更便宜的 Flash，请用官方调用名 deepseek-flash。
根据 DeepSeek 官方文档（https://api-docs.deepseek.com/quick_start/pricing/），
deepseek-flash 当前对应的模型版本就是 DeepSeek-V4.1-Flash-1017。
不要把 DeepSeek-V4.1-Flash-1017 当作模型 ID 来传；官方要求使用 deepseek-flash。
旧名 deepseek-v4-flash 也会被服务器转到同一款 Flash，并按 Flash 价格计费。

  python translate_batch.py --model deepseek-flash

可选：改用 Gemini 或 Grok
------------------------
  python translate_batch.py --provider gemini
  python translate_batch.py --provider xai

Gemini 用环境变量 GEMINI_API_KEY，默认模型 gemini-4-hydrogen（免费档可用）。
Grok 用环境变量 XAI_API_KEY，默认模型 grok-4.7（需在 https://console.x.ai/ 预充值）。

常用参数
--------
  python translate_batch.py --batch-size 800   每次请求的条数（默认 400）
  python translate_batch.py --only story       先只译正文（script.rpy）
  python translate_batch.py --limit 2          先试跑两个批次
  python translate_batch.py --dry-run          只统计，不调用 API
  python translate_batch.py --delay 1.5        批次之间的间隔秒数
  python translate_batch.py --timeout 600      单次请求最长等待秒数
  python translate_batch.py --provider gemini  改用 Gemini
  python translate_batch.py --model 模型名      更换模型

请只填写 new，不要改 id、speaker、text。
原文里的 Ren'Py 标签（如 {time=9}、{w}、{nw}）必须在译文中原样保留。
API 密钥只从环境变量读取，脚本里不会写入密钥。

专有名词
--------
  以同目录下 PROMPT.txt 中的锁定术语表为准（已按你填好的译法更新）。
  人名和 Sekimeiya、Spun Glass、Xyn 一律保留英文；Tanya 必须写成「坦桑娅」。
  未在 PROMPT.txt 里锁定的词（如 copy point、Nomdaid、结局名）由模型自行决定，但全文须统一。

条目构成
--------
  story      22,581  正文（script.rpy）
  tips          677  游戏内提示
  questions     458  向玩家提出的问题和选项
  ui            398  菜单、界面、角色显示名等
  notes         282  游戏内笔记
  合计       24,396

如何填回游戏
------------
  python merge_back.py

会在 output/ 下生成两种结果，请只选用一种，不要同时放进同一份游戏：

1) output/tl/zh_cn/
   标准的 translate zh_cn 文件。把整个 zh_cn 文件夹复制到游戏的 game/tl/zh_cn/。
   能覆盖对白、选项，以及源码里已经用 _() 包起来的界面文字。
   笔记概要、提示标题、SceneTitle 等没有用 _() 的内容不会自动生效。

2) output/patched/   （推荐，覆盖更全）
   在原始 .rpy 的对应位置直接换成中文。
   先备份游戏里的原文件，再把 patched/ 中的文件按同样路径复制到游戏的 game/ 目录
   （例如 patched/script.rpy → game/script.rpy）。
   重新启动游戏后，Ren'Py 会重新编译。

如果只翻译了部分条目，未填写的会保持英文。

未提取的内容
------------
下面这些基本是程序逻辑或曲目原名，没有放进翻译列表：
  - scripts/translations.rpy、analytics.rpy、analytics_default_values.rpy
  - debug.rpy、effect_snow.rpy、keybinding.rpy
  - search_note_functions.rpy、setup_sprites.rpy
  - setup_music.rpy 中的乐曲标题和艺术家名（曲目原名，通常不翻译）
  - 文件名、变量名、标签名、纯代码、图片/音效路径
