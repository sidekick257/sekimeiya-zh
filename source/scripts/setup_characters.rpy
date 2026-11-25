## @TODO: Different colors for character name and character text for supreme clarity

image narrator_pov_img = Text("∅", size=12, yoffset=GuiElementScaling(3), xoffset=GuiElementScaling(-30), outlines=gui.dialogue_outline[gui.preference("dialogue_outline_idx")])
image atsuki_indicator = Text(
    "@",
    size=22,
    yoffset=GuiElementScaling(-4),
    outlines=gui.dialogue_outline[gui.preference("dialogue_outline_idx")],
    color="#1cad49" if persistent._gui_preference['colored_speaker'] else "#ffffff")
image atsuki_indicator_small = Text(
    "@",
    size=15,
    yoffset=GuiElementScaling(-4), outlines=gui.dialogue_outline[gui.preference("dialogue_outline_idx")],
    color="#1cad49" if persistent._gui_preference['colored_speaker'] else "#ffffff")
image atsuki_indicator_b = Text(
    "B",
    size=10,
    yoffset=GuiElementScaling(12),
    xoffset=GuiElementScaling(-4), outlines=gui.dialogue_outline[gui.preference("dialogue_outline_idx")],
    color="#1cad49" if persistent._gui_preference['colored_speaker'] else "#ffffff")

init -50 python:
    def creator_pov_tag(tag, argument, contents):

        if len(renpy.game.contexts)==1:
            ## We're in the main game
            rv = []

            if 'image' in contents[0][1]:
                ## Atsuki offset
                txt_temp = renpy.text.text.Text("@", size=22)
            else:
                txt_temp = renpy.text.text.Text(contents[0][1])

            width = txt_temp.render(0,0,0,0).width
            offset = int(20-GuiElementScaling(width))

            rv += [
                contents[0],
                (renpy.TEXT_TAG, "space="+str(offset)),
                (renpy.TEXT_TAG, "image=narrator_pov_img"),
                ]

            return rv

        else:
            ## We're on the search screen or tips, don't add the indicator
            ## On the search screen, it extends the size of single-line entries down to two lines
            return contents

    config.custom_text_tags["creator_pov"] = creator_pov_tag

    chr_c    = CharacterData(_("Creator"), "∅", force_symbol=True, category='special')
    chr_nar  = CharacterData(_("Narrator"), "", category='special')
    chr_nar2 = CharacterData(_("Narrator (Internal)"), "", category='special')
    chr_aka  = CharacterData(_("Akaro"), _("A"), "#dda065", category='main')
    chr_aka2 = CharacterData(_("Akaro"), _("{creator_pov}A{/creator_pov}"), "#dda065", category='main')
    chr_aka3 = CharacterData(_("Akaro"), _("A"), "#dda065", bg_color=(1.0, 0.65, 0.31), category='main')
    chr_aki  = CharacterData(_("Erina"), _("E"), "#e3ca78", category='main')
    chr_aki2 = CharacterData(_("Erina"), _("{creator_pov}E{/creator_pov}"), "#e3ca78", category='main')
    chr_aki3 = CharacterData(_("Erina"), "", category='main')
    chr_ats  = CharacterData(_("Narrator (Spoken)"), _("—"), category='special')
    chr_ats2 = CharacterData(_("Atsuki"), _("{image=atsuki_indicator}"), "#1cad49", category='main')
    chr_ats2_small = CharacterData(_("Atsuki"), _("{image=atsuki_indicator_small}"), "#1cad49", category='main')
    chr_ats3 = CharacterData(_("Atsuki"), _("{creator_pov}{image=atsuki_indicator}{/creator_pov}"), "#1cad49", category='main')
    chr_ats4 = CharacterData(_("Atsuki"), _("{image=atsuki_indicator}"), "#1cad49", bg_color=(0.6047, 0.9451, 0.6667), category='main')
    chr_ats2b = CharacterData(_("Atsuki B"), _("{image=atsuki_indicator}{image=atsuki_indicator_b}"), "#1cad49", category='main')
    chr_isl  = CharacterData(_("Isla"), _("I"), "#f3b9f2", category='main')
    chr_isl2 = CharacterData(_("Isla"), _("{creator_pov}I{/creator_pov}"), "#f3b9f2", category='main')
    chr_kat  = CharacterData(_("Katei"), _("K"), "#bcd6c4", category='main')
    chr_kat2 = CharacterData(_("Katei"), _("{creator_pov}K{/creator_pov}"), "#bcd6c4", category='main')
    chr_kat3 = CharacterData(_("Katei"), _("K"), "#bcd6c4", bg_color=(0.52, 0.83, 0.76), category='main')
    chr_mii  = CharacterData(_("Narrator (Spoken)"), _("—"), category='special')
    chr_mii2 = CharacterData(_("Miiya"), _("{creator_pov}M{/creator_pov}"), "#EE3D00", category='main')
    chr_mii3 = CharacterData(_("Narrator (Spoken)"), _("—"), bg_color=(1.0, 1.0, 1.0), category='special')
    chr_mii4 = CharacterData(_("Miiya"), _("M"), "#EE3D00", category='main')
    chr_sai  = CharacterData(_("Sai"), _("Ψ"), "#80adff", category='main')
    chr_sai2 = CharacterData(_("Sai"), _("{creator_pov}Ψ{/creator_pov}"), "#80adff", category='main')
    chr_sai3 = CharacterData(_("Sai"), _("Ψ"), "#80adff" , bg_color=(0.5, 0.67, 1.0), category='main')
    chr_sai4 = CharacterData(_("Sai"), "", category='main')
    chr_san  = CharacterData(_("Naomi"), _("N"), "#f8f190", category='main')
    chr_san2 = CharacterData(_("Naomi"), _("{creator_pov}N{/creator_pov}"), "#f8f190", category='main')
    chr_shi  = CharacterData(_("Shiroya"), _("S"), "#acf6f4", category='main')
    chr_shi2 = CharacterData(_("Narrator (Spoken)"), _("—"), category='special')
    chr_shi3 = CharacterData(_("Shiroya"), _("{creator_pov}S{/creator_pov}"), "#acf6f4", category='main')

    chr_q    = CharacterData(_("?"), _("?"), "#000", category='side')
    chr_q2   = CharacterData(_("?"), _("{creator_pov}?{/creator_pov}"), category='side')
    chr_oth  = CharacterData(_("Other"), _("O"), "#CCC", category='side')
    chr_oth2 = CharacterData(_("Other"), _("{creator_pov}O{/creator_pov}"), category='side')
    chr_ata  = CharacterData(_("Atase"), _("{creator_pov}T{/creator_pov}"), category='main')
    chr_dar  = CharacterData(_("Darfee"), _("D"), "#8a6c24", category='side') #hex color of coffee
    chr_dar2 = CharacterData(_("Darfee"), _("{creator_pov}D{/creator_pov}"), "#8a6c24", category='side')
    chr_gan  = CharacterData(_("Shop Owner"), _("{creator_pov}G{/creator_pov}"), category='side')
    chr_ido  = CharacterData(_("Ido"), _("{creator_pov}Y{/creator_pov}"), category='side')
    chr_kro  = CharacterData(_("Jiro"), _("{creator_pov}X{/creator_pov}"), category='side')
    chr_lei  = CharacterData(_("Lei"), _("{creator_pov}L{/creator_pov}"), "#c2bfd2", category='side')
    chr_sur  = CharacterData(_("Suripo"), _("P"), "#98FB98", category='side')
    chr_sur2 = CharacterData(_("Suripo"), _("{creator_pov}P{/creator_pov}"), "#98FB98", category='side')
    chr_vai  = CharacterData(_("Vaisude"), _("V"), "#CFCC7E", category='side')
    chr_vai2 = CharacterData(_("Vaisude"), _("{creator_pov}V{/creator_pov}"), category='side')


    ## Main characters
    a   = NVLCharacter2(chr_ats)
    c2a = NVLCharacter2(chr_ats2)
    c2a2= NVLCharacter2(chr_ats2b)
    a4  = NVLCharacter2(chr_ats2_small, what_size=15)
    ann = NVLCharacter2(chr_ats3)
    ak  = NVLCharacter2(chr_aka)
    ak2 = NVLCharacter2(chr_aka, is_recording=True)
    ak4 = NVLCharacter2(chr_aka, what_size=15)
    aknn = NVLCharacter2(chr_aka2)
    aki   = NVLCharacter2(chr_aki)
    aki4  = NVLCharacter2(chr_aki, what_size=15)
    akinn = NVLCharacter2(chr_aki2)
    il   = NVLCharacter2(chr_isl)
    il2  = NVLCharacter2(chr_isl, is_recording=True)
    il4  = NVLCharacter2(chr_isl, what_size=15)
    ilnn = NVLCharacter2(chr_isl2)
    k    = NVLCharacter2(chr_kat)
    k4   = NVLCharacter2(chr_kat, what_size=15)
    knn  = NVLCharacter2(chr_kat2)
    m    = NVLCharacter2(chr_mii)
    m2   = NVLCharacter2(chr_mii4)
    c2s  = NVLCharacter2(chr_mii)
    mnn  = NVLCharacter2(chr_mii2)
    s    = NVLCharacter2(chr_shi)
    c3s  = NVLCharacter2(chr_shi2)
    s4   = NVLCharacter2(chr_shi, what_size=15)
    snn  = NVLCharacter2(chr_shi3)
    sa   = NVLCharacter2(chr_san)
    sann = NVLCharacter2(chr_san2)
    sai   = NVLCharacter2(chr_sai)
    sai2  = NVLCharacter2(chr_sai, is_recording=True)
    sai4  = NVLCharacter2(chr_sai, what_size=15)
    sainn = NVLCharacter2(chr_sai2)

    an   = NVLCharacter2(chr_ats4, is_speaker=False)
    akn  = NVLCharacter2(chr_aka3, is_speaker=False)
    kn   = NVLCharacter2(chr_kat3, is_speaker=False)
    c2sn = NVLCharacter2(chr_mii3, is_speaker=False)
    sain = NVLCharacter2(chr_sai3, is_speaker=False)

    ## Minor characters
    ta  = NVLCharacter2(chr_ata)
    e   = NVLCharacter2(chr_oth) #Receptionist
    d   = NVLCharacter2(chr_dar)
    v   = NVLCharacter2(chr_vai)
    dnn = NVLCharacter2(chr_dar2)
    vnn = NVLCharacter2(chr_vai2)
    gan = NVLCharacter2(chr_gan)
    gan2= NVLCharacter2(chr_gan, what_size=15)
    ido = NVLCharacter2(chr_ido)
    kr  = NVLCharacter2(chr_kro)
    lei = NVLCharacter2(chr_lei)
    su   = NVLCharacter2(chr_sur)
    sunn = NVLCharacter2(chr_sur2)

    ## Special characters
    c   = NVLCharacter2(chr_c, is_speaker=False)
    orb = NVLCharacter2(CharacterData("Tip Orb", ""), is_speaker=False)
    i   = NVLCharacter2(chr_nar, is_speaker=False)
    n   = NVLCharacter2(chr_nar2, is_speaker=False, what_prefix="{i}", what_suffix="{/i}")
    nm  = NVLCharacter2(chr_nar2, is_speaker=False, what_prefix="{i}", what_suffix="{/i}")
    nn  = NVLCharacter2(chr_oth2)
    ns  = NVLCharacter2(chr_oth)
    saicenter = NVLCharacter2(chr_sai4, what_text_align=0.5, what_xalign=0.5, what_yalign=0.44, what_size=29, is_speaker=False)
    akicenter = NVLCharacter2(chr_aki3, what_text_align=0.5, what_xalign=0.5, what_yalign=0.44, what_size=29, is_speaker=False)

    q  = NVLCharacter2(chr_q, what_color="#000000", what_outlines=[( 2, "#FFFC", 0, 0)])
    q4 = NVLCharacter2(chr_q, what_color="#000000", what_outlines=[( 2, "#FFFC", 0, 0)], what_size=15, what_line_leading=1)
    c4 = NVLCharacter2(chr_q2)
    c5 = NVLCharacter2(chr_oth2)



init -51 python:
    class CharacterData:
        def __init__(self, name, symbol, color="#FFF", bg_color=None, force_symbol=False, category='main'):
            self.name = name
            self.symbol = symbol
            self.color = color
            self.bg_color = bg_color
            self.force_symbol = force_symbol
            self.category = category

        def indicator(self):
            if self.force_symbol:
                return self.symbol

            if self.symbol:
                if gui.preference("speaker_indicator") == "emdash":
                    return "—"
                elif gui.preference("speaker_indicator") == "circle":
                    return "•"
                elif gui.preference("speaker_indicator") == "symbol":
                    return self.symbol
            return None

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                extra = True
                if hasattr(other, 'category'):
                    extra = extra and self.category==other.category
                if hasattr(other, 'force_symbol'):
                    extra = extra and self.force_symbol==other.force_symbol
                return self.name==other.name and self.symbol==other.symbol and self.color==other.color and extra
            else:
                return False 


    class ADVCharacter2(ADVCharacter):
        def __call__(self, what, interact=True, _call_done=True, multiple=None, **kwargs):
            _mode = kwargs.pop("_mode", None)
            _with_none = kwargs.pop("_with_none", None)

            if kwargs:
                return Character(kind=self, **kwargs)(what, interact=interact, _call_done=_call_done, multiple=multiple, _mode=_mode, _with_none=_with_none)

            # Check self.condition to see if we should show this line at all.
            if not (self.condition is None or renpy.python.py_eval(self.condition)):
                return True

            if not isinstance(what, basestring):
                raise Exception("Character expects its what argument to be a string, got %r." % (what,))

            # Figure out multiple and final. Multiple is None if this is not a multiple
            # dialogue, or a step and the total number of steps in a multiple interaction.

            global multiple_count

            if multiple is None:
                multiple_count = 0

            else:
                multiple_count += 1
                multiple = (multiple_count, multiple)

                if multiple_count == multiple[1]:
                    multiple_count = 0

            if multiple is None:

                old_attr_state = self.handle_say_attributes(False, interact)

                old_side_image_attributes = renpy.store._side_image_attributes

                if self.image_tag:
                    attrs = (self.image_tag,) + renpy.game.context().images.get_attributes(None, self.image_tag)
                else:
                    attrs = None

                renpy.store._side_image_attributes = attrs

                if not interact:
                    renpy.store._side_image_attributes_reset = True

            if renpy.config.voice_tag_callback is not None:
                renpy.config.voice_tag_callback(self.voice_tag)

            try:

                if interact:
                    mode = _mode or self.mode
                    renpy.exports.mode(mode)
                else:
                    renpy.game.context().deferred_translate_identifier = renpy.game.context().translate_identifier

                # Figure out the arguments to display.
                display_args = self.display_args.copy()
                display_args["interact"] = display_args["interact"] and interact

                if multiple is not None:
                    display_args["multiple"] = multiple

                if _with_none is not None:
                    display_args["with_none"] = _with_none

                ## MODIFICATION START
                who = self.name
                what = self.what_prefix + what + self.what_suffix

                self.do_add(who, what)
                self.do_display(who, what, cb_args=self.cb_args, **display_args)

                # Indicate that we're done.
                if _call_done:

                    self.do_done(who, what)

                    # Finally, log this line of dialogue.
                    if who and isinstance(who, (str, unicode)):
                        renpy.exports.log(who)
                    elif who and isinstance(who, CharacterData):
                        renpy.exports.log(who.name)

                    renpy.exports.log(what)
                    renpy.exports.log("")
                ## MODIFICATION END

            finally:

                if (multiple is None) and interact:
                    renpy.store._side_image_attributes = old_side_image_attributes

                    if old_attr_state is not None:
                        _, images = old_attr_state
                        before = images.get_attributes(None, self.image_tag)

                    if self.restore_say_attributes(False, old_attr_state, interact):
                        after = images.get_attributes(None, self.image_tag)
                        self.handle_say_transition('restore', before, after)

    class NVLCharacter2(ADVCharacter2):

        def __init__(self,
                who=renpy.character.NotSet,
                is_speaker=True,
                is_recording=False,
                **properties):

            self.data = who

            if is_speaker:
                properties["what_prefix"] = languages.current.what_prefix
                properties["what_suffix"] = languages.current.what_suffix

            if is_recording:
                properties["who_outlines"]  = [ ( 3, "#060", 0, 0), ( 1, "#000", 1, 1) ]
                properties["what_outlines"] = [ ( 3, "#060", 0, 0), ( 1, "#000", 1, 1) ]


            #properties["ctc"] = "ctc"
            #properties["ctc_pause"] = "ctc"
            #properties["ctc_position"] = "nestled-close"

            kind = store.nvl

            if "clear" in properties:
                self.clear = properties.pop("clear")
            else:
                self.clear = kind.clear

            ADVCharacter2.__init__(
                self,
                who,
                kind=kind,
                callback=speaker_currycb(self.data.name),
                **properties)

        def pop_nvl_list(self):
            if len(nvl_list)>0:
                store.nvl_list.pop()

        ## Everything below is an exact copy-paste from NVLCharacter
        def push_nvl_list(self, who, what, multiple=None):

            kwargs = self.show_args.copy()
            kwargs["properties"] = python_dict(self.properties)
            kwargs["what_args"] = python_dict(self.what_args)
            kwargs["who_args"] = python_dict(self.who_args)
            kwargs["window_args"] = python_dict(self.window_args)
            kwargs["multiple"] = multiple

            if multiple:

                def multiple_style(k):
                    style = kwargs[k]["style"]
                    style = "block{}_multiple{}_{}".format(multiple[0], multiple[1], style)
                    kwargs[k]["style"] = style

                multiple_style("what_args")
                multiple_style("who_args")
                multiple_style("window_args")

            store.nvl_list.append((who, what, kwargs))

        def do_add(self, who, what, multiple=None):

            if store.nvl_list is None:
                store.nvl_list = [ ]

            if store._nvl_language != _preferences.language:
                store.nvl_list = [ ]
                store._nvl_language = _preferences.language

            while config.nvl_list_length and (len(nvl_list) + 1 > config.nvl_list_length):
                nvl_list.pop(0)

        def do_display(self, who, what, multiple=None, **display_args):

            page = self.clear or nvl_clear_next()

            if config.nvl_page_ctc and page:
                display_args["ctc"] = config.nvl_page_ctc
                display_args["ctc_position"] = config.nvl_page_ctc_position

            if config.nvl_paged_rollback:
                if page:
                    checkpoint = True
                else:
                    if renpy.in_rollback():
                        return
                    checkpoint = False
            else:
                checkpoint = True

            if multiple is not None:
                self.push_nvl_list(who, what, multiple=multiple)
            else:
                self.push_nvl_list(who, what)

            renpy.display_say(
                who,
                what,
                nvl_show_core,
                checkpoint=checkpoint,
                multiple=multiple,
                **display_args)

            self.pop_nvl_list()

        def do_done(self, who, what, multiple=None):

            if multiple is not None:
                self.push_nvl_list(who, what, multiple=multiple)
            else:
                self.push_nvl_list(who, what)

            if multiple is None:
                start = -1
            elif multiple[0] == multiple[1]:
                start = -multiple[0]
            else:
                start = 0

            for i in range(start, 0):
                nvl_list[i][2]["what_args"]["alt"] = ""
                nvl_list[i][2]["who_args"]["alt"] = ""

            if self.clear:
                nvl_clear()

            self.add_history("adv", who, what)

        def do_extend(self):
            renpy.mode(self.mode)
            store.nvl_list = store.nvl_list[:-1]

            self.pop_history()
