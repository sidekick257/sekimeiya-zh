init python:
    sm_entries_old = python_dict()
    sm_entries_new = python_dict()
    sm_entries_preset = python_dict()
    
    sm_selected_name = "atsuki"
    sm_selected_expr = "neutral"
    sm_selected_pose = "1a"
    sm_selected_size = "m"
    sm_selected_pose_modifier = ""
    sm_selected2_pose_modifier = "p"
    sm_selected_effect = "noeffect"
    sm_selected_position = "p23"
    sm_selected_cleanliness = "smoke"
    sm_selected_zorder = 0
    sm_current_label = None
    
    def GetSpriteDetails():
        global sm_entries_old, sm_entries_preset, sm_entries_new, sm_current_label
        sm_entries_old = python_dict()
        sm_entries_preset = python_dict()
        
        current_label = renpy.game.contexts[0].current
        if sm_current_label != current_label:
            ## Clear our updates if we moved in the script
            sm_entries_new = python_dict()
            sm_current_label = current_label
        
        if ("game/script.rpy" in current_label[0]):
            current_node = renpy.game.script.lookup(current_label)
            details = GetScriptDetails(current_node, all_characters=True)
            
            sm_entries_preset = details['sprite_list'].copy()
            for k in sm_entries_preset:
                sm_entries_preset[k]['name'] = sm_entries_preset[k]['size'][:-1]
                sm_entries_preset[k]['at_str'] = 'p11'
                try:
                    sm_entries_preset[k]['zorder'] = int(sm_entries_preset[k]['zorder'])
                except:
                    pass
                
                try:
                    for ref_pos in ['p11', 'p12', 'p22', 'p13', 'p23', 'p33', 'p14', 'p24', 'p34', 'p44', 'p15', 'p25', 'p35', 'p45', 'p55']:
                        loc = eval(ref_pos).atl.loc
                        temp = sm_entries_preset[k]['at'][0]
                        
                        if temp == loc or \
                           (type(temp) == renpy.display.transform.ATLTransform and temp.atl.loc == loc):
                            sm_entries_preset[k]['at_str'] = ref_pos
                            break
                except:
                    pass
            
            """
            'katei': {
                'cleanliness': 'smoke',
                'atl': None,
                'state': '',
                'base': '1a',
                'done': False,
                'at': [<ATL Transform 109bc470 ('game/scripts/setup_sprites.rpy', 389)>],
                'at_str': 'p12'
                'zorder': 2,
                'expression': 'serious',
                'other': '',
                'size': 'kateim',
                'name': 'katei'
                }
            """
        
        for disp in renpy.game.contexts[0].scene_lists.layers["master"]:
            ## Get the current list of displayed sprites
            if disp.tag not in store.sprites:
                continue
            
            name = disp.tag[:-1]
            if name in sm_entries_preset:
                sm_entries_old[name] = sm_entries_preset[name].copy()
        
        ## Split the data into 
        rv = python_dict()
        rv['unchanged'] = python_dict()
        rv['removed'] = python_dict()
        rv['modified'] = python_dict()
        rv['added'] = python_dict()
        rv['remainder'] = python_dict()
        
        for k in sm_entries_new:
            if k in sm_entries_old:
                if sm_entries_new[k] == None:
                    rv['removed'][k] = sm_entries_old[k]
                else:
                    rv['modified'][k] = sm_entries_new[k]
            else:
                rv['added'][k] = sm_entries_new[k]
        
        for k in sm_entries_old:
            if (k not in rv['removed']) and (k not in rv['modified']) and (k not in rv['added']):
                rv['unchanged'][k] = sm_entries_old[k]
        
        for k in sm_entries_preset:
            if (k not in rv['removed']) and (k not in rv['modified']) and (k not in rv['added']) and (k not in rv['unchanged']):
                rv['remainder'][k] = sm_entries_preset[k]
        
        return rv
    
    def SpriteCommandFromSpriteDetails(entry, all=False):
        rv = ""
        rv += entry['size']
        rv += ' ' + entry['base']
        rv += ' ' + entry['expression']
        if entry['other'] != '':
            rv += ' ' + entry['other']
        rv += ' ' + entry['cleanliness']
        rv += ' bright'
        
        if all:
            rv += ' at ' + entry['at_str']
            
            if entry['zorder'] != 0:
                rv += ' zorder ' + str(entry['zorder'])
        return rv
    
    def SpriteDetailsFromSpriteAdder():
        rv = python_dict()
        
        rv['at_str'] = sm_selected_position
        
        rv['base'] = sm_selected_pose
        if sm_selected_name=='shiroya' and (sm_selected_pose in ['1a', '1b']):
            rv['base'] += sm_selected_pose_modifier
        if sm_selected_name=='shiroya2':
            rv['base'] = "1c"
            rv['base'] += sm_selected2_pose_modifier
        
        rv['cleanliness'] = sm_selected_cleanliness
        rv['expression'] = sm_selected_expr
        rv['name'] = sm_selected_name
        rv['size'] = sm_selected_name + sm_selected_size
        
        rv['other'] = ''
        if sm_selected_name=='isla':
            rv['other'] = sm_selected_effect
        
        rv['zorder'] = sm_selected_zorder
        
        #rv['at'] = [<ATL Transform 109bc470 ('game/scripts/setup_sprites.rpy', 389)>]
        #rv['atl'] = None
        #rv['done'] = False
        #rv['state'] = ''
        return rv
    
    def SpriteAdderFromSpriteDetails(entry):
        global sm_selected_name, sm_selected_size, sm_selected_pose
        global sm_selected_pose_modifier, sm_selected2_pose_modifier, sm_selected_effect, sm_selected_expr
        global sm_selected_cleanliness, sm_selected_position, sm_selected_zorder
        
        sm_selected_name = entry['name']
        sm_selected_size = entry['size'][-1]
        sm_selected_pose = entry['base'][0:2]
        if sm_selected_name == 'shiroya' and len(entry['base'])>2:
            sm_selected_pose_modifier = entry['base'][2:]
        if sm_selected_name == 'shiroya2' and len(entry['base'])>2:
            sm_selected2_pose_modifier = entry['base'][2:]
        sm_selected_expr = entry['expression']
        if sm_selected_name == 'isla':
            sm_selected_effect = entry['other']
        sm_selected_cleanliness = entry['cleanliness']
        sm_selected_position = entry['at_str']
        sm_selected_zorder = entry['zorder']
    
    def SpriteMenuPreviewAllCommands():
        for k in store.sprites:
            renpy.hide(k)
        
        entries = python_dict()
        
        for k in sm_entries_new:
            entries[k] = sm_entries_new[k]
        for k in sm_entries_old:
            if k not in entries:
                entries[k] = sm_entries_old[k]
        
        return entries
    
    def SpriteMenuPreviewSingle():
        entry = SpriteDetailsFromSpriteAdder()
        
        ## Show every existing sprite except for the new one
        entries = SpriteMenuPreviewAllCommands()
        for k in entries:
            if k==entry['name']:
                continue
            if entries[k] != None:
                cmd = SpriteCommandFromSpriteDetails(entries[k])
                renpy.show(cmd, at_list=[eval(entries[k]['at_str'])], zorder=entries[k]['zorder'])
        
        ## Show the new sprite
        cmd = SpriteCommandFromSpriteDetails(entry)
        renpy.show(cmd, at_list=[eval(entry['at_str'])], zorder=entry['zorder'])
        
        renpy.show_screen('sprites_preview_single')
    
    def SpriteMenuPreviewAll():
        entries = SpriteMenuPreviewAllCommands()
        
        for k in entries:
            if entries[k] != None:
                cmd = SpriteCommandFromSpriteDetails(entries[k])
                renpy.show(cmd, at_list=[eval(entries[k]['at_str'])], zorder=entries[k]['zorder'])
        
        renpy.show_screen('sprites_preview_all')
    
    def SpriteMenuUpdateCommand():
        entry = SpriteDetailsFromSpriteAdder()
        sprite_name = entry['name']
        sm_entries_new[sprite_name] = entry
    
    def SpriteMenuRevertCommand(sprite_name):
        if sprite_name in sm_entries_new:
            del sm_entries_new[sprite_name]
    
    def SpriteMenuRemoveCommand(sprite_name):
        if sprite_name in sm_entries_old:
            sm_entries_new[sprite_name] = None
        elif sprite_name in sm_entries_new:
            del sm_entries_new[sprite_name]
    
    def SpriteMenuRemoveAll():
        global sm_entries_new
        
        sm_entries_new = python_dict()
        for k in sm_entries_old:
            sm_entries_new[k] = None
    
    script_sprite_line_offset = 0
    def SaveSpriteDetailsToScript(at_bg_change=False, transition=None, tint=None):
        """
        at_bg_change: Add changes at the last bg change
        transition: Add all changes before the current line in a block. Put a transition at the end of the block specified as a string
        """
        global script_sprite_line_offset
        
        entries = GetSpriteDetails()
        start_node = renpy.game.script.lookup(renpy.game.contexts[0].current)
        node_idx = GetGlobalIndexFromNode(start_node)
        node_idx_offset = 0
        
        ## Determine the location to insert lines
        if at_bg_change:
            while True:
                node_idx_offset -= 1
                temp_node = GetNodeFromGlobalIndex(node_idx+node_idx_offset)
                
                if type(temp_node)==renpy.ast.Show and temp_node.imspec[0][0]=='bg':
                    break
                
                if type(temp_node)==renpy.ast.Scene:
                    break
            
            node = GetNodeFromGlobalIndex(node_idx+node_idx_offset+1)
        
        else:
            node = GetNodeFromGlobalIndex(node_idx-1)
        
        fname = node.filename
        line_num = node.linenumber
        
        ## Get the file's contents and absolute location
        f = renpy.file(fname.replace('game/',''))
        contents = f.read().decode("utf-8")
        contents = contents.split("\n")
        path = f.name
        f.close()
        
        ## Create the sprite commands
        cmds = python_list()
        if tint:
            cmds.append('$ SpriteTint("' + tint +'")')
        
        for e_type in ['modified', 'added']:
            for name, details in entries[e_type].items():
                cmd = 'show ' + SpriteCommandFromSpriteDetails(details, all=True)
                cmds.append(cmd)
        
        for name, details in entries['removed'].items():
            cmds.append('hide ' + details['size'])
        
        if transition:
            cmds.append('with ' + transition)
        
        ## Get the correct indentation
        next_line = contents[line_num]
        indent = " "*(len(next_line)-len(next_line.lstrip()))
        
        ## Make gaps in the script that we'll later fill with the correct data
        for cmd in cmds:
            contents.insert(line_num+script_sprite_line_offset-1, indent+cmd)
            script_sprite_line_offset += 1
        
        ## Save the file
        contents = "\n".join([y.replace('\r','') for y in contents])
        f = open(path, "w")
        f.write(contents.encode("utf-8"))
        f.close()

    def SpriteDetailsBackjump():
        ## Jump to the last say before an nvl clear
        start_node = renpy.game.script.lookup(renpy.game.contexts[0].current)
        node_idx = GetGlobalIndexFromNode(start_node)
        node_idx_offset = 0
        
        found_clear = False
        
        while True:
            node_idx_offset -= 1
            node = GetNodeFromGlobalIndex(node_idx+node_idx_offset)
            
            if type(node)==renpy.ast.UserStatement and "nvl clear" in node.line:
                found_clear = True
            
            if found_clear and type(node)==renpy.ast.Say:
                break
        
        JumpToScriptNode(node, confirm=False)()

screen sprites_menu:
    predict False ## Avoid predicting this screen
    
    tag menu
    style_prefix "sprite_menu"
    
    default sprite_tint = None
    
    python:
        sm_entries = GetSpriteDetails()
    
    frame:
        background '#0008'
        xsize 1.0
        ysize 1.0
        
        vbox:
            style_prefix "sprite_menu2"
            spacing 5
            xalign 0.5
            yalign 0.1
            
            hbox:
                spacing 5
                textbutton "Done - Last BG change" action [Return(), Function(SaveSpriteDetailsToScript, at_bg_change=True, tint=sprite_tint)]
                textbutton "Done - dissolve" action [Return(), Function(SaveSpriteDetailsToScript, transition="dissolve", tint=sprite_tint)]
                textbutton "Done - fastdissolve" action [Return(), Function(SaveSpriteDetailsToScript, transition="fastdissolve", tint=sprite_tint)]
                null width 100
                textbutton "Backjump - Last nvl clear" action [Function(SpriteDetailsBackjump)]
                
            hbox:
                spacing 5
                ## For Add, select the first available sprite
                if len(sm_entries['remainder'])>0:
                    textbutton "Add" action [SetVariable("sm_selected_name", sorted(sm_entries['remainder'].keys())[0]), ShowMenu('sprites_adder')]
                else:
                    textbutton "Cannot add, reopen menu"
                textbutton "Preview" action Function(SpriteMenuPreviewAll)
                textbutton "Delete All" action Function(SpriteMenuRemoveAll)
            
            hbox:
                spacing 5
                ## For Add, select the first available sprite
                textbutton "Unchanged Tint" action SetScreenVariable("sprite_tint", None)
                textbutton "Normal" action SetScreenVariable("sprite_tint", "normal")
                textbutton "Dark" action SetScreenVariable("sprite_tint", "dark")
                textbutton "Sunset" action SetScreenVariable("sprite_tint", "sunset")
                textbutton "Green" action SetScreenVariable("sprite_tint", "green")
        
        vbox:
            xalign 0.5
            ypos 0.55
            spacing 5
            
            # Green = Added, Yellow = Modified, Red = Removed, Transparent = Unchanged
            for e_type, e_color in [('unchanged', '#0008'), ('removed', '#f008'), ('modified', '#ff08'), ('added', '#0f08')]:
                for k in sorted(sm_entries[e_type]):
                        hbox:
                            spacing 5
                            button:
                                text SpriteCommandFromSpriteDetails(sm_entries[e_type][k], all=True):
                                    hover_color '#888'
                                    idle_color '#ddd'
                                    size 16
                                background e_color
                                action [Function(SpriteAdderFromSpriteDetails, sm_entries[e_type][k]), ShowMenu('sprites_adder', k)]
                                xsize 500
                            
                            textbutton "Delete" xsize 100 action Function(SpriteMenuRemoveCommand, k)
                            textbutton "Revert" xsize 100 action Function(SpriteMenuRevertCommand, k)
    
    use navigation

screen sprites_adder(locked_char=None):
    predict False ## Avoid predicting this screen
    
    tag menu
    style_prefix "sprite_inserter"
    
    key "game_menu" action ShowMenu('sprites_menu')
    
    default grid_width = 8
    default grid_height = 3
    default sprite_expr_crop = {
        "akaro": (275, 140, 120, 120),
        "atsuki": (160, 140, 120, 120),
        "darfee": (230, 125, 120, 120),
        "erina": (179, 150, 120, 120),
        "isla": (175, 320, 120, 120),
        "katei": (170, 160, 120, 120),
        "lei": (180, 150, 120, 120),
        "miiya": (180, 170, 120, 120),
        "naomi": (160, 200, 120, 120),
        "sai": (190, 170, 120, 120),
        "sai2": (190, 170, 120, 120),
        "shiroya": (221, 185, 120, 120),
        "shiroya2": (221, 185, 120, 120),
        "vaisude": (170, 170, 120, 120),
        }
    default sprite_pose_crop = {
        "akaro": (0, 32, 344, 608),
        "atsuki": (22, 59, 239, 541),
        "darfee": (0, 32, 344, 608),
        "erina": (44, 33, 213, 567),
        "isla": (14, 157, 272, 442),
        "katei": (45, 47, 249, 553),
        "lei": (0, 32, 309, 568),
        "miiya": (51, 32, 209, 568),
        "naomi": (37, 55, 230, 545),
        "sai": (9, 35, 260, 565),
        "sai2": (9, 35, 260, 565),
        "shiroya": (0, 51, 294, 548),
        "shiroya2": (0, 51, 294, 548),
        "vaisude": (38, 46, 236, 367),
        }
    
    frame:
        background '#0008'
        
        vbox:
            xalign 1.0
            frame:
                background "#0009"
                xalign 1.0
                yalign 0.0
                
                hbox:
                    vbox:
                        xsize 80
                        if locked_char:
                            textbutton locked_char.capitalize() xfill True:
                                action SetVariable("sm_selected_name", locked_char)
                        else:
                            ## Only show characters that aren't already added
                            for name in ['akaro', 'atsuki', 'darfee', 'erina', 'isla', 'katei', 'lei', 'miiya', 'naomi', 'sai', 'sai2', 'shiroya', 'shiroya2', 'vaisude']:
                                if (name not in sm_entries_old) and (name not in sm_entries_new):
                                    textbutton name.capitalize() xfill True:
                                        if name in sm_entries_preset:
                                            action [Function(SpriteAdderFromSpriteDetails, sm_entries_preset[name]), SetVariable("sm_selected_name", name)]
                                        else:
                                            action [SetVariable("sm_selected_name", name)]
                    null width 5
                    add Solid('#fff8', xsize=1, ysize=270)
                    null width 5
                    
                    vbox:
                        xsize 80
                        textbutton "Small" action SetVariable("sm_selected_size", "s") xfill True
                        textbutton "Medium" action SetVariable("sm_selected_size", "m") xfill True
                        textbutton "Large" action SetVariable("sm_selected_size", "l") xfill True
                        
                        null height 5
                        add Solid('#fff8', xsize=80, ysize=1)
                        null height 5
                        
                        textbutton "Clean" action SetVariable("sm_selected_cleanliness", "clean") xfill True
                        textbutton "Smoke" action SetVariable("sm_selected_cleanliness", "smoke") xfill True
                        if sm_selected_name == "erina":
                            textbutton "Blood" action SetVariable("sm_selected_cleanliness", "blood") xfill True
                        if sm_selected_name == "atsuki":
                            textbutton "Ascended" action SetVariable("sm_selected_cleanliness", "smoke2") xfill True
                        
                        null height 5
                        add Solid('#fff8', xsize=80, ysize=1)
                        null height 5
                        
                        if sm_selected_name == "shiroya":
                            text "Pendant"
                            textbutton "Off" action SetVariable("sm_selected_pose_modifier", "") xfill True
                            textbutton "Under" action SetVariable("sm_selected_pose_modifier", "p1") xfill True
                            textbutton "Over" action SetVariable("sm_selected_pose_modifier", "p2") xfill True
                        elif sm_selected_name == "shiroya2":
                            text "Pendant"
                            textbutton "Off" action SetVariable("sm_selected2_pose_modifier", "") xfill True
                            textbutton "On" action SetVariable("sm_selected2_pose_modifier", "p") xfill True
                        elif sm_selected_name == "isla":
                            text "Effect"
                            textbutton "None" action SetVariable("sm_selected_effect", "noeffect") xfill True
                            textbutton "Glasses" action SetVariable("sm_selected_effect", "glasses") xfill True
                            textbutton "Sparkle" action SetVariable("sm_selected_effect", "sparkle") xfill True
                            textbutton "Question" action SetVariable("sm_selected_effect", "question") xfill True
                    
                    null width 5
                    add Solid('#fff8', xsize=1, ysize=270)
                    null width 5
                    
                    vbox:
                        spacing 10
                        xsize 80
                        
                        null height 50
                        textbutton "Preview" xfill True action Function(SpriteMenuPreviewSingle) # Show this real quick
                        textbutton "Accept" xfill True action [Function(SpriteMenuUpdateCommand), ShowMenu('sprites_menu')]
                        textbutton "Cancel" xfill True action ShowMenu('sprites_menu')
            
            null height 5
            add Solid('#fff8', xsize=240, ysize=1)
            null height 5
            
            default pos_width = 300
            frame:
                background "#0009"
                style_prefix "sprite_inserter_position"
                xalign 1.0
                yalign 0.5
                padding (0,0,0,0)
                hbox:
                    vbox:
                        xsize 50
                        text "zorder"
                        textbutton "0" action SetVariable("sm_selected_zorder", 0) xfill True
                        textbutton "1" action SetVariable("sm_selected_zorder", 1) xfill True
                        textbutton "2" action SetVariable("sm_selected_zorder", 2) xfill True
                    
                    null width 5
                    add Solid('#fff8', xsize=1, ysize=100)
                    null width 5
                    
                    vbox:
                        hbox:
                            textbutton "p11" action SetVariable("sm_selected_position", "p11") xsize pos_width
                        hbox:
                            textbutton "p12" action SetVariable("sm_selected_position", "p12") xsize pos_width/2
                            textbutton "p22" action SetVariable("sm_selected_position", "p22") xsize pos_width/2
                        hbox:
                            xsize pos_width
                            textbutton "p13" action SetVariable("sm_selected_position", "p13") xsize pos_width/3
                            textbutton "p23" action SetVariable("sm_selected_position", "p23") xsize pos_width/3
                            textbutton "p33" action SetVariable("sm_selected_position", "p33") xsize pos_width/3
                        hbox:
                            xsize pos_width
                            textbutton "p14" action SetVariable("sm_selected_position", "p14") xsize pos_width/4
                            textbutton "p24" action SetVariable("sm_selected_position", "p24") xsize pos_width/4
                            textbutton "p34" action SetVariable("sm_selected_position", "p34") xsize pos_width/4
                            textbutton "p44" action SetVariable("sm_selected_position", "p44") xsize pos_width/4
                        hbox:
                            xsize pos_width
                            textbutton "p15" action SetVariable("sm_selected_position", "p15") xsize pos_width/5
                            textbutton "p25" action SetVariable("sm_selected_position", "p25") xsize pos_width/5
                            textbutton "p35" action SetVariable("sm_selected_position", "p35") xsize pos_width/5
                            textbutton "p45" action SetVariable("sm_selected_position", "p45") xsize pos_width/5
                            textbutton "p55" action SetVariable("sm_selected_position", "p55") xsize pos_width/5

        if sm_selected_name+"m" in store.sprites:
            vbox:
                hbox:
                    python:
                        expressions = python_list()
                        for expr in sorted(store.sprites[sm_selected_name+"m"].group_to_attributes["expression"]):
                            if "dark_" not in expr:
                                expressions.append(expr)
                    
                    vbox:
                        for row in range(grid_height):
                            hbox:
                                spacing 1
                                for col in range(grid_width):
                                    python:
                                        idx = col + grid_width*row
                                        expr = expressions[idx] if idx<len(expressions) else None
                                    
                                    if expr:
                                        button:
                                            padding (0,0,0,0)
                                            action SetVariable("sm_selected_expr", expr)
                                            vbox:
                                                add Crop(sprite_expr_crop[sm_selected_name], Flatten("{}m {} bright {}".format(sm_selected_name, expr, sm_selected_cleanliness)))
                                                text expr xalign 0.5
                
                hbox:
                    spacing 2
                    python:
                        poses = python_list()
                        for pose in sorted(store.sprites[sm_selected_name+"s"].group_to_attributes["base"]):
                            if len(pose)==2:
                                poses.append(pose)
                    
                    for pose in poses:
                        button:
                            action SetVariable("sm_selected_pose", pose)
                            vbox:
                                add Transform(Crop(sprite_pose_crop[sm_selected_name], Flatten("{}s {} bright {}".format(sm_selected_name, pose, sm_selected_cleanliness))), zoom=0.5)
                                text pose xalign 0.5

screen sprites_preview_single():
    predict False ## Avoid predicting this screen
    tag menu
    for k in ["game_menu", "dismiss"]:
        key k action [ShowMenu('sprites_adder')]

screen sprites_preview_all():
    predict False ## Avoid predicting this screen
    tag menu
    for k in ["game_menu", "dismiss"]:
        key k action [ShowMenu('sprites_menu')]

style sprite_menu_button:
    background None
    activate_sound None
    hover_sound None
    padding (10,10,10,10)

style sprite_menu_button_text:
    xalign 0.5
    yalign 0.5
    text_align 0.5
    hover_color '#888'
    idle_color '#ddd'
    selected_color '#f88'

style sprite_menu2_button is sprite_menu_button:
    xfill True
    background '#00f8'
    xsize 100
    ysize 100

style sprite_menu2_button_text is sprite_menu_button_text

style sprite_inserter_button:
    background None
    selected_background "#ff08"
    hover_background "#f008"
    activate_sound None
    hover_sound None

style sprite_inserter_text:
    size 14
    outlines [(2, "#0004", 0, 0), (1, "#0009", 1, 1), (1, "#000", 0, 0)]

style sprite_inserter_position_button is sprite_inserter_button:
    xfill True

style sprite_inserter_position_button_text:
    xalign 0.5
