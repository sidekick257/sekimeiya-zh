#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成中文版菜单标题图（替代 gui/header_<英文>.png）。

原图是透明底、白色发光字、两侧菱形装饰。这里用同样的思路重画。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_PATH = r"E:\steam\steamapps\common\The Sekimeiya Spun Glass\game\fonts\SourceHanSansCN-Bold.otf"
FALLBACK = r"E:\steam\steamapps\common\The Sekimeiya Spun Glass\game\tl\zh_cn\SourceHanSansCN-Regular.otf"
OUT_DIR = r"E:\steam\steamapps\common\The Sekimeiya Spun Glass\game\gui"

GLOW = (128, 231, 247)
WHITE = (255, 255, 255)

TITLES = ["设置", "地图", "笔记", "关系图", "关系图教程", "笔记教程", "搜索", "提示", "保存", "关于", "历史"]

HEIGHT = 72
FONT_SIZE = 44


def make(text, font_path, out_path):
    font = ImageFont.truetype(font_path, FONT_SIZE)
    # 量一下文字
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    tw = r - l
    th = b - t

    pad = 24
    dia = 10
    gap = 14
    W = tw + 2 * (pad + dia + gap)
    H = HEIGHT
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    x = (W - tw) / 2 - l
    y = (H - th) / 2 - t

    # 发光层
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, font=font, fill=GLOW + (255,))
    cx = W / 2
    for dx in (-1, 1):
        px = cx + dx * (tw / 2 + gap + dia / 2)
        cy = H / 2
        gd.polygon([(px, cy - dia), (px + dia, cy), (px, cy + dia), (px - dia, cy)], fill=GLOW + (255,))

    blurred = glow.filter(ImageFilter.GaussianBlur(6))
    for _ in range(3):
        img.alpha_composite(blurred)

    # 白色主体
    d2 = ImageDraw.Draw(img)
    d2.text((x, y), text, font=font, fill=WHITE + (255,))
    for dx in (-1, 1):
        px = cx + dx * (tw / 2 + gap + dia / 2)
        cy = H / 2
        d2.polygon([(px, cy - dia), (px + dia, cy), (px, cy + dia), (px - dia, cy)], fill=WHITE + (255,))

    img.save(out_path)
    print("%s -> %s (%dx%d)" % (text, os.path.basename(out_path), W, H))


def main():
    font = FONT_PATH if os.path.exists(FONT_PATH) else FALLBACK
    print("font:", font)
    os.makedirs(OUT_DIR, exist_ok=True)
    for t in TITLES:
        make(t, font, os.path.join(OUT_DIR, "header_%s.png" % t))


if __name__ == "__main__":
    main()
