import json
import re
from pathlib import Path

base = Path(r"D:\work\sekimeiya\sekimeiya-zh-latest")
entries_path = base / "all_entries.json"
tl_path = base / "output" / "tl" / "zh_cn" / "script.rpy"
out_path = base / "script_zh.rpy"

data = json.loads(entries_path.read_text(encoding="utf-8"))
tl_text = tl_path.read_text(encoding="utf-8")

trans = {}
for e in data["entries"]:
    old = (e.get("text") or "").strip()
    new = (e.get("new") or "").strip()
    if old and new and old != new:
        trans[old] = new

print(f"all_entries 里有 {len(trans)} 条有效翻译")

count = 0
def repl(m):
    global count
    old = m.group(1)
    if old in trans:
        count += 1
        return f'# "{old}"\n    "{trans[old]}"'
    return m.group(0)

new_tl = re.sub(
    r'#\s*"(.*?)"\s*\n\s*"(.*?)"',
    repl,
    tl_text,
    flags=re.DOTALL
)

out_path.write_text(new_tl, encoding="utf-8")
print(f"已替换 {count} 条 -> {out_path}")