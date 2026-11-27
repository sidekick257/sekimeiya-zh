#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把译文重新打包成非侵入式补丁，并装进游戏目录。

用法：
    python sync_patch.py              # 只重新生成 patch/
    python sync_patch.py --install    # 生成后复制进游戏

游戏位置可用 --game 指定，默认读环境变量 SEKIMEIYA_GAME 或下面这个路径。
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "patch")
DEFAULT_GAME = r"E:\steam\steamapps\common\The Sekimeiya Spun Glass\game"


def run(script):
    print(">> " + script)
    subprocess.check_call([sys.executable, os.path.join(HERE, script)], cwd=HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--game", default=os.environ.get("SEKIMEIYA_GAME", DEFAULT_GAME))
    args = ap.parse_args()

    run("make_strings.py")
    run(os.path.join("review", "make_tagged_strings.py"))

    if not args.install:
        return

    game = args.game
    if not os.path.isdir(game):
        sys.exit("找不到游戏目录：%s" % game)

    # tl/ 与 gui/ 都是新增文件，不会覆盖原版资源
    for rel in ("tl", "gui"):
        base = os.path.join(PATCH, rel)
        for path in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            if os.path.isdir(path):
                continue
            out = os.path.join(game, rel, os.path.relpath(path, base))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(path, out)
            # 删掉旧编译产物，强制重编译
            for ext in (".rpyc",):
                stale = out[:-4] + ext if out.endswith(".rpy") else None
                if stale and os.path.exists(stale):
                    os.remove(stale)
    shutil.copy2(os.path.join(PATCH, "zz_search_all.rpy"), os.path.join(game, "zz_search_all.rpy"))
    print("已安装到 %s" % game)


if __name__ == "__main__":
    main()
