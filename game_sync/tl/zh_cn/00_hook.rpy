# Auto-generated hook: look up say/menu text in the string translation table.
# Copy the whole tl/zh_cn folder to:  <game>/game/tl/zh_cn/
#
# This covers dialogue, menu choices, and strings already wrapped in _().
# Notes, tip titles, SceneTitle, and some UI literals are NOT wrapped in _()
# in the original game — use output/patched/ for those (do not mix both methods).

init 999 python:
    config.say_menu_text_filter = _
