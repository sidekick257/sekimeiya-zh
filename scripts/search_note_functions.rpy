init -20 python:
    import re

    all_statements_indexed = {k: v for v, k in enumerate(renpy.game.script.all_stmts)}

    def GetGlobalIndexFromNode(node):
        return all_statements_indexed[node]

    def GetNodeFromGlobalIndex(idx):
        return renpy.game.script.all_stmts[idx]

    def GetMousePos():
        ## Get position and project it to a virtual 1280x720 canvas
        multiplier = 1.0/GuiElementScaling(1.0, cast_int=False)

        pos = pygame.mouse.get_pos()
        return (int(multiplier*pos[0]), int(multiplier*pos[1]))

    def MenuClickAction(num=1):
        pos = GetMousePos()

        ## Compute the position of the context menu
        height = 11 + num*27
        width = 158

        x_offset = pos[0]+width-1220
        if x_offset<20:
            x_offset = 20

        y_offset = pos[1]+height+60-650
        if y_offset<80:
            y_offset = 80

        return (pos[0]-x_offset, pos[1]-y_offset)

    def GetChannelFromString(x):
        try:
            return re.search(r'channel=[\'"](.*?)[\'"]', x).group(1)
        except:
            return "music"

    def GetScriptDetails(target_node, all_characters=False):
        ## Get all details about the script prior to this point (background, sprites, music, etc)
        ## If all_characters is true, get the most recent sprite settings for all sprites, regardless if they're hidden or not
        ##
        ## Note: this only works properly for the english script since that's the script that contains ALL the instructions
        ## If we're using a translation, we first switch over to the english script to find the relevant context

        done = False
        line_offset = 1

        node_idx = GetGlobalIndexFromNode(target_node)
        node_list = []

        ## Initial state
        bg = None
        bgm_credits_name = ""
        position_history = python_list()
        explanation = False
        music = python_dict()
        music_vol = python_list()
        overlay_list = python_dict()
        snow_state = 0
        sprite_list = python_dict()
        tint = 'normal'
        tip_orb = None
        sprite_attrib_groups = ['base', 'expression', 'other', 'state', 'cleanliness']

        found_bg = False
        found_bgm_credits = False
        found_explanation = False
        found_first_line = False
        found_music = False
        found_overlay = False
        found_positions = False
        found_snow = False
        found_tint = False

        rv = python_dict()

        while not done:
            line_offset -= 1
            node = GetNodeFromGlobalIndex(node_idx+line_offset)

            if not found_first_line and type(node)==renpy.ast.Translate:
                tl_node = renpy.game.script.translator.lookup_translate(node.identifier)
                if type(tl_node)==renpy.ast.Say:
                    node_list.append(tl_node)

            elif type(node)==renpy.ast.Python:
                if "PlayMusic" in node.code.source:
                    found_music = True
                    channel = GetChannelFromString(node.code.source)
                    if channel not in music:
                        music[channel] = node.code.source
                elif "StopMusic" in node.code.source:
                    found_music = True
                    channel = GetChannelFromString(node.code.source)
                    if channel not in music:
                        music[channel] = 'StopMusic(channel="{}", fadeout=0)'.format(channel) ## Remove any fadeout, instantly stop
                elif "renpy.music.set_volume" in node.code.source:
                    ## Only add if the channel isn't already defined
                    channel = GetChannelFromString(node.code.source)
                    channel_exists = False
                    for vol in music_vol:
                        if channel == GetChannelFromString(vol):
                            channel_exists = True
                            break
                    if not channel_exists:
                        music_vol = [node.code.source] + music_vol

                elif not found_positions and "MapSetPosition" in node.code.source:
                    position_history.append(node.code.source)
                    if len(position_history) >= map_position_count:
                        found_positions = True

                elif not found_positions and "MapResetPosition" in node.code.source:
                    found_positions = True

                elif not found_explanation and "explanation" in node.code.source:
                    found_explanation = True
                    explanation = node.code.source.split('=')[1].lower().strip() in ("true", "1")

                elif not found_bgm_credits and "bgm_credits_name" in node.code.source:
                    found_bgm_credits = True
                    bgm_credits_name = node.code.source.split('=')[1].strip().replace('"', '')

                elif not tip_orb and "TipOrbHide" in node.code.source:
                    tip_orb = -1
                elif not tip_orb and "TipOrbShow" in node.code.source:
                    tip_orb = node.code.source.split('"')[1].strip()

                elif not found_tint and "SpriteTint" in node.code.source:
                    found_tint = True
                    tint = node.code.source.split('"')[1].lower().strip()

                elif not found_snow and node.code.source[0:5]=="Snow(":
                    found_snow = True
                    snow_state = int(re.search(r'\((.*?)[,\)]', node.code.source).group(1))

            elif type(node)==renpy.ast.UserStatement:
                if not found_first_line and len(node_list)>0 and "nvl clear" in node.line:
                    found_first_line = True

                elif "play" == node.line[:4] or "stop" == node.line[:4]:
                    tokens = node.line.split(" ")
                    action = tokens.pop(0)
                    channel = tokens.pop(0)
                    final_command = ""

                    if channel not in music:
                        if action=="play":
                            fname = tokens.pop(0)
                            while fname.count('"') < 2:
                                fname += " " + tokens.pop(0)
                            final_command = 'renpy.sound.play({},channel="{}",'.format(fname, channel)
                        else:
                            final_command = 'renpy.sound.stop(channel="{}",'.format(channel)

                        sound_looping = False
                        while len(tokens)>1:
                            param = tokens.pop(0)
                            if param == "loop":
                                final_command += "loop=True,"
                                sound_looping = True
                            elif param == "noloop":
                                final_command += "loop=False,"
                            else:
                                val = tokens.pop(0)
                                final_command += "{}={},".format(param, val)

                        if (channel not in ["music", "glitch"]) and (not sound_looping):
                            music[channel] = None
                        else:
                            music[channel] = final_command[:-1]+")"

            elif type(node)==renpy.ast.Hide:
                if node.imspec[4] == 'master_overlay':
                    key = " ".join(node.imspec[0])
                    if key not in overlay_list:
                        overlay_list[key] = None

                elif not found_bg and not all_characters:
                    name = node.imspec[0][0]
                    if (name in store.sprites):
                        spr = store.sprites[name]
                        if (spr.name in sprite_list and sprite_list[spr.name] is not None):
                            sprite_list[spr.name]['done'] = True
                            continue

                        sprite_list[spr.name] = None

            elif type(node)==renpy.ast.Show or type(node)==renpy.ast.Scene:
                if node.imspec and node.imspec[4] == 'master_overlay':
                    key = " ".join(node.imspec[0])
                    if key not in overlay_list:
                        overlay_list[key] = python_dict()
                        overlay_list[key]['at'] = [eval(x) for x in node.imspec[3]]
                        overlay_list[key]['zorder'] = node.imspec[5]
                        overlay_list[key]['atl'] = node.atl

                elif (all_characters or not found_bg):
                    if not found_bg and node.imspec[0][0] == "bg":
                        found_bg = True
                        bg = " ".join(node.imspec[0])
                    else:
                        if node.imspec is None:
                            continue

                        ## Process sprites
                        size = node.imspec[0][0]
                        if (size not in store.sprites):
                            continue

                        spr = store.sprites[size]
                        if (spr.name in sprite_list) and (sprite_list[spr.name] is None or sprite_list[spr.name]['done']):
                            continue

                        if spr.name not in sprite_list:
                            ## Initialize
                            sprite_list[spr.name] = python_dict()
                            sprite_list[spr.name]['size'] = node.imspec[0][0]
                            sprite_list[spr.name]['at'] = python_list()
                            sprite_list[spr.name]['zorder'] = None
                            sprite_list[spr.name]['atl'] = None
                            sprite_list[spr.name]['done'] = False
                            for group in sprite_attrib_groups:
                                sprite_list[spr.name][group] = ''

                        ## Make sure it's the same size
                        if size != sprite_list[spr.name]['size']:
                            continue

                        ## Update properties
                        for x in node.imspec[0][1:]:
                            for group in sprite_attrib_groups:
                                if x in spr.group_to_attributes[group]:
                                    if sprite_list[spr.name][group] == '':
                                        sprite_list[spr.name][group] = x
                                    break

                        if sprite_list[spr.name]['at'] == python_list():
                            for x in node.imspec[3]:
                                sprite_list[spr.name]['at'].append(eval(x))

                        if sprite_list[spr.name]['zorder'] is None:
                            if node.imspec[5]:
                                sprite_list[spr.name]['zorder'] = node.imspec[5]
                            else:
                                sprite_list[spr.name]['zorder'] = 0

                        if node.atl and sprite_list[spr.name]['atl'] is None:
                            sprite_list[spr.name]['atl'] = node.atl

            if node.name == 'start':
                done = True
            elif all_characters:
                if len(sprite_list)>=10:
                    done = True
            elif found_first_line and found_music and found_bg and found_positions and found_snow:
                done = True

        rv['bg'] = bg
        rv['bgm_credits_name'] = bgm_credits_name
        rv['position_history'] = position_history
        rv['explanation'] = explanation
        rv['music'] = music
        rv['music_vol'] = music_vol
        rv['overlay_list'] = overlay_list
        rv['node_list'] = node_list
        rv['snow'] = snow_state
        rv['sprite_list'] = sprite_list
        rv['sprite_attrib_groups'] = sprite_attrib_groups
        rv['tint'] = tint
        rv['tip_orb'] = tip_orb
        return rv

    class SetScreenVariableCallback(Action, DictEquality):
        def __init__(self, variable, callback):
            self.variable = variable
            self.callback = callback

        def __call__(self):
            SetScreenVariable(self.variable, self.callback())()

    class JumpFromChart(Action, DictEquality):
        def __init__(self, name):
            self.name = name

        def __call__(self):
            found = False
            target_node = None
            last_label = None
            idxs = [
                (renpy.game.script.all_stmts.index(search.start_node), renpy.game.script.all_stmts.index(search.end_node)),
                (renpy.game.script.all_stmts.index(search.start_node_tips), renpy.game.script.all_stmts.index(search.end_node_tips))
                ]

            for (idx_start, idx_end) in idxs:
                if found:
                    break

                for idx in range(idx_start, idx_end):
                    node = renpy.game.script.all_stmts[idx]
                    if type(node)==renpy.ast.Label:
                        last_label = node.name

                    elif type(node)==renpy.ast.Python and "ChartNode" in node.code.source:
                        if self.name == node.code.source.split('"')[1]:
                            target_node = node
                            found = True
                            break

            if target_node:
                if "tip_" in last_label and persistent.tip_visibility[last_label[4:]]==0:
                    renpy.show_screen(
                        "display_message",
                        message="Cannot jump to tip. Unlock it first.")
                    renpy.restart_interaction()

                else:
                    JumpToScriptNode(target_node, confirm=False)()

    class JumpToScriptNode(Action, DictEquality):
        label_lines = None

        def __init__(self, node, confirm=True):
            self.node = node
            self.confirm = confirm
            type(self).GetLabels()

        @classmethod
        def GetLabels(cl):
            if cl.label_lines:
                return

            labels = renpy.get_all_labels()
            lines = python_list()
            for t in labels:
                if (t[0] != "_"):
                    node = renpy.game.script.lookup(t)
                    if "script.rpy" in node.filename:
                        lines.append(node.next.name[2])

            lines.sort()
            cl.label_lines = lines

        def __call__(self):
            if store._in_replay:
                renpy.show_screen(
                    "display_message",
                    message="Jump is disabled during tip segments.")

                renpy.restart_interaction()

            elif self.confirm:
                layout.yesno_screen("Jump to this message?", JumpToScriptNode(self.node, confirm=False))

            elif "tips.rpy" in self.node.filename:
                #renpy.show_screen(
                #    "display_message",
                #    message="Cannot jump to tips. Use the Tip Menu.")
                #renpy.restart_interaction()

                # Get all tip labels and sort them
                tip_titles = python_dict()
                for label in renpy.get_all_labels():
                    if not label.startswith("tip_"):
                        continue

                    if label == "tip_base_link":
                        continue

                    tip_node = renpy.game.script.lookup(label).next
                    idx = GetGlobalIndexFromNode(tip_node)
                    tip_titles[idx] = label[4:]

                tip_titles = OrderedDict(sorted(tip_titles.items()))

                prev_title = tip_titles.values()[0]
                node_idx = GetGlobalIndexFromNode(self.node)
                for idx, title in tip_titles.items():
                    if idx >= node_idx:
                        CallTip(prev_title)
                        break
                    prev_title = title

                return

            else:
                ## Borrowed heavily from RollbackLog.rollback()
                ## Get information about the script before the target node
                details = GetScriptDetails(self.node)

                ## Store the variables
                store.explanation = details['explanation']

                ## Stop all sounds
                renpy.music.stop('sound')
                renpy.music.stop('channel2')
                renpy.music.stop('channel3')
                if 'glitch' not in details['music']:
                    renpy.music.stop('glitch')

                ## Set the music and move it to the game context
                #store.bgm_name = "<Use PlayMusic()>"
                store.bgm_credits_name = details['bgm_credits_name']
                for channel, val in details['music'].items():
                    if channel in ["music", "glitch"]:
                        currently_playing = renpy.music.get_playing(channel) or "----------"

                        fname = val
                        if "PlayMusic" in val:
                            track = re.search(r'\([\'"](.*?)[\'"][\), ]', val).group(1)
                            entry = GetMusicEntry(track)
                            fname = entry.fname_loop

                        if fname in currently_playing:
                            ## Don't cut the audio, just keep going
                            pass
                        else:
                            eval(val)
                    elif val:
                        ## Sound channel
                        eval(val)

                if len(details['music_vol']) == 0:
                    renpy.music.set_volume(1.0, delay=0, channel='music')
                for val in details['music_vol']:
                    eval(val)

                renpy.game.contexts[0].music[0] = renpy.music.get_channel("sound").context
                renpy.game.contexts[0].music['channel2'] = renpy.music.get_channel("channel2").context
                renpy.game.contexts[0].music['channel3'] = renpy.music.get_channel("channel3").context
                renpy.game.contexts[0].music['glitch'] = renpy.music.get_channel("glitch").context
                renpy.game.contexts[0].music[7] = renpy.music.get_channel("music").context

                ## Set the BG and sprites
                renpy.scene()
                renpy.show(details['bg'])

                for key, sprite in details['sprite_list'].items():
                    if sprite is None:
                        continue

                    temp = sprite['size']
                    for group in details['sprite_attrib_groups']:
                        temp += ' '+sprite[group]

                    # Handle any manual position or transforms
                    at_list = sprite['at']
                    if sprite['atl']:
                        at_list.append(renpy.display.transform.ATLTransform(sprite['atl']))

                    renpy.show(temp, at_list=at_list, zorder=sprite['zorder'])

                renpy.game.contexts[0].scene_lists.layers["master"] = renpy.scene_lists().layers["master"]

                ## Set overlays
                renpy.scene(layer='master_overlay')
                for img, overlay in details['overlay_list'].items():
                    if overlay:
                        # Handle any manual position or transforms
                        at_list = overlay['at']
                        if overlay['atl']:
                            at_list.append(renpy.display.transform.ATLTransform(overlay['atl']))

                        renpy.show(img, layer='master_overlay', at_list=at_list, zorder=overlay['zorder'])

                renpy.game.contexts[0].scene_lists.layers["master_overlay"] = renpy.scene_lists().layers["master_overlay"]

                ## Set the scene name
                node_idx = GetGlobalIndexFromNode(details['node_list'][-1])
                for entry in search.scene_titles:
                    if entry.global_index > node_idx:
                        break
                    store.scene_title = entry.what

                ## Set the chapter number
                for c_num, global_idx in enumerate(search.chapter_global_idxs):
                    if global_idx > node_idx:
                        break
                    store.chapter = c_num+1

                ## Set up the nvl list
                nvl_clear()
                if len(details['node_list'])>1:
                    for node in reversed(details['node_list'][1:]):
                        chr = renpy.ast.eval_who(node.who, node.who_fast)
                        chr.push_nvl_list(chr.name, chr.what_prefix + node.what + chr.what_suffix)

                ## Show the tip orb, if any
                if details['tip_orb'] and details['tip_orb'] != -1:
                    TipOrbShow(details['tip_orb'], stop=False)
                else:
                    TipOrbHide()

                ## Evaluate snow
                Snow(details['snow'], fast=True)
                renpy.game.contexts[0].scene_lists.layers["snow_layer"] = renpy.scene_lists().layers["snow_layer"]

                ## Process the sprite tint
                SpriteTint(details['tint'])


                ## Remove existing minimap
                for element in renpy.game.contexts[0].scene_lists.layers["screens"]:
                    if "minimap_proxy" in element.tag:
                        renpy.game.contexts[0].scene_lists.layers["screens"].remove(element)

                ## Update map positions (MUST BE AFTER TIP ORB)
                MapResetPositions()
                for temp in reversed(details['position_history']):
                    eval(temp)
                MinimapHandleVisibility()

                ## Make sure the window management is handled automatically
                store._window_auto = True

                ## Finally, go to the line
                renpy.jump_out_of_context(self.node.name)