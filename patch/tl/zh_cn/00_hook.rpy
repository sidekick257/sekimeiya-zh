init 999 python:
    import re as _dsh_re

    _dsh_cn = ("tl/zh_cn/IBMPlexSansSC-Text.ttf", False, False)
    for _f in ("fonts/Acumin-BdPro.otf", "fonts/Cabin-Bold2.ttf",
               "fonts/Cabin-Medium.ttf", "fonts/Cabin-Medium2.ttf",
               "fonts/Cabin-SemiBold.ttf", "fonts/arial.ttf"):
        for _b in (False, True):
            for _i in (False, True):
                config.font_replacement_map[(_f, _b, _i)] = _dsh_cn

    _dsh_zw = _dsh_re.compile(r"\{(?:w|nw|p|cps)(?:=[^}]*)?\}")
    _dsh_time = _dsh_re.compile(r"\{time=([^}]*)\}")
    _dsh_any_tag = _dsh_re.compile(r"\{[^}]*\}")

    def _dsh_time_text(arg, fmt24):
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
        ampm = "a.m."
        if h >= 12:
            ampm = "p.m."
            h -= 12
        if h == 0:
            h = 12
        if ":" in arg:
            return "{}:{} {}".format(h, m, ampm)
        return "{} {}".format(h, ampm)

    def _dsh_plain(s):
        """把带标签的显示文本变成纯文本（{time} 按当前设置渲染，其余标签去掉）。"""
        if "{time=" in s:
            fmt24 = getattr(store.persistent, "time_format_24", True)
            s = _dsh_time.sub(lambda m: _dsh_time_text(m.group(1), fmt24), s)
        return _dsh_any_tag.sub("", s)

    def _dsh_lookup(s):
        t = renpy.translate_string(s)
        if t != s:
            return t
        table = store.dsh_tagged_strings
        cands = [s, _dsh_zw.sub("", s)]
        if "{time=" in s:
            for fmt24 in (True, False):
                r = _dsh_time.sub(lambda m: _dsh_time_text(m.group(1), fmt24), s)
                cands.append(r)
                cands.append(_dsh_zw.sub("", r))
        for c in cands:
            v = table.get(c)
            if v is not None:
                return v
        return None

    _dsh_quotes = (u'"', u"\u201c")

    def dsh_tr(s):
        if not isinstance(s, basestring):
            return s
        v = _dsh_lookup(s)
        if v is not None:
            return v
        if len(s) >= 2 and s[0] in _dsh_quotes and s[-1] in (u'"', u"\u201d"):
            v = _dsh_lookup(s[1:-1])
            if v is not None:
                return s[0] + v + s[-1]
        return s

    config.say_menu_text_filter = dsh_tr
    _ = dsh_tr

    ## 搜索条目惰性翻译
    _dsh_se = getattr(store, "SearchEntry", None)
    if _dsh_se is not None and not getattr(_dsh_se, "_dsh_patched", False):
        _dsh_se._dsh_patched = True
        _dsh_fget = _dsh_se.what.fget
        _dsh_fset = _dsh_se.what.fset
        def _dsh_get(self):
            return dsh_tr(_dsh_fget(self))
        _dsh_se.what = property(_dsh_get, _dsh_fset)

    ## 搜索匹配与复制：去掉标签（原来只处理了 {time}）
    _dsh_srch = getattr(store, "Search", None)
    if _dsh_srch is not None and not getattr(_dsh_srch, "_dsh_patched", False):
        _dsh_srch._dsh_patched = True
        _dsh_ismatch = _dsh_srch.IsMatch

        def _dsh_ismatch_new(self, src, target):
            if isinstance(src, basestring):
                src = _dsh_plain(src)
            return _dsh_ismatch(self, src, target)
        _dsh_srch.IsMatch = _dsh_ismatch_new

        def _dsh_copy_new(self, node):
            try:
                entry = self.CreateSearchEntry(store.GetGlobalIndexFromNode(node))
                text_raw = _dsh_plain(entry.what.replace("    ", ""))
                store.clipboard.copy(text_raw, text_raw)
            except Exception:
                pass
        _dsh_srch.Copy = _dsh_copy_new

    ## 显示层兜底；∅ 这个字形中文字体没有，强制用字体组
    import renpy.text.text as _dsh_textmod
    if not getattr(_dsh_textmod, "_dsh_patched", False):
        _dsh_textmod._dsh_patched = True
        _dsh_orig = _dsh_textmod.Text.__init__
        def _dsh_init(self, *args, **kwargs):
            if args and isinstance(args[0], basestring):
                args = (dsh_tr(args[0]),) + args[1:]
            elif isinstance(kwargs.get("text"), basestring):
                kwargs["text"] = dsh_tr(kwargs["text"])
            if (args and args[0] == u"\u2205") or kwargs.get("text") == u"\u2205":
                kwargs.setdefault("font", dsh_font)
            _dsh_orig(self, *args, **kwargs)
        _dsh_textmod.Text.__init__ = _dsh_init

    ## 预建的说话人指示符图片：重建一份带字体组的
    try:
        _sc = store.GuiElementScaling
        _outl = store.gui.dialogue_outline[store.gui.preference("dialogue_outline_idx")]
        _pov = _dsh_textmod.Text(u"\u2205", size=12, yoffset=_sc(3), xoffset=_sc(-30),
                                 outlines=_outl, font=dsh_font)
        renpy.image("narrator_pov_img", _pov)
    except Exception as e:
        print("DSH_POV_ERR %r" % e)
