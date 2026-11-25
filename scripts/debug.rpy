init -20 python:
    def dumpVar(obj, under=False):
        import types
        import inspect

        s = "\n{}, id={}\n".format(type(obj), hex(id(obj)))
        methods = ""
        variables = ""

        for attr in dir(obj):
            try:
                if not under and attr[0] == "_":
                    continue

                var = getattr(obj, attr)
                if type(var)==types.MethodType:
                    args = ', '.join(inspect.getargspec(var).args)
                    methods += "obj.%s(%s)\n" % (attr, args)
                else:
                    variables += "obj.%s = %r\n" % (attr, var)
            except Exception as e:
                s += "Exception ({}): {}\n".format(attr, e)

        s += """---------------
----Methods----
---------------
{}-----------------
----Variables----
-----------------
{}\n""".format(methods, variables)
        return s
            
    import time
    try:    logFile = renpy.os.path.join( config.basedir, 'logFile.txt' )
    except: logFile = None

    def log(*args):
        if not config.developer:
            return

        msg = python_list()
        for arg in args:
            if type(arg) in [NoneType, str, unicode, int, long, float, bool, list, python_list, tuple, dict, python_dict, set, python_set]:
                msg.append("{}".format(arg))
            else:
                msg.append(dumpVar(arg, under=False))
        msg = ", ".join(msg)
    
        if not logFile is None:
            FH = open( logFile, "a" )
            FH.write( "[{}] {}\n".format( time.strftime("%Y-%m-%d %H:%M:%S"), msg ) )
            FH.close()

    def getLabels():
        labels = renpy.get_all_labels()
        out = python_list()
        for t in labels:
            if (t[0] != "_") and not t.startswith("debug_") and not t.startswith("tip_"):
                out.append(t)
                
        out.sort()
        return ", ".join(out) #[(x, x) for x in out]
    
    
    import cProfile, pstats
    profiler = None
    
    def startProfiling():
        global profiler
        profiler = cProfile.Profile()
        profiler.enable()
    
    def stopProfiling(sort_name='tottime'):
        global profiler
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats(sort_name)
        stats.print_stats(20)
        stats.print_callees(1.0)
        #stats.print_callers(20)

    def UnlockAllMessages():
        renpy.game.persistent._seen_ever.clear()
        idxs = [
                (renpy.game.script.all_stmts.index(search.start_node), renpy.game.script.all_stmts.index(search.end_node)),
                (renpy.game.script.all_stmts.index(search.start_node_tips), renpy.game.script.all_stmts.index(search.end_node_tips))
                ]

        for (idx_start, idx_end) in idxs:
            for idx in range(idx_start, idx_end):
                node = renpy.game.script.all_stmts[idx]
                
                if type(node.name) == tuple and type(node):
                    renpy.game.persistent._seen_ever[node.name] = True

    def ProcessSpriteBlocks():
        ## Control which sprites brighten and darken in BeginSpriteChange() blocks
        ##  Once this runs, delete all lines marked with "#delete555"
        ##
        ## Script must already be wrapped with $ BeginSpriteChange() and $ EndSpriteChange()
        ## Easy way to do that is to run the following (assuming no begin sprites at all)
        ##
        ### . matches newline
        ## Find:
        ## ^([ ]+)(show )(akaro|atsuki|arfee|erina|isla|katei|lei|miiya|naomi|sai|shiroya|vaisude)(.*?with.*?)\n
        ## 
        ## Replace:
        ## \1$ BeginSpriteChange\(\)\n\1\2\3\4\n\1$ EndSpriteChange\(\)\n
        import re
        UnlockAllMessages()

        idxs = [
            (renpy.game.script.all_stmts.index(search.start_node), renpy.game.script.all_stmts.index(search.end_node)),
            (renpy.game.script.all_stmts.index(search.start_node_tips), renpy.game.script.all_stmts.index(search.end_node_tips))
            ]

        for (idx_start, idx_end) in idxs:
            ## Get the file's contents and absolute location
            fname = renpy.game.script.all_stmts[idx_start].filename

            f = renpy.file(fname.replace('game/',''))
            contents = f.readlines()
            path = f.name
            f.close()

            contents = [y.replace('\r','') for y in contents]

            ## Process data
            cleared = True
            found_sprites = python_dict()
            block_start_linenumber = 0
            hit_dialogue = False
            delete_begin = 0
            delete_end = 0
            for idx in range(idx_start, idx_end):
                try:
                    node = renpy.game.script.all_stmts[idx]
                    linenumber = node.linenumber - 1
                    
                    if type(node) == renpy.ast.UserStatement and node.line == "nvl clear":
                        cleared = True
                        found_sprites.clear()
                        
                        if block_start_linenumber > 0:
                            contents[block_start_linenumber] = contents[block_start_linenumber][:-1] + "#delete555\n"
                            delete_begin += 1

                    elif type(node) == renpy.ast.Python and "BeginSpriteChange" in node.code.source:
                        found_sprites.clear()
                        if cleared:
                            ## Mark this as a node to delete
                            contents[linenumber] = contents[linenumber][:-1] + "#delete555\n"
                            delete_begin += 1
                        else:
                            block_start_linenumber = linenumber
                            hit_dialogue = False

                    elif type(node) == renpy.ast.Python and "EndSpriteChange" in node.code.source:
                        if cleared:
                            ## Mark this as a node to delete
                            contents[linenumber] = contents[linenumber][:-1] + "#delete555\n"
                            delete_end += 1

                    elif not hit_dialogue and type(node) == type(node)==renpy.ast.Show:
                        if node.imspec is None:
                            continue

                        if node.imspec[4] == 'master_overlay' or node.imspec[0][0] == "bg":
                            continue

                        ## Process sprites
                        spr_name = node.imspec[0][0]
                        if (spr_name not in store.sprites):
                            continue

                        found_sprites[spr_name[:-1]] = linenumber


                    elif type(node) == renpy.ast.Say:
                        if not cleared and not hit_dialogue:
                            if node.who in ['i', 'n', 'nm', 'c']:
                                ## Add darken_all=False to BeginSpriteChange
                                contents[block_start_linenumber] = contents[block_start_linenumber][:-2] + "darken_all=False" + contents[block_start_linenumber][-2:]
                            else:
                                ## Add bright to the detected sprite
                                speaker = renpy.ast.eval_who(node.who, True).name.name.lower()
                                if speaker in found_sprites:
                                    spr_linenumber = found_sprites[speaker]

                                split_line = contents[spr_linenumber].split()

                                if 'dark' in split_line:
                                    print(spr_linenumber+1, 'dark conflict - ', contents[spr_linenumber][:-1])
                                elif 'bright' in split_line:
                                    pass
                                    #print(spr_linenumber+1, 'redundant bright - ', contents[spr_linenumber][:-1])
                                else:
                                    contents[spr_linenumber] = re.sub(r'([  ]+show ..*?)( at|\n)', r'\1 bright\2', contents[spr_linenumber])
                        
                        found_sprites.clear()
                        cleared = False
                        hit_dialogue = True
                        block_start_linenumber = 0
                except Exception as e:
                    raise Exception(e.message + "\n\nIdx: {} Node: {} Line: {}".format(idx, node, linenumber))

            print(delete_begin, delete_end)

            ## Write data
            contents = "".join([y.replace('\r','') for y in contents])
            f = open(path, "w")
            f.write(contents)
            f.close()

    def CheckSpriteBlocks():
        idxs = [
            (renpy.game.script.all_stmts.index(search.start_node), renpy.game.script.all_stmts.index(search.end_node)),
            (renpy.game.script.all_stmts.index(search.start_node_tips), renpy.game.script.all_stmts.index(search.end_node_tips))
            ]

        for (idx_start, idx_end) in idxs:
            ## Get the file's contents and absolute location
            fname = renpy.game.script.all_stmts[idx_start].filename

            f = renpy.file(fname.replace('game/',''))
            contents = f.readlines()
            path = f.name
            f.close()

            contents = [y.replace('\r','') for y in contents]

            ## Process data
            began = False
            map_line = 0
            map_count = 0
            found_map = False
            bg_line = 0
            found_bg = False
            for idx in range(idx_start, idx_end):
                try:
                    node = renpy.game.script.all_stmts[idx]
                    linenumber = node.linenumber
                    
                    if type(node) == renpy.ast.Python and "BeginSpriteChange" in node.code.source:
                        if began:
                            print(linenumber, 'double BeginSpriteChange')
                        began = True

                    if type(node) == renpy.ast.Say and began:
                        print(linenumber, 'BeginSpriteChange contains say statements')

                    if type(node) == renpy.ast.Python and "EndSpriteChange" in node.code.source:
                        if not began:
                            print(linenumber, 'double EndSpriteChange')
                        began = False

                    ## For good measure, check the maps
                    if type(node) == renpy.ast.Python and "MapSetPosition" in node.code.source:
                        map_line = linenumber
                        found_map = True

                    if type(node) == renpy.ast.Say and found_map:
                        print(map_line + map_count*2, 'Map needs fade')
                        map_count += 1
                        found_map = False

                    ## Detect BG discontinuities
                    if type(node) == type(node)==renpy.ast.Show:
                        if node.imspec is None:
                            continue

                        if node.imspec[0][0] == "bg":
                            found_bg = True

                    if type(node) == renpy.ast.Say and found_bg:
                        print(linenumber, 'Teleport')
                        found_bg = False

                    if type(node) == renpy.ast.With:
                        found_map = False
                        found_bg = False

                except Exception as e:
                    raise Exception(e.message + "\n\nIdx: {} Node: {} Line: {}".format(idx, node, linenumber))

            ## For good measure, check the maps
            


label debug:
    menu (spacing=1):
        "Jump to label":
            $ narrator(getLabels() + "{fast}", interact=False)
            $ text = renpy.input("")
            $ if renpy.has_label(text): renpy.jump(text)
            jump debug
        "BG":
            label debug_bg:
            menu (spacing=1):
                "Bedroom":
                    show bg bedroomday3
                "Entrance":
                    show bg entrance1
                "Park Bench":
                    show bg snow1b
                "Tower (Night)":
                    show bg towernight
                "Return":
                    jump debug  
            jump debug_bg
        "Inputs":
            label debug_inputs:
            menu (spacing=1):
                "Character Select":
                    call character_select("Who died in the cabinet?", show_timeline=True) from _call_character_select
                    $ i("Selected: "+ c5answer)
                    nvl clear
                "Map Select 1":
                    call map_select("On the second floor, where was the Future Sekimeiya when the world switch occurred?", number=1) from _call_map_select
                    $ i("Selected: "+ c5answer)
                    nvl clear
                "Map Select 2":
                    call map_select("On the second floor, where was the Future Sekimeiya when the world switch occurred?", number=2) from _call_map_select_1
                    $ i("Selected: "+ c5answer)
                    nvl clear
                "Map Select 3":
                    call map_select("On the second floor, where was the Future Sekimeiya when the world switch occurred?", number=3) from _call_map_select_2
                    $ i("Selected: "+ c5answer)
                    nvl clear
                "Map Select 4":
                    call map_select("On the second floor, where was the Future Sekimeiya when the world switch occurred?", number=4) from _call_map_select_3
                    $ i("Selected: "+ c5answer)
                    nvl clear
                "Return":
                    jump debug
            jump debug_inputs
        "Music":
            label debug_music:
            menu (spacing=1):
                "Trinity Project":
                    $ PlayMusic("trinityproject")
                "Twice as dead":
                    $ PlayMusic("twiceasdead")
                "Return":
                    jump debug  
            jump debug_music
        "Snow":
            jump debug_effects_snow
        "Sprites":
            jump debug_sprites
        "Text":
            menu (spacing=1):
                "Scenario":
                    jump debug_text
                "Speaker Colors":
                    jump debug_speaker
                "Explanation":
                    jump debug_explanation
                "Return":
                    jump debug
        "Tips":
            jump debug_tips
        "Unlock":
            jump debug_unlock
        "Process all sprite blocks":
            $ ProcessSpriteBlocks()
            i "Processed all"
            jump debug
        "Check sprite blocks":
            $ CheckSpriteBlocks()
            i "Checked"
            jump debug
        #"Clear Persistent":
        #    $ renpy.game.persistent._clear()
        #    $ renpy.game.persistent._seen_ever = python_dict()
        #    $ persistent._clear()
        #    i "Done"
        #    jump debug

label debug_unlock:
    menu (spacing=1):
        "Unlock All Tips (1)":
            python:
                for t in tip_list:
                    persistent.tip_visibility[t] = 1
            i "Unlocked all tips (1)"
        "Unlock All Tips (2)":
            $ UnlockAllTips(2)
            i "Unlocked all tips (2)"
        "Unlock All Notes":
            $ UnlockAllNotes()
            i "Unlocked all notes"
        "Unlock Map":
            python:
                for temp in range(9):
                    UnlockMap(str(temp)+"b")
            i "Unlocked map"
        "Unlock Messages":
            $ UnlockAllMessages()
            i "Unlocked all messages"
        "Return":
            jump debug
    jump debug_unlock

label debug_effects_snow:
    menu (spacing=1):
        "0: No snow":
            $ Snow(0)
        "1: Light Snow":
            $ Snow(1)
        "2: Heavy Snow":
            $ Snow(2)
        "3: Blizzard":
            $ Snow(3)
        "1 fast: Light Snow":
            $ Snow(1, fast=True)
        "2 fast: Heavy Snow":
            $ Snow(2, fast=True)
        "3 fast: Blizzard":
            $ Snow(3, fast=True)
        "Return":
            jump debug
    jump debug_effects_snow

label debug_speaker:
    scene bg entrance2
    nvl clear
    c2a "Atsuki. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    ak "Akaro{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    aki "Akira{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    il "Isla{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    k "Katei{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    m2 "Miiya{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    s "Shiroya{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    sa "Sanae{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    sai "Sai{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    ns "Other{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    d "Darfee{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    v "Vaisude{nw}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    su "Suripo. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    nvl clear
    gan "Gan. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    ta "Atase. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    ido "Ido. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    kr "Jiro. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    lei "Lei. Lorem ipsum dolor sit amet, consectetur adipiscing elit.{nw}"
    q "Unknown. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    jump debug
    

init python:
    pass
    #config.image_cache_size_mb = 500 # default is 300 mb
    #config.predict_statements = 50 # Look X statements ahead to predict images. default is 10
    
    ## Predict all sprites ahead of time
    #renpy.start_predict("images/sprites/*/small/*.*")
    #renpy.start_predict("images/sprites/*/medium/*.*")
    #renpy.start_predict("images/sprites/*/large/*.*")
    
    #renpy.start_predict("images/bg entrance*.*")
    #renpy.start_predict("images/bg hallway*.*")
    #renpy.start_predict("images/bg office*.*")
    #renpy.start_predict("images/bg security*.*")
    #renpy.start_predict("images/bg seki*.*")
    #renpy.start_predict("images/bg attic*.*")

label debug_text:
    scene bg entrance2
    nvl clear
    i "Here she comes."
    
    show shiroyal 1ap1 neutral at p25
    s "Shiroya"
    i "Narrator"
    a "Narrator (Spoken)"
    
    show miiyal 3b smile at p45
    m2 "Miiya"
    a "Narrator (Spoken)"
    show shiroyal angry at p25
    
    s "Shiroya"
    i "Narrator"
    
    hide shiroyal
    i "Narrator"

    nvl clear
    scene bg ina with dissolve
    sai "Hey!"
    if not gui.preference("colored_text") and not gui.preference("colored_speaker"):
        i "Sai sounded upset."
    i "The previous message can only be seen if colored names/text is off"
    
    scene bg bedroomday1
    i "Some more"
    i "{i}Some italics test to see if it actually works!{/i}"
    nvl clear
    i "Overflow text\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n."
    jump debug

label debug_explanation:
    scene bg entrance2
    nvl clear
    $ explanation = True
    i "Here she comes."
    i "A bit more text to play with to really see if it respects what I want."
    s "Shiroya"
    i "Narrator"
    a "Narrator (Spoken)"
    
    nvl clear
    $ explanation = False
    jump debug

label debug_tips:
    nvl clear
    show shiroyal at p15
    show miiyal at p55
    $ UnlockTip("dead")
    s "Changing the speaker. {tip=dead}Tip 1{/tip} and {tip=note}Tip 2{/tip}"
    i "More text"
    i "Even more text"
    nvl clear
    
    #$ UnlockTip("Tanya")
    $ TipOrbShow("Tanya")
    i "And here is a tip orb"
    $ TipOrbHide()
    nvl clear
    
    i "Some filler between the two orbs"
    i "Some filler between the two orbs"
    i "Some filler between the two orbs"
    
    $ TipOrbShow("bootstrap")
    i "There's an orb here but it doesn't appear on the first playthrough."
    i "Try skipping through it next time you play. It'll force you to stop."
    $ TipOrbHide()
    $ UnlockAllTips(1)
    
    jump debug

label debug_sprites:
    python:
        debug_sprite_character = "atsuki"
        debug_sprite_size = "m"
        debug_sprite_base = "1a"
        debug_sprite_pos = p35
    
label debug_sprites2:
    $ debug_sprite = debug_sprite_character+debug_sprite_size
    
    scene bg entrance1
    $ renpy.show(debug_sprite + " " + debug_sprite_base, at_list=[debug_sprite_pos])
    
    menu (spacing=1):
        "Character":
            label debug_sprites_character:
            menu (spacing=1):
                "Akaro":
                    $ debug_sprite_character = "akaro"
                    $ debug_sprite_base = "1a"
                "Atsuki":
                    $ debug_sprite_character = "atsuki"
                    $ debug_sprite_base = "1a"
                "Darfee":
                    $ debug_sprite_character = "darfee"
                    $ debug_sprite_base = "1a"
                    $ debug_sprite_size = "l"
                "Erina":
                    $ debug_sprite_character = "erina"
                    $ debug_sprite_base = "1a"
                "Isla":
                    $ debug_sprite_character = "isla"
                    $ debug_sprite_base = "1a"
                "Katei":
                    $ debug_sprite_character = "katei"
                    $ debug_sprite_base = "1a"
                "Miiya":
                    $ debug_sprite_character = "miiya"
                    $ debug_sprite_base = "1a"
                "Naomi":
                    $ debug_sprite_character = "naomi"
                    $ debug_sprite_base = "1a"
                "Sai":
                    $ debug_sprite_character = "sai"
                    $ debug_sprite_base = "1a"
                "Shiroya":
                    $ debug_sprite_character = "shiroya"
                    $ debug_sprite_base = "1a"
                "Vaisude":
                    $ debug_sprite_character = "vaisude"
                    $ debug_sprite_base = "1a"
                    $ debug_sprite_size = "l"
                "Return":
                    jump debug_sprites2
            
            scene bg entrance1
            $ renpy.show(debug_sprite_character+debug_sprite_size + " " + debug_sprite_base, at_list=[debug_sprite_pos])
            jump debug_sprites_character
        "Effects" if len(store.sprites[debug_sprite].group_to_attributes["other"])>0:
            python:
                rv = python_list()
                for expr in sorted(store.sprites[debug_sprite].group_to_attributes["other"]):
                    rv.append((expr, expr))
                debug_sprite_base = renpy.display_menu(rv)
            jump debug_sprites2
        "Expressions":
            nvl clear
            python:
                for idx, expr in enumerate(sorted(store.sprites[debug_sprite].group_to_attributes["expression"])):
                    if idx%15==0:
                        nvl_clear()
                    if "dark_" in expr:
                        continue
                    renpy.show(debug_sprite + " " + expr, at_list=[debug_sprite_pos])
                    #renpy.with_statement(fastdissolve)
                    i(expr)
            jump debug_sprites2
        "Pose / Base":
            python:
                rv = python_list()
                for expr in sorted(store.sprites[debug_sprite].group_to_attributes["base"]):
                    if "dark_" in expr:
                        continue
                    rv.append((expr, expr))
                debug_sprite_base = renpy.display_menu(rv)
            jump debug_sprites2
        "Position":
            label debug_sprites_position:
            menu (spacing=1):
                "pos15":
                    $ debug_sprite_pos = p15
                "pos25":
                    $ debug_sprite_pos = p25
                "pos35":
                    $ debug_sprite_pos = p35
                "pos45":
                    $ debug_sprite_pos = p45
                "pos55":
                    $ debug_sprite_pos = p55
                "Return":
                    jump debug_sprites2
            
            $ renpy.show(debug_sprite + " " + debug_sprite_base, at_list=[debug_sprite_pos])
            jump debug_sprites_position
        "Size":
            label debug_sprites_size:
            menu (spacing=1):
                "Small":
                    $ debug_sprite_size = "s"
                "Medium":
                    $ debug_sprite_size = "m"
                "Large":
                    $ debug_sprite_size = "l"
                "Return":
                    jump debug_sprites2
            
            scene bg entrance1
            $ renpy.show(debug_sprite_character+debug_sprite_size + " " + debug_sprite_base, at_list=[debug_sprite_pos])
            jump debug_sprites_size
        "Tint":
            label debug_sprites_tint:
            menu (spacing=1):
                "Normal":
                    $ SpriteTint("normal")
                    jump debug_sprites_tint
                "Sunset / Dawn / Orange":
                    $ SpriteTint("sunset")
                    jump debug_sprites_tint
                "Dark / Night / Evening":
                    $ SpriteTint("dark")
                    jump debug_sprites_tint
                "Green":
                    $ SpriteTint("green")
                    jump debug_sprites_tint
                "Return":
                    jump debug_sprites2
            jump debug_sprites_tint
        "Test - Multiple Sprites":
            label debug_sprites_many:
            menu (spacing=1):
                "Small":
                    $ debug_sprite_size = "s"
                "Medium":
                    $ debug_sprite_size = "m"
                "Large":
                    $ debug_sprite_size = "l"
                "2a":
                    scene bg entrance1
                    $ renpy.show("atsuki"+debug_sprite_size, at_list=[p12])
                    $ renpy.show("sai"+debug_sprite_size, at_list=[p22])
                "2b":
                    scene bg entrance1
                    $ renpy.show("erina"+debug_sprite_size, at_list=[p12])
                    $ renpy.show("shiroya"+debug_sprite_size, at_list=[p22])
                "3a":
                    scene bg entrance1
                    $ renpy.show("atsuki"+debug_sprite_size, at_list=[p13])
                    $ renpy.show("erina"+debug_sprite_size, at_list=[p33])
                    $ renpy.show("sai"+debug_sprite_size, at_list=[p23])
                "3b":
                    scene bg entrance1
                    $ renpy.show("isla"+debug_sprite_size, at_list=[p13])
                    $ renpy.show("shiroya"+debug_sprite_size, at_list=[p33])
                    $ renpy.show("miiya"+debug_sprite_size, at_list=[p23])
                "4a":
                    scene bg entrance1
                    $ renpy.show("atsuki"+debug_sprite_size, at_list=[p14])
                    $ renpy.show("shiroya"+debug_sprite_size, at_list=[p24])
                    $ renpy.show("isla"+debug_sprite_size, at_list=[p44])
                    $ renpy.show("erina"+debug_sprite_size, at_list=[p34])
                "4b":
                    scene bg entrance1
                    $ renpy.show("akaro"+debug_sprite_size, at_list=[p14])
                    $ renpy.show("naomi"+debug_sprite_size, at_list=[p24])
                    $ renpy.show("sai"+debug_sprite_size, at_list=[p44])
                    $ renpy.show("miiya"+debug_sprite_size, at_list=[p34])
                "5a":
                    scene bg entrance1
                    $ renpy.show("atsuki"+debug_sprite_size, at_list=[p15])
                    $ renpy.show("shiroya"+debug_sprite_size, at_list=[p25])
                    $ renpy.show("isla"+debug_sprite_size, at_list=[p55])
                    $ renpy.show("erina"+debug_sprite_size, at_list=[p45])
                    $ renpy.show("miiya"+debug_sprite_size, at_list=[p35])
                "5b":
                    scene bg entrance1
                    $ renpy.show("akaro"+debug_sprite_size, at_list=[p15])
                    $ renpy.show("katei"+debug_sprite_size, at_list=[p25])
                    $ renpy.show("sai"+debug_sprite_size, at_list=[p55])
                    $ renpy.show("erina"+debug_sprite_size, at_list=[p45])
                    $ renpy.show("naomi"+debug_sprite_size, at_list=[p35])
                "Return":
                    jump debug_sprites2
                    
            jump debug_sprites_many
        "Return":
            jump debug