## Make sure there's a $ StopOnTip(x) before each inline tip, making sure there is no {w} in the text before the tip (some lines where {w} is important we place the code after the line. However, make sure nvl clear doesn't immediately follow it) 

init -12 python:
    def TipOrbShow(name, stop=True):
        if persistent.tip_visibility and persistent.tip_visibility[name]>=1:
            """
            Copied from renpy.show_screen, but display it on the lowest context. Good for search jumps
            """
            #renpy.show_screen("tip_orb", name)
            screen_name = "tip_orb"
            _args = (name, persistent.tip_visibility[name]==1)
            
            screen = renpy.display.screen.get_screen_variant(screen_name)
            if screen is None:
                raise Exception("Screen %s is not known.\n" % (screen_name))

            _layer = renpy.display.screen.get_screen_layer(screen_name)
            _tag = screen.tag
            _widget_properties = python_dict()
            _transient = False
            kwargs = python_dict()
            scope = { }
            scope["_args"] = _args
            

            d = renpy.display.screen.ScreenDisplayable(screen, _tag, _layer, _widget_properties, scope, transient=_transient)
            _zorder = d.zorder

            old_d = renpy.display.screen.get_screen(_tag, _layer)
            if old_d and old_d.cache:
                d.cache = old_d.cache
                d.miss_cache = renpy.display.screen.cache_get(screen, _args, kwargs)
                d.phase = renpy.display.screen.UPDATE
            else:
                d.cache = renpy.display.screen.cache_get(screen, _args, kwargs)
                d.phase = renpy.display.screen.SHOW
            
            sls = renpy.game.contexts[0].scene_lists
            sls.add(_layer, d, _tag, zorder=_zorder, transient=_transient, keep_st=True, name=screen_name)
            
            if persistent.tip_visibility[name]==1 and stop:
                StopOnTip(name)
            
            MinimapHandleVisibility()
    
    def TipOrbHide():
        """
        Copied from renpy.hide_screen, but display it on the lowest context. Good for search jumps
        """
        #renpy.hide_screen("tip_orb")
        screen_name = 'tip_orb'
        
        layer = renpy.display.screen.get_screen_layer(screen_name)
        screen = renpy.display.screen.get_screen_variant(screen_name)
        if screen is not None:
            #renpy.exports.hide(screen.tag, layer=layer)
            
            sls = renpy.game.contexts[0].scene_lists
            sls.remove(layer, screen_name)

            if renpy.config.missing_hide:
                renpy.config.missing_hide(name, layer)
        
        MinimapHandleVisibility()
    
    def TipOrbVisible():
        for temp in renpy.game.contexts[0].scene_lists.layers["screens"]:
            if temp.name == "tip_orb":
                return True
        return False
    
    def StopOnTip(name):
        ## Stop if we haven't seen this tip before
        if name in persistent.tip_visibility.keys() and persistent.tip_visibility[name] == 1:
            if renpy.config.skipping:
                renpy.config.skipping = None
    
    def UnlockTip(name):
        if name not in persistent.tip_visibility.keys() or persistent.tip_visibility[name] == 0:
            persistent.tip_visibility[name] = 1
    
    def UnlockAllTips(val):
        for tip in tip_list:
            if persistent.tip_visibility[tip] < val:
                persistent.tip_visibility[tip] = val
    
    def CallTip(label, scope=python_dict()):
        if store._in_replay:
            renpy.sound.play('sounds/sys18.wav', channel="system")
            renpy.show_screen(
                "display_message",
                message="Jumping to another tip is disabled during tip segments.")

            renpy.restart_interaction()
            return
        
        renpy.sound.play('sounds/sys17.wav', channel="system")
        called_from_menu = True
        try:
            if renpy.game.contexts[1].scene_lists.layers["screens"][0].name[0] not in ["tips", "search", "chart"]:
                raise Exception()
        except:
            called_from_menu = False
        
        """
        Modified from call_replay()
        """

        renpy.game.log.complete()

        old_log = renpy.game.log
        renpy.game.log = renpy.python.RollbackLog()

        sb = renpy.python.StoreBackup()
        renpy.python.clean_stores()

        context = renpy.execution.Context(True)
        ## Make sure the music continues normally
        context.music = renpy.game.contexts[-1].music
        
        renpy.game.contexts.append(context)

        if renpy.display.interface is not None:
            renpy.display.interface.enter_context()

        # This has to be here, to ensure the scope stuff works.
        renpy.exports.execute_default_statement()

        for k, v in renpy.config.replay_scope.iteritems():
            setattr(renpy.store, k, v)

        for k, v in scope.iteritems():
            setattr(renpy.store, k, v)

        store._in_replay = label
        store.scene_title = 'Tip: '+ tip_list[label]
        store.called_from_menu = called_from_menu
        MapResetPositions() ## Initialize position history in the new scope

        try:

            context.goto_label("tip_base_link")
            renpy.execution.run_context(False)

        except renpy.game.EndReplay:
            pass

        finally:

            context.pop_all_dynamic()

            renpy.game.contexts.pop()
            renpy.game.log = old_log
            sb.restore()

            if renpy.game.interface and renpy.game.interface.restart_interaction and renpy.game.contexts:
                renpy.game.contexts[-1].scene_lists.focused = None

            renpy.config.skipping = None

        if renpy.config.after_replay_callback:
            renpy.config.after_replay_callback()
        
        ## Check if we've read all tips
        if not persistent.read_all_tips:
            found = True
            for v in persistent.tip_visibility.values():
                if v != 2:
                    found = False
                    break

            if found:
                persistent.read_all_tips = True
                achievement.grant("tips_complete")
                achievement.sync()
        
        ## Update link colors in the top context
        if not called_from_menu:
            if len(nvl_list)>0:
                del nvl_list[-1]
            raise renpy.game.RestartTopContext()
    
    def tip_tag(tag, argument, contents):
        if persistent.tip_visibility[argument] == 0:
            return contents
        elif persistent.tip_visibility[argument] == 1:
            return [
                    (renpy.TEXT_TAG, "a=tip:"+argument),
                ] +contents + [
                    (renpy.TEXT_TAG, "/a"),
                ]
        elif persistent.tip_visibility[argument] == 2:
            return [
                    (renpy.TEXT_TAG, "a=tip:"+argument),
                    (renpy.TEXT_TAG, "color=#FCC"),
                ] +contents + [
                    (renpy.TEXT_TAG, "/color"),
                    (renpy.TEXT_TAG, "/a"),
                ]

    ## Adds the "tip" handler to hyperlinks
    ## eg. {a=tip:1}TIP 001{/a}
    config.hyperlink_handlers["tip"] = CallTip
    
    ## {tip=label}TIP 001{/tip}
    config.custom_text_tags["tip"] = tip_tag
    
    
label tip_base_link:
    call _start_store from _call__start_store

    python:
        _init_language()
        renpy.block_rollback(purge=True)
        
        persistent.tip_visibility[_in_replay] = 2
        
        show_tip_overlay = (store._in_replay not in tip_overlay) or (tip_overlay[store._in_replay] == True)
    
    scene bg black
    window show
    nvl clear
    with dissolve
    
    if show_tip_overlay:
        show overlay_tip onlayer master_overlay zorder -1
    python:
        if store.called_from_menu:
            ## If we don't clear the master layer, sprites will appear if a character speaks thanks to the BrightenSprite() function
            backup_master_layer = renpy.game.contexts[0].scene_lists.layers["master"]
            renpy.game.contexts[0].scene_lists.layers["master"] = python_list()
    
    $ renpy.call("tip_"+store._in_replay)
    
    nvl clear
    scene bg black
    if show_tip_overlay:
        hide overlay_tip onlayer master_overlay
    with dissolve
    
    $ Pause(0.5)
    
    python:
        if store.called_from_menu:
            renpy.game.contexts[0].scene_lists.layers["master"] = backup_master_layer
            renpy.game.contexts[-1].scene_lists.layers["screens"] = renpy.game.contexts[-2].scene_lists.layers["screens"]
        else:
            ## Fade out back to the game by mimicking the background of the top context
            renpy.game.contexts[-1].scene_lists.layers["master"] = renpy.game.contexts[0].scene_lists.layers["master"]
    
    ## Done to force a smooth fadeout after changing the top context scenes
    hide overlay_tip onlayer master_overlay
    with dissolve
    
    return

default orb_hovered = False
screen tip_orb(tip, highlighted=True):
    zorder 100
    style_prefix "tip_orb"

    button at tip_orb_fadein_tf:
        yalign 1.0
        xalign 1.0
        if highlighted:
            add "gui/tip_orb.png" at tip_orb_tf
        else:
            add "gui/tip_orb2.png" at tip_orb_tf
        action [SetVariable("orb_hovered", False), Function(CallTip, tip)]
        hovered SetVariable("orb_hovered", True)
        unhovered SetVariable("orb_hovered", False)
        activate_sound None
        
    showif orb_hovered:
        window:
            at tf_dropdown_menu
            xfill True
            yfill True
            background None
            padding (0,0,0,0)
            
            frame:
                background None
                xsize 125
                xanchor 1.0
                xpos 1.0
                yanchor 1.0
                ypos 0.86
                
                text tip_list[tip]:
                    size 15
                    xalign 0.5
                    text_align 0.5
                    outlines [ ( 2, "#000000", 0, 0) ]

transform tip_orb_fadein_tf:
    on appear:
        alpha 0
        ease 0.5 alpha 1.0
    on show:
        alpha 0
        ease 0.5 alpha 1.0
    on hide:
        ease 0.5 alpha 0.0
        
transform tip_orb_tf:
    zoom 0.7
    rotate 0
    subpixel True
    
    block:
        linear 6.0 rotate 360
        rotate 0
        repeat

screen tips():
    predict False ## Avoid predicting this screen
    tag menu
    
    style_prefix "tips"
    
    use game_menu(_("Tips"), padded=(0, 63, 0, 0)):
        add "gui/bg_tips.png":
                xalign 0.55
                yalign 0.5
              
        frame:
            background None
            xalign 0.5
            ypos -35    
             
            
            vbox:
                $ examples = 2
                $ seen = sum(value == 2 for value in persistent.tip_visibility.values())
                $ total = len(persistent.tip_visibility)
                text "{} out of {}".format(seen-examples, total-examples):
                    xalign 0.5
                    ypos -3
                
                frame:
                    xsize 315
                    ysize 550
                        
                    viewport:
                        yinitial 0.0
                        scrollbars "vertical"
                        mousewheel True
                        #draggable True

                        vbox:
                            spacing 2
                            if persistent.tip_visibility:
                                for tip in tip_list.keys():
                                    if not tip.startswith('example'):
                                        if persistent.tip_visibility[tip] == 2:
                                            button:
                                                action Function(CallTip, tip)
                                                #background "#0003"
                                                xfill True
                                                right_margin 14
                                                text tip_list[tip]:
                                                    color '#fff'
                                                    outlines [ ( 1, "#000", 0, 0) ]
                                                    hover_color '#00bfff'
                                                    size 20
                                                    xalign 0.5
                                                    text_align 0.5
                                        else:
                                            button:
                                                #background "#0005"
                                                xfill True
                                                right_margin 14
                                                text "???":
                                                    color "#fff"
                                                    outlines [ ( 1, "#000", 0, 0) ]
                                                    size 20
                                                    xalign 0.5
