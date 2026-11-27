# 中文字体。拉丁与汉字用 IBM Plex SC，数学符号（∅ 空集、箭头等）回落到 DejaVu，
# 因为 Plex SC 没有 U+2205 —— 说话人指示用的 ∅ 会变成方块。

init -10 python:
    dsh_font = FontGroup().add("tl/zh_cn/IBMPlexSansSC-Text.ttf", 0x0000, 0x20FF).add("DejaVuSans.ttf", 0x2100, 0x23FF).add("tl/zh_cn/IBMPlexSansSC-Text.ttf", 0x2400, 0x10FFFF)

translate zh_cn style default:
    font dsh_font

translate zh_cn style say_dialogue:
    font dsh_font

translate zh_cn style say_thought:
    font dsh_font

translate zh_cn style menu_choice:
    font dsh_font

translate zh_cn style button_text:
    font dsh_font

translate zh_cn style label_text:
    font dsh_font

translate zh_cn style pref_label:
    font dsh_font

translate zh_cn style radio_button_text:
    font dsh_font

translate zh_cn style check_button_text:
    font dsh_font
