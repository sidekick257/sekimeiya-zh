#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成自定义文本标签的补充翻译表。

游戏给 {time=...} 这种标签注册了自定义渲染函数，搜索界面的文本已经
把标签替换成了显示值（如 9:00），和翻译表里的原始 key 对不上，所以
这里生成「渲染后英文 -> 中文」的补充表。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "patch", "tl", "zh_cn", "zz_tagged_strings.rpy")

TIME_TAG = re.compile(r"\{time=([^}]*)\}")


def render_time(arg, fmt24):
    """复刻游戏 time_tag 的渲染结果。"""
    if fmt24:
        if ":" in arg:
            return arg
        if arg and arg[-1] == ".":
            return arg[:-1] + ":00."
        return arg + ":00"

    if arg and arg[-1] == ".":
        arg = arg[:-1]
    if ":" in arg:
        h, m = arg.split(":")
        h = int(h)
    else:
        h = int(arg)
    t = "a.m."
    if h >= 12:
        t = "p.m."
        h -= 12
    if h == 0:
        h = 12
    if ":" in arg:
        return "{}:{} {}".format(h, m, t)
    return "{} {}".format(h, t)


def main():
    ZERO_WIDTH = re.compile(r"\{(?:w|nw|p|cps)(?:=[^}]*)?\}")
    entries = [e for e in json.load(open("all_entries.json", encoding="utf-8"))["entries"]
               if e.get("group") == "story" and (e.get("new") or "").strip()]

    # 主表里没有的条目（导出时被多行字符串卡掉的那些），也放进补充表
    main_table = open(os.path.join(HERE, "patch", "tl", "zh_cn", "strings_script.rpy"), encoding="utf-8").read()

    def in_main(en):
        esc = en.replace("\\", "\\\\").replace('"', '\\"')
        return ('old "%s"' % esc) in main_table

    table = {}
    missing = 0
    for e in entries:
        en = e["text"]
        zh = e["new"]
        if not in_main(en):
            table[en] = zh
            missing += 1

    for e in entries:
        en = e["text"]
        zh = e["new"]
        if ZERO_WIDTH.search(en):
            table[ZERO_WIDTH.sub("", en)] = zh
        if not TIME_TAG.search(en):
            continue
        for fmt24 in (True, False):
            rendered = TIME_TAG.sub(lambda m: render_time(m.group(1), fmt24), en)
            table[rendered] = zh
            # 有些显示路径会把零宽标签也一并吃掉
            table[ZERO_WIDTH.sub("", rendered)] = zh

    # 去重后如果两个 key 指向不同译文，保留第一个
    lines = ["# 自动生成：自定义文本标签渲染后的补充翻译表。", "", "init -1 python:", "    dsh_tagged_strings = {"]
    for k, v in table.items():
        lines.append("        %s: %s," % (repr(k), repr(v)))
    lines.append("    }")
    lines.append("")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("写了 %d 条" % len(table))


if __name__ == "__main__":
    main()
