## config.interact_callbacks
## config.start_interact_callbacks
## config.with_callback
## config.menu_arguments_callback

#Make sure these definitions are the very first things that's loaded
init offset = -9999

#######################
## Persistent Variables
#######################
# Game variables
default persistent.last_script_version = config.version

default persistent.started = False
default persistent.mainmenu2 = False
default persistent.mainmenu3 = False
default persistent.mainmenu4 = False
default persistent.mainmenu5 = False
default persistent.mainmenu6 = False
default persistent.finished = False

# Debug
default persistent.log_nvl_overflow = False

# Options
default persistent.pref_screen = "general"

default persistent.sprite_dark_tint = 0.6
default persistent.sprite_darken = True
default persistent.sprite_darken_transition = True
default persistent.time_format_24 = True
default persistent.pref_click_short_pauses = False #:)
default persistent.sprite_change_text_opacity = 0.1
default persistent.sprite_change_pause_duration = 0.2
default persistent.prev_nvl_text_opacity = 1.0
default persistent.prev_nvl_text_fadein_enabled = False
default persistent.game_menu = "save"
default persistent.sprite_change_text_dim_enabled = False

# Tips
default persistent.tip_visibility = python_dict()
default persistent.read_all_tips = False

# Map
default persistent.notified_map_unlock = False
default persistent.map_unlocked = [0]*9
default persistent.mappos = False
default persistent.minimap = False

# Search
default persistent.search_exact_match = False
default persistent.search_clear_initial = False
default persistent.search_case_sensitive = False

# Notes
default persistent.notes = False #If we've opened the notes before or not
default persistent.note_meta = python_dict()
default persistent.notes_input_visible = True
default persistent.notes_width = 500

# Chapter 5 questions
default persistent.save_scum_detected = False
default persistent.c5_score = python_dict()
default persistent.c5_answers = python_dict()
default persistent.c5_times = python_dict()

# Stats
default persistent.playtime = {'total':0, 'game':0, 'search':0, 'map':0, 'notes':0, 'other':0, 'session':0, 'unfocused':0}
default persistent.runtime_start_time = time.time() # Playtime counter

default persistent.num_sessions = 0
default persistent.copy_detected = False
default persistent.analytics_logged = python_dict()
default persistent.last_updated_stats = 0 ## This is the last time I pulled the stats manually

# Chart
default persistent.chart = False

#######################
## Store (Temporary) Variables
#######################
# Game
default explanation = False # Is the game currently in explanation mode (text on left side only)
default chapter = ""
default scene_title = ""
default bgm_credits_name = ""

# Menu
default preferences_changed = False

# GUI
default sprite_changed_disable_prev_fade = False
default nvl_text_alpha = 1.0
default nvl_dialogue_count = 0
default nvl_dialogue_count_changed = False

#And reset the offset
init offset = 0

init python:
    def StartupOperations():
        ## Called at the splash screen. Handles script updates
        persistent.playtime['session'] = 0
        persistent.num_sessions += 1
        renpy.game.preferences.self_voicing = False
        MapResetPositions()

        # Steam achievements
        CheckAllEndingsAchievement()
        achievement.sync()

        ## Version 0.2 changes
        if persistent.last_script_version is None and config.version != "0.1":
            persistent.last_script_version = "0.1"

            if "c1_018" in persistent.note_meta:
                note_meta = persistent.note_meta["c1_018"]
                if note_meta.IsLineUnlocked(8):
                    note_meta.UnlockLine(9)

            if "c3_011" in persistent.note_meta:
                note_meta = persistent.note_meta["c3_011"]
                if note_meta.IsLineUnlocked(6):
                    note_meta.UnlockLine(7)

            if "c5_008" in persistent.note_meta:
                note_meta = persistent.note_meta["c5_008"]
                if note_meta.IsLineUnlocked(2):
                    note_meta.UnlockLine(3)

            #if persistent.enable_c5_questions is None and c5_answers.IsQuestionSeen("map kitchen clue"):
            #    persistent.enable_c5_questions = True

        if persistent.last_script_version != config.version:
            #######
            ## Version changed. Update script
            #######
            ## @TODO: Update persistent._chosen
            ## Use the following to improve results? persistent.end[0-9], UnlockMap

            from collections import OrderedDict
            import jellyfish

            if 'unfocused' not in persistent.playtime:
                persistent.playtime['unfocused'] = 0

            ## Get all scene titles and sort them
            all_scenes = [(x.what, x.global_index) for x in search.scene_titles]
            all_scenes = sorted(all_scenes, key=lambda x: x[1])

            ## Pick out the elements we've seen already
            seen_scenes = [x for x in all_scenes if x[0] in persistent.analytics_logged['scenes'].keys()]
            if len(seen_scenes)>0:
                persistent.started = True
            seen_notes = notes.GetSeenNotes()
            seen_labels = [x for x in persistent._seen_ever if type(x)==str]
            seen_choices = python_dict()
            for key, choice_text  in persistent._chosen:
                linenum = key[-1]
                seen_choices[linenum] = choice_text
            seen_choices = OrderedDict(sorted(seen_choices.items()))

            ## Get the last auto save data. This point will take us to the exact line in the script we're at
            filename = __slotname('1', page='auto')
            save_json = FileJson('1', page='auto', empty=None)
            saved_node = GetNodeClosestToSave(filename, save_json, check_if_seen=False)

            ## Go through the entire script from the start
            splashscreen_node = renpy.game.script.lookup('splashscreen')
            idxs = [
                (GetGlobalIndexFromNode(splashscreen_node), GetGlobalIndexFromNode(search.end_node)+1),
                (GetGlobalIndexFromNode(search.start_node_tips), GetGlobalIndexFromNode(search.end_node_tips)+1)
                ]

            accumulated_nodes = python_list()
            final_nodes = python_list()
            idx_end_of_if_block = python_list()
            idx_end_of_condition = python_list()
            line_numbers = python_list()
            seen_scenes_idx = 0

            for (idx_start, idx_end) in idxs:
                current_idx = idx_start
                while current_idx < idx_end:
                    node = renpy.game.script.all_stmts[current_idx]

                    if type(node)==renpy.ast.Python:
                        accumulated_nodes.append(node)
                        if "SceneTitle" in node.code.source and len(seen_scenes) > 0 and seen_scenes_idx+1 < len(seen_scenes):
                            scene_name = node.code.source.split('"')[1]
                            if seen_scenes[seen_scenes_idx+1][0] == scene_name:
                                ## The scenes are consecutive, store these messages
                                final_nodes.extend(accumulated_nodes)
                                seen_scenes_idx += 1
                            #else:
                            #    print("Clear SceneTitle: {}".format(scene_name))
                            accumulated_nodes = python_list()
                        elif "UnlockNote" in node.code.source:
                            if node.code.source in seen_notes:
                                final_nodes.extend(accumulated_nodes)
                            #else:
                            #    print("Clear: {}".format(node.code.source))
                            accumulated_nodes = python_list()
                        elif "ChapterEnd" in node.code.source:
                            chapter_key = "C" + node.code.source[node.code.source.find("(")+1 : node.code.source.find(")")]
                            if chapter_key in persistent.playtime:
                                final_nodes.extend(accumulated_nodes)
                            #else:
                            #    print("Clear ChapterEnd: {}".format(chapter_key))
                            accumulated_nodes = python_list()
                        elif "ShowQuestion" in node.code.source:
                            ## Update the score variable so the if condition can be evaluated later
                            question_name = node.code.source.split('"')[1]
                            store.c5_answers.last_answer = c5_answers.GetAnswerRaw(question_name)
                            if store.c5_answers.last_answer != None:
                                final_nodes.extend(accumulated_nodes)
                                accumulated_nodes = python_list()
                        elif "MarkQuestion" in node.code.source:
                            question_name = node.code.source.split('"')[1]
                            if store.c5_answers.IsQuestionSeen(question_name):
                                final_nodes.extend(accumulated_nodes)
                                accumulated_nodes = python_list()

                    elif type(node)==renpy.ast.Label:
                        if node.name in seen_labels:
                            final_nodes.extend(accumulated_nodes)
                        #else:
                        #    print("Clear Label: {}".format(node.name))
                        accumulated_nodes = python_list()

                    elif type(node)==renpy.ast.Menu:
                        ## Check if any of the choices have been selected, then unlock this menu accordingly
                        ## Check which menu choices have been selected by cross-referencing
                        ##  persistent.chosen. Do Levenshtein Distance and linenumber comparisons
                        ##  to make sure the stored and current lines are similar/matched
                        min_distance = 1e9
                        for item in node.items:
                            choice_text, choice_seen, choice_block = item
                            for linenum, val in seen_choices.items():
                                ## Only check nearby strings
                                if abs(linenum-node.linenumber) < 3000:
                                    min_distance = min(min_distance, jellyfish.levenshtein_distance(choice_text, val))

                        if min_distance < 10:
                            accumulated_nodes.append(node)
                            final_nodes.extend(accumulated_nodes)
                            accumulated_nodes = python_list()

                    elif type(node)==renpy.ast.If:
                        choice_node = node
                        found_true_condition = False

                        ## Recursively expand nested tailing if statements until we find the last node
                        last_if_block_node = node.entries[-1][1][-1]
                        while type(last_if_block_node) == renpy.ast.If:
                            last_if_block_node = last_if_block_node.entries[-1][1][-1]
                        idx_end_of_if_block.append( GetGlobalIndexFromNode(last_if_block_node) )

                        for _condition, block in node.entries:
                            if "total_answers" in _condition:
                                ## Ignore these cases
                                pass
                            elif eval(_condition):
                                found_true_condition = True

                                ## Recursively expand nested tailing if statements until we find the last node
                                last_condition_node = block[-1]
                                while type(last_condition_node) == renpy.ast.If:
                                    last_condition_node = last_condition_node.entries[-1][1][-1]
                                idx_end_of_condition.append( GetGlobalIndexFromNode(last_condition_node) )

                                current_idx = GetGlobalIndexFromNode(block[0])-1
                                line_numbers.append((last_condition_node.linenumber, last_if_block_node.linenumber))
                                break # No need to evaluate the rest of the conditions

                        if not found_true_condition:
                            ## Skip the entire if statement
                            current_idx = idx_end_of_if_block.pop()

                    elif type(node) in [renpy.ast.Say, renpy.ast.Hide, renpy.ast.Show, renpy.ast.Scene, renpy.ast.With]:
                        accumulated_nodes.append(node)

                    elif type(node) == renpy.ast.UserStatement and node.line.startswith("play movie"):
                        accumulated_nodes.append(node)

                    ## If this is the autosave point, store all data up to this point
                    if node == saved_node:
                        final_nodes.extend(accumulated_nodes)
                        accumulated_nodes = python_list()

                    current_idx += 1
                    if len(idx_end_of_condition)>0 and current_idx > idx_end_of_condition[-1]:
                        current_idx = idx_end_of_if_block[-1] + 1
                        idx_end_of_condition.pop()
                        idx_end_of_if_block.pop()
                        line_numbers.pop()

            #print(len(final_nodes))
            #if len(final_nodes)>0:
            #    print(final_nodes[0].linenumber)
            #    print(final_nodes[-1].linenumber)
            #else:
            #    print('No messages seen')

            ## Save the data
            renpy.game.persistent._seen_ever.clear()
            for node in final_nodes:
                persistent._seen_ever[node.name] = True

        persistent.last_script_version = config.version

        analytics.CopyCheck()

    ## Define a new load action that can somewhat handle different versions
    def __slotname(name, page=None, slot=False):

        if slot:
            return name

        if page is None:
            page = persistent._file_page

        try:
            page = int(page)
            page = page + persistent._file_folder * config.file_pages_per_folder
        except ValueError:
            pass

        if config.linear_saves_page_size is not None:
            try:
                page = int(page)
                name = int(name)
                return str((page - 1) * config.linear_saves_page_size + name)
            except ValueError:
                pass

        return str(page) + "-" + str(name)

    def __newest_slot():
        """
        Returns the name of the newest slot.
        """

        return renpy.newest_slot(r'\d+')

    def GetNodeClosestToSave(filename, save_json, check_if_seen=True):
        if not renpy.can_load(filename):
            ## Save file doesn't exist, jump out
            return None

        min_global_idx = -1
        max_global_idx = -1
        if save_json and 'scene' in save_json:
            scene_name = save_json['scene']
            scene_titles = OrderedDict()
            for entry in search.scene_titles:
                scene_titles[entry.what] = entry
            scene_titles_keys = scene_titles.keys()

            if scene_name in scene_titles_keys:
                ## Let's look at all messages in this scene
                scene_idx = scene_titles_keys.index(scene_name)
                if scene_idx+1<len(scene_titles):
                    end_node = scene_titles[scene_titles_keys[scene_idx+1]].node
                else:
                    end_node = search.end_node

                min_global_idx = GetGlobalIndexFromNode(scene_titles[scene_name].node)
                max_global_idx = GetGlobalIndexFromNode(end_node)

        if min_global_idx == -1:
            ## Scene name doesn't exist. Look at all values in this chapter
            chapter_labels = ["start", "chapter2", "chapter3", "chapter4", "chapter5", "the_end"]
            if save_json and 'chapter' in save_json and save_json['chapter'] not in [None, '']:
                chapter_idx = int(save_json['chapter'])
                start_node = renpy.game.script.lookup(chapter_labels[chapter_idx])
                end_node = renpy.game.script.lookup(chapter_labels[chapter_idx+1])

                min_global_idx = GetGlobalIndexFromNode(start_node)
                max_global_idx = GetGlobalIndexFromNode(end_node)

        if min_global_idx == -1:
            ## Our previous methods failed. Look through the entire script
            min_global_idx = GetGlobalIndexFromNode(search.start_node)
            max_global_idx = GetGlobalIndexFromNode(search.end_node)

        ## Build a list of say nodes
        say_nodes = python_list()
        for idx in range(min_global_idx, max_global_idx):
            node = GetNodeFromGlobalIndex(idx)
            if type(node)==renpy.ast.Say and (not check_if_seen or node.name in persistent._seen_ever):
                say_nodes.append(node)
        #print("Min linenum to search: {}, Max linenum to seach: {}, Say node count: {}".format(
        #    GetNodeFromGlobalIndex(min_global_idx).linenumber,
        #    GetNodeFromGlobalIndex(max_global_idx).linenumber,
        #    len(say_nodes))
        #    )

        roots, rollbacklog = renpy.loadsave.loads(renpy.loadsave.location.load(filename))
        if 'store._last_say_who' in roots:
            import jellyfish
            last_who = roots['store._last_say_who']
            last_what = roots['store._last_say_what']
            best_nodes = python_list()

            #print('\n\n--Saved--')
            #print(last_who, last_what)

            #print('---NVL entries--')
            #for entry in roots['store.nvl_list']:
            #    print(entry[1])

            for idx_node, node in enumerate(say_nodes):
                if node.who != last_who:
                    continue

                ## Make sure the strings are of similar lengths to avoid the expensive computation
                if 0.75 < 1.0*len(node.what)/len(last_what) < 1.3333:
                    #score = jellyfish.jaro_distance(node.what, last_what)
                    score = jellyfish.levenshtein_distance(node.what, last_what)
                    best_nodes.append((score, node))
                    if score == 0:
                        break
            best_nodes = sorted(best_nodes, key=lambda x: x[0])
            #for x in best_nodes[:min(3, len(best_nodes))]:
            #    who = renpy.ast.eval_who(x[1].who, x[1].who_fast)
            #    print(x[0], who.name.name, ":", x[1].what, )
            #print('===========')

            if len(best_nodes)>0:
                return best_nodes[0][1]

        return None


    class FileLoad2(Action, DictEquality):
        """
        :doc: file_action

        Loads the file.

        `name`
            The name of the slot to load from. If None, an unused slot will be
            used, and hence the file will not be loadable.

        `confirm`
            If true and not at the main menu, prompt for confirmation before loading the file.

        `page`
            The page that the file will be loaded from. If None, the
            current page is used.

        `newest`
            If true, the button is selected if this is the newest file.

        `cycle`
            Ignored.

        `slot`
            If True, `name` is taken to be a slot name, and `page` is ignored.
        """

        alt = "Load slot [text]"
        slot = None

        def __init__(self, name, confirm=True, page=None, newest=True, cycle=False, slot=False):

            if name is None:
                name = __unused_slot_name(page)

            self.name = name
            self.confirm = confirm
            self.page = page
            self.newest = newest
            self.slot = slot

            try:
                self.alt = __("Load slot %s: [text]") % (name,)
            except:
                self.alt = "Load slot %s: [text]" % (name,)

        def __call__(self):

            if not self.get_sensitive():
                return

            fn = __slotname(self.name, self.page, self.slot)

            if not main_menu:
                if self.confirm:
                    if config.autosave_on_quit and not fn.startswith("auto-"):
                        renpy.loadsave.force_autosave()
                    layout.yesno_screen(layout.LOADING, FileLoad(self.name, False, self.page, slot=self.slot))
                    return

            #renpy.load(fn)
            self.execute_load(self.name, fn)

        def get_sensitive(self):
            if _in_replay:
                return False

            return renpy.can_load(__slotname(self.name, self.page, self.slot))

        def get_selected(self):
            if not self.confirm or not self.newest:
                return False

            return __newest_slot() == __slotname(self.name, self.page, self.slot)

        def execute_load(self, slot, filename):
            roots, rollbacklog = renpy.loadsave.loads(renpy.loadsave.location.load(filename))
            saved_label = rollbacklog.current.context.current

            try:
                saved_node = renpy.game.script.lookup(saved_label)
                renpy.exports.play("sounds/sys8.wav") #Play this as an activate_sound
                JumpToScriptNode(saved_node, confirm=False)()
                return
            except renpy.script.ScriptError:
                pass

            save_json = FileJson(slot, empty=None)
            target_node = GetNodeClosestToSave(filename, save_json, check_if_seen=True)
            if target_node != None:
                renpy.exports.play("sounds/sys8.wav") #Play this as an activate_sound
                JumpToScriptNode(target_node, confirm=False)()

            renpy.show_screen(
                "display_message",
                message="Invalid save file.")
            renpy.restart_interaction()


init -10 python:
    def time_tag(tag, argument):
        if persistent.time_format_24:
            ## If there's no trailing colon, add ":00"
            if ":" in argument:
                return [(renpy.TEXT_TEXT, argument)]

            ## Remove any trailing dot
            if argument[-1]==".":
                return [(renpy.TEXT_TEXT, argument[:-1]+":00.")]
            return [(renpy.TEXT_TEXT, argument+":00")]

        ## Trim the ending period (don't need it since a.m. already ends on one)
        if argument[-1]==".":
            argument = argument[:-1]

        if ":" in argument:
            h, m = argument.split(":")
            h = int(h)
        else:
            h = int(argument)

        t = "a.m."
        if h >= 12:
            t = "p.m."
            h -= 12
        if h == 0:
            h = 12

        if ":" in argument:
            return [(renpy.TEXT_TEXT, "{}:{} {}".format(h,m,t))]
        else:
            return [(renpy.TEXT_TEXT, "{} {}".format(h,t))]

    config.self_closing_custom_text_tags["time"] = time_tag

    def SceneTitle(val):
        store.scene_title = val
        renpy.invoke_in_thread(analytics.SendSceneEvent, val)

    def ChapterEnd(chapter):
        chapter_key = "C"+str(chapter)
        if chapter_key in persistent.playtime:
            return

        total_prev_time = 0
        for i in range(1, chapter):
            key = "C" + str(i)
            if key in persistent.playtime:
                total_prev_time += persistent.playtime[key]

        chapter_time = persistent.playtime['total'] - total_prev_time
        persistent.playtime[chapter_key] = chapter_time

        renpy.invoke_in_thread(analytics.SendChapterTime, chapter_key, chapter_time)

    def Pause(val):
        ## Do a very short hard pause to prevent accidentally clicking through, then make the rest a soft pause
        ## Any pause greater than 3.0 seconds is automatically a hard pause
        try:
            if not persistent.pref_click_short_pauses:
                renpy.pause(val, hard=True)
            else:
                if val >= 3.0:
                    renpy.pause(val, hard=True)
                else:
                    hard_limit = 0.1
                    renpy.pause(hard_limit, hard=True)
                    if (val > hard_limit):
                        renpy.pause(val-hard_limit)
        except IndexError:
            pass

    def BeginSpriteChange(darken_all=True):
        if not persistent.sprite_change_text_dim_enabled:
            return

        if darken_all:
            if persistent.sprite_darken:
                for sprite in renpy.game.contexts[0].scene_lists.layers['master']:
                    if sprite.tag == 'bg' or sprite.tag == 'black':
                        continue

                    x = python_list(sprite.name)
                    if 'bright' in x:
                        x.remove('bright')
                    if 'dark' in x:
                        x.remove('dark')

                    x.append('dark')
                    renpy.show(' '.join(x))

        store.nvl_text_alpha = persistent.sprite_change_text_opacity
        renpy.with_statement(fastdissolve)
        store.sprite_changed_disable_prev_fade = True

    def EndSpriteChange():
        if not persistent.sprite_change_text_dim_enabled:
            return

        if persistent.sprite_change_pause_duration > 0.001:
            Pause(persistent.sprite_change_pause_duration)
        store.nvl_text_alpha = 1.0
        renpy.with_statement(fastdissolve)

# Entry points from the game into menu-space.
label _game_menu_new(*args, **kwargs):
    if not persistent.game_menu:
        return

    $ renpy.play("sounds/sys6.wav", channel="system")

    call _enter_game_menu from _call__enter_game_menu_10

    if renpy.has_label("game_menu"):
        jump expression "game_menu"

    if renpy.has_screen(persistent.game_menu):
        ## SUPREME HACK - Run initializations right here before the menu is called
        if persistent.game_menu == "search":
            $ search.UpdateMessages()

        $ renpy.show_screen(persistent.game_menu, *args, **kwargs)
        $ ui.interact()

        if store.preferences_changed:
            $ store.preferences_changed = False
            #$ renpy.invoke_in_thread(analytics.UpdatePreferences)
        jump _noisy_return

    jump expression persistent.game_menu
