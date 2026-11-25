## Navigation
## @TODO: Scroll text immediately if we're typing in a note that's off-screen

## Other
## @TODO: Completely breaks on lower resolutions
## @TODO: Using GoToNote from search sometimes lands in the wrong position/doesn't compute note heights correctly, especially if there's a lot of text in a previous note or we go to another chapter
## @TODO: Focusing a note, scrolling way up/down and trying to type results in nothing being sent to that note

python early:
    ## Persistent class has to be declared in an early block
    class NoteMeta(python_object):
        collapsed = False
        visible_lines = 0
        user_note = ""
        height = -1

        def __eq__(self, other):
            if isinstance(other, NoteMeta):
                return self.user_note == other.user_note and self.collapsed == other.collapsed and self.visible_lines == other.visible_lines
            return False

        def __ne__(self, other):
            return not self.__eq__(other)

        def __repr__(self):
            return "<NoteMeta: {:.30}..., Collapsed: {}, Visible: {}>".format(self.user_note, self.collapsed, self.visible_lines)

        def IsSeen(self):
            return self.visible_lines > 0

        def IsLineUnlocked(self, idx):
            return self.visible_lines & (1<<idx)

        def UnlockLine(self, val):
            self.visible_lines |= 1<<val

init -10 python:
    def UnlockNote(name, val=None):
        if name not in persistent.note_meta:
            persistent.note_meta[name] = NoteMeta()

        if val is None:
            pass
        elif val==0:
            persistent.note_meta[name].visible_lines = 2**32 - 1
        else:
            persistent.note_meta[name].UnlockLine(val-1)

    def UnlockAllNotes():
        for meta in persistent.note_meta.values():
            meta.visible_lines = 2**32 - 1

    def CheckAllNotes():
        unlocked_lines = python_dict()

        ## Scan the script to make sure all notes are fully unlocked
        start_idx = GetGlobalIndexFromNode(search.start_node)
        end_idx = GetGlobalIndexFromNode(search.end_node)

        for idx in range(start_idx, end_idx):
            node = GetNodeFromGlobalIndex(idx)
            if type(node)==renpy.ast.Python:
                if "UnlockNote" in node.code.source:
                    temp = node.code.source[len("UnlockNote("):-1].replace('"', '').split(", ")

                    if temp[0] not in unlocked_lines:
                        unlocked_lines[temp[0]] = 0
                    unlocked_lines[temp[0]] |= 1<<(int(temp[1])-1)

        for id, lines in unlocked_lines.items():
            summary = notes.dict[id].summary_list

            for idx in range(len(summary)):
                if not(1 << idx & lines):
                    print("{}, line {}".format(id, idx+1))

    from collections import OrderedDict

    class NoteManager(python_object):
        def __init__(self):
            self.dict = OrderedDict()
            self.buttons = python_dict()
            self.lists = python_list()
            self.positions = python_list()
            self.current_focus = None
            self.chapter = 0
            self.view = None
            self.vbox = None

            self.width1 = 130
            self.width2 = 50
            self.width3 = 500*2 + 12
            self.xoffset = 20
            self.line_width = 2
            self.line_color = '#FFF8'

            self.hide_menus = [SetScreenVariable("colors_visible", False), SetScreenVariable("menu_visible", False)]
            self.initial_button_ignore = config.keymap['button_ignore']
            self.initial_button_select = config.keymap['button_select']

            for _ in range(5):
                self.lists.append(python_list())
                self.positions.append(0)

        @property
        def position(self):
            return self.positions[self.chapter]

        @position.setter
        def position(self, val):
            self.positions[self.chapter] = val

        @property
        def max_position(self):
            rv = 0

            for idx, note in enumerate(self.list):
                if note.id in self.buttons and note.meta.IsSeen():
                    rv += persistent.note_meta[note.id].height

            if self.view:
                rv -= int(self.view.height)
            else:
                rv -= 575
            return rv

        @property
        def list(self):
            return self.lists[self.chapter]

        def add(self, value):
            entry = NoteEntry(**value)
            self.dict[entry.id] = entry
            self.lists[entry.chapter-1].append(entry)

            if entry.id not in persistent.note_meta:
                persistent.note_meta[entry.id] = NoteMeta()

        def Clear(self):
            self.buttons.clear()

        def Show(self):
            ## Done like this to prevent clicking on something else, moving over a new button and releasing to activate the new button
            config.keymap['button_ignore'] = python_list()
            config.keymap['button_select'] = [ 'mousedown_1' ] #, 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ]
            renpy.clear_keymap_cache()

        def Hide(self):
            config.keymap['button_ignore'] = self.initial_button_ignore
            config.keymap['button_select'] = self.initial_button_select
            renpy.clear_keymap_cache()

        def CollapseAll(self, state):
            for idx, note in enumerate(self.lists[self.chapter]):
                note.meta.collapsed = state

            self.Repopulate()

        def CopyDetails(self, note_num, details='all'):
            note = notes.list[note_num]
            rv = python_list()

            if details=='all':
                rv.append("Title: {} ({}-{})".format(note.scene, note.chapter, note.note_idx))

                if note.IsFullyUnlocked():
                    people = note.GetPeople()
                    people = ", ".join(people.split('\n'))
                    rv[-1] += '\nWith: '+ people
                else:
                    rv[-1] += '\nWith: <Locked>'

            if details=='all' or details=='overview':
                final_overview = ""

                for s_idx, smry in enumerate(note.summary_list):
                    if note.meta.IsLineUnlocked(s_idx):
                        smry = renpy.filter_text_tags(smry, allow=gui.history_allow_tags)
                        if smry[0] == "-":
                            if s_idx > 0:
                                final_overview += '\n\n'
                            final_overview += smry[1:] + ':'
                        elif smry[0] == "*":
                            bg_text, bg_name = smry[1:].split('|')
                            final_overview += '\n* <Image: ' + bg_text + '>'
                        else:
                            if "{time" in smry:
                                txt_temp = renpy.text.text.Text(smry)
                                txt_temp.update()
                                smry = "".join([x[1] for x in txt_temp.tokens])
                            final_overview += '\n* ' + smry

                rv.append(final_overview)

            if details=='all':
                if note.meta.user_note and details=='all':
                    rv.append("------------------------\n"+note.meta.user_note)
            elif details=='user_note':
                rv.append(note.meta.user_note)

            text_raw = "\n\n".join(rv)
            #text_clean = renpy.filter_text_tags(text_raw, allow=gui.history_allow_tags)
            #clipboard.copy(text_clean, text_raw)
            try:
                clipboard.copy(text_raw, text_raw)
            except:
                pass

        def GetSeenNotes(self):
            rv = python_list()
            for note_list in self.lists:
                for note in note_list:
                    if note.meta.IsSeen():
                        rv.append("UnlockNote(\"{}\")".format(note.id))
                    for idx in range(32):
                        if note.meta.IsLineUnlocked(idx):
                            rv.append("UnlockNote(\"{}\", {})".format(note.id, idx+1))
            return rv

        def IsUnlocked(self, chapter):
            for n in self.lists[chapter]:
                if n.meta.IsSeen():
                    return True
            return False

        def Initialize(self):
            for idx, note in enumerate(self.lists[self.chapter]):
                if note.id in self.buttons:
                    if type(self.buttons[note.id].child.children[1].child) != renpy.display.im.Image:
                        ## This entry is already complete, don't recompute
                        continue

                if note.meta.IsSeen():
                    w_hbox = HBox(style="notes_hbox", spacing=12)


                    ## Field: Title
                    if note.meta.collapsed:
                        w_temp = HBox(style="notes_frame", xsize=self.width1, padding=(0,0,0,0))
                        w_temp.add(Window(ConstantText(str(idx+1), style="notes_text", xalign=0.5), xalign=0.0, padding=(0,0,5,0), background=None, xsize=25))
                        w_temp.add(Window(ConstantText(note.scene, style="notes_text"), xalign=0.0, padding=(0,0,0,0), background=None, xsize=self.width1-25))
                    else:
                        w_temp = Window(style="notes_title_frame", xsize=self.width1, padding=(0,0,0,0))
                        w_temp.add(ConstantText("{size=24}%d{/size}\n\n%s" % (idx+1, note.scene), style="notes_text", xalign=0.5, yalign=0.5, text_align=0.5))
                    w_hbox.add(w_temp)


                    ## Field: With
                    w_hbox.add(VBox(style="notes_vbox", xsize=self.width2, yalign=0.5))
                    if note.IsFullyUnlocked():
                        if note.meta.collapsed:
                            temp = note.GetPeopleCollapsed()
                        else:
                            temp =  note.GetPeople()
                        w_hbox.child.add(ConstantText(temp, style="notes_text", text_align=0.5, xalign=0.5))
                    else:
                        w_hbox.child.add(Image("gui/chart/lock.png", xalign=0.5))


                    ## Field: Overview
                    w_temp = VBox(style="notes_vbox")
                    if persistent.notes_input_visible:
                        overview_width = self.width3 - persistent.notes_width - 12
                    else:
                        overview_width = self.width3

                    if note.meta.collapsed:
                        overview_text = []
                        overview_images = []
                        counter = 0
                        for s_idx, smry in enumerate(note.summary_list):
                            if note.meta.IsLineUnlocked(s_idx):
                                counter += 1
                                if smry[0] == "-":
                                    overview_text.append("{color=#cff}" + smry[1:] + "{/size}")
                                elif smry[0] == "*":
                                    pass
                                else:
                                    if "{time" in smry:
                                        txt_temp = renpy.text.text.Text(smry)
                                        txt_temp.update()
                                        smry = "".join([x[1] for x in txt_temp.tokens])

                                    overview_text.append("\u2022 "+ smry[:overview_width//10] + "[...]")

                                if counter >= 1:
                                    break

                    else:
                        overview_text = []
                        overview_images = []
                        for s_idx, smry in enumerate(note.summary_list):
                            if note.meta.IsLineUnlocked(s_idx):
                                if smry[0] == "-":
                                    if s_idx > 0:
                                        overview_text.append('{size=9} {/size}')
                                    overview_text.append("{color=#cff}" + smry[1:] + "{/size}")
                                elif smry[0] == "*":
                                    bg_text, bg_name = smry[1:].split('|')
                                    overview_images.append(TextButton(
                                        bg_text,
                                        style='notes_explanation_button',
                                        text_style='notes_explanation_button_text',
                                        hovered=Show('image_popup', bg_name=bg_name),
                                        unhovered=Hide('image_popup'),
                                        action=[SetScreenVariable("menu_visible", False), Hide('image_popup'), Show('image_popup_full', bg_name=bg_name, transition=Dissolve(0.2))]
                                        ))
                                else:
                                    overview_text.append("\u2022 "+ smry)


                        w_temp.add(ConstantText('\n'.join(overview_text), style="notes_text", rest_indent=12, newline_indent=True))

                        for overview_image in overview_images:
                            w_temp.add(overview_image)

                    w_hbox.add(Window(child=w_temp, style="notes_overview_frame", one=True, padding=(3,0,0,0), background=None, xsize=overview_width))


                    ## Field: Note
                    if persistent.notes_input_visible:
                        w_temp = VBox(style="notes_vbox", xsize=persistent.notes_width)

                        if note.meta.collapsed:
                            text_clean = renpy.filter_text_tags(note.meta.user_note, allow=gui.history_allow_tags)
                            text_clean = text_clean.split('\n')
                            temp = ""
                            if len(text_clean)>0:
                                temp = text_clean[0][:persistent.notes_width//8]

                            ## Escape any square brackets, which renpy interprets as variables
                            temp = temp.replace("[", "[[")
                            w_temp.add(ConstantText(temp, style="notes_input"))
                        else:
                            w_temp.add(note.input)

                        w_hbox.add(Window(child=w_temp, style="notes_frame", one=True, padding=(3,0,0,0), background=None))


                    ## Save this button
                    w_button = Button(
                        w_hbox,
                        style = "notes_button",
                        id = "button_{}".format(idx),
                        padding = (5,5,5,5),
                        key_events = True, ## Allows the button to process key inputs when not focused/hovered
                        action = ClickNoteEntry(idx)
                        )

                    bg_color = ""

                    if note.creator:
                        if idx%2:
                            bg_color = "#6004"
                        else:
                            bg_color = "#9334"
                    else:
                        if idx%2:
                            bg_color = "#0004"
                        else:
                            bg_color = "#3334"

                    w_button.style.background = bg_color
                    w_button.style.hover_background = Frame(Composite(
                        (20, 20),
                        (0, 0),  bg_color,
                        (0, 0),  Solid(notes.line_color,xsize=self.line_width,ysize=20),
                        (20-self.line_width, 0), Solid(notes.line_color,xsize=self.line_width,ysize=20)
                        ), self.line_width,1,self.line_width,1, xsize=notes.xoffset+notes.width1+notes.width2+notes.width3+14)

                    self.buttons[note.id] = w_button
                    w_button.render(0,0,0,0)
                    persistent.note_meta[note.id].height = int(w_button.window_size[1]) + notes.line_width

        def UpdateNoteHeights(self):
            for idx, note in enumerate(self.list):
                if note.id in self.buttons:
                    self.buttons[note.id].render(0,0,0,0)
                    persistent.note_meta[note.id].height = int(self.buttons[note.id].window_size[1]) + notes.line_width

        def SetChapter(self, val):
            self.chapter = val
            self.Repopulate()
            self.view.set_yoffset(self.position) # Load current chapter position
            self.FocusInput(-1)

        def TypingCallback(self, inp):
            return
            input_y = self.view.children[0].offsets[self.current_focus*2][1]
            caret_y = inp.getCaretPos()[1]
            new_position = input_y + caret_y
            print(new_position, self.position, self.view.height)
            print('-------')

            if new_position > self.position + self.view.height or self.position > new_position:
                self.position = min(max(0, new_position), self.max_position)

        def SetNoteNumber(self, val):
            new_position = 0

            for idx, note in enumerate(notes.list):
                if note.meta.IsSeen():
                    if idx < val:
                        new_position += persistent.note_meta[note.id].height
                    else:
                        break

            if new_position > self.position + self.view.height or self.position > new_position:
                self.position = min(max(0, new_position), self.max_position)

        def FocusInput(self, val, clicked=True):
            if val == self.current_focus:
                return

            for idx, note in enumerate(self.list):
                note.input.disable()

            if val == -1:
                self.current_focus = None
            else:
                self.current_focus = val
                note = self.list[val]
                note.input.enable(clicked)

        def FocusNext(self, clicked=True):
            if self.current_focus is None:
                start_num = -1
            else:
                start_num = self.current_focus

            note_num = (start_num + 1) % len(self.list)
            while note_num != start_num:
                if not self.list[note_num].meta.collapsed:
                    self.FocusInput(note_num, clicked)
                    break
                note_num = (note_num + 1) % len(self.list)

            ## Set input in view
            self.SetNoteNumber(note_num)
            self.Populate()

        def FocusPrev(self, clicked=True):
            if self.current_focus is None:
                start_num = len(self.list)
            else:
                start_num = self.current_focus

            note_num = (start_num - 1) % len(self.list)
            while note_num != start_num:
                if not self.list[note_num].meta.collapsed:
                    self.FocusInput(note_num, clicked)
                    break
                note_num = (note_num - 1) % len(self.list)

            ## Set input in view
            self.SetNoteNumber(note_num)
            self.Populate()

        def ToggleTag(self, tag, val=None):
            if self.current_focus is not None:
                self.list[self.current_focus].input.toggleTag(tag, val)

        def Scroll(self, increment=1):
            self.position = min(max(0, self.position+50*increment), self.max_position)
            self.Populate()

            ## Hide any open menus
            for i in self.hide_menus:
                i()

        def AdjustNoteWidth(self, offset):
            if (offset > 0 and persistent.notes_width < 750) or (offset < 0 and persistent.notes_width > 250):
                persistent.notes_width += offset
                self.Repopulate()

        def Populate(self):
            self.view = renpy.get_widget(None, "notes_vp")
            self.vbox = renpy.get_widget(None, "notes_vp_vbox")
            if self.vbox is None:
                return
            self.vbox._clear()
            view_bar = renpy.get_widget(None, "notes_vp_bar")

            height_top = 0
            height_bottom = 0
            padded_top = False

            for idx, note in enumerate(notes.list):
                if note.meta.IsSeen():
                    w_button = notes.buttons[note.id]

                    if not padded_top:
                        if self.position > height_top + persistent.note_meta[note.id].height:
                            height_top += persistent.note_meta[note.id].height
                            continue

                        self.view.child.add(Solid(None, xsize=1, ysize=height_top))
                        padded_top = True
                    else:
                        if self.position + self.view.height > height_top + height_bottom:
                            height_top += persistent.note_meta[note.id].height
                        else:
                            height_bottom += persistent.note_meta[note.id].height
                            continue

                    self.vbox.add(w_button)
                    self.vbox.add(Solid(notes.line_color, xsize=self.width1+self.width2+self.width3+36-2, ysize=notes.line_width))

            self.view.set_yoffset(self.position)
            view_bar.per_interact()

        def Repopulate(self):
            if not renpy.is_init_phase():
                self.Clear()
                self.Initialize()
                self.position = min(max(0, self.position), self.max_position)
                self.Populate()

                for temp in notes.hide_menus:
                    temp()

                renpy.restart_interaction()

    notes = NoteManager()

    class NoteEntry(python_object):
        def __init__(self, id, chapter=1, scene="", people=python_list(), summary=python_list(), creator=False):
            self.id = id
            self.chapter = chapter
            self.note_idx = int(id[3:])
            self.scene = scene
            self.people = people
            self.summary = summary
            self.creator = creator
            self.input = Input2(
                id="note_input_{}".format(self.id),
                style="notes_input",
                caret_ysize=17,
                is_note=True,
                is_rich_textbox=True,
                editable=False,
                initial_value=self.meta.user_note,
                changed=self.Update,
                enter_callback=self.EnterCallback,
                typing_callback=notes.TypingCallback,
                highlight_color=gui.highlight_color,
                copypaste=True)

        @property
        def meta(self):
            if not persistent.note_meta:
                persistent.note_meta = python_dict()

            if self.id not in persistent.note_meta:
                persistent.note_meta[self.id] = NoteMeta()

            return persistent.note_meta[self.id]

        @property
        def summary_list(self):
            return self.summary[1:-1].split("\n")

        def IsFullyUnlocked(self):
            return self.meta.visible_lines >= (1<<len(self.summary_list))-1

        def EnterCallback(self):
            return "\n"

        def GetPeople(self):
            result = python_list()
            for p in sorted(self.people.split(" ")):
                temp = p[0:3].lower()

                name = None
                if temp == "aka":
                    name = "Akaro"
                elif temp == "ats":
                    name = "Atsuki"
                elif temp == "eri":
                    name = "Erina"
                elif temp == "isl":
                    name = "Isla"
                elif temp == "kat":
                    name = "Katei"
                elif temp == "mii":
                    name = "Miiya"
                elif temp == "nao":
                    name = "Naomi"
                elif temp == "sai":
                    name = "Sai"
                elif temp == "shi":
                    name = "Shiroya"
                elif temp == "dar":
                    name = "Darfee"

                if name:
                    result.append(name)

            return "\n".join(result)

        def GetPeopleCollapsed(self):
            if self.people == "":
                return ""

            num_people = len(self.people.split(" "))
            return str(num_people)

        def Update(self, text):
            persistent.note_meta[self.id].user_note = text
            self.meta.height = int(notes.buttons[self.id].window_size[1])

    class GoToNote(Action, DictEquality):
        def __init__(self, entry):
            self.chapter = entry.what[0]-1
            self.number  = entry.what[1]-1

        def __call__(self):
            #notes.SetChapter(self.chapter)
            notes.chapter = self.chapter
            #notes.Repopulate()
            #notes.view.set_yoffset(self.position) # Load current chapter position
            #notes.FocusInput(-1)
            
            notes.SetNoteNumber(self.number)
            
            notes.view.set_yoffset(notes.position)
            #notes.Repopulate()

    class ClickNoteEntry(Action, DictEquality):
        def __init__(self, note_num):
            self.note_num = note_num

        def __call__(self):
            x, y = GetMousePos()

            if persistent.notes_input_visible:
                trigger_width = notes.xoffset+notes.width1+notes.width2+notes.width3+36 - (persistent.notes_width+12)
            else:
                trigger_width = 1280

            if notes.list[self.note_num].meta.collapsed or x < notes.xoffset+notes.width1:
                # Toggle
                notes.list[self.note_num].meta.collapsed ^= True
                notes.Repopulate()

            elif x < trigger_width:
                if renpy.current_screen().scope["menu_visible"]:
                    SetScreenVariable("menu_visible", False)()
                else:
                    ## Get idx of closest note
                    idx = None
                    entry = (notes.chapter+1, self.note_num+1)
                    for n in search.note_unlocks:
                        if n.what==entry:
                            idx = n.global_index
                            break

                    ## Get the first Say node
                    if idx is None:
                        raise Exception("idx for note {} not found".format(entry))

                    end_idx = GetGlobalIndexFromNode(search.end_node)
                    while idx < end_idx:
                        idx += 1
                        if type(GetNodeFromGlobalIndex(idx))==renpy.ast.Say:
                            break

                    if idx == end_idx:
                        raise Exception("Couldn't find Say node after node {}".format(entry))

                    ## Show clicky menu
                    SetScreenVariableCallback("menu_position", Function(MenuClickAction, 4))()
                    SetScreenVariable("menu_visible", True)()
                    SetScreenVariable("clicked_search_idx", idx)()
                    SetScreenVariable("clicked_note_num", self.note_num)()
            else:
                ## Focus the input
                notes.FocusInput(self.note_num, True)
                for action in notes.hide_menus:
                    action()

define notestutorial = 1
style access2:
    background "gui/notes/access.png"
    hover_background "gui/notes/access2.png"
    xsize 310
    ysize 50
    hover_sound "sounds/sys2.wav"
    activate_sound "sounds/sys6.wav"

screen notes_tutorial:
    tag menu
    modal True
    predict True
    use game_menu(_("Notes_tutorial"), padded=(40, 85, 40, 30)):
        style_prefix "notes_tutorial"

    showif notestutorial == 1:
        add "images/notes_tutorial1.png" at dissolve_tf_squared
    #showif tutorial == 2:
    #    add "main_menu" at dissolve_tf_squared
    showif notestutorial == 2:
        add "images/notes_tutorial2.png" at dissolve_tf_squared
    showif notestutorial == 3:
        add "images/notes_tutorial3.png" at dissolve_tf_squared
    showif notestutorial == 4:
        add "images/notes_tutorial4.png" at dissolve_tf_squared
    showif notestutorial == 5:
        add "images/notes_tutorial5.png" at dissolve_tf_squared
    showif notestutorial == 6:
        add "images/notes_tutorial6.png" at dissolve_tf_squared
    showif notestutorial == 7:
        add "images/notes_tutorial7.png" at dissolve_tf_squared
    showif notestutorial == 8:
        add "images/notes_tutorial8.png" at dissolve_tf_squared
    showif notestutorial == 9:
        add "images/notes_tutorial9.png" at dissolve_tf_squared
    showif notestutorial == 10:
        add "images/notes_tutorial10.png" at dissolve_tf_squared
    showif notestutorial == 11:
        add "images/notes_tutorial11.png" at dissolve_tf_squared



    showif not notestutorial == 1:
        button:
            style "arrow"
            at dissolve_tf
            yalign 0.87
            xoffset 70
            activate_sound "sounds/sys13.wav"
            action SetVariable("notestutorial", notestutorial-1)
    else:
        if persistent.notes:
            button:
                style "access2"
                at dissolve_tf
                yalign 0.84
                xalign 0.5
                action [Function(EnableMenu, "notes"), ShowMenu('notes')], SetVariable("persistent.notes", True), SetVariable("notestutorial", 1)

    showif not notestutorial == 11:
        button:
            style "arrow2"
            at dissolve_tf
            yalign 0.87
            xoffset 1165
            activate_sound "sounds/sys13.wav"
            action SetVariable("notestutorial", notestutorial+1)
    else:
        button:
            style "access2"
            at dissolve_tf
            yalign 0.84
            xalign 0.5
            action [Function(EnableMenu, "notes"), ShowMenu('notes')], SetVariable("persistent.notes", True), SetVariable("notestutorial", 1)

screen notes(initial_entry=None):
    predict False ## Avoid predicting this screen
    tag menu

    default colors_visible = False
    default selected_color = "#fff"
    default menu_visible = False
    default menu_position = (0,0)
    default clicked_search_idx = None
    default clicked_note_num = None

    key "input_focus_down" action Function(notes.FocusNext, clicked=False)
    key "input_focus_up" action Function(notes.FocusPrev, clicked=False)
    key "mousedown_1" action notes.hide_menus
    #key "viewport_up" action Function(notes.Scroll, increment=-1)
    #key "viewport_down" action Function(notes.Scroll, increment=1)

    $ notes.Initialize()
    key "game_menu" action [Hide('notes', transition=config.exit_transition), Return()] #Needed to proc `on "hide"`
    for ac in ["replaced", "hide"]:
        on ac action Function(notes.Hide)
    for ac in ["replace", "show"]:
        on ac action Function(notes.Show)


    use game_menu(_("Notes"), padded=(notes.xoffset, 40, 20, 23)):
        style_prefix "notes"

        frame:
            background Frame("gui/notes_titled_frame.png", gui.titled_frame_borders, tile=gui.frame_tile)
            padding (0, 0, 0, 0)
            if persistent.notes_input_visible:
                add Solid("#0003", xsize=persistent.notes_width+12, ysize=558-39, ypos=39+39, xpos=notes.width1+notes.width2+notes.width3+36-2 - (persistent.notes_width+12))
                add Solid(notes.line_color, xsize=notes.line_width, ysize=558, ypos=39, xpos=notes.width1+notes.width2+notes.width3+36-2 - (persistent.notes_width+12))
            add Solid(notes.line_color, xsize=notes.line_width, ysize=558, ypos=39, xpos=notes.width1+12-2)
            add Solid(notes.line_color, xsize=notes.line_width, ysize=558, ypos=39, xpos=notes.width1+notes.width2+24-2)

            hbox:
                spacing 2
                xanchor 1.0
                xpos 0.98
                xoffset 10
                yoffset 7

                null width 50

                button:
                    style "notes_formatting_button"
                    action notes.hide_menus+[Function(notes.CollapseAll, False)]
                    selected False
                    activate_sound "sounds/sys3.wav"
                    text "EXPAND\nALL" style "notes_formatting_button_text"
                button:
                    style "notes_formatting_button"
                    action notes.hide_menus+[Function(notes.CollapseAll, True)]
                    selected False
                    activate_sound "sounds/sys3.wav"
                    text "COLLAPSE\nALL" style "notes_formatting_button_text"

                if persistent.notes_input_visible:
                    null width 2

                    for tag in ["b","i","u","s"]:
                        button:
                            style "notes_formatting_button"
                            xsize 27
                            action notes.hide_menus+[Function(notes.ToggleTag, tag)]
                            if notes.current_focus is not None:
                                selected tag in notes.list[notes.current_focus].input.open_tags[0]
                            else:
                                selected False
                            fixed:
                                text "{"+tag+"}"+tag.upper()+"{/"+tag+"}":
                                    style "notes_formatting_button_text"
                                    size 25
                                    line_spacing -5

                    button hover_sound "sounds/sys2.wav" action [Function(notes.ToggleTag, "color", selected_color)] + notes.hide_menus:
                        add Solid(selected_color, xsize=23, ysize=23)
                    null width 3

                    button action ToggleScreenVariable("colors_visible"):
                        hover_sound "sounds/sys2.wav"
                        grid 3 3:
                            spacing 1
                            add Solid("#ffffff", xsize=7, ysize=7)
                            add Solid("#000000", xsize=7, ysize=7)
                            add Solid("#ff0000", xsize=7, ysize=7)

                            add Solid("#ff9900", xsize=7, ysize=7)
                            add Solid("#ffff00", xsize=7, ysize=7)
                            add Solid("#00ff00", xsize=7, ysize=7)

                            add Solid("#00ffff", xsize=7, ysize=7)
                            add Solid("#4a86e8", xsize=7, ysize=7)
                            add Solid("#ff00ff", xsize=7, ysize=7)
                    null width 1


                    imagebutton idle "gui/notes/left.png" ysize 33 yoffset -7 xsize 27 xoffset 6 action Function(notes.AdjustNoteWidth, 20):
                        hover_sound "sounds/sys2.wav"
                        activate_sound "sounds/sys9.wav"
                    null width 3
                    imagebutton idle "gui/notes/right.png" ysize 33 yoffset -7 xsize 27 xoffset 6 action Function(notes.AdjustNoteWidth, -20):
                        hover_sound "sounds/sys2.wav"
                        activate_sound "sounds/sys9.wav"

                button:
                    style "notes_formatting_button"
                    xsize 74
                    selected False
                    activate_sound "sounds/sys10.wav"

                    if persistent.notes_input_visible:
                        text "HIDE\nNOTES" style "notes_formatting_button_text"
                    else:
                        text "SHOW\nNOTES" style "notes_formatting_button_text"

                    action notes.hide_menus+[
                        ToggleField(persistent, "notes_input_visible"),
                        Function(notes.Repopulate),
                        ]

            vbox:
                yoffset 2
                hbox:
                    style_prefix "search_chapter"
                    spacing 4
                    xoffset 20
                    yoffset 3
                    text "CHAPTER" style "frame_title_text" yalign 0.5
                    null width 20
                    for i in range(5):
                        if notes.IsUnlocked(i):
                            textbutton str(i+1):
                                action notes.hide_menus+[Function(notes.SetChapter, i)]
                                selected notes.chapter==i
                    null width 1

                    button:
                        style "notes_formatting_button"
                        yoffset 3
                        action [Function(EnableMenu, "notes_tutorial"), ShowMenu('notes_tutorial')]
                        activate_sound "sounds/sys15.wav"
                        text "VIEW\nTUTORIAL" style "notes_formatting_button_text"
                frame:
                    background "#0008"
                    padding (5,10,5,-3)

                    hbox:
                        spacing 12
                        vbox:
                            xsize notes.width1
                            label _("TITLE") text_ypos -1 style "frame_title"

                        vbox:
                            xsize notes.width2
                            label _("WITH") text_ypos -1 style "frame_title"

                        vbox:
                            if persistent.notes_input_visible:
                                xsize notes.width3 - persistent.notes_width - 12
                            else:
                                xsize notes.width3
                            label _("OVERVIEW") text_ypos -1 style "frame_title"

                        if persistent.notes_input_visible:
                            vbox:
                                xsize persistent.notes_width
                                label _("NOTES") text_ypos -1 style "frame_title"

                # Horizontal header line
                add Solid(notes.line_color, xsize=notes.width1+notes.width2+notes.width3+36-2, ysize=notes.line_width)

                hbox:
                    spacing 0
                    massive_viewport:
                        id "notes_vp"
                        xsize notes.width1+notes.width2+notes.width3+36-2
                        #mousewheel True
                        scroll_action notes.Scroll
                        yinitial notes.position
                        #draggable True
                        arrowkeys False

                        vbox:
                            style_prefix "notes"
                            id "notes_vp_vbox"

                    vbar:
                        id "notes_vp_bar"
                        value FieldValue(notes, "position", notes.max_position, action=notes.Populate, style="scrollbar")
                        bar_invert True

        showif colors_visible:
            frame:
                xalign 0.9
                ypos 30
                padding (2,2,2,2)
                background "#000"

                vbox:
                    for row in [
                    ["#000000", "#434343", "#666666", "#999999", "#b7b7b7", "#cccccc", "#d9d9d9", "#efefef", "#f3f3f3", "#ffffff"],
                    ["#980000", "#ff0000", "#ff9900", "#ffff00", "#00ff00", "#00ffff", "#4a86e8", "#0000ff", "#9900ff", "#ff00ff"],
                    ["#e6b8af", "#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e0e3", "#c9daf8", "#cfe2f3", "#d9d2e9", "#ead1dc"],
                    ["#dd7e6b", "#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#a4c2f4", "#9fc5e8", "#b4a7d6", "#d5a6bd"],
                    ["#cc4125", "#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6d9eeb", "#6fa8dc", "#8e7cc3", "#c27ba0"],
                    ["#a61c00", "#cc0000", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3c78d8", "#3d85c6", "#674ea7", "#a64d79"],
                    ["#85200c", "#990000", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#1155cc", "#0b5394", "#351c75", "#741b47"],
                    ["#5b0f00", "#660000", "#783f04", "#7f6000", "#274e13", "#0c343d", "#1c4587", "#073763", "#20124d", "#4c1130"],
                    ]:
                        hbox:
                            for color in row:
                                button action [Function(notes.ToggleTag, "color", color), SetScreenVariable("colors_visible", False), SetScreenVariable("selected_color", color)]:
                                    add Solid(color,xsize=18,ysize=18)

        showif menu_visible:
            frame:
                style_prefix "notes_popup"
                xpos menu_position[0]
                ypos menu_position[1]
                xsize 160
                at tf_dropdown_menu

                vbox:
                    textbutton _("Go to Search") action [Function(search.UpdateMessages), ShowMenu('search', clicked_search_idx)] xfill True
                    textbutton _("Copy All") action [Function(notes.CopyDetails, clicked_note_num, 'all')]+notes.hide_menus xfill True
                    textbutton _("Copy Overview") action [Function(notes.CopyDetails, clicked_note_num, 'overview')]+notes.hide_menus xfill True
                    textbutton _("Copy Note") action [Function(notes.CopyDetails, clicked_note_num, 'user_note')]+notes.hide_menus xfill True

    ## Deselect all inputs
    if initial_entry:
        timer 0.01 action Function(notes.Populate)
        timer 0.05 action Function(notes.UpdateNoteHeights)
        timer 0.10 action GoToNote(initial_entry)
        timer 0.20 action Function(notes.FocusInput, initial_entry.what[1]-1)
        
    else:
        timer 0.01 action Function(notes.Populate)
        timer 0.10 action Function(notes.FocusInput, -1)
        timer 0.20 action Function(notes.UpdateNoteHeights)

style notes_text:
    size 14
    outlines [(0,"#0009",1,1)]

style notes_input is input:
    caret At(Solid("#fff", style='notes_input_caret'), caret_blink)
    size 14
    outlines [(0,"#0009",1,1)]
    color "#fff"
    line_spacing 1

style notes_input_solid is notes_input:
    caret At(Solid("#fff", style='notes_input_caret'), caret_solid)

style notes_input_caret:
    xsize 1
    xoffset 1
    ysize 17

style notes_button is gui_button:
    padding (1,1,1,1)
    activate_sound None
    hover_sound None

style notes_formatting_button is gui_button:
    ysize 27
    background None
    #hover_background "#fff4"
    selected_background "#fff2"
    hover_sound "sounds/sys2.wav"

style notes_formatting_button_text is button_text:
    xalign 0.5
    yoffset 2
    text_align 0.5
    color "#fff"
    hover_color gui.hover_color
    selected_color gui.idle_color
    font "fonts/Acumin-BdPro.otf"
    size 14
    line_spacing -3
    kerning -1

style notes_title_frame is frame:
    yalign 0.5
    padding (3,3,3,3)
    background Transform("gui/notes_bg.png", xalign=0.5, yalign=0.5)
    yminimum 80


style notes_popup_frame is popup_frame
style notes_popup_button is popup_button
style notes_popup_button_text is popup_button_text

screen image_popup_full(bg_name):
    modal True
    for k in ['game_menu', 'dismiss']:
        key k action Hide('image_popup_full', transition=Dissolve(0.2))
    add bg_name

screen image_popup(bg_name):
    add bg_name:
        zoom 0.35
        alpha 0.85
        xalign 0.5
        yanchor 1.0
        ypos 0.93

style round_button is button:
    background Frame("gui/button/round_button_idle.png", 10, 10)
    hover_background Frame("gui/button/round_button_hover.png", 10, 10)
    top_margin 2
    bottom_margin 2

style notes_explanation_button is round_button:
    xsize 300

style notes_explanation_button_text is button_text:
    color "#fff"
    xalign 0.5
    yoffset 2
