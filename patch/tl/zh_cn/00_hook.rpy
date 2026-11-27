# 非侵入式汉化入口：不改游戏脚本/字体/options，只新增 tl/ 与本文件。
#
# 1) 游戏自带语言系统把 _() 解析成恒等函数，renpy.translate_string() 才是好的。
# 2) {time=...} 等自定义标签会被 translate_string 先渲染，用补充表兜底。
# 3) 搜索索引在 init 阶段建立（那时翻译没生效），给 SearchEntry.what 加惰性翻译。
# 4) 界面里有些地方内联写死 Cabin/Acumin 字体（无汉字），用 font_replacement_map
#    把它重定向到中文字体 —— 键和值都是 (字体, 粗体, 斜体) 三元组。

init 999 python:
    _dsh_cn = ("tl/zh_cn/IBMPlexSansSC-Text.ttf", False, False)
    for _f in ("fonts/Acumin-BdPro.otf", "fonts/Cabin-Bold2.ttf",
               "fonts/Cabin-Medium.ttf", "fonts/Cabin-Medium2.ttf",
               "fonts/Cabin-SemiBold.ttf", "fonts/arial.ttf"):
        for _b in (False, True):
            for _i in (False, True):
                config.font_replacement_map[(_f, _b, _i)] = _dsh_cn

    def dsh_tr(s):
        if not isinstance(s, basestring) or dsh_busy[0]:
            return s
        t = renpy.translate_string(s)
        if t != s:
            return t
        r = store.dsh_tagged_strings.get(s)
        if r is not None:
            return r
        dsh_busy[0] = True
        try:
            tmp = renpy.text.text.Text(s)
            tmp.update()
            msg = "".join([x[1] for x in tmp.tokens if isinstance(x[1], basestring)])
        finally:
            dsh_busy[0] = False
        if msg != s:
            r = store.dsh_tagged_strings.get(msg)
            if r is not None:
                return r
        return s

    dsh_busy = [False]
    config.say_menu_text_filter = dsh_tr
    _ = dsh_tr

    _dsh_se = getattr(store, "SearchEntry", None)
    if _dsh_se is not None and not getattr(_dsh_se, "_dsh_patched", False):
        _dsh_se._dsh_patched = True
        _dsh_fget = _dsh_se.what.fget
        _dsh_fset = _dsh_se.what.fset
        def _dsh_get(self):
            return dsh_tr(_dsh_fget(self))
        _dsh_se.what = property(_dsh_get, _dsh_fset)

    import renpy.text.text as _dsh_textmod
    if not getattr(_dsh_textmod, "_dsh_patched", False):
        _dsh_textmod._dsh_patched = True
        _dsh_orig = _dsh_textmod.Text.__init__
        def _dsh_init(self, text, *args, **kwargs):
            if isinstance(text, basestring) and not dsh_busy[0]:
                text = dsh_tr(text)
            _dsh_orig(self, text, *args, **kwargs)
        _dsh_textmod.Text.__init__ = _dsh_init
