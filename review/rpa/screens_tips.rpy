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
Made with Ren'Py.RENPY RPC2   .   "     E"  #              x^­\€ÕÑv÷YØÆtB2Æ:l‹sSâ®ç*ûà8Ä´w+Y'ißJW —„”ÃÎŸŞ{ï½÷^ÿô„@€-”$@ ÿßÌ¼İ}«†ùßIoßÔ73oŞÌÛ{Î´	wj²wö”)SFlååË%wÚæGönÒ;Cûíqwzo>ÕJÅrv¿sgÔúİ™É¬²K•ñ”åUc›JùjÌÕyƒ;»gÂíHöÎÀô’5l»szOÅÇ!|<ÇËª|¥êÑoÛ.y™j¾â¥TeÜmşÂÜgÛ;¦ßè!öXÕÛÃD+*_Vùê¸;oóÃ‡êa¬˜/Ù¥Úğ€­Üù[„·Á|Ñf‚GÁ½32@Ò¸Gõ»G’ì¯:åRÌ=²YY²åœí™·C1÷Ì;1¹ejï5'N™ËÙƒñ=ùÊv5°Û)&‰¡¥q¯Z®tïQ5»ó‚XÿåãR³WµKÕ´É{ù|RÆ­R®õÓ>BØq÷rADÿ%‰à3}_W®äí\|P•‡ã²>8ÉˆÎ—ÆjÕx.ïUŠÖx<_—KñªcÇ‹åQÛ«Æ³åRšOÅ¯(—¢¬âm©¬/Ô†+^„ŒI6x D2Äd¼; ÉÊj ä/c©!O´^Z*AÄìî^Ş ®£$"œ–%%¤SCvU‹š±TŞ*U“S!:,ŒÇó^¼§\²C…’••÷ìø†±¬]©Â’‰İ2y‘GóKåj|©<ZJ]]JÄÅ#$š°œ²mu,ó¼ægªÖ0h1ñ%PHf4Ÿ#±+ª…Vó6i¸ÂVœÉå³ÕdÈQ¦ª¬’—‡ÕaÊåVÑ³,ûGõÚ4‡ô²@ ëãÆJ`¬/Á‹šèÇCşÔ¸bÁH®•
D»ëÅ,­¢­u°4Nbã'+¿D…sgKãdİ¡†à×•U— —’l–‹¹LKC»Jš,EJÿò§TÖÊ:uv¥Á‡1%âW¹ÔpŞó2ÛJ]ü0–B5‘æ—ÆeC¦È”s©ŠcÁ˜[8LzÇúËölX°aQWYnêpÿM^voÜ¾¯‰ÃÉ …8m#)¥¼¾®~¸½]²3E„ÒĞğ¼¢—²r¹¤o59ßŒdå»3ò»¹Í@‰¶]ÉxUØKã‰º›†€Óvá<ˆdl´Dµ»#ÛKØ18$6‰Ûò¥ü°UÙğ¢½7Ø&àÔÆ^³1Ÿ³“zs1sã^à`æu/ğÉ±6¢ñ±ÿ‹ùÿø¡ÙÿAìÄ}ŠãÑØÿ_²>e—Gì¤ZOi=bÛ0ëÁü»¾4”¡•ªÛ”ZMÓÛ)“â‡e:lR¸ÚzhÏ¯ÚÃ•x¾t.—b’^_Bgt‰şchš¥$0²z¡ª5UŠ“³1ÓÊæï²9±‰×¹ˆ€ûyc¯-S‰²W/Ùy8iqi$V ²0Şş|¥‚•i³(şÄ+²+á?ÍIsàâA
È¬“	ûX–§È–ˆû®·§œ_n²wY±½äˆU4-!Ï†@~L!6²¸­	`zü¢8PEUõİ!<­³˜8Ğ€]Ô[|w$1	3iÄTe§2ùRFÙ”>„4uö[®•°âIr±GŸqş÷–¯IZ#‹—Æ³U*ÙÅîa¯‰07$ÏÉÈFÍ¹·Î>3Ã¶çYCvbiÃı¤;±)4¬'^-ÃËHºáh¤^ÒqÊyrñ\Mñ{öĞ0Ò4/e0àÎ2vKU!yÕVV–óT“{ò£ĞWÚ*ã¼¶ÊÈb5ì\†N´TƒuîZU†Â‰nÓË#ÛtcÌ }œœ¿}è£³ƒ—XOÈ„>a¥TÕŒ0ÍuQ€Í‰{h	M$³_†0wÍmå\~08C¬6-C½‘mÏÈMŠå!òáJÑ®"¦†ê§tÏ¢‰tÌrs|jW¹X°²û·–‡LŒŞ@€LOD TöZÌ¬UôDaL?Îm«„Ä“CÖt:`³Çìl¬)µNƒI>º6 ¤†k^>Û"5[†Eççõ1”U©Ø¥\R³`ĞLÉ?ß±•ZYD{9€E7îhnLNÁ‡l•ÑøM©ÅÛc•²‚«‰àvÈªq¬ZˆÀ`ÂÑ¹i|$Ü õ¾-Ñ¹#©<¨âß0Z¡gaU%µ+ÒB Û.Cnıˆª>0b¥8J¦ÆQS²çj¾Z¤óÁb„Üâ‹—ñ¾ç÷ M©~HR«²Ë†¼;Ê^L‰vàĞ"A#ˆj~ña¨\-#uå$WpzÁöSÚß›CKUµR°ÈìÙ†J%˜ÙÌ†RnWİ^Q±<9@ğÁ|	^oD¶&+åJ†Cn‘+Ÿ5"C]”Ú;À"1ºÎïu”Pxå±TÍDÃmè tÒ0BRèMvÎ‹šœ­š%9Ñ¨Nnœ¾RƒålÍÃ&¦SRc OIìŒ$·>Q2SºÈDküWû™EÂú-^{`Ó¹>­Qø0’e[9^LÚsBÜƒ”,˜{[ÜŸ}¿uÂ‰,¦F6ªB‰ŸÑ_œB(Zñ8 öö7K€áZ¦X©êÅ ä("äíp©!Ô…ªìn(=èíËp·úéŞxÉ7ùh6ÅÖÇƒHÒˆm²4Räl²ób#]%
9»÷öÁ¼BOâjœa¥ˆ-”úì)Wü-J‡)^ b”äªj!5’ImdÈ¦£şÚçC¡ I¨õÁÄG%yF±íÙ?‚Ê8YhT}É"áÔÛÃ½{2{.»‰Õ±.H,ñÑu6f™ıñ%>cñ%ñÃE|•h†ëi‹fØô_´æ:É–‹eÕ½ğòuëšŠğÿS#m†¯9­Ô‹ÅtDrÆ&hëÊà”ú•±–\,Õgœp2Âg6e\dÃÆTmÕ1÷Î‚-Ó¹Wr£{·%htO®ğ*¸§t§årêæ;îœélî™;uÊîiÎ‘Î=êŒğãn|×&,ü3: [9›pÏ@$FÉBi”0g@‹zça8²“»gq§b)¤ığ»¸G³ğ3ŸiÎ$ûİN³ÏDZ‹¹gƒä\štæ8Z’í,É2F)æ ¿ï0›êt7±8œY¸çôÎÅgJñp‚i»˜'$ƒØ&¹¶ü äuH¼ µ2éœyĞYÔ{4Áñ¡ ½Ê	D¸	ô0¾:ª®”b¸çİy@·&I³ÀT(Á–à|’€SêÌ¼0éïP—é"ê2}äc8óå«È‘JC5œ:±ÅIld•e”>/$+55dKß)k}øÎd–+b1îqíÍ@ê¡aÓLêÂ…1­3½1iôÕqH~Ün˜òÍÚ”/v`Á®¿˜;Y—h›¸™TuºC&h˜ßnJ^cî¥ĞÌePÓÚdï,è&?ìUàë’½Ó¨Ã7¤}È&{zúñÿª»^ÛJWî†è.&z9÷<­jÑ½Â·Éßƒ~”vÚ³Õnÿxs7‚‡Màas’mˆz…±ß-ÒÃô×ÄİÊL–ÊjØ*ºÛBÚ»™v[%·2ŠV•Šîöƒ¤„ŞcqØ&2¢¢=‚=ÛİqFôö6jŠº;{ÀÇÑ|)WÓJº»Èˆ*Ü	š»›¿ÈwCò¼ô¤»·gÒİg´F{ûİ+Ù“¼Ú C{îUınY'‰|5DîO:[zœ­!Ë–ågû^?æğg'#Âş§ƒ¨r3´¨»YÙd¢òàÚI×¨gĞËEu¿/_ub®úƒ ?d„€4vt`¬(7é×n€kÇÜ/•^¹8b»ûa‡·Şxƒ[®aY>£¹\Úrk´¹\ß¤%•æTZ!O¾µÁJ6Æ\|*àö´¿ßÆ:	}/³\åÖ;2…î‹ŞúˆSè] ÆtEwìŞvÇ€r<é”¶ÜæKıîu¦o`Acîõ ıLLœˆ¸Æ³’l"Ú¹	ûà½ó16ŒV>Òmı<-[î>ToÕç ÙDõvŸjÕ}n(Ì>æy=¿GbÜí:¤Y“îháĞ6	\7ú¡í …¶ÏRh£=ŸM›ç‘œ›Ğ VÉhn£=…v¢ ô$	É0Ÿº³Ô 6X)‘EüuBCwèpöÂ†pÖËŠùÎîÃkâEĞÄ‹}M¼„4±B†œ—°ÑÈ18±¤>œvº/Õ»4Õ—5P½’©¾\S½‹©;ú+|7~%è¿ªÑ¯bğWGÜøî7~»±CûZòØ×‘Ç¾PS`~P¿1é´‹ÆorÌÜÇDßì±÷ñ*‡üè-ÀöVíG÷Fıèj†{›ßy{+ßy´u/¬ø@ó.²â{ßy·á;ÔL‹¹ï½÷bâû"¾óşÃõÚg> Ó¿Ôx{?sùÁĞ>Äî@±ìÃ õ#–]ÃS?êä!M$`}RÜ)>€O÷k)X!‰î×:#ãú$¦}Ê7®O“qQˆÛaá¬ìJ­ît?|húlƒe˜Ïiz@,—-‡È¿à#ÿ"!ß;õ©}øÿçpMœ¾¥ûÖ×&ÚT­ª–+¢TûãO›¸t«™İªÜ/a¡Òõå†…º–ê+z¡2BYòW±P_K:OË|¿Kz<b¾Óø†Ÿ ’Ù~ˆ¿e˜í Oùv£Ù~Ü?³ı. ş—Ìö‰³}¢aİÅÍÀ˜û=Pú>  _.©ú'Ë2?Ò\Úd«t/íÇ€ÿ	qª/›½—Í~JâÍÛ2Å™¿mêTV.ƒıÌˆë¥so†ŸÃÍÆm°_pVşK˜=|”ò.à¸¿r Dı5æÿ¢nÙ¤“üÈù5¯bÕı­d*(¹¿C„	›%ø½ÜÇ³ßjûƒlÚj ãĞöŒ¤ãYkB9µİjÄø?êSkà6ğs»¡wA¼ÍÛ<÷ÉC‡€jZ „?Emºsÿ¿Ò*pú#m_÷N=Ù+®H!qÅuÀİ[åJOÌ½@›pïN¦g²º÷p¸XwŒ»÷¦g°€÷±¸úÊ@z6Ú¶£¸¦áŞßïş]B°ÜÚ€ª)e\ŞÕå> mN'E?¦"EO÷=é>Ì©´W/Ú¸eæÇ I”ƒ[iî? ?ƒàÿ	øüŒş;=ptÊ}”×‰îcéÙú^™ûoç±t‡…Bñ8nò¹÷¤;0Y2–æ‰ƒé9n8¢öóI§s{(=G{5Q²'=K$RSñÍy0İƒEÅr5`5&Ó3‡Ë9«¨¦c$415_Ó³pÉãÙL|yáì[~rÍÏs+g¥cá¡ZÍÂ3öÛ›Jƒå˜š§7¨üšPsğ3	`]¯ÚFúÕ4ÎÇÊ(Øå¶C'?äñ¯jçÔ<Úé”-”x5Ÿ„+í~u$¬gR-À¯ÍÆJøQGù²Şxƒ:šæM¨c«k·™TÇ2ÙLcÿ¨:&ÖÒ(asØOÔñLî‚lbŒÆÍ²˜:Qä~Ë}Ë=“íDLâ‘©á’dëp
©¹ƒ‹ÏYÛS§âëÁô¿=¤-ÔS§1¦ÓIûûUœ5F‰³U… G…F´r6úÔÕAu†H=Ö§"õB-õ¬Pê3}~Æ-(»ä›~ªK-øÙ–À/Öğ³Cø¤?Vß)ğ¶À/Ñğ!üR^ºË !¤éÛmW÷ÒİJº6’0"š´Ò{ÁïZIÒºÊ…»VùJg¿Z&tçİ”Ğ=GÓÒí"ºt¨á8¾µ¡ËEµ\°Ï'ì+ûJ}~ˆ}a§HP+…øÏh_äR«…À‘Dà\!p&pdH` ã©m=Äß;ĞVOaD/ˆ¢Ñ…Ñ‚ÑE²ÓGè(é[ucH¸ß°kW¤ckÙjcêbÌIÏvÊU¯R®ªKğí`½9=—Ú\~£L]ÊOt°™…`3Ÿİ	Wv3—ğìË0á@ºƒ_KœÂY¨Å©Ö1´Ÿ[uğéÀUµ!×ÕÔz~*^¹!äÙÜ!p:V—ã|ñ
üšPIã£Ïİœ©“j‹¥Éj3£ŞÂJ+4Ä¤­¢ß9¤ßm¢ß­ß9¾~›Ä‰µT³‰©íÂÕæj§ÁÕmWâ¯…Ü…oZv3à¤˜ÒS Ğq @¢àÇ‰4¾„a‚ò½÷Q| 4üÇˆÿ}Â¯æ?ÚÇ•²
†Iˆz{ñbÂ]È˜ºŠh¶ úˆ„Ä§ÄP-¦ª”†êjƒ~¿Ğ¿¦¾UˆPlêdæ`Í¤@öq@¯æíZo†UÔPMF`Ïğ\­ğkYo–¡ğ;¢fpÄÔÉPã†Æ³™k¯q»ÆEâ¹¤ñ!‘ØÑÏ54^hPhAJõaS¡+D£ûüEÁ?\¿N£sÛhôO-5ZV›µÛ,+C]ˆü®ŒI°ğ
«Í5şç¨Â†ß)Ò³¸›'"Öe¢ª*²Mº«‰l#Z¶£}İùk<Ê$Ç’1Šˆ…K<n,ñux}°ÄFS=“æñöõ±	š:UÔªƒ™.Ê£öYâËLêYÂü±Äü³…ùçhæş²ÊñÇğIÑL`+ğÇüóşùş¸ş>üx=ü¤ÀOğ7
ü|à)HĞ1xHÕï'/$'’ÿ$/ÒHN‘¼˜Ğ¾ZAHÀM3'»–òÿ:ÕKÍ‰„æ¥‚æeÍ‰!š—cÈ6Ã¿!Á/×ª±}\Z©WĞª!'/ÑÖ}Àˆş~ò×FëV¯4láUl¯mVfšIê5-Láµl
­5ø:ıdıõ"ú´è'‡¢¿10/í'd+V«7	ø)şf‹?%«¿ cV)ë”ƒÃ2º·	‚S	ÁÛÁ;4‚SCï$”;ãÊ’gäƒïèÓúİı}Zı^Ÿüxù÷	‚Ó	ÁûÁ4‚ÓCôÉyâ¤+µæ\õ!ø‡ü#<‚40œB{Û8©mÜÙÄ6>fØÆÇÙ6>Ú1IMUõIß4êvâO±ipD•’÷å«Õ§E¨…$ÔgD¨Ïj¡†B}tB‡†H’Òšú¼ÀŸIğ_ø/jø3Cø/<oÿÔø5uÂñeÁ±ˆp|Ep|UãXâøá *!Üº´6Ï T=Œ¯À‚…]üô.ü¿3Ş¯¾.xÏ"¼ß¼ßÔxÏ
ñ~+X0½—ğÛaô#¶‡~¨o“JÍ¬â;„·t|©<ŞG÷Õw…`‚ş¯ü&˜ğ	Öí‰6ûß]-ö?l{œW|¸ñ¡”5‚ÚÊÕVÔˆé³råõCáêGÌUP&z÷ôÕivP)JúEõŒçë=Ô·Ã¡á˜ú) åÏåM¥îTç™…ŸûënØo¦ùfÙGı‚f5?Cş’é^¥ú•ÁJµÛeê\ö×ÂÉoğkBı–IOG–«~'ëÑ‰´E¯˜påá÷=˜7=õŒô«[ĞoÇAãVÁıGÆ}á.h;ü;êvpM®4câg6»°îÌHAˆÿ¥ø6Ôäòho#
Ù1õWaãNÆt‹8;›Wè&zêo¤$ü›Òå³ìiôËGÊE¾äªî&§gáÍ)jÔ=4Ÿ«r¸u˜îÀlQÌ½¤.)=‘[Ş'Úë"k¾ŸL¨¿aT-º|kN(=õ ‰’Gd2ƒút¬dÚ±ğÍ=õKü0qA{šUÄË[İ.õƒî?…î¿êéNªG0d¥gãm:ŠêQÂÉ~ÁqŠîÜZÊ×ÿc¬µ›ú?»NÿóC­å'xş“<Ô¨\e…H‘=R›V?+ ÀDÊCõRò:A­g“Z§ 
C¼©øEj=;ŒJÓ0d´T>_Ó18¡fĞì&|-‰ğ,0óg,ëL€ƒş¢?KèÏÖô—‰l£ ˜Ó°\Ë±©Ï1ğÅßõø&Õ\SD¬ %ï¯Ñ<–m>Ë¦lYİÉõ-àùGµĞö]/š¿FËHGÇˆLÇj™–…kt\³5:ù:¡_©Ã[£E§)¢ÿ¡’¦Ÿj³F'·Z£S|§
¾ÓêñMªÓëÖ¨Æş¤+ğØ¸Il%qÁsã	¶’÷`+Iµ`+Yl%1^Ğ»Æ™½HCë]c?ïgÑ<Ş&
¼5ÔÕÓcÚ|ÓI²Ê;MÓYYg:g›¦³„ç/m±DzØ¦³Œ4N¡ôºry8p²óTJ¾’ğµK+|eh@Ë›Ğ
æneîV=îVwU™îñ€?ß²Wc«…±s5c«BÆÎkÆØfìüŒ­~:Œ]@ŒQ.GwnP†‹6/İ­&/»5‹«C/°¨7ÚK˜ÅKMKXSg	—™–°–ç¯k!†–ÀŠ¤ÍûŠRÏE\/¯!7Ç—k×´q×+–‡¶Ş•çv©ÂM‚ps=ÂIµ¥Ù*me‘¶µéü§³J=-Íç|’t»0¶C3v~¸6;MÆüäQ26¼“`[Hªwa
ò™İÌísÁ.@î2ıLóTšhpŠKY®ôP¢‘h¯0²	"Ñ{‰è”iş]£+éº}ê*îchD­;´óÔÕÌX?ŞãÜëÜÇ^NwÇ©ÿqK•AÚgfsTedõºII×
vK+©;TÒ i·IÿÌLŞSYAt)!Ê	"[#º4D4ˆ!Ûy´@¤4ìœÇ{œ':O:‡
ÔƒcÆ©
T œNTtAü"˜µİ
ÔlÓuÌ¿éS5·
º6ÄÚpx™¸Ê^0`İ©ÒEâ<f5©Êá6aLdÕ÷3º"¡KÏÂíT¼å¯†IÔ± ËM\µJOG—U•Hîôzç_•CÔÔ€½Lß}—V_Ep»Œ[1«Ì$R=ÏS†ûU•öèÂP&™ —Bª&Ú^KÚmjm¯µ=F|Êµ¸\Î¦†İüEy)~îJ}ôTã¦ëÓõ˜Ië(O¯ÈZ#'ğ@/Æ´ŸJÇsZ>§Åš˜Éw.Õ³i.)?‡E¾E–^Åİf¹‘Ğ…åÆçò4]ÄC>Ÿ‡Zñ_@£§©‰¬^­&EÒõ\ØIhI×…=_g‘1^(ğ¸¦'ğ/ÒğŒškŠz é—£Ä?0$r‡Ò/ôëıËıË5úu-äëÚÈïiv ÷uù
Öå+]ZUé^Åúl]¥{µ0½‘˜~0ıZÍôÆP'¯óuÚP’y½Ào"ø7ü5ü¦şMOë¨Ë\´õ,[¹Z½Y 7ô[ú­zsı¶pEÚW¹®hSåº·I•ëí@ìkô¬ÑwevGÊcê]4+¬…O¨wûÚò¬z}§×Hªy\0¤°İ¦œË‡íµå±˜z/¡nYĞİÖÄ:ü‚î}MÄy1ß$ê?À¤ŞçZ`I?È’Šß¯»3èµú-
.â¨Ó\A£}Ã³è\úÃ!+ÔGdÙz¦Êå)õQyéå	õ1|«øÆ©“µ‚&ıq&ı	ƒôßµÑOj¢—SÂF!¢§6L¯Ñ×ø¯¬7Æøëa½5Ö©>%ìn÷Ùı4i=Êåv“ËÏ0—Ÿ5¸| ËÏi.Ï¢}ùn‘ŞÅ«X-_
èTŸ.vø\|¡‘‹Ì…—_d.¾d¡UµõË4¥yÁô+Bsù×Wñşõ5šãÿ®Ğ¿¾î/ŸöN|…wªoğnş¦ Kï¿!.k—„¡Ğ»Š’Œë'âğ•xy0~ıDï6â¾>şÚx™oZ¸Ò@š¾wªï
;¹Ä)|Os°³EDİÙ&¢>Ø.¢~ŸÕıƒPİ­"êYİÜ¹2Z+QŞş‘°»—Øı±°ûÍîŞPa?%m8n9Õ«»ÔÏ|ß$à?×àûBğ›C}·†é6Áğ¡&ÑãdÚö~ÉÊøU ‰ny{”ŞëV¿¦™Mğ¿aÍĞÔqzW©ŒBÛoEº«Hºß‰t¿×Ò]J÷RíV¸ÍÆoİ(ª¼Ó@Â®	u‹ ê#T·
ª?jT}!ªÛ|TÃe\ÍuìèÁïvAr5!¹CüI#¹:Dòç@Û‘¸Z!ÀWMLı…tSÑøÁğÊ6kòp“5ù«±&wòšÜhİ¾T m‰Î#Áé¸àU¬¬4%é$¾Ò^KÒŞ-ÒŞ£¥½6”ö^Éõ‡Bû)ÓfgúG9î#9ôÕ”ûY¿³²ıü3Ú"·•>@ Ò"Ä’îKËèª’Õ´H¾‡E¾hù¬àP¬3Ø2ÿ2ø—™Áé0ƒ}ßšl©—ãvzÏ°M>ÆøşÍä°ïëÜz *¢{şU?-ë#ş­Â°”­	”3¿Ê«ÿÈzBä ¹¹i¹¹äRĞ$U¾§âó„š†Ÿ¾ê8O' Ññ|ôw%é54p‘âù¼Q¼”\¬#ôâN5“&.Ø–åz.>ƒŸÙDJ¶^ÏÌÄƒ‰ÇL=ùPÏ1ƒû#p®øï(÷9p?/ä~>sPà—<êOâPúr¤‘#!ˆGi!rõBÍ¼cğò¸)q
q,ñ¤Cèqx<Òi§@w›]©8¦HÁ¿x<¾4¿ğ§NŞ¹X+¼Ÿ¤yùd5¿\qŠÀ;ªÀŸ¦áşt‚§´OÑ•T¼¤†òt[¦7eù*$yBr† Ih$ùÉBéÌ€.ĞµÎsí6Qñ‰&ÑäLCÍ‹XÍg…jn•%-f5óKqôR2„!•/^888¸X%E ı$P§t¶h(ĞÒJ]S˜–ŠšÂËuSØè/¤EBºL¦4ÒbˆôBÊ7€é:®
s|¥]ææ¯KPªå‚j…F5¢ZI¨êºî+ºÔ*.qV€ÏÕÀ%£
KÀM»îk¾Lğçü¾Â_Hğ-»î	
áèk•Ç%¡Å4ä’—†f}ğËuP¯Ôë4êB‹$±Ğ&I|²u|R­'ü~%d›Şålz²‘Š†)×¼\wæù±a#CnbÈ¶±a3MiîÈ[Dì*‰½UÄŞ¦Å®†í¡UiíÈÛIì$;5’ZˆdW¸,íYµqä)R\*˜÷Xw:ÙÃ:I‡:iåÈ{˜œ GN¨}"Ğ(	D;/ºR4
tiåğ¹OÒ«i¿F:"½†6z_F€Ç	øZ¶4ğx<@ÀM½/+ğ×|Nàm]?.QƒçyŸ&qÉ%—$”#(Ge^P4Ê‘3ÒÆc¦6®,÷òøÚÈ~bL.â3§à>›=–1R abCO+éi>ÇOéÎß†ºzpûd˜›xe’È¸}‚×›TE$sY2zk–àÌ×šJªBP{2õQVóÇx^­\€ÅÕv/Â6¦w2Æ:l‹sÅ”£¸€ëÙØ–}pbï´w+Y'ig¥+Æ—@Î6ôŞ{ò§÷Ş{/„ô¤@IHøÿŞ{³»³j6IR|§Õ¼o^Ÿ7ófï¦IcîÄd×ô	&ÙÊË•Šî¤OìÚ<¡k2í±GİÉ]3ğ[µX(õí±³î”j;5Ù§ìby4ey•Ø†b®s§µİìNïsg$»¦`xÑ´İ™]gà×üz¾×§råŠG?m»èe*¹²—RåQ7¶ñÓ³f8[Ş2y¿{”PÚ#wV'OZV¹’ÊUFİÙ?tèPWÏ
¹¢]¬öÚÊ³IxëÏlğè#˜pn×Tô’4î1=î±†$ÛF+N©sƒ,ÇC–D–¾RÖvOŒŒ[ƒG1÷$Œ;9¹ib×õ'O˜ËÚıñ¹òVÕ»Ã)'‰¡Eq¯R*wìTU»í¢XÿÉõÇË¤f¯b+)h!3”ór½¹¤Œ[Ålóo»	°çÒ%DÿI$ÁïôyM©œ³³ñ~UŒ‹}<p’/Š÷V+ñlÎ+¬Ñx®/ãÇJÃ¶W‰÷•Šh>¿ªTDIÅ=ÛR}N<_,{‘iÌiƒ/d’1ïˆ'H²’êùËXjÀÃ7Z/M• bvt,i kæ ˆ§eIÉÔ©»¢EÍY*g+Iƒ©&çñœï,íP¡¤Deå<;¾n¤Ï.WÉÄ<ß£ñÅR%¾§X.¦®+&âóã‘)°œ²mu,ó¸Æg*Ö ´˜ø($3œË’ØeU‚B+9›4\f/Îds}•dÈQ¦¢¬¢—ƒ×aÈ•VÁ³”=ÃÚ6)½>€ƒèÆø˜a	<ëN°Q=ø’«·Xğ$ÛL¢İµâ–VoÁÖ:X'±ñ/+?ëDEpg‹âd¡†à{K*Ë&È¦ä×z6K…l¦)‡¡_%M–"% ¿ü[ªÏêsjüJ?ÆH\eSƒ9ÏË0m3uñ—°ª‰4¿(.F™"WÎ¦Êgn0émk¯Ø¹.`Á†ODC!d¹aÀı/yÙ±~ëî_ ‡–ÉiIé,åu·÷ ìí¢) •†ç¼”•Í&}¯Éún$–ïÈÈÏÆ>%Úv9ãU8a/ŠS&êh˜BN[¥ó “±_ĞBÕî<ÙZÄŠÁ)±AîØ’+æ­òzì]Á2 6Öšõ¹¬Ô‹‹™˜ë×#ÿ§k?k#šÿèü¿€¿ãşËD¨Sö‘û#yŸòx4÷ÿ¼OÙƒ¥!;©³Öa½G|nİŸàğÏ2d©šE©Ù0½œòtâBüÏ¹»®öZó+ö`9+AÈ¥xJ¯;¡+ºDOÈ14M@))Œj V¨JUãlÌ´²ù³,Nìâ5!"ä~Åèàµi)‘Bõê%Û¤¬".Â
DãíÉ•Ë°L£øC¯È¯„ÿ4ÍAˆ% ³N.x$ìÃ,‡©–ˆûö·Ã/1Ù»¢P ‡^rÈ*˜cG 8¦1nó	0¼'~IPQU†¢ƒ(„§5³ƒ êµz‰ïˆ&a%œªìT&WÌ(›Ê‡pN]ı–ªE¬ø&¹À£ß±ÿõ–¬J[CÅû«X´	<„¿&Â\W<'#5×ŞºúÌÚgØ‰EuCô7‰(¡á=ñJ	¾XBÑ@#õzTSÍ“g«ŠGà±g¢LóRC¶p¦P±[ªÉ+¶²ú¸N5¹§8
c¥¥2.h©Œ>XÃÎfhGA‹Uxw®e(<ˆ˜è2½$²L×çZÇ)ğÓ‡nÚ;x‰Eñ„l@è7XJUÌÓ¨PØ\¸‡Ğ@‚°úe
sÕÜRÊæúƒ=Ñj×2ÔYöŒÚ¤P@",ì
rj¨~*÷ğ]´Áó‚ÚÆ#ŸÚ^*z­¾=›K&¢×€éH”Ê^‘Õ²(Œé¯û
¶UDaƒAHˆ!kºœ
Ğì»¯JŞ”Z#ÛÁ$o]ëRƒU/××¤4[£ó÷µq”U.ÛÅlR³`Ì¸’¿¿c/ï·úíe]¸£µi08…²UFã›RŠ·GÊ%…PÁí2U-`Y±€`ÒÑ¹gQ|(\ õº-Ùµ¶#©fÅÿ¡èĞ=€•Ô¡H†@µ	,Cnş¿„ªMŒ°çS©Ô8kJõ\ÉU
´?X€”{Q|ÁÂ ßwóøƒ A Õ>’ÒÃ*o·!ï¶’—#W¢8ô„HÒ²šø0Pª”Pºcæ$Ÿ ôb÷‚å§¸§.7‡ªªÅÀÈÙ†J%˜ÕÌºbv{ÍZQ¶<Ù@ğ?ı¹"¢ŞÈluL–Kå%†ì(2W®ÏÈ5Y:êï ‹äèš¸×Y"€ğz9ËÃT&ˆ¦Û0@h§a¤¤0¬\5Ø[5*r¢Y"ÜØ}¥úK}U‹˜.}H>¥°3ŠÜÚBÉ,é"­~Š_[äj”	k—xÇÖÅ<´FéÃ(F”meÙ˜´æ„ØıT,˜k{ÂŸc¿yÁ‰*¦J6ªBL;?»#¾4úX0e¢èŒ¯À^°·§~_<¦kZbE¤ªƒÀqˆ³‡8Á¥p.TápÃÑƒ^¾Œp«î}—VãPlm>ˆ8¢M‡
\M¶]j”«4CÖ.Äı/»á^a$ñiœá¥È-Túì,•ı%Jo‡)_àÄ(É§F8©’t(òh!C5uç¯İ>´"µŞ˜øPRgZîı#PÆÎBCu×‹„©—‡ëºvfv^q
«b]”XèÃµÕW™=ñ…>cñ…ñ#>ßJ4ÂzÆ¢>ı¿­±NúJ…’ê˜wåš5EøÏÔÁ ğóĞL}±XLg$gi‚–®v8¿¡­2lÉ‡¥zFú¬ Â¦Š‹|Øª½:æâÌİ4™{%ûİS¹-AK {Z¥—?Ğ‘{úAçHZ.gl¼ïş©ÎÆÎY'ìwÏtvæ:è¤8è¹Pg„×÷,ã÷xu¼×ÂÿÈf®&Ü³Ñ I Q2O%ÌÄ9ÃĞü®ÙxYÉİs¹‹S¶Ê~$xÏ]Ğ©Yø‘Ï‚4g’=n›Ùg"­ÅÜó0åBL¹(éÌt´$[Y’Å)fßÏMuBº;X®,Üó»fáw*ñ°ƒiÛ™'ƒX&¹¶ä äuH¼¥˜kYÒ9ç 3¿ëX¢ãMA„z¹ˆpæwÀøŠ¨º¶Q‰á®Ü€[•¤Q`*”`Kp!I@Sê"Œ¼8éœèP—éê2}ÓÇ°çËUP#ªØub‰“ÜÈ*Ë(½_H–«jÀ–¾S,Ö|ónÉ-—ÆbÜ/â³;4©O„†M]1©.Œamq¬IãAw-§TáÇí€+ß©]ùRìãúÆ¼šUq™ö‰;IUg9ä‚†ûí â5æ^Í\5­NvMƒnrƒ^!±&Ù5‰:|ºÑ‡ªa¼³³ÿ«¸kµàèÊ]×Nº'½’{V¥à^åûä¯1tî´g«şö æ®ÀÃÆ$ûõ
3â¿›¤‡éÛÄİÌLKjĞ*¸[Â¹wğÜì•ÜÊ(X:p·$%to<‡o¢"*ØCX³İmáD¿áh£¦¨{u×Qøu8WÌ–†ãdIw;…ÍŠpCæîà2ÂİÉ”<.=îîêww­Ñ®÷$¯ÚËÔ{mÛÕÅNÍ.lqôĞ=\¸Lú¶Ü	ÑÄ—Ëv3÷Ö‹ïÂ®¥#¶€lPÄ¶Ëíí:­a e.XÙ»´ß^µÊíÓ¡ùïbµ#ñ+´sWn¶ëÄÚœÚ†„ı=î€CæsÀv.élêt6;†]ˆùınŞÙz€gcmßå\Íò V‰Ó¦Z¹{ÈAw°ãà!ÃË…qw:-:ĞdÉîÊõi»C….xQc®7æVt†¸«V—”N±k–>üÄv«wH§#@vç*NÌà„5reš¥Ú«W²roŒ4¶×!ÆÜ}l!ì¿½RaÈvÇ°wï¿Ù}°-~ntáoÚtw´³$1ò]ñ½œ‚ï=‡RŞİuá´¡?æ>|>Ø·h±ïa…a³<Îw`f…6§»¿Ç=àìëš«=ØÌYîA°{Ø½ÏO:7mºÇ–zÜÛÌ$Ï¹·cî`à#9äEI%	ıä®9x6ˆ;Ø—è¯À%›ÅKÜcÖ{1ëK öRšõ^ÖŠû²P˜İ,ÌËƒLóŠNYîÕF´ÆİWÒbËkÀ«€õjx­Ÿ 5€:¼‰o\psG›¥j9£¹6_ZµÒ‚3:¡LH)~ø\]Ø‰¦Š•ûZhè>÷_W—÷»X1¯×yÿ¾0ï³&Ş M¼Ñ×Ä›Hó(·ÊÆ+²œ$Ö®;mî›1ëzÖ·ÔÍzÏúV=ë<«Qú¼,A©íí˜ÿfj»„’Ù;«Óéå{'õ¥Ax2KÜw…9ëA'Û…#ÑÂÈû’Ó»99½¿·>9Ñôûİ÷E’ÓƒuÉéıœœÊC <ôAÊCÒyÈ¡|óá1÷#cîGuà=häÙåc~QB«íÇÁÍ'’N«%ö“¹°v3ŸŸr‚õÏ’ŠùOí3zê‡¢1Ó}ÖAœ®Yœ–}÷À|‘"î¡ Î¿dÄ9uHcî—1ßW0ğ«‘8ÿÚ‘Æ9_G˜>L2Ssù0t¿É¡Ky÷[˜ëÛFŞ½‡~Ç¹ÒD’ëw!Å#â{ ø>Iñˆ–‚ÂYó­3
„`Øı@ø¥ãm`’í©mîÀ{Tûûëü=ÃlÜ©ııQ‰2örÿ	ÀêƒÿŒÀwM<|¾ùÏ’CƒÕ4ÕÔ8Õõ›E/=Lÿ!^zxÆ“û	òˆn(Ô§U÷ç0ÔcÚP¿¨3Ôl¨_jC=f¤Còä_ÁP¿N:ÏÈ}Oz2â¾Ïq—àä¶wø·†Ûöò{êİö^pÿÜö>üÜö©:·}ªn±ßÎŞ˜û{ÌôşQ¿Üì3ö_÷AÖÇ,< ¹´ÉWé²áŸ@ÿ qªo¾7)¹8³7Mpæl™8‘U‡~¹`­œïÇÜ‡ğşb\ñ{”·Z…Û#F©ãS9÷1g.Ğ êãÿ7ˆJØRP$ù+çq¶bÅı»TU8tÿ]M&l–à	¹di¡ÈÅUÅJ¡z3•(ş%¶&ÀÈVüßÆzô¤Ÿ»IOŸ§¼8ÄØ8ëéC‡ 5ÉW‚š€8l èÖULMÄã¶›Õ$üèS“ñƒ,Âe›ôõÕ”Ğ+,M¡èÄ•Ï›åÚVLM€iø1¦¦}z*G§š\+/Ğ7¨™x”Bâ«}KúĞEÒÓÑ¬Æåu¾éQĞØÉÔrc¡{I{»š¯ ÷É0‰š#ŒÍŒß„gÚ0ãj.M@[*¯2Z°qCÎîÏ …8
n'ªck
a+XÇi¬)!Öñxd§§ƒ.Õ©š,M}(u"	5]ß8T'áSÍ°ĞHÅMOu2§g€);«NÁçƒé™îÁ¢CãŸêÒYFÔ“q¤NgÂi¢uA“ÀéØ_ZÔ[Qg
ÿ“&§§–²VAEXóª8Ÿ†-kß·N¿ë×ÿ8»lZ:Á¨Dhe²ï6ÿtfC±¿SóÄÈç°‘ç³‘ceİŞì¹l±l12Lª’Äy¸“p
ø‚·±gà”KY Wç‘|yš»G-$ò<‘u«E$*†ÁHÑ¬—Å¾¬°UŠÆ©ó‰v‡ŸK@«vc:Ï±gX-¡ÕŞôœx²X©ÔRnQê€0ıÚ¸ˆSËEî,÷J–{*»“º€Ä#ïÄÚ
ì°ŠÍÂ½Š>ÛSâãÁô\¿›¨]ÛS1ÒÅ$¸ù%¬4ÚAXÈzL™~+kãfC¥_uˆàÓÈI/Á/Ó‚O¿ÜgiÔ‚¾‹~À¤ÚÕB?èWıM?=¤_ëÓÔÒ¯úD¥Ğ_¥ég„ôë}z¹€ù/†4İ;ìÊ.ºKFºC[_ºuøY-Ê}.ŠÛy¹r[Ú óÎ¦y7Ê¼›ô¼³Ãy7Ó¼”ItÅÄq|j1/C©-‚>‡Ğ;}«FŸ¢o#tÊÕbˆvk|‘K]-Ml—	vè	'ØIĞ¾’Ô6„}†oªhÇç“ ¹Dõ€vk ¹!PÙé£tÓœô­®Á#íã~/½×v¬!\ª­fÇ©k1&=İ)U¼r©¢ºñé`:=‹£~kU]Çßè|3ùfG.ygXÜ=p =ƒ!M~=qŠx¡¦¸Ê0µäŸ»uş™Ë6.8ªø[	L+äÙŒK¨^|…pìÃ1•%hÄß
¢ÏİÌ‰ãÊf±ôiêgèVÚ¾º´äˆ~g’~s¢ß¼ÖïL_¿RÅj:å‹©=ÂU¹4¸ºÇà*OüHÌk9‹ô@'˜Ó–™–2KgÈ<¥‹¼‘-\|“•Lzõ¤,¡DŠIá‰-E,ô’*YyÃ1DÉ†×x1<ÂÚ˜¢éPÃ4…d©Ä@5w¾=U.$Ôˆ1ÿ¨Ì¿·v~+q£ØÄñ<¹ÍÁ<;K¼ä€¶é½Z{†oTÑ…@†¿‘ÇjµïcÕj¿/êGaSïÏ2ôşl&¾é°z¿¹•ŞŸ#rÏ"½?Wä~–{V¨÷[½çëÔ:.j¥î‚©Ö¥¢×ışÁ?X‹_£×Y-ôú»¦z½¨6ë¸³Ó+-ƒÏÇ xûm¬¹Ûµÿ>ªöcƒ/ UKè½PD¬)yÕ‹D¶cIw/Ù^¢e;Ö×oé—ò”/3¦üƒ`<™iè—†~Ó¾20´q®^EãxÁ®‹·WAptØXéÏdñ²ÎÏ‹|!N½FD8Dx­ˆğ:-Âñ¡ù_ODUÙŞU*˜UÍ„ş¢£Ğ¿IÓŸÒ¿Ù§­¥‹ĞŸHôoú·iúCú·=%Úu¨Úær¼S@Ş¥AN
Aş@h¥-#=à¶¢®¦“í‹ø¿mêİs2Á¼G`Ş«aNaŞ‡G¶™‚üµ	û†RµÛÍí‰˜z?ÆH?ÑÜqœöñFîğW˜?Öû¸ú€ádwøPèd™~jHª7÷†°74WâGEúÓHú‰ô×ÒŸJÿ‰À¼Ü^Û¯Ò–®PŸòÓ‰üSBşiM~zHşß#V±Ï)û"”yŸ€3àsğypFğ š7ß<£Hü¢PŸIÔ_ê/kê3Cê¯øÓÖMÿU8‹ ¾& _× g… ßğ§•é‰“öÔª•ê›B'òo	ù·5y<$ÿNà;ùÖîqj÷¸¿{|×pï±{|?tb’zóê¾wÔ¯Í?dïàšØ•Šú%+ÔD®y$×"×µ\óB¹î$µĞ~"R|ã<OıDèÏ!úŸ
ıÏ4ı9!ıÏ‰ºB`ğ„ñÁ˜O¿Œ_iŒù!Æ¯	ƒ&„ÔŞ!óœB%|<_Š»(óÚù?(ÜÛñ¿¶xúàK¸w	îİ÷Ü÷·ÍôºÂïÒ?±ôº‡´jÖ÷î¾àî õºéf¹ºO&LĞ„¿“	¯'LøÖ¬…‰káMÖB,\iüØø‹¢œ¥:t £şHÜHÇ}q&£î®`®‚³©·OŞ¯şD£ƒã©dp2ó '3ÜÄU³Á˜ú3¾äCù°†ÔwrÌÂ#¾İ½ü_h¼yÖ¤¥Q÷–¥¯t×[=f°R)Ä¶[ÃºÆ}\8ù~Œ©¿#éÉ¨~Õ?ÄmØÌ´èe%>”xO¦cÁZOıOzÔ¿êà·bòoÁ~’±Ÿ"ì¼;Ã¿=£æ‡h@pÙ$¯›€`Sño@Ü»3#y™|¾ôÕ,²mÁA`%ˆì˜šŒïÁÆFšJHéé}9…^®§¦á#m¯&´û¬=›C¥_—VÓ1'5x›5ƒÆóQ î¯¦gàn¿(f&ë”Ka£s·´“7E cjMŒvß›ÓG…§¢š¯{Ò³išL¿Ş5«9<w,|TMÃÔ\â‚V6«€× ƒyÛÕ1Æ¼ÇÊ¼ÇÕÎ;®Ç#+=ïeR.P'&Çç)º½m)_ÿ'²ÖN2õ^şOæ/µ–Oáñ§ò£zå)+4OŠìÌ“Ú´úYy–8/RV+%Û	j=Ôzºˆw†ï¼0+IâåµT>_g1_ñ&|-Œğ˜ù3Ìz¶¨w!ÍŸùçéùEm½ ç42×¬ëó¼soA-Ş¸Jšò c—;|µ±lç™6Z\c£…¦ñøÅMtA¤Gl£T3-&/2µk™‡6ZÒÈFK™¯eMøJ™–‹NS4ÿ
™¥?ÕÂF4³Ñ*ïBÁ»¨o\]\c£*Ç“>öÇŠÀÑ`)¹Dp:'XJŞ¥äRš-XJ–KÉex×«ÆåB}…¦Ö«Æ^5VÓ8^&ò¼4Ôœ$¬¡¯i-ğ]g-«|é:Ëj\çJÓu®âñë›˜ˆHØu6Æ)•î-•ƒ »@m…/#nQ7k…/hK#êdî¶6ánù3ánqGéP•èFøó³Ïrbìjal»flyÈØFŒídÆÒM[ñLÛEŒQ-G··p<Ùrîİ­ ©L‹×hW„,^aQ/´İÌâu¦'¬ªñ„Ó®çñ™&"iè	¬HZl°®)u%RàÂñ*âØ{5Ç«Z„k_y¨ÒY¶²]e@[ ûkÇÕ@#+9,R®‰H>+å›ºÏ…$éa¬ »0´Í ÉX´ªÁÛ-¶…¢ºˆ!¨gJÌmÙ4ØE¨]¦£Uari.q©Ê•$J4)aÄcF‚LôNd¢
éÑì8^$£*¾Êëşâ 3À¬Î<5óºu8Â2‡Ô3ÌS—0ÏıAŞwá½İ,ÙKcä B:qf›Vİ(&í Íí“ùÆ´æ:BÍ=‹TŞ -H¾'/ªgĞåt“ İ¬.ƒGvZyš-4şòÜîËs“/O½<5ôòÔËcèÔ(O½<]Òè#õKà8Ô»ËSÇNŸşIïO¨C–×M¸ç²ºÇêâsú¼ÑEËëv—>c¾£œåákL‹ìg¸—†ÑøËê éˆztOŒO¹Ò“ÑT·’2ÒSèïL¨ç‡ĞÔ0¼B¿o!ıÂÛûvÆ~³ÊLb“ Çyê…xÜ£^D_vêƒ¤L2A/"'ÚÔ‹Å«É/¼T›`uh‚—ŸrÃ0›µ©eB×#q_¹LoRÕË¤WÒ+ë‘^ÅÆô•§-²G˜¯&ÓJÛbÒ¥m:)—U¯aMLå{¾êµ4FG¿E~=‹,dš‡”gR¾Gê6À™øMü¨UàÍ4"zZ Ç(+V¨·ˆ¼kù8Pä}›–w­qèk.Ò+¤=É;„~Ÿ
ı»4ı:ã$õE]„úÓìw‚Ñ$è?öÄ‡Ùïø5ÿ^Ÿ†_Ód¿¦ÅşÏ6ğ¾:ßÏêü@ Î|‹³½²J›Ÿí}Hø^O|Xøşˆæ{}¨–új­;Åù˜Ğo úı'4ı†ş“DO¦Ô‡c´Z-^¶B}J¨7õ§…ú3šzcHıÙĞ(­ÏÆ®jq6öPƒ³±Ï‘×jı<+õR™İ¡ŞÒˆú"
ÏÑÇÔ—|mÈ¹®ú2}¦š7*9\ÚÔy½ÅQ0oÑW—Fbê+„Şô0xKñƒn ÑW‰ÿ™Qÿ0õ5|öuö,¬Dó#ºw9…îù«o’]pgH}‹†à¶-,öˆEï€Ó®Yª¾-–ëœ(÷¼Ôw|ÓË;ê»øTéõÛ–Ç«½y=õ÷xêïSÿEËLú=é•TæÑ_¨ÂŸˆªÒŸq¨ò_İX*o,òÇ#zk±MıPØİê³û#Òz”Ë­&—w0—?6¸|´–Ë;5—çÒZ*¹@ï"ãUÀ¦/¥´©ŸÛ|.~ZÏÅ6æBûäÏ˜‹Ÿ>™oqLûÕø¤õ—2ívŠ²_áwDÙ¯i4c¶‡Qöß‚:Fñ1ªîâD|·ÿVï‰ïÁ#7ë=	a_×r*Dn‹#bâ¥şøc	¼^‹WFğŸ`ãÅ¾wá)3øÜ¦î®æ³Qáà÷šƒ«›¤Ö«[¤Ö¿¶J­`ÿ1Ôx‹Ôz?kœ{_FÇcÆwÇÔï
uögR8‘ã.UĞ0Y±¢]=$ä»‰üa!D“ïÉÿª¼uVL·ÈŠ5È!’Wjü+ëã±@’ærö0ıuõ8lÜÑÿ+‡FÒ{]¸¤eœÓı]¼–ü‡ø„ğÚPÀ’~håÂ5;~ıKÑÁ==Hø‰6¡ş%PİõozRCu‡POùPƒ%\'vìè¾ñi¹@	È,Q ×… ñ(ÒŞk|ÃÀ×NLMA]j?àgÅkZ˜åñf™LhÚ,Sğ;s‰G.¨ò5kT–(½¹˜†Q¼·ğÊVŸ47i/¿ß@OÇ÷x†ø†Pà™x$W*ò­W©L‹UêoD‰‘(úÒËQ,Ê,E–¢¿GîªÕÙD ÷9øU÷ošfZu4š»Å"ùæŠ|Çhù¬`[­+Ûc™ãşaV¶<µYÙVØ+qõH€ï°jÈ'1¤êÊ»Š¢!şmB-ñşÅÅğH\,r-;E~¹\ÿÙ'uŠH×KÒ*Ò¦¥ë¤“KG§š>ƒ¹:ÓôŸQM÷AÓg…šô½	.Rüj©7Œw°’tÂ^Ğ¦Î~úø\Xø™§ùé«Õö9ÌÄ|ƒ‰™ÚæéMmŸk°€i“í¿£d!@[(ÀyÌÄ>~¡æp§‰jš…"G–äX$r,ÖrdkåH1/ç¼<iÊÁ\˜r´Ó½K˜v)ÓrôÒ%Ë&75–Ñ(iLø·é-ÀÆ7Õr‘ ŸOE‚•Z‚ş0®/À£Æw6V	½Cô
ıEšŞ	é/&zª]Å›Xj G×"‘s&,Y®.tÈ¥$‚\†Gºb ›zÍK`»E|ªAr¹ÜĞô¬éÕ¡¦[PkXÓüš#½2yHëæõ÷÷/PkE¦=$Ó:‘éJ-ÓP¦«H15f²5š—èF³Ñe^/ İ  5h!İD |á˜®ÓãÚ¢0ÇĞÑ¹îeş6Ô Am¨N5Bm%¨šNşÒvµMˆ‹|²+ÄÛ5qÑ8Ù%â†üB_"ú´ĞïÒô¥~7Ñ7íäSFF™0®Œk5F9Äè¦®Ì¼õÖ{:OĞ×tFCç›ÔùõãÓÍ{ëãêÂ÷ÏL,ö¾^ö>YÚEó•[s…¯Cı$‘eb›‰—$úiTãˆá+$¼#Âç´ğ•P¯y²MóˆŞ# U)È ©† ÅĞ8­#Zµˆè	r•7oÎ–µ”Y-n¨–­µ˜ ˆN(Od&™*"SUË4Ê4DŠ9òˆĞĞQ:‚î%Ğú0¼QˆG‰xŸiâÑøYDÜ0Ÿ-ô{‰ş&¡¿YÓïéŸZ©.„Kò†Pâ²Ë.K¨ç	äAŞ"ãr¨Ièµ‰õÆåF!ßIÙOŒéßàwz‹+söHÆ¨‹zØ­z˜"äøWÚs¶àĞ>¸Ú2ÈÂç“DÆÕ¼°¥nÉngÉèe¢3_Ô*2éBR{<õÿSgCbd—lXn(™ş'Ç°Made with Ren'Py.init -20 python:
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
                renpy.jump_out_of_context(self.node.name)Made with Ren'Py.RENPY RPC2   .   Ã     ñ  Ã              x^İ\ÿãÆu¿‹ãÆİºq“¶I¿—aŠòjéİs.1Ö¥ÁÅqrö]ŒìÅ8@'”Ä•˜¥D‰¤övcĞş£ÿIÿ†ş;ŠşĞ? ?Õù¼73ä9¤¨uÙ g‰œyóŞ›÷mŞ{£ıÊ«í]ïù×îÜ¹s¦Y”¬·_yüŸ~|çùkxtŞl_{ş>íÖq2»çÛ¯îÆÛ×½Y®77~åG?]GùÑöúÿ¶ıÚÓWÛ7¼ç_Åğu°
·üüŸñqïd³4ÚäÙ;Y¤³ådäáäb·åX0óÓÍÍãÿ|óå“ÿxíóí‘ ^çÛ?yÊkoÒ(I£üfûæãÿıâ‹/áY­Ãõn5ÓíŸ~t—‡]DqÈë~ı€u·o=s§DİöÏÆÛoh”}r“/“õÑö› íÏAÛ_ÚfÉ<Üş¥1îm¿…qßö€Í|çÎQ´Ú$iî¤áÑQÇ“,òp®ól­çáu8w†Îg—œ+ç"I«séDk‡ˆ
Sõ‡‰{¾à/À¬ò¬ÿêèh^8†ù‡q2âŸÄ§Éê)ñÖø§ÿàÈÁ_æ»tíØÑÀqŠæ¤Í¯MH-X0¸„ö$Ùeá'IæÉùŒÎjçÑ&ÂÄŸù§ï|¸‹>ˆ™-ç³ {ºğğtàÌ X`S>üqgaŸçò?›$ÃÌÍ³eEKø‹0Ÿà±'FI‚=LöÊÕŞÆ€Ñé¸? ‹kÏÏÆı¾`ÂpÿQÍ.È‚éa/†g±28^V¢ÅŸ–a´XæDØ™sì`îÛ÷¾Ï/^Fó|IÏï¿WN¹$YHãrÇ<ìäìŞ½S]8jÌû÷NÅvÒŸ6QäW7&¼³ñ±Àçø{§'ß»_€TÃŞO©Í}OŒ4x)ğ;Qá³ñ‰š&¹Ş<Zëu“ç)m§Ÿ<½)I›”B²Ùxio&fG/zîØóßşAŸ?õÎuß_¤Énã‰¯gá&¯sW»,š¹…4Ÿ³Îü(Ìƒ(Î¼<HINHà¬X/f9L”1°ıŸy²±_,”<’¬PÉ÷³r6-4>‘±)©†‘ ‹§ÄQF1W™.ğô)–ççÓÅjû3`LÈâáë*ıˆHt'K JÒV²bYêHx½‰ƒu@ãj˜ƒåŒy4S3øÍä*‰­ğx8¸QÈËµéÙ:y) æË`Ôá$½õ)9ƒ{ë$]qçÀtL’tªsB‚	rHÛtÂrBj:êMƒ,„ğô@kfä×è[’/Ã”>02ôa‡Áš¶1ËzÓ/’İz>a®—»­Ì·¼mâ­˜{¥0l´œeªbuAÉ^Ëè!ï6‘\E<·<–|-GM¿²n»°^KøUHgîø—z§Ëş	Œ[a H…ÜÛ<ŠÒŒcm¾P€Bÿè¬-Yc[°;ùÍF:¹á°ˆCügi°Îblk‰"MÌZ„ê®+—S’Ô“är·™¨'¾Íá™¢ø«E‰#!÷u<ÎÍÒ)º
åöƒÍ&\Ï‹™uÊÃ´ÛI‰I»Ÿ@û°ù£‚1§ ÅÏ’]:«ğƒ0\Uòö,İ	³¢ÿI{,ö±nÖ«k˜ì‘,R0h#¯g"¯VäW#9~ŒE«ğü˜Cîylş°ˆî$yÊºŸ½rÎE0“]><í÷|‹« WúÂc©?Á!èÌS8Øœì6‚Ê²ñÛ—IË$¼†2M•;GÁğ0JRm»´€ÆB<äseÜVlú^ÃÈªjæ4ƒË[¤2AµH·ôsëÚ9F¬X¸Wc•úÎ–±´üdİ'Áæ<Ìm³;è¸Ó
†Š”iê¤Û8jyU }çáĞY
ÇE2ƒ¡ÑB5s»Éé¬¶	‡1àç!dı@Cxk$tgÏû =è¸	3j°J£9¤ºG~†SUîõ†½>"sx³—aêõıaÑÆë“Nyn;câ¹¦µnc³i:La5ô<ˆLÚĞ±’i	m÷Ğ*iôÓQí,ôz.Åu½.4ª€’){m~–N—ß‘¦2=)ƒq¶Â¤«øçËäåÁğ›8àŠİ–èl<8dšÏ9
†ïqâ*ƒHëÊw{P®hgÔ9ª%Ô«ğG§î‡C÷<·n‡â2(¶"nR(M O_xâL:xÑ§3iÍDGTK(ÛĞı"Ós•ªÅu0ß"¢ì?<›¹¾Š:Î¤å^RŒİÄã,ÒÁöºP¯×ÊàŒ@|wìÀm»8knê¯ê+çÉeÈ§f †Ëu*F‰ôçsqDÓüM²ñNë‘fª¶»ˆÖşÉjEì*ÌºS²yùîQ,´^ 9dfÙÃÀå±½c…š8‚ñ„p©däúÎûÎ½æÊUA*şw¼‡j±*›z"œÄYb=÷‰,ï³W#>-‚RÆÙ;‘Ë©ï”0™E$;-NRfFÆµp¸¶Øúé™àØ·AšÊ8(W#FÁ}Ò9±[ı‡gÍlß ­´Ú+²j	HŒœ€="\ZD†7ÔaÚXš4$íˆPÓ_•ÜÖˆ—-V‰Ø:¹=jœhhÁ­]ˆš«€²NİÅÎ£Ï^!²®::1a‚k—P+Á%zìÚQdÊ!ÕÁ×léûl‰a›sÇ`xËY¤vô-²|Õ­lgU!+£'È»ıRH
*[ÜC¯D‰‘U¶	g#˜øƒŞ
éú0ÈDU¯®¨#‘Áu\ÿ—I$|—¬¼ÍêÒÉg=½hW<}Ä3)ƒPcc{˜+ƒ
ÄEFr¸¾4Ü&	HÛˆğx0D…r±äê(ÚÊ„o¶1rDóëI0H1Ã/VĞò©$ƒZ~u¤Æ(c¦oZDÒ:wÔ£ô_XÛj;f	2fkKF©Ù—¨k¨Vv°‹¸RlMáˆ=yv>«Á‡é…(–qåï¿t×æUkQÓ‰Q/ÈyûF!L
3\w¼.2†’èwÇv³ÀûU’Î‘N/òuÂıÎ ‚<.gãËc€gê&mu"O‰6²ÈÈæ'‰êéšK&çÚ×«Uåë­[³¯È#´•4µ9Ø8\×ì¡Pô+Êï7i…á¡	Ò:w1m4ïp\m1ÃÊDé•M"1™„©Õîµ¥6yØèÂx+>–V°yÃC<;mEñO«ÅÙÄÂ‰Ù5íf•9ÂòÔK‘`£Y›Æ‰À5£lÍmæ¯,›Ù'{Ê%Hvùb?ÊdûiÍ8$ÛEĞê_÷‡$t¤¸ßA”as¹£Øğß¹½±úÈÕÙƒ–µ¿$s©›Bn‹ÈÕLòDnÎ1ÙH°¹}ƒ¤ùkß'Ú¨ı`šµØïëÖó°&ã,atTÕ½µ”zVZZ’ö¸á6ÒÍ1‰*<È¸ä°SYI…µØëDM§;º¿Gö­gúÑ†XˆöhÿÉwÿR¢—¢“IPdÂrÔj&÷2m‘åPBè
<âeA'FšW4FöÙñSÛgxM9³şÃá™Öå¤ØÔİÚl ×Ê‰oE<X~1‹qe¦ÙTˆê²Ì’ô
­*v²Ó…öÄìï‘ïÍ‡ÅèjGW£µ:Ô¾c8—Àoù“ùœ
™å;úV¼×Ï<DPŒ*2×ElÁm@Å{JÄó«2#_¾+˜R~¯1<¯>ØxQÌ¢º¢ÚSn9’/ø³x'ú*Ó«££Yd™ƒò+:ÎÂpıiFÁ4AV§ÁìÒ½„çGh§ú`»C—c~#ƒIê9œ Ï1Ê'/ãÊJ‰éÔ) h'ñÕ ª>ÚÅÔDPy ÿ#–¤çrI|Æ©Xpàà½~ıd’üÇ»Õ†ºşĞ)’æ’L¦ J¤Ê²àU7ÜYëji\­É®šÂ®¡+˜†”]4‚B´íqYÍ¶¶µäúÜÔ†Q?#*r`÷¡å´¥eÖœ…¾ 1§?ø­¬:İ&»bbİ—q…eÔ%Lí}işZ|\r&FÖÒ‡¼QõP¡Ë, e¨PÑ³µmKZruM_E'µèY®:ĞÆ¬I^ìq!OìÿH†k kö¶{‰â+õÓu,ÔªX•XùÚöšlsøfjAiM•ĞP£‡ÚJõ.7ª¦3õ«‰7º·€ô:÷iÈU”EÓˆ¬ì¨8úîƒ1ÊÃ–h@V·:œ ÍÜk$ÎGh³@£ë
İ¢ÁÍCåˆ¡û¥0d\	ûˆuøÎ/ø.…¡½‘úA}KéS`…ÎU6$ğH¸ zÒ[ûl¥52ÍÏÑMdöB#-$V²	Ú4èÆ¬7ÆV”»ZÉn¶Tó7†‹#‚{““¤Ô¬¿Ğ[CÒ„ï“È³‰OÅpÎ—Æô}4,²ª+<æ_ØM¯B4PÎÄÊ‘3½]ŒúËb_£Ê”Eáû‹•‹<8 >:ïÈÎˆÇÚ¾)FÙ³!dé¸¼$æÕÔÀË)e‰3¼;q-9©Æ^WÑàêåÖj‹+o˜à"Ni_Ô}š{GÛm´ŒÑ•¶5£{ZM§dOÈp'Fã…Égğ™ÓÍåÓy–ë*Ğ	wÿTo;ªvGµ.TšŠ*)°©Íù®:n#BZğŸªN†¢‹rØ?èÂonˆFg¨"XVÌeÉÚà€#ñşZ¿j¦€ášú(nÜ4µ±¸Ğ}-“bºo—ƒê/ı…Œ{å1[™æ)ˆë(X—¨*ªX—hY(ày"zË^FùMsätr¿)m[@!CMè-¤ë	d1/ªİA´}JÏk÷}RĞ:j­—T$ğºÑ(7ƒC(Ò\Z„ülóF;ø3*…s:ydB4Å;ì#Mµ‚Ñ¬¡h\ì¸Á§6%8¯Ä»s«yj>w¶ŞÉ)äÙ¤WŸ,B‹A¬êˆZEŠCK¬ZØnHé ˆŞC¯$Ç ³gû*L ~Íìor\õLT3Œ¹¸PÃyšw¬¸×KXo³±UÂÑÅuII^ÌQQzZã;5õ¸£Òj´Çó(Ù°t¯ëÀw+a=z¢¤§Êb2—Rßû:DK„·—–îÙ‘ê»
WIÈ%¸7†Ä¼J„ÒJ«°«>9{gŒ]ög»lÈã›	yoÑˆ¥ó…ïvŠ7åj8<)şìmOÖÀ\5İ:ëûúUŒl9!$¿d„ËkŒ/¼ÊÆÑÀ©e”ÚÌ‹Œ¶Ô-˜Á—öè)¥Ş> ïn%!Ô|è’Ùì3•ÜØfĞD¹`6¯¶'·(Gnk[jOzsÀÚ—ÅQPãnØ—²3†Ê”±)æ"¿Ù§ätãq±z·FÜZ‡Õ!]_–—Y{BùëŞÄª_bá:·í\±D”|)š"øyº±+® q‡CM«$ŠËÒí«yİÁ–V³¾²­_f‰w9ÿZ5	òÃ»·ZBİÖd{ß-˜ôıV¸âÊ²ì>/—Q;S%Px<ÍìC˜›‘ÙGÇr»œI7¬¾–\G‘NFdVÛ¯&·5¬Ò†8¾¨Ü¾ªJ×tÜ(äÚÊîM%m„˜M´=§w,æÉ2pm­ıºÖËw·%$®lÚå{«¶“WÀÔéZl«L>ù|E•nú?|ö1_z¥/²îEµ\²^ugQCEb®Å†ò¿GÔP‡
aURm‘&-Õ­Û!–U!­rƒ|zg¹gÔ-õC„›KÕaO’(Ö1¬6§ZBûÕb *U†ü›å¬VCí®ÒêJ‘sE¾É=kƒÅæ¶¢cÂ¶ÈNcK&CqÑÎòfÑ*Vş]È–êGî(cåğ²¶ÿ<YX%­ä9B#v]EÜÇ)Q@bÙ«Å±Ş‚ıEü ŒópÏAÓ~€”ı{åzTfà/—™.h÷"³	~òdà(”D±¦ü9I|õ†zÅËa¶~hfœ/C˜\2Æ„ß±yS¯™"\¦šğeªŠ‹­†ŒÚÎZï…—âô'£è'–ç°ÊºŸšòLKê/é€ÂÉËe"úèñA^HÃ§ÉÌªı¤0[¦şf—áÇ—@ÿ=Q7vRŞî	Ò	Ñ5ı| äøLãøm¶»ÀÛ®çS°ª TŞ„DGËc$´O,×jÄ¥Ljì.™VÀBĞ‚ã»şAêHe?f”7<Ûª(†LğuÂ2¸àÎº7É…‹.á²Íûqk[Ë½ÖIÚÑ2×:u®QC×½3"Å¯4i9ÕêaÃJ&WÔ2×rª¡Ãö
u!¾/&×"£,—ñó`a÷¥D¢œ‡ÅQG[ÁÓxxWàR½q§\¯á q¥†BH«j×»r,ÚÍG;‚aâôDğå'Ğ•8ü´¨gv–ZYy	¿ 1v(Xnmì;aPÍr‚â~à·&ùT)BŠêvÿhûWË·>ºË?Şöùö¯ùçÑğÓf³íßäSş²Ä¢íßşûò Ÿ‚óÿÿõåGw?ßşİòëË·–øy·%~~¥éÚş½öùv¿ø¿ökl?å¹í?â×ØüjÛw<L'(ü»qåïmİ§‡¡õ_ÿóúòñöÍ»w>ßşa†eÃ_û¿Vp³Ix^İ\ÿãÆu¿‹ãÆİºq“¶I¿—aŠòjéİs.1Ö¥ÁÅqrö]ŒìÅ8@'”Ä•˜¥D‰¤övcĞş£ÿIÿ†ş;ŠşĞ? ?Õù¼73ä9¤¨uÙ g‰œyóŞ›÷mŞ{£ıÊ«í]ïù×îÜ¹s¦Y”¬·_yüŸ~|çùkxtŞl_{ş>íÖq2»çÛ¯îÆÛ×½Y®77~åG?]GùÑöúÿ¶ıÚÓWÛ7¼ç_Åğu°
·üüŸñqïd³4ÚäÙ;Y¤³ådäáäb·åX0óÓÍÍãÿ|óå“ÿxíóí‘ ^çÛ?yÊkoÒ(I£üfûæãÿıâ‹/áY­Ãõn5ÓíŸ~t—‡]DqÈë~ı€u·o=s§DİöÏÆÛoh”}r“/“õÑö› íÏAÛ_ÚfÉ<Üş¥1îm¿…qßö€Í|çÎQ´Ú$iî¤áÑQÇ“,òp®ól­çáu8w†Îg—œ+ç"I«séDk‡ˆ
Sõ‡‰{¾à/À¬ò¬ÿêèh^8†ù‡q2âŸÄ§Éê)ñÖø§ÿàÈÁ_æ»tíØÑÀqŠæ¤Í¯MH-X0¸„ö$Ùeá'IæÉùŒÎjçÑ&ÂÄŸù§ï|¸‹>ˆ™-ç³ {ºğğtàÌ X`S>üqgaŸçò?›$ÃÌÍ³eEKø‹0Ÿà±'FI‚=LöÊÕŞÆ€Ñé¸? ‹kÏÏÆı¾`ÂpÿQÍ.È‚éa/†g±28^V¢ÅŸ–a´XæDØ™sì`îÛ÷¾Ï/^Fó|IÏï¿WN¹$YHãrÇ<ìäìŞ½S]8jÌû÷NÅvÒŸ6QäW7&¼³ñ±Àçø{§'ß»_€TÃŞO©Í}OŒ4x)ğ;Qá³ñ‰š&¹Ş<Zëu“ç)m§Ÿ<½)I›”B²Ùxio&fG/zîØóßşAŸ?õÎuß_¤Énã‰¯gá&¯sW»,š¹…4Ÿ³Îü(Ìƒ(Î¼<HINHà¬X/f9L”1°ıŸy²±_,”<’¬PÉ÷³r6-4>‘±)©†‘ ‹§ÄQF1W™.ğô)–ççÓÅjû3`LÈâáë*ıˆHt'K JÒV²bYêHx½‰ƒu@ãj˜ƒåŒy4S3øÍä*‰­ğx8¸QÈËµéÙ:y) æË`Ôá$½õ)9ƒ{ë$]qçÀtL’tªsB‚	rHÛtÂrBj:êMƒ,„ğô@kfä×è[’/Ã”>02ôa‡Áš¶1ËzÓ/’İz>a®—»­Ì·¼mâ­˜{¥0l´œeªbuAÉ^Ëè!ï6‘\E<·<–|-GM¿²n»°^KøUHgîø—z§Ëş	Œ[a H…ÜÛ<ŠÒŒcm¾P€Bÿè¬-Yc[°;ùÍF:¹á°ˆCügi°Îblk‰"MÌZ„ê®+—S’Ô“är·™¨'¾Íá™¢ø«E‰#!÷u<ÎÍÒ)º
åöƒÍ&\Ï‹™uÊÃ´ÛI‰I»Ÿ@û°ù£‚1§ ÅÏ’]:«ğƒ0\Uòö,İ	³¢ÿI{,ö±nÖ«k˜ì‘,R0h#¯g"¯VäW#9~ŒE«ğü˜Cîylş°ˆî$yÊºŸ½rÎE0“]><í÷|‹« WúÂc©?Á!èÌS8Øœì6‚Ê²ñÛ—IË$¼†2M•;GÁğ0JRm»´€ÆB<äseÜVlú^ÃÈªjæ4ƒË[¤2AµH·ôsëÚ9F¬X¸Wc•úÎ–±´üdİ'Áæ<Ìm³;è¸Ó
†Š”iê¤Û8jyU }çáĞY
ÇE2ƒ¡ÑB5s»Éé¬¶	‡1àç!dı@Cxk$tgÏû =è¸	3j°J£9¤ºG~†SUîõ†½>"sx³—aêõıaÑÆë“Nyn;câ¹¦µnc³i:La5ô<ˆLÚĞ±’i	m÷Ğ*iôÓQí,ôz.Åu½.4ª€’){m~–N—ß‘¦2=)ƒq¶Â¤«øçËäåÁğ›8àŠİ–èl<8dšÏ9
†ïqâ*ƒHëÊw{P®hgÔ9ª%Ô«ğG§î‡C÷<·n‡â2(¶"nR(M O_xâL:xÑ§3iÍDGTK(ÛĞı"Ós•ªÅu0ß"¢ì?<›¹¾Š:Î¤å^RŒİÄã,ÒÁöºP¯×ÊàŒ@|wìÀm»8knê¯ê+çÉeÈ§f †Ëu*F‰ôçsqDÓüM²ñNë‘fª¶»ˆÖşÉjEì*ÌºS²yùîQ,´^ 9dfÙÃÀå±½c…š8‚ñ„p©däúÎûÎ½æÊUA*şw¼‡j±*›z"œÄYb=÷‰,ï³W#>-‚RÆÙ;‘Ë©ï”0™E$;-NRfFÆµp¸¶Øúé™àØ·AšÊ8(W#FÁ}Ò9±[ı‡gÍlß ­´Ú+²j	HŒœ€="\ZD†7ÔaÚXš4$íˆPÓ_•ÜÖˆ—-V‰Ø:¹=jœhhÁ­]ˆš«€²NİÅÎ£Ï^!²®::1a‚k—P+Á%zìÚQdÊ!ÕÁ×léûl‰a›sÇ`xËY¤vô-²|Õ­lgU!+£'È»ıRH
*[ÜC¯D‰‘U¶	g#˜øƒŞ
éú0ÈDU¯®¨#‘Áu\ÿ—I$|—¬¼ÍêÒÉg=½hW<}Ä3)ƒPcc{˜+ƒ
ÄEFr¸¾4Ü&	HÛˆğx0D…r±äê(ÚÊ„o¶1rDóëI0H1Ã/VĞò©$ƒZ~u¤Æ(c¦oZDÒ:wÔ£ô_XÛj;f	2fkKF©Ù—¨k¨Vv°‹¸RlMáˆ=yv>«Á‡é…(–qåï¿t×æUkQÓ‰Q/ÈyûF!L
3\w¼.2†’èwÇv³ÀûU’Î‘N/òuÂıÎ ‚<.gãËc€gê&mu"O‰6²ÈÈæ'‰êéšK&çÚ×«Uåë­[³¯È#´•4µ9Ø8\×ì¡Pô+Êï7i…á¡	Ò:w1m4ïp\m1ÃÊDé•M"1™„©Õîµ¥6yØèÂx+>–V°yÃC<;mEñO«ÅÙÄÂ‰Ù5íf•9ÂòÔK‘`£Y›Æ‰À5£lÍmæ¯,›Ù'{Ê%Hvùb?ÊdûiÍ8$ÛEĞê_÷‡$t¤¸ßA”as¹£Øğß¹½±úÈÕÙƒ–µ¿$s©›Bn‹ÈÕLòDnÎ1ÙH°¹}ƒ¤ùkß'Ú¨ı`šµØïëÖó°&ã,atTÕ½µ”zVZZ’ö¸á6ÒÍ1‰*<È¸ä°SYI…µØëDM§;º¿Gö­gúÑ†XˆöhÿÉwÿR¢—¢“IPdÂrÔj&÷2m‘åPBè
<âeA'FšW4FöÙñSÛgxM9³şÃá™Öå¤ØÔİÚl ×Ê‰oE<X~1‹qe¦ÙTˆê²Ì’ô
­*v²Ó…öÄìï‘ïÍ‡ÅèjGW£µ:Ô¾c8—Àoù“ùœ
™å;úV¼×Ï<DPŒ*2×ElÁm@Å{JÄó«2#_¾+˜R~¯1<¯>ØxQÌ¢º¢ÚSn9’/ø³x'ú*Ó«££Yd™ƒò+:ÎÂpıiFÁ4AV§ÁìÒ½„çGh§ú`»C—c~#ƒIê9œ Ï1Ê'/ãÊJ‰éÔ) h'ñÕ ª>ÚÅÔDPy ÿ#–¤çrI|Æ©Xpàà½~ıd’üÇ»Õ†ºşĞ)’æ’L¦ J¤Ê²àU7ÜYëji\­É®šÂ®¡+˜†”]4‚B´íqYÍ¶¶µäúÜÔ†Q?#*r`÷¡å´¥eÖœ…¾ 1§?ø­¬:İ&»bbİ—q…eÔ%Lí}işZ|\r&FÖÒ‡¼QõP¡Ë, e¨PÑ³µmKZruM_E'µèY®:ĞÆ¬I^ìq!OìÿH†k kö¶{‰â+õÓu,ÔªX•XùÚöšlsøfjAiM•ĞP£‡ÚJõ.7ª¦3õ«‰7º·€ô:÷iÈU”EÓˆ¬ì¨8úîƒ1ÊÃ–h@V·:œ ÍÜk$ÎGh³@£ë
İ¢ÁÍCåˆ¡û¥0d\	ûˆuøÎ/ø.…¡½‘úA}KéS`…ÎU6$ğH¸ zÒ[ûl¥52ÍÏÑMdöB#-$V²	Ú4èÆ¬7ÆV”»ZÉn¶Tó7†‹#‚{““¤Ô¬¿Ğ[CÒ„ï“È³‰OÅpÎ—Æô}4,²ª+<æ_ØM¯B4PÎÄÊ‘3½]ŒúËb_£Ê”Eáû‹•‹<8 >:ïÈÎˆÇÚ¾)FÙ³!dé¸¼$æÕÔÀË)e‰3¼;q-9©Æ^WÑàêåÖj‹+o˜à"Ni_Ô}š{GÛm´ŒÑ•¶5£{ZM§dOÈp'Fã…Égğ™ÓÍåÓy–ë*Ğ	wÿTo;ªvGµ.TšŠ*)°©Íù®:n#BZğŸªN†¢‹rØ?èÂonˆFg¨"XVÌeÉÚà€#ñşZ¿j¦€ášú(nÜ4µ±¸Ğ}-“bºo—ƒê/ı…Œ{å1[™æ)ˆë(X—¨*ªX—hY(ày"zË^FùMsätr¿)m[@!CMè-¤ë	d1/ªİA´}JÏk÷}RĞ:j­—T$ğºÑ(7ƒC(Ò\Z„ülóF;ø3*…s:ydB4Å;ì#Mµ‚Ñ¬¡h\ì¸Á§6%8¯Ä»s«yj>w¶ŞÉ)äÙ¤WŸ,B‹A¬êˆZEŠCK¬ZØnHé ˆŞC¯$Ç ³gû*L ~Íìor\õLT3Œ¹¸PÃyšw¬¸×KXo³±UÂÑÅuII^ÌQQzZã;5õ¸£Òj´Çó(Ù°t¯ëÀw+a=z¢¤§Êb2—Rßû:DK„·—–îÙ‘ê»
WIÈ%¸7†Ä¼J„ÒJ«°«>9{gŒ]ög»lÈã›	yoÑˆ¥ó…ïvŠ7åj8<)şìmOÖÀ\5İ:ëûúUŒl9!$¿d„ËkŒ/¼ÊÆÑÀ©e”ÚÌ‹Œ¶Ô-˜Á—öè)¥Ş> ïn%!Ô|è’Ùì3•ÜØfĞD¹`6¯¶'·(Gnk[jOzsÀÚ—ÅQPãnØ—²3†Ê”±)æ"¿Ù§ätãq±z·FÜZ‡Õ!]_–—Y{BùëŞÄª_bá:·í\±D”|)š"øyº±+® q‡CM«$ŠËÒí«yİÁ–V³¾²­_f‰w9ÿZ5	òÃ»·ZBİÖd{ß-˜ôıV¸âÊ²ì>/—Q;S%Px<ÍìC˜›‘ÙGÇr»œI7¬¾–\G‘NFdVÛ¯&·5¬Ò†8¾¨Ü¾ªJ×tÜ(äÚÊîM%m„˜M´=§w,æÉ2pm­ıºÖËw·%$®lÚå{«¶“WÀÔéZl«L>ù|E•nú?|ö1_z¥/²îEµ\²^ugQCEb®Å†ò¿GÔP‡
aURm‘&-Õ­Û!–U!­rƒ|zg¹gÔ-õC„›KÕaO’(Ö1¬6§ZBûÕb *U†ü›å¬VCí®ÒêJ‘sE¾É=kƒÅæ¶¢cÂ¶ÈNcK&CqÑÎòfÑ*Vş]È–êGî(cåğ²¶ÿ<YX%­ä9B#v]EÜÇ)Q@bÙ«Å±Ş‚ıEü ŒópÏAÓ~€”ı{åzTfà/—™.h÷"³	~òdà(”D±¦ü9I|õ†zÅËa¶~hfœ/C˜\2Æ„ß±yS¯™"\¦šğeªŠ‹­†ŒÚÎZï…—âô'£è'–ç°ÊºŸšòLKê/é€ÂÉËe"úèñA^HÃ§ÉÌªı¤0[¦şf—áÇ—@ÿ=Q7vRŞî	Ò	Ñ5ı| äøLãøm¶»ÀÛ®çS°ª TŞ„DGËc$´O,×jÄ¥Ljì.™VÀBĞ‚ã»şAêHe?f”7<Ûª(†LğuÂ2¸àÎº7É…‹.á²Íûqk[Ë½ÖIÚÑ2×:u®QC×½3"Å¯4i9ÕêaÃJ&WÔ2×rª¡Ãö
u!¾/&×"£,—ñó`a÷¥D¢œ‡ÅQG[ÁÓxxWàR½q§\¯á q¥†BH«j×»r,ÚÍG;‚aâôDğå'Ğ•8ü´¨gv–ZYy	¿ 1v(Xnmì;aPÍr‚â~à·&ùT)BŠêvÿhûWË·>ºË?Şöùö¯ùçÑğÓf³íßäSş²Ä¢íßşûò Ÿ‚óÿÿõåGw?ßşİòëË·–øy·%~~¥éÚş½öùv¿ø¿ökl?å¹í?â×ØüjÛw<L'(ü»qåïmİ§‡¡õ_ÿóúòñöÍ»w>ßşa†eÃ_û¿Vp³IÈŠ^‡ıS{æç çåÓ)úMade with Ren'Py.## @TODO: Different colors for character name and character text for supreme clarity

image narrator_pov_img = Text("âˆ…", size=12, yoffset=GuiElementScaling(3), xoffset=GuiElementScaling(-30), outlines=gui.dialogue_outline[gui.preference("dialogue_outline_idx")])
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

    chr_c    = CharacterData(_("Creator"), "âˆ…", force_symbol=True, category='special')
    chr_nar  = CharacterData(_("Narrator"), "", category='special')
    chr_nar2 = CharacterData(_("Narrator (Internal)"), "", category='special')
    chr_aka  = CharacterData(_("Akaro"), _("A"), "#dda065", category='main')
    chr_aka2 = CharacterData(_("Akaro"), _("{creator_pov}A{/creator_pov}"), "#dda065", category='main')
    chr_aka3 = CharacterData(_("Akaro"), _("A"), "#dda065", bg_color=(1.0, 0.65, 0.31), category='main')
    chr_aki  = CharacterData(_("Erina"), _("E"), "#e3ca78", category='main')
    chr_aki2 = CharacterData(_("Erina"), _("{creator_pov}E{/creator_pov}"), "#e3ca78", category='main')
    chr_aki3 = CharacterData(_("Erina"), "", category='main')
    chr_ats  = CharacterData(_("Narrator (Spoken)"), _("â€”"), category='special')
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
    chr_mii  = CharacterData(_("Narrator (Spoken)"), _("â€”"), category='special')
    chr_mii2 = CharacterData(_("Miiya"), _("{creator_pov}M{/creator_pov}"), "#EE3D00", category='main')
    chr_mii3 = CharacterData(_("Narrator (Spoken)"), _("â€”"), bg_color=(1.0, 1.0, 1.0), category='special')
    chr_mii4 = CharacterData(_("Miiya"), _("M"), "#EE3D00", category='main')
    chr_sai  = CharacterData(_("Sai"), _("Î¨"), "#80adff", category='main')
    chr_sai2 = CharacterData(_("Sai"), _("{creator_pov}Î¨{/creator_pov}"), "#80adff", category='main')
    chr_sai3 = CharacterData(_("Sai"), _("Î¨"), "#80adff" , bg_color=(0.5, 0.67, 1.0), category='main')
    chr_sai4 = CharacterData(_("Sai"), "", category='main')
    chr_san  = CharacterData(_("Naomi"), _("N"), "#f8f190", category='main')
    chr_san2 = CharacterData(_("Naomi"), _("{creator_pov}N{/creator_pov}"), "#f8f190", category='main')
    chr_shi  = CharacterData(_("Shiroya"), _("S"), "#acf6f4", category='main')
    chr_shi2 = CharacterData(_("Narrator (Spoken)"), _("â€”"), category='special')
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
                    return "â€”"
                elif gui.preference("speaker_indicator") == "circle":
                    return "â€¢"
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
Made with Ren'Py.RENPY RPC2   .   ã       ã              x^Í\K—ÉUÖx4x\HØ 0ÆvNŠ¡³¤V©ú¡–4¦f¬‘Zc½Zƒ%D›¢I²2³*“ªÎ¬|”Ô8öBØ³aë•Ík1KşóX°0~ 6œá»ùˆÈŒ¨êÑÀÁÒQ«*#âŞ÷7nö¿ô"yÍÚÿò©S§úiÆQò¥»ÿõäş©ı×ñhê'¯ï¿‰O‹h»SßKN/’7,7õ£ùqÏÉòÎ(Ì;É/u”|yïEò¦µÓ#çĞO¾²ÿ6>Nğñræ¦á<Ï.g~¾˜Ûnà¤›_/'»ÿüÖ›ÁƒŸ½şqòË|µ”'oí1Äó4ŒÓ0?N~åÁ¾¶ßÁ“YùÑâpä§É¯ŞãÔÃ™ÏP9!Ê³ûo`Ùˆö”üÚAòUq?‡ÎÄï$_Ã†~ú¾!7öüäœ0í£ã›xÔI~ó~Ëº÷š4´{4O;É×÷ÿ+c3–ùó¿zi®Yøş`csİ8Çcğbğá"Üù‡~”?rllbmu×#íè¥­>ÆãENLÈ“EØóBgO¾]<ÒÃyê}ÈÈõ-³9Á½#³{ĞM~;8{ïõ”|Ûü«ÉÛo6yû­àìâÇ#‹ß`"Ë“o3æøOYbä£à¤ûî¿ÿÇÁİì­×N}œ˜LÕœ|–œßÎg™2†‡&Ğßİ?ËÔ)M<NíyüÔÆĞËä ²ŞÚEş¤¿‡}¬YÁW‚B¡ş
eaN@ªƒù§	z qw’îL¿hçá:D|}ÿßJuü1¿k®³Ln››ü‹^v—¶»|ÊÿŠ€8(7ÅéÀ<¿á:ŞöuÓÇÆœ5Ë¡4=Â¶ka×Øtß³³¹ïLıtíÀğg™o˜çÇìÙM.A€§!õ¶Ù
¾	¶Ô’=ô
Éö&Ğ Õ‚‰j#à"
¸Xœ<[LC;Œ¼Ğ%ñ¼L6›e±lÑ¶ –¿‡X®bé”bÙab¹Šé×J±\çbù×%bÙ¸r±üB‹ä]ˆ¤‘|[ÿ}IGI'øN!’,’gL$ïÕ"9§‰:³ÙËä}¦ÓÌwî† ˜€`>s¦ÌM&˜[˜¾[
æ6ÌË‚ù@´—ş*Állö²ÄáÁ¤~¡e÷!dw²û¸s‡dwFİ™à{…ìîÊ²;f²»WËî«*Ù^&÷!·3¹= ª=Anÿ¹=dr»ûégŸ}†çJÉ}$…¥<ˆ£Nòå÷â‘Ù3'ø‡êş×¾uêTÇóÇ–V>7w&ş­N:YP¸Z‡cŠÈeİw™Ÿb?àœˆ-Pàï±YG˜5lğ‰Õdú>5Æğ = Hk!Eâ5#Œ*\ÃşÁpã †#Á¢/ùQnçşáP9„œÿàq½ôæİ
+¹Hè*8åæ9A5¤
ä³ĞËPQêÏO­ş:ûÛí±	Õtğ1?Œrk³©°ù]&°ğ"xX*y,ÈíPüSˆèñîşcûñ×3›;®?0/fyjqjº…q._Ç„4hhS±V!åé`Aj’e¡Ğ¾¤Ü]§ƒOãpÒsYBø¤Î$š‚şš`mCŸ±2Hm—v70n–é-'w,Û2oråÇ>Œ"wÇ©ëÛÙñá(§&àäş$Nk·.ò°µ.
n(îiƒ
E\²~SET¹Ş°îÀªÒÈ™uWr¦’”S'i1özƒ9ïyNçŠDÖ¡FÅ HI“è¹Àâ7_¿Ç–jßËˆMl"Y½şºÑïí\¡Ÿ[ØSÍ_i#¡’#»i9Gv9µş–ë\½¦çH¨äˆHâÈ®Š#+q(9RáÕHÜf-ÕAÃz4§~Ä4Jğóş}Ò©$R=µøY
XÀxÎA3-|Á¹Yd°:± OV”p4|õI‘©MB#ª¯nk*‘®Üèö«n±¹¹Zù¡÷ıí«¤ù×·¯l0;ØÙ¹ªµ0{¤'Âø`…@5Ü°G'â~˜Í”ªy'›•x‡«Ìxkt}¼©3@ÀQê¤ G²¿;*a-G1ur%©÷àùK­¿Çi¹Ş»­£€”´Š€$bï©ˆ]‰C©ÕËˆ5è

ıŞµ-úyuG§;‡¡ÚÖÁés9€S2æA—Ú 1æŠ1»»[·ú}óCÉ˜$7B‹/ø±ÄK‘Ò¶ÅÍ<àê²œâÌQ3ù‘Sjİ§?åp®õçzW%wk8o?ı©Š¹+Q(™«%ÕX7$­cÎ
®«ÉZ!˜aJ¾8´A0s"MŒKFî®æÚxãºVƒ H“‘Õ€$Nî)}ÍrFæA˜Æ•-<âä:îxg¬õ6Y û+Ú(À©E,Q&íÿ‘jÿz¢YÚœhrñ÷‹hÄş7Ï÷†…_$©É¦:›/!H$¾ß&QÈ~j 1rªXù0|v@@öô“vóæM9­— (5H„"‘÷ğ„äáÀ¢Îğs'óË8.¦2—ŒÎÓœbn9éØ/!ß*¼³ãnÊêÈÅb0É”ró(i÷·”H‡…!™hŒıQÏ‡Ï¢JX¢OÈæĞ‹ÕI‹W£$°?8!Øiª{6¯Şş	áÎ|µ3¹_¥-¹÷Uìv7GcOÎ¾[ËêCî£®zJÚ?âêqıÚí®Ë)’:H‰$r?R‘»ÉSMD}â„ÙÂ+ÕùIaÇ·oŞ¼º«3e€RÒ+ƒ’~r±u:X2<ÍŞ“ûU=bÓ"ÕÆ‰
•…MG7¸ÉF75K7Gİ³­…\»Ög“ÛüŠê
VD‘İF§xS‡‰?ŠmLu#ÌìÔwãÔÃm«£Ğ|Šîšùª¦:²PŸ HP{¬ëø0[˜†Z\!p…8Å(Qá\B£ˆEªMaTÉ„p¦!-¹Î4”Ñ‘¨ÛlÔ¸q
Á(ğ()Ãhq[7ˆuˆc”Gã¶\)M&e
å0ë0Ó¡ÛÁRõbä* ½¥M‰ë8€á&2””Îd‘1Ò¨FN”OÒ°N[1Â†5:„¥±<YÉS¶BV"<ÒRG\‚Ğ»£m†¿¸eÜvPA'óÒhŠ‡8U¶Ğ|z)@gÔ^‰x*´IC”:O©œ0\›¯!I"rO3Šü§ÛyªD8év<((sÂRÍ(E¢n‡ÁxÎ•qÏ[^)Òcy1¼‹öm® év(ÛPâ9Ôx¡3Õ¸’-tJ¸ £J¯YíªÄ§TÖ’©”kûæãÙ`:Bp7)Ø·•Rg“¨ê«¦ëTÓQOi‚/xNWöáÑÀ|¾ !Ü.cşè2u;|«Š¥_¬ÆB¡¿àv¤q›¤İä\\øù©ÎàØNØºY&Ñ ßC5=<j>8.l—ëx—ÅuµgY†a¶ü…»ƒs©JI²ìĞÀ¹”M!UÈĞ2 æùÛ·oÓáî(Ğ|ÓIÔ)Ï*Ûsñ…ì™ï°tk¡Qƒ—RÈ+Ê}rÕHà¢û»Íş8ù#Şösä»É~>b_÷’üuİ1òœ]qÿ1»‰¦iôsQÏnéR?
ŸÿDìá9ÀÅôŸ
wÛÿ„»m›ßmÿ¿Ûş¤¼Ûş³€n²,@S¿Àvé{ç<.°İ™“eòµ¿á¥›m-+anÛVæÏÆë5áV˜İìÑ½6o¸¼ ®ªRµG˜$]²¨×.¼Õ7É¾GĞÁWú¯ºÍd!†øyQ1ö¿<T’„Ñò£<A$“Ä¯$Åı%á)>Ö±Ä¨ª³‡qª¸é'.âzíA„-ß W»ÂN•—üÂ¸¼šlE¶Q÷™]c00LÿĞs²À”×•ìnKº÷gŸ¼¦îÌ_
ş'_ <—¾¼ŠƒÅÆH'eÙ¶ŸTzÃõSYhaFYîP_ …Ú“m›Ù‹m³‰pä):é˜&1ìœÌÉ©Y€ÃY+5h­C„Ãá9‘ÇÑVå¶R}_…JÔºÏN2Ş¥Ò8İ©LxP,`æ\í h(Æ
‹®÷Ç\I¹9fÑ4Æ¸°¤ù¤.s/e@Ì—İ¸õD¨
ˆß
†sÏ†6ÒY¥‰N)h£ß¶èZàS<èNñàp1ËÃùÌpwáÂôÚ|ÊÆb†}ˆ^WèèÍã¹e²gğ´¨nK±Ÿ…y`GxÖœ^´ÖT¬€VqJWRíŞÂÁÜpß]k5öZnåÙz¿õÇu£Úuù3iKö_*‚õGEÿH}çs•Ô÷ä…9Ú©‘2>oIšSş³©o¶1½Û°B$lbŒš3a„Ê/úxñ›ĞPìòİ#×Ÿmhs)û^ ”haAÏ@ˆ¥êô2òØAåqİ˜`“ï¤=ÓxÇàLWu%µ}õd2‹GÎ¬â?Ú7Q®¥dJÊjQr P·~H»³«±
­S’»©pK[«L­dMoÕ¤kPmµÕ»FËO²Ær^H4Ä3Ã<µáés²C¦‘\ÏLÎ1G‹ÜÏ¬"‡)­eÉÎ*mÑ&pÅf©]O=I"°É1F‹Ö­v'z3 á¶RM\ïÔb¯¡ÕåS²ŞÄÇ9¤Ş+wo2yÃmu!	•è«pK[’_Íì€ZÊr!¥4TÍ*F£¸Ê;	µ.ƒZ´Í=q°"®3×8rÜ)A»múá¥¹t*€
W™§ÇKz7¡äúˆ"¸R†‹¾´ZùöàÎâ4ÏØ‹~œDĞí¾UèÂªŸRK=‚v„•àáCvV.RÍÕ‹]ñÂl>##E,mW|ÉÍ-y;âøĞ,¹ÈºµC”‰”3—j¤èyÔŠÁÎUÙC³\ÃH(¿,Å"$Zlã©“
BTÃ8!¯ŸTñªr<i‚Å ;Ñóš\¹È—	¥=N6Ó‹mÇó1c~2—%XN)ØXOÃùrÄt%<½â%>"Ç—øí¦³­s ¶{iSEœô–'T>€u·™ÖÕ‡Æ™Åº±ˆBzÉª™ •¾V6k¼ñDäÈÛf':ÙéI•@Å1…çı¢û(ğ°C|Ù
ßÃ7%­F‚Zä’”iŒÖÔÙl…ó¬Ò•2]êrnÙÿ«è¿6ì·6ßz I4R‘¥–Í8­°Ø]`®Ó˜tš>òq~£çU¾NU™Ş#’RF£I™ä­Õ§,^9c^9ı"”µÍ\EvÒ°Ö
‚×p`ŒÁë„Ut~„”ëâÒR|‹£]"k16(òˆòÑÛ‹óG~Ş~×@(³¶ù¶ˆ7Â<!mÍ¹paÆxñ-}ñ`ZÍãŠzadşÊãDMˆl5ä¡)xz»fN4Y°dÒ] À+wÂ‰Ê^Ğ_…ÏĞÑZİ’/£6®
Í@z‡†e .©*E³j3<¬–à²s
7ºFı6iU‹ø²|ÍÈ KœÙ’!:ØSÌe‰èi]­ÖÀ§˜¨Æ9)Ş„Œ²eñPIÓ ­Ş/\ğåËŞş‘–MV›pÉ„PE+ÊÊÊ0ÚÖi
~­©¬¶A?ÚCe†>(¡¤’Çîˆ'Ş¤ü<N­°†’ı CKlpÚáRE•—^ç*‡»ïõl.åÄV3îr¶6P,2”„D”iPˆa•$ÅKb¼&TæbY?c	Q3æÓ†f-o¦¼¼ÜbãU¾?¼]9’ŠûåZfÜF½´®µ§^‰ünÉB>ªXQÒà¬'´W/Ï³E«)g.9€‘:TÕˆ,?ùÖTÍØHUİN†&{dÊ.…«bªÉŞ´şÂ.Áããó&]:y•¸àmºZP,Áa ´¯‚éjæ50WŸ„7vÆ==“˜¿=¯ìŠi‚©\åÒ¸©8ó9Ş´Ä4¿(º
Dò(N¼ØùyŒ†nh$óTÑsÈ×«ßÆ,Š;ÌŒ‹˜h¼#WıòyÖ+–y	NdMQÖ@n»àg~÷½H/–NÑm»”ÿZ’Ã¹mÃxO3¿¡ì%4æØúmÁ”gµåÂiÕn£ôo<l¡ÄAèÙ›~†pâÍZØ8±İÜe»¦/²ä:æñ—"kÆ•ë%j­Â¯`àé¦ny5A™×4ğyvó²Sëö¯½ò(nà»ÓyŒCM³ÄÅOÍyé)LçªaT¡³´Ç?z½´•%´,E­¦´qêiT9d}½G+)xª<@é°Vf4PªwŠ»JÙ£dl©N ªŒ×­©¤È,j£ëS‘Ú×ìÔÛPÚ÷5ŠC‚º&"Ÿ¤ŒGaÕTêx%»ºPöÿ'Ñ•7¸+HÉ¦.Õ×!¬–Rn
±™.Û«¯Í×ğ«õÂ‚%6RNWÜÙ )0BÊîq²@DcdQ:çax0ÜD
"dnCÓ™åÌ=™ò½|{M™³)—ˆÖZ	Úd0'­òÏlŠ~v€˜÷Ä-Óñ²!©Xåâöğô”ĞJaÃÜ}±ZvUø®Í¶ÃåÃw/m(b:×Edÿ%qèññĞãóIÑããhí	Ä¬£g\tô|B]9Ã ìŞ~ÑÄ÷Ù+úd‚œ í9!û%<èÜa¿b•yÔ)Øošúó½º]è/ğ)G?ÿãŞÿ sc)x^Í\K—ÉUÖx4x\HØ 0ÆvNŠ¡³¤V©ú¡–4¦f¬‘Zc½Zƒ%D›¢I²2³*“ªÎ¬|”Ô8öBØ³aë•Ík1KşóX°0~ 6œá»ùˆÈŒ¨êÑÀÁÒQ«*#âŞ÷7nö¿ô"yÍÚÿò©S§úiÆQò¥»ÿõäş©ı×ñhê'¯ï¿‰O‹h»SßKN/’7,7õ£ùqÏÉòÎ(Ì;É/u”|yïEò¦µÓ#çĞO¾²ÿ6>Nğñræ¦á<Ï.g~¾˜Ûnà¤›_/'»ÿüÖ›ÁƒŸ½şqòË|µ”'oí1Äó4ŒÓ0?N~åÁ¾¶ßÁ“YùÑâpä§É¯ŞãÔÃ™ÏP9!Ê³ûo`Ùˆö”üÚAòUq?‡ÎÄï$_Ã†~ú¾!7öüäœ0í£ã›xÔI~ó~Ëº÷š4´{4O;É×÷ÿ+c3–ùó¿zi®Yøş`csİ8Çcğbğá"Üù‡~”?rllbmu×#íè¥­>ÆãENLÈ“EØóBgO¾]<ÒÃyê}ÈÈõ-³9Á½#³{ĞM~;8{ïõ”|Ûü«ÉÛo6yû­àìâÇ#‹ß`"Ë“o3æøOYbä£à¤ûî¿ÿÇÁİì­×N}œ˜LÕœ|–œßÎg™2†‡&Ğßİ?ËÔ)M<NíyüÔÆĞËä ²ŞÚEş¤¿‡}¬YÁW‚B¡ş
eaN@ªƒù§	z qw’îL¿hçá:D|}ÿßJuü1¿k®³Ln››ü‹^v—¶»|ÊÿŠ€8(7ÅéÀ<¿á:ŞöuÓÇÆœ5Ë¡4=Â¶ka×Øtß³³¹ïLıtíÀğg™o˜çÇìÙM.A€§!õ¶Ù
¾	¶Ô’=ô
Éö&Ğ Õ‚‰j#à"
¸Xœ<[LC;Œ¼Ğ%ñ¼L6›e±lÑ¶ –¿‡X®bé”bÙab¹Šé×J±\çbù×%bÙ¸r±üB‹ä]ˆ¤‘|[ÿ}IGI'øN!’,’gL$ïÕ"9§‰:³ÙËä}¦ÓÌwî† ˜€`>s¦ÌM&˜[˜¾[
æ6ÌË‚ù@´—ş*Állö²ÄáÁ¤~¡e÷!dw²û¸s‡dwFİ™à{…ìîÊ²;f²»WËî«*Ù^&÷!·3¹= ª=Anÿ¹=dr»ûégŸ}†çJÉ}$…¥<ˆ£Nòå÷â‘Ù3'ø‡êş×¾uêTÇóÇ–V>7w&ş­N:YP¸Z‡cŠÈeİw™Ÿb?àœˆ-Pàï±YG˜5lğ‰Õdú>5Æğ = Hk!Eâ5#Œ*\ÃşÁpã †#Á¢/ùQnçşáP9„œÿàq½ôæİ
+¹Hè*8åæ9A5¤
ä³ĞËPQêÏO­ş:ûÛí±	Õtğ1?Œrk³©°ù]&°ğ"xX*y,ÈíPüSˆèñîşcûñ×3›;®?0/fyjqjº…q._Ç„4hhS±V!åé`Aj’e¡Ğ¾¤Ü]§ƒOãpÒsYBø¤Î$š‚şš`mCŸ±2Hm—v70n–é-'w,Û2oråÇ>Œ"wÇ©ëÛÙñá(§&àäş$Nk·.ò°µ.
n(îiƒ
E\²~SET¹Ş°îÀªÒÈ™uWr¦’”S'i1özƒ9ïyNçŠDÖ¡FÅ HI“è¹Àâ7_¿Ç–jßËˆMl"Y½şºÑïí\¡Ÿ[ØSÍ_i#¡’#»i9Gv9µş–ë\½¦çH¨äˆHâÈ®Š#+q(9RáÕHÜf-ÕAÃz4§~Ä4Jğóş}Ò©$R=µøY
XÀxÎA3-|Á¹Yd°:± OV”p4|õI‘©MB#ª¯nk*‘®Üèö«n±¹¹Zù¡÷ıí«¤ù×·¯l0;ØÙ¹ªµ0{¤'Âø`…@5Ü°G'â~˜Í”ªy'›•x‡«Ìxkt}¼©3@ÀQê¤ G²¿;*a-G1ur%©÷àùK­¿Çi¹Ş»­£€”´Š€$bï©ˆ]‰C©ÕËˆ5è

ıŞµ-úyuG§;‡¡ÚÖÁés9€S2æA—Ú 1æŠ1»»[·ú}óCÉ˜$7B‹/ø±ÄK‘Ò¶ÅÍ<àê²œâÌQ3ù‘Sjİ§?åp®õçzW%wk8o?ı©Š¹+Q(™«%ÕX7$­cÎ
®«ÉZ!˜aJ¾8´A0s"MŒKFî®æÚxãºVƒ H“‘Õ€$Nî)}ÍrFæA˜Æ•-<âä:îxg¬õ6Y û+Ú(À©E,Q&íÿ‘jÿz¢YÚœhrñ÷‹hÄş7Ï÷†…_$©É¦:›/!H$¾ß&QÈ~j 1rªXù0|v@@öô“vóæM9­— (5H„"‘÷ğ„äáÀ¢Îğs'óË8.¦2—ŒÎÓœbn9éØ/!ß*¼³ãnÊêÈÅb0É”ró(i÷·”H‡…!™hŒıQÏ‡Ï¢JX¢OÈæĞ‹ÕI‹W£$°?8!Øiª{6¯Şş	áÎ|µ3¹_¥-¹÷Uìv7GcOÎ¾[ËêCî£®zJÚ?âêqıÚí®Ë)’:H‰$r?R‘»ÉSMD}â„ÙÂ+ÕùIaÇ·oŞ¼º«3e€RÒ+ƒ’~r±u:X2<ÍŞ“ûU=bÓ"ÕÆ‰
•…MG7¸ÉF75K7Gİ³­…\»Ög“ÛüŠê
VD‘İF§xS‡‰?ŠmLu#ÌìÔwãÔÃm«£Ğ|Šîšùª¦:²PŸ HP{¬ëø0[˜†Z\!p…8Å(Qá\B£ˆEªMaTÉ„p¦!-¹Î4”Ñ‘¨ÛlÔ¸q
Á(ğ()Ãhq[7ˆuˆc”Gã¶\)M&e
å0ë0Ó¡ÛÁRõbä* ½¥M‰ë8€á&2””Îd‘1Ò¨FN”OÒ°N[1Â†5:„¥±<YÉS¶BV"<ÒRG\‚Ğ»£m†¿¸eÜvPA'óÒhŠ‡8U¶Ğ|z)@gÔ^‰x*´IC”:O©œ0\›¯!I"rO3Šü§ÛyªD8év<((sÂRÍ(E¢n‡ÁxÎ•qÏ[^)Òcy1¼‹öm® év(ÛPâ9Ôx¡3Õ¸’-tJ¸ £J¯YíªÄ§TÖ’©”kûæãÙ`:Bp7)Ø·•Rg“¨ê«¦ëTÓQOi‚/xNWöáÑÀ|¾ !Ü.cşè2u;|«Š¥_¬ÆB¡¿àv¤q›¤İä\\øù©ÎàØNØºY&Ñ ßC5=<j>8.l—ëx—ÅuµgY†a¶ü…»ƒs©JI²ìĞÀ¹”M!UÈĞ2 æùÛ·oÓáî(Ğ|ÓIÔ)Ï*Ûsñ…ì™ï°tk¡Qƒ—RÈ+Ê}rÕHà¢û»Íş8ù#Şösä»É~>b_÷’üuİ1òœ]qÿ1»‰¦iôsQÏnéR?
ŸÿDìá9ÀÅôŸ
wÛÿ„»m›ßmÿ¿Ûş¤¼Ûş³€n²,@S¿Àvé{ç<.°İ™“eòµ¿á¥›m-+anÛVæÏÆë5áV˜İìÑ½6o¸¼ ®ªRµG˜$]²¨×.¼Õ7É¾GĞÁWú¯ºÍd!†øyQ1ö¿<T’„Ñò£<A$“Ä¯$Åı%á)>Ö±Ä¨ª³‡qª¸é'.âzíA„-ß W»ÂN•—üÂ¸¼šlE¶Q÷™]c00LÿĞs²À”×•ìnKº÷gŸ¼¦îÌ_
ş'_ <—¾¼ŠƒÅÆH'eÙ¶ŸTzÃõSYhaFYîP_ …Ú“m›Ù‹m³‰pä):é˜&1ìœÌÉ©Y€ÃY+5h­C„Ãá9‘ÇÑVå¶R}_…JÔºÏN2Ş¥Ò8İ©LxP,`æ\í h(Æ
‹®÷Ç\I¹9fÑ4Æ¸°¤ù¤.s/e@Ì—İ¸õD¨
ˆß
†sÏ†6ÒY¥‰N)h£ß¶èZàS<èNñàp1ËÃùÌpwáÂôÚ|ÊÆb†}ˆ^WèèÍã¹e²gğ´¨nK±Ÿ…y`GxÖœ^´ÖT¬€VqJWRíŞÂÁÜpß]k5öZnåÙz¿õÇu£Úuù3iKö_*‚õGEÿH}çs•Ô÷ä…9Ú©‘2>oIšSş³©o¶1½Û°B$lbŒš3a„Ê/úxñ›ĞPìòİ#×Ÿmhs)û^ ”haAÏ@ˆ¥êô2òØAåqİ˜`“ï¤=ÓxÇàLWu%µ}õd2‹GÎ¬â?Ú7Q®¥dJÊjQr P·~H»³«±
­S’»©pK[«L­dMoÕ¤kPmµÕ»FËO²Ær^H4Ä3Ã<µáés²C¦‘\ÏLÎ1G‹ÜÏ¬"‡)­eÉÎ*mÑ&pÅf©]O=I"°É1F‹Ö­v'z3 á¶RM\ïÔb¯¡ÕåS²ŞÄÇ9¤Ş+wo2yÃmu!	•è«pK[’_Íì€ZÊr!¥4TÍ*F£¸Ê;	µ.ƒZ´Í=q°"®3×8rÜ)A»múá¥¹t*€
W™§ÇKz7¡äúˆ"¸R†‹¾´ZùöàÎâ4ÏØ‹~œDĞí¾UèÂªŸRK=‚v„•àáCvV.RÍÕ‹]ñÂl>##E,mW|ÉÍ-y;âøĞ,¹ÈºµC”‰”3—j¤èyÔŠÁÎUÙC³\ÃH(¿,Å"$Zlã©“
BTÃ8!¯ŸTñªr<i‚Å ;Ñóš\¹È—	¥=N6Ó‹mÇó1c~2—%XN)ØXOÃùrÄt%<½â%>"Ç—øí¦³­s ¶{iSEœô–'T>€u·™ÖÕ‡Æ™Åº±ˆBzÉª™ •¾V6k¼ñDäÈÛf':ÙéI•@Å1…çı¢û(ğ°C|Ù
ßÃ7%­F‚Zä’”iŒÖÔÙl…ó¬Ò•2]êrnÙÿ«è¿6ì·6ßz I4R‘¥–Í8­°Ø]`®Ó˜tš>òq~£çU¾NU™Ş#’RF£I™ä­Õ§,^9c^9ı"”µÍ\EvÒ°Ö
‚×p`ŒÁë„Ut~„”ëâÒR|‹£]"k16(òˆòÑÛ‹óG~Ş~×@(³¶ù¶ˆ7Â<!mÍ¹paÆxñ-}ñ`ZÍãŠzadşÊãDMˆl5ä¡)xz»fN4Y°dÒ] À+wÂ‰Ê^Ğ_…ÏĞÑZİ’/£6®
Í@z‡†e .©*E³j3<¬–à²s
7ºFı6iU‹ø²|ÍÈ KœÙ’!:ØSÌe‰èi]­ÖÀ§˜¨Æ9)Ş„Œ²eñPIÓ ­Ş/\ğåËŞş‘–MV›pÉ„PE+ÊÊÊ0ÚÖi
~­©¬¶A?ÚCe†>(¡¤’Çîˆ'Ş¤ü<N­°†’ı CKlpÚáRE•—^ç*‡»ïõl.åÄV3îr¶6P,2”„D”iPˆa•$ÅKb¼&TæbY?c	Q3æÓ†f-o¦¼¼ÜbãU¾?¼]9’ŠûåZfÜF½´®µ§^‰ünÉB>ªXQÒà¬'´W/Ï³E«)g.9€‘:TÕˆ,?ùÖTÍØHUİN†&{dÊ.…«bªÉŞ´şÂ.Áããó&]:y•¸àmºZP,Áa ´¯‚éjæ50WŸ„7vÆ==“˜¿=¯ìŠi‚©\åÒ¸©8ó9Ş´Ä4¿(º
Dò(N¼ØùyŒ†nh$óTÑsÈ×«ßÆ,Š;ÌŒ‹˜h¼#WıòyÖ+–y	NdMQÖ@n»àg~÷½H/–NÑm»”ÿZ’Ã¹mÃxO3¿¡ì%4æØúmÁ”gµåÂiÕn£ôo<l¡ÄAèÙ›~†pâÍZØ8±İÜe»¦/²ä:æñ—"kÆ•ë%j­Â¯`àé¦ny5A™×4ğyvó²Sëö¯½ò(nà»ÓyŒCM³ÄÅOÍyé)LçªaT¡³´Ç?z½´•%´,E­¦´qêiT9d}½G+)xª<@é°Vf4PªwŠ»JÙ£dl©N ªŒ×­©¤È,j£ëS‘Ú×ìÔÛPÚ÷5ŠC‚º&"Ÿ¤ŒGaÕTêx%»ºPöÿ'Ñ•7¸+HÉ¦.Õ×!¬–Rn
±™.Û«¯Í×ğ«õÂ‚%6RNWÜÙ )0BÊîq²@DcdQ:çax0ÜD
"dnCÓ™åÌ=™ò½|{M™³)—ˆÖZ	Úd0'­òÏlŠ~v€˜÷Ä-Óñ²!©Xåâöğô”ĞJaÃÜ}±ZvUø®Í¶ÃåÃw/m(b:×Edÿ%qèññĞãóIÑããhí	Ä¬£g\tô|B]9Ã ìŞ~ÑÄ÷Ù+úd‚œ í9!û%<èÜa¿b•yÔ)Øošúó½º]è/ğ)G?ÿãŞÿ sc)È2¢±è~ÇoÑ6è©¸CMade with Ren'Py.init -100 python:
    store.bgm_name = "---"
    store.bgm_credits_name = ""

    renpy.music.register_channel("sfx", mixer="sfx", loop=True)
    renpy.music.register_channel("channel2", mixer="sfx", loop=True)
    renpy.music.register_channel("channel3", mixer="sfx", loop=True)
    renpy.music.register_channel("glitch", mixer="music", loop=True)
    renpy.music.register_channel("system", mixer="system", loop=False)
    
    ## The name of the audio channel used by renpy.play(), hover_sound, and activate_sound.
    ## Make sure all of the default 'audio #' channels are system sounds
    config.play_channel = 'audio'
    for temp in range(0, 9):
        renpy.audio.audio.get_channel('audio '+str(temp)).mixer = 'system'

    class MusicEntry:
        def __init__(self, name, artist, art=None, fname_noloop="", fname_loop="", loop_start=None, loop_end=None, show_in_musicroom=True, play_in_musicroom=True, unused=False, exclusive=False):
            self.name = name
            self.artist = artist
            self.art = art
            self.fname_loop = fname_loop
            self.fname_noloop = fname_noloop
            self.loop_start = loop_start
            self.loop_end = loop_end
            self.show_in_musicroom = show_in_musicroom
            self.play_in_musicroom = play_in_musicroom
            self.unused = unused
            self.exclusive = exclusive
        
        def match(self, other):
            name = self.name.lower()
            other = other.lower()
            return other==name or other==name.replace(' ','')
    
    class ComposerEntry:
        def __init__(self, twitter=None, website=None):
            self.twitter = twitter
            self.website = website
    
    def GetMusicEntry(track):
        found_entry = None
        for entry in all_music_entries:
            if entry.match(track):
                found_entry = entry
                break
        return found_entry
    
    from collections import OrderedDict
    all_music_entries = python_list()
    all_music_entries.append(MusicEntry(
        name="2085 a Space Odyssey",
        artist="Volant",
        art="images/albumart/one.jpg",
        fname_noloop="music/original/2085aspaceodyssey.ogg",
        fname_loop="music/2085aspaceodyssey.ogg",
        loop_start=19.258,
        ))
    all_music_entries.append(MusicEntry(
        name="Abdication",
        artist="Husked",
        art="images/albumart/abdication.png",
        fname_noloop="music/original/abdication.ogg",
        fname_loop="music/abdication.ogg",
        exclusive=True,
        loop_start=32.524,
        ))
    all_music_entries.append(MusicEntry(
        name="Abdication (Alt)",
        artist="Husked",
        art="images/albumart/abdication.png",
        fname_noloop="music/original/abdication.ogg",
        fname_loop="music/abdicationfull.ogg",
        show_in_musicroom=False,
        loop_start=32.524,
        ))
    all_music_entries.append(MusicEntry(
        name="Animals",
        artist="Shurk",
        art="images/albumart/perform.jpg",
        fname_noloop="music/original/animals.ogg",
        fname_loop="music/animals.ogg",
        loop_start=241.430,
        ))
    all_music_entries.append(MusicEntry(
        name="Anomaly",
        artist="auvic & grayscreen",
        art="images/albumart/soulfireinsight.jpg",
        fname_noloop="music/original/anomaly.ogg",
        fname_loop="music/anomaly.ogg",
        loop_start=54.498,
        ))
    all_music_entries.append(MusicEntry(
        name="Aphelion",
        artist="Ninety",
        art="images/albumart/aphelion.png",
        fname_noloop="music/original/aphelion.ogg",
        fname_loop="music/aphelion.ogg",
        loop_start=27.512,
        ))
    all_music_entries.append(MusicEntry(
        name="Basin City",
        artist="Ekcle",
        art="images/albumart/basincity.jpg",
        fname_noloop="music/original/basincity.ogg",
        fname_loop="music/basincity.ogg",
        loop_start=52.855,
        ))
    all_music_entries.append(MusicEntry(
        name="Beguile",
        artist="opaqity",
        art="images/albumart/beguile.jpg",
        fname_noloop="music/original/beguile.ogg",
        fname_loop="music/beguile.ogg",
        loop_start=62.737,
        ))
    all_music_entries.append(MusicEntry(
        name="Breathing Space",
        artist="opaqity",
        art="images/albumart/breathingspace.png",
        fname_noloop="music/original/breathingspace.ogg",
        fname_loop="music/breathingspace.ogg",
        loop_start=62.758,
        ))
    all_music_entries.append(MusicEntry(
        name="Call Of The Void",
        artist="opaqity",
        art="images/albumart/callofthevoid.jpg",
        fname_noloop="music/callofthevoid.ogg",
        fname_loop="music/callofthevoid.ogg",
        loop_start=51.983,
        ))
    all_music_entries.append(MusicEntry(
        name="CC5",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/cc5.ogg",
        fname_loop="music/cc5.ogg",
        loop_start=2.048,
        ))
    all_music_entries.append(MusicEntry(
        name="Ceol",
        artist="John Tejada",
        art="images/albumart/ceol.png",
        fname_noloop="music/original/ceol.ogg",
        fname_loop="music/ceol.ogg",
        loop_start=62.077,
        ))
    all_music_entries.append(MusicEntry(
        name="Changed Mind",
        artist="opaqity",
        art="images/albumart/changedmind.png",
        fname_noloop="music/original/changedmind.ogg",
        fname_loop="music/changedmind.ogg",
        loop_start=16.234,
        ))
    all_music_entries.append(MusicEntry(
        name="Chillish",
        artist="Jake Kaiser",
        art="images/albumart/chillish.png",
        fname_noloop="music/original/chillish.ogg",
        fname_loop="music/chillish.ogg",
        loop_start=17.044,
        ))
    all_music_entries.append(MusicEntry(
        name="Closure",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/closure.ogg",
        fname_loop="music/closure.ogg",
        loop_start=16.536,
        ))
    #all_music_entries.append(MusicEntry(
    #    name="Didactic",
    #    artist="Grim Fables",
    #    art="images/albumart/didactic.png",
    #    fname_noloop="music/original/didactic.ogg",
    #    fname_loop="music/didactic.ogg",
    #    loop_start=0,
    #    unused=True,
    #    ))
    all_music_entries.append(MusicEntry(
        name="Double Existence",
        artist="Pfirter",
        art="images/albumart/black.jpg",
        fname_noloop="music/original/doubleexistence.ogg",
        fname_loop="music/doubleexistence.ogg",
        loop_start=118.883,
        play_in_musicroom=False,
        ))
    all_music_entries.append(MusicEntry(
        name="Double Vision",
        artist="Adri",
        art="images/albumart/doublevision.png",
        fname_noloop="music/original/doublevision.ogg",
        fname_loop="music/doublevision.ogg",
        loop_start=0,
        ))
    all_music_entries.append(MusicEntry(
        name="Duo",
        artist="Shurk",
        art="images/albumart/perform.jpg",
        fname_noloop="music/original/duo.ogg",
        fname_loop="music/duo.ogg",
        loop_start=2.475,
        ))
    all_music_entries.append(MusicEntry(
        name="Dusk Two",
        artist="opaqity",
        art="images/albumart/dusktwo.jpg",
        fname_noloop="music/original/dusktwo.ogg",
        fname_loop="music/dusktwo.ogg",
        loop_start=21.811,
        ))
    all_music_entries.append(MusicEntry(
        name="Dysania",
        artist="Primate",
        art="images/albumart/naturalselection.jpg",
        fname_noloop="music/original/dynasia.ogg",
        fname_loop="music/dynasia.ogg",
        loop_start=11.331,
        ))
    all_music_entries.append(MusicEntry(
        name="Exposed",
        artist="Primate",
        art="images/albumart/outoftime.jpg",
        fname_noloop="music/original/exposed.ogg",
        fname_loop="music/exposed.ogg",
        loop_start=11.316,
        ))
    all_music_entries.append(MusicEntry(
        name="False Illusions",
        artist="modus.",
        art="images/albumart/falseillusions.jpg",
        fname_noloop="music/original/falseillusions.ogg",
        fname_loop="music/falseillusions.ogg",
        loop_start=16.006,
        ))
    all_music_entries.append(MusicEntry(
        name="Fever Dream",
        artist="synce",
        art="images/albumart/feverdream.jpg",
        fname_noloop="music/original/feverdream.ogg",
        fname_loop="music/feverdream.ogg",
        loop_start=58.757,
        ))
    all_music_entries.append(MusicEntry(
        name="Flourishing",
        artist="Nyah",
        art="images/albumart/flourishing.jpg",
        fname_noloop="music/original/flourishing.ogg",
        fname_loop="music/flourishing.ogg",
        loop_start=6.812,
        ))
    all_music_entries.append(MusicEntry(
        name="Flows",
        artist="Jake Kaiser",
        art="images/albumart/flows.jpg",
        fname_noloop="music/original/flows.ogg",
        fname_loop="music/flows.ogg",
        loop_start=5.334,
        ))
    all_music_entries.append(MusicEntry(
        name="Flutter",
        artist="Adri",
        art="images/albumart/flutter.png",
        fname_noloop="music/original/flutter.ogg",
        fname_loop="music/original/flutter.ogg",
        loop_start=34.244,
        unused=True,
        ))
    all_music_entries.append(MusicEntry(
        name="Gateway",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/gateway.ogg",
        fname_loop="music/gateway.ogg",
        loop_start=25.949,
        ))
    all_music_entries.append(MusicEntry(
        name="Heal",
        artist="John Tejada",
        art="images/albumart/heal.png",
        fname_noloop="music/original/heal.ogg",
        fname_loop="music/heal.ogg",
        loop_start=30.525,
        ))
    all_music_entries.append(MusicEntry(
        name="Hicaz",
        artist="Shurk",
        art="images/albumart/perform.jpg",
        fname_noloop="music/original/hicaz.ogg",
        fname_loop="music/hicaz.ogg",
        loop_start=61.768,
        ))
    all_music_entries.append(MusicEntry(
        name="Hicaz (Alt)",
        artist="Shurk",
        art="images/albumart/perform.jpg",
        fname_noloop="music/original/hicaz.ogg",
        fname_loop="music/hicazfull.ogg",
        loop_start=30.259,
        show_in_musicroom=False,
        ))
    all_music_entries.append(MusicEntry(
        name="Iucid",
        artist="opaqity",
        art="images/albumart/iucid.png",
        fname_noloop="music/original/iucid.ogg",
        fname_loop="music/iucid.ogg",
        loop_start=29.926,
        ))
    all_music_entries.append(MusicEntry(
        name="Kenopsia",
        artist="Rodriguez Jr.",
        art="images/albumart/kenopsia.png",
        fname_noloop="music/original/kenopsia.ogg",
        fname_loop="music/kenopsia.ogg",
        loop_start=46.130,
        ))
    all_music_entries.append(MusicEntry(
        name="Local Theory",
        artist="Adri",
        art="images/albumart/localtheory.png",
        fname_noloop="music/original/localtheory.ogg",
        fname_loop="music/localtheory.ogg",
        loop_start=125.396,
        ))
    all_music_entries.append(MusicEntry(
        name="Looking Glass",
        artist="Bustre",
        art="images/albumart/lookingglass.jpg",
        fname_noloop="music/original/lookingglass.ogg",
        fname_loop="music/lookingglass.ogg",
        loop_start=21.606,
        ))
    all_music_entries.append(MusicEntry(
        name="Looming",
        artist="Nyah",
        art="images/albumart/looming.jpg",
        fname_noloop="music/original/looming.ogg",
        fname_loop="music/looming.ogg",
        loop_start=16.712,
        ))
    all_music_entries.append(MusicEntry(
        name="Loves Me Loves Me Not",
        artist="auvic",
        art="images/albumart/lovesmelovesmenot.png",
        fname_noloop="music/original/lovesmelovesmenot.ogg",
        fname_loop="music/lovesmelovesmenot.ogg",
        loop_start=21.772,
        ))
    all_music_entries.append(MusicEntry(
        name="Mifune",
        artist="Ã‚me",
        art="images/albumart/ame.jpg",
        fname_noloop="music/original/mifune.ogg",
        fname_loop="music/mifune2.ogg",
        loop_start=16.885,
        ))
    all_music_entries.append(MusicEntry(
        name="Natural Selection",
        artist="Primate",
        art="images/albumart/naturalselection.jpg",
        fname_noloop="music/original/naturalselection.ogg",
        fname_loop="music/naturalselection.ogg",
        loop_start=25.611,
        ))
    all_music_entries.append(MusicEntry(
        name="Nia",
        artist="Ã‚me",
        art="images/albumart/ame.jpg",
        fname_noloop="music/original/nia.ogg",
        fname_loop="music/nia.ogg",
        loop_start=123.874,
        ))
    all_music_entries.append(MusicEntry(
        name="Outershell",
        artist="Ninety & synce",
        art="images/albumart/outershell.jpg",
        fname_noloop="music/original/outershell.ogg",
        fname_loop="music/outershell.ogg",
        loop_start=38.632,
        ))
    all_music_entries.append(MusicEntry(
        name="Passage",
        artist="mistwin",
        art="images/albumart/passage2.jpg",
        fname_noloop="music/original/passage.ogg",
        fname_loop="music/passage.ogg",
        loop_start=23.397,
        ))
    all_music_entries.append(MusicEntry(
        name="Relentless Pursuit",
        artist="auvic",
        art="images/albumart/relentlesspursuit.jpg",
        fname_noloop="music/original/relentlesspursuit.ogg",
        fname_loop="music/relentlesspursuit.ogg",
        loop_start=13.898,
        ))
    all_music_entries.append(MusicEntry(
        name="Reverence",
        artist="Meakii",
        art="images/albumart/reverence.png",
        fname_noloop="music/original/reverence.ogg",
        fname_loop="music/reverence.ogg",
        loop_start=30.861,
        ))
    all_music_entries.append(MusicEntry(
        name="Ripple",
        artist="Adri",
        art="images/albumart/ripple.png",
        fname_noloop="music/original/steps.ogg",
        fname_loop="music/steps.ogg",
        loop_start=0,
        ))
    all_music_entries.append(MusicEntry(
        name="Rise Of The White Dwarf",
        artist="Pfirter",
        art="images/albumart/black.jpg",
        fname_noloop="music/original/riseofthewhitedwarf.ogg",
        fname_loop="music/riseofthewhitedwarf.ogg",
        loop_start=20.844,
        play_in_musicroom=False,
        ))
    all_music_entries.append(MusicEntry(
        name="Room With No Windows",
        artist="Nyah",
        art="images/albumart/thesewallsareourgraves.jpg",
        fname_noloop="music/original/roomwithnowindows.ogg",
        fname_loop="music/roomwithnowindows.ogg",
        loop_start=10.754,
        ))
    all_music_entries.append(MusicEntry(
        name="Sequence",
        artist="shimaL",
        art="images/albumart/sequence.jpg",
        fname_noloop="music/original/sequence.ogg",
        fname_loop="music/sequence.ogg",
        loop_start=59.764,
        ))
    all_music_entries.append(MusicEntry(
        name="Sequence of Events",
        artist="gyrofield",
        art="images/albumart/sequenceofevents.jpg",
        fname_noloop="music/original/sequenceofevents.ogg",
        fname_loop="music/sequenceofevents.ogg",
        loop_start=89.915,
        ))
    all_music_entries.append(MusicEntry(
        name="Setsa",
        artist="Ã‚me",
        art="images/albumart/setsa.jpg",
        fname_noloop="music/original/setsa.ogg",
        fname_loop="music/setsa.ogg",
        loop_start=61.047,
        ))
    all_music_entries.append(MusicEntry(
        name="Shiro",
        artist="Ã‚me",
        art="images/albumart/ame.jpg",
        fname_noloop="music/original/shiro.ogg",
        fname_loop="music/shiro.ogg",
        loop_start=62.347,
        ))
    all_music_entries.append(MusicEntry(
        name="Somber",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/somber.ogg",
        fname_loop="music/somber.ogg",
        loop_start=62.347,
        ))
    all_music_entries.append(MusicEntry(
        name="Sotto",
        artist="Nyah",
        art="images/albumart/sotto.jpg",
        fname_noloop="music/original/sotto.ogg",
        fname_loop="music/sotto.ogg",
        loop_start=17.445,
        ))
    all_music_entries.append(MusicEntry(
        name="Stage Fright",
        artist="Shurk",
        art="images/albumart/perform.jpg",
        fname_noloop="music/original/stagefright.ogg",
        fname_loop="music/stagefright.ogg",
        loop_start=30.156,
        ))
    all_music_entries.append(MusicEntry(
        name="Subterrain",
        artist="Nyah",
        art="images/albumart/subterrain.jpg",
        fname_noloop="music/original/subterrain.ogg",
        fname_loop="music/subterrain.ogg",
        loop_start=11.327,
        ))
    all_music_entries.append(MusicEntry(
        name="Swelter",
        artist="auvic & Robot Love",
        art="images/albumart/soulfireinsight.jpg",
        fname_noloop="music/original/swelter.ogg",
        fname_loop="music/swelter.ogg",
        loop_start=43.075,
        ))
    all_music_entries.append(MusicEntry(
        name="There's Always Tomorrow",
        artist="opaqity",
        art="images/albumart/theresalwaystomorrow.png",
        fname_noloop="music/original/theresalwaystomorrow.ogg",
        fname_loop="music/theresalwaystomorrow.ogg",
        loop_start=7.011,
        ))
    all_music_entries.append(MusicEntry(
        name="Timeleap",
        artist="shimaL",
        art="images/albumart/timeleap.jpg",
        fname_noloop="music/original/timeleap.ogg",
        fname_loop="music/timeleap.ogg",
        loop_start=36.049,
        ))
    all_music_entries.append(MusicEntry(
        name="Trinity Project",
        artist="Famous Spear",
        art="images/albumart/trinityproject.jpg",
        fname_noloop="music/original/trinityproject.ogg",
        fname_loop="music/trinityproject.ogg",
        loop_start=52.417,
        ))
    all_music_entries.append(MusicEntry(
        name="Twice As Dead",
        artist="Nyah",
        art="images/albumart/twiceasdead.jpg",
        fname_noloop="music/original/twiceasdead.ogg",
        fname_loop="music/twiceasdead.ogg",
        loop_start=50.903,
        ))
    all_music_entries.append(MusicEntry(
        name="Two Days Of Rain",
        artist="Nyah",
        art="images/albumart/thesewallsareourgraves.jpg",
        fname_noloop="music/original/twodaysofrain.ogg",
        fname_loop="music/twodaysofrain.ogg",
        loop_start=33.717,
        loop_end=205.456,
        ))
    all_music_entries.append(MusicEntry(
        name="Two Days Of Rain Alternative",
        artist="Nyah",
        art="images/albumart/thesewallsareourgraves.jpg",
        fname_noloop="music/original/twodaysofrainalternative.ogg",
        fname_loop="music/twodaysofrainalternative.ogg",
        show_in_musicroom=False,
        loop_start=33.717,
        loop_end=205.456,
        ))
    all_music_entries.append(MusicEntry(
        name="Two Days Of Rain (Alt)",
        artist="Nyah",
        art="images/albumart/thesewallsareourgraves.jpg",
        fname_noloop="music/original/twodaysofrainalternative.ogg",
        fname_loop="music/twodaysofrainalternative.ogg",
        loop_start=33.717,
        loop_end=205.456,
        ))
    all_music_entries.append(MusicEntry(
        name="Vanity",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/vanity.ogg",
        fname_loop="music/vanity.ogg",
        loop_start=17.113,
        ))
    #all_music_entries.append(MusicEntry(
    #    name="Walls",
    #    artist="opaqity",
    #    art="images/albumart/walls.jpg",
    #    fname_noloop="music/original/walls.ogg",
    #    fname_loop="music/walls.ogg",
    #    loop_start=0,
    #    ))
    all_music_entries.append(MusicEntry(
        name="Why Did I Fade Away",
        artist="opaqity",
        art="images/albumart/whydidifadeaway.png",
        fname_noloop="music/original/whydidifadeaway.ogg",
        fname_loop="music/whydidifadeaway.ogg",
        loop_start=73.093,
        ))
    all_music_entries.append(MusicEntry(
        name="Winter",
        artist="Clayfacer",
        art="images/albumart/passage.jpg",
        fname_noloop="music/original/winter.ogg",
        fname_loop="music/winter.ogg",
        loop_start=40.082,
        ))
    all_music_entries.append(MusicEntry(
        name="Wither",
        artist="Nyah",
        art="images/albumart/wither.jpg",
        fname_noloop="music/original/wither.ogg",
        fname_loop="music/wither.ogg",
        loop_start=65.609,
        ))
    
    
    composer_details = python_dict()
    composer_details["Adri"] = [ComposerEntry(
        twitter="https://twitter.com/TrinititeTeam",
        website=None,
        )]
    composer_details["ak+q"] = [ComposerEntry(
        twitter="https://twitter.com/akqmusic",
        website="https://soundcloud.com/ak_q",
        )]
    composer_details["Ã‚me"] = [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/ame",
        )]
    composer_details["auvic"] = [ComposerEntry(
        twitter="http://www.twitter.com/auvicmusic",
        website="http://www.soundcloud.com/auvicmusic",
        )]
    composer_details["Bustre"]= [ComposerEntry(
        twitter="https://twitter.com/KonkaiUK",
        website="https://soundcloud.com/bustre",
        )]
    composer_details["Clayfacer"]= [ComposerEntry(
        twitter="https://twitter.com/Clayfacer",
        website="https://soundcloud.com/clayfacer",
        )]
    composer_details["Ekcle"]= [ComposerEntry(
        twitter="https://twitter.com/ekclemusic",
        website="www.ekclemusic.com",
        )]
    composer_details["Grim Fables"]= [ComposerEntry(
        twitter="https://twitter.com/GrimFables",
        website="https://soundcloud.com/grimfables",
        )]
    composer_details["Famous Spear"]= [ComposerEntry(
        twitter="https://twitter.com/FamousSpearCA",
        website="https://soundcloud.com/famousspear",
        )]
    composer_details["gyrofield"]= [ComposerEntry(
        twitter="https://twitter.com/gyrofield",
        website="https://soundcloud.com/gyrofieldmusic",
        )]
    composer_details["grayscreen"]= [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/grayscreen",
        )]
    composer_details["Husked"]= [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/husked",
        )]
    composer_details["Jake Kaiser"]= [ComposerEntry(
        twitter="https://twitter.com/jakekaisermusic",
        website="https://linktr.ee/jakekaisermusic",
        )]
    composer_details["John Tejada"]= [ComposerEntry(
        twitter="https://twitter.com/johntejada",
        website="https://soundcloud.com/paletterecordings",
        )]
    composer_details["Meakiidetails"]= [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/wearemeakii",
        )]
    composer_details["modus."]= [ComposerEntry(
        twitter="https://twitter.com/iammodus",
        website="https://open.spotify.com/artist/1ASCCDEpi3FWTb0jVDJhA2?si=lf-TShscTEaY7CgOIiPRyQ",
        )]
    composer_details["mistwin"]= [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/mistwin",
        )]
    composer_details["Ninety"]= [ComposerEntry(
        twitter=None,
        website="https://soundcloud.com/ninety-7",
        )]
    composer_details["Nyah"]= [ComposerEntry(
        twitter="https://twitter.com/idkNyah",
        website="https://soundcloud.com/imnyah",
        )]
    composer_details["opaqity"]= [ComposerEntry(
        twitter=None,
        website="https://www.audiotool.com/user/opaqity/",
        )]
    composer_details["Pfirter"]= [ComposerEntry(
        twitter="https://twitter.com/pfirter",
        website="www.mindtripmusic.com",
        )]
    composer_details["Primate"]= [ComposerEntry(
        twitter="https://twitter.com/smallprintrec",
        website="https://facebook.com/primatemusicjoe",
        )]
    composer_details["Robot Love"]= [ComposerEntry(
        twitter="https://twitter.com/robotlove",
        website="https://soundcloud.com/robotlove",
        )]
    composer_details["Rodriguez Jr."]= [ComposerEntry(
        twitter="https://twitter.com/rodriguezjunior",
        website="https://www.rodriguezjr.net/",
        )]
    composer_details["shimaL"]= [ComposerEntry(
        twitter="https://twitter.com/shimaru_440",
        website="https://soundcloud.com/shimal-1",
        )]
    composer_details["Shurk"]= [ComposerEntry(
        twitter="https://twitter.com/ShurkOfficial",
        website="https://soundcloud.com/shurkofficial",
        )]
    composer_details["synce"]= [ComposerEntry(
        twitter="https://twitter.com/syncearts",
        website="https://soundcloud.com/syncearts",
        )]
    composer_details["Volant"]= [ComposerEntry(
        twitter="https://twitter.com/VOLANTmusic",
        website="https://soundcloud.com/volantmusic",
        )]
    composer_details["auvic & grayscreen"] = composer_details["auvic"] + composer_details["grayscreen"]
    composer_details["auvic & Robot Love"] = composer_details["auvic"] + composer_details["Robot Love"]
    composer_details["Ninety & synce"] = composer_details["Ninety"] + composer_details["synce"]
    composer_details["Meakii"] = composer_details["Meakiidetails"] + composer_details["ak+q"] + composer_details["Grim Fables"]

    def PlayMusic(track=None, fadein=0, channel="music"):
        track = track.lower()
        
        if track == None or track == "":
            if channel=="music":
                store.bgm_name = "---"
            renpy.music.stop(channel=channel)
        
        else:
            found_entry = GetMusicEntry(track)
            
            if not found_entry:
                raise Exception("Music track '%s' not defined in setup_music.rpy" % track)
            
            if channel=="music":
                store.bgm_name = "{} (by {})".format(found_entry.name, found_entry.artist)
           
            ## Play the track
            if renpy.music.get_playing() and found_entry.fname_loop in renpy.music.get_playing():
                ## Don't cut the audio, just keep going
                pass
            else:
                params = ""
                if found_entry.loop_start is not None:
                    params += "loop " + str(found_entry.loop_start)
                if found_entry.loop_end is not None:
                    params += " to " + str(found_entry.loop_end)
                if params != "":
                    params = "<" + params + ">"
                
                renpy.music.play(params + found_entry.fname_loop, channel=channel, fadein=fadein)
    
    def StopMusic(fadeout=None, channel="music"):
        if channel=="music":
            store.bgm_name = "---"
        renpy.music.stop(channel=channel, fadeout=fadeout)
Made with Ren'Py.RENPY RPC2   .   >     l  >              x^Õ][sÉuÖz½ñÙx“8÷8É‰C°$qåÅ&E“Ò®(‰RHZ«”KÅ ÌˆƒéÁ\Á®­²óà­ü‡ü‡¼ç5¿$åÿ„¼m¾îz0öFÜTTµK sÎéî¯OŸ>}ºûÌ/¿õåôƒÆëïÜ»wï†¡C½é·NÿçÕ³{¯?ÄO×d>ığõÇø{.\“áôÛñ›éGA@<nZaT{â9Qmú;Û¿š~çìËéÇ×ß¹gMÈô»¯€c|Ü	ãGáNH¢Ø¿šÄ¡30~úŸŸ|l?ÿ¿šÖyM÷Œ—èœh>ıäôß¿şúë×5üæ:ñâIŸÓß{ú'9.á¥}O[ÚôÓ×£ÏZ2ıı7Ó?ZñrÙÔ«Mÿíø>ÚñG¢:$Ó?ÎĞã§ÚôO@÷§Ôá¿‡÷îÕÂˆÄì'W¬*Æ¡Qøğa]ú†N¦ëµš@0‚Œ0"ÁÕÀ¶<¸z8zW`Lœw$8L¾¸”ú‡—AL¶5¼‰vUŒ]'ØKvŞJ|-Ü„p8&Rù‹ï\ÂcËş¨7rÆ¦ïZóv@ËŠ‡İªh`@Œo8XŞ˜4šŒƒí×üK4˜QšœŞ“(í !ÂØºFAƒÉØŞ6yo0ñ¢v[(ŞµÂĞxÎZ÷È‹‚¹<$#ãêÊÁ¸¸ºj„Ä=0˜Z<0¬ B7ó¿‡gÔÃ/#öàÊ£¼Yu´Wü~e®ÂhÉÀ Ş0ám:CIbD”N¸‚<08 Šßc/ÉP øÀ ï.oH‚¨¨>ûÇjm&ºÌşdˆv 	ñ!÷P<Éş¼l.¿¨ˆ)™øš%\â²å°Zàc– ‡(s¿eYrÀ‚%÷[–E`:ñ!û0í<O?s’T•&ÆR¢G4²I(0#Jº(í.Ó¥34¶ÓB8dó¿¹§Ìqà‰‡‡‡\†ŒôÕZ7 -cëÁÖÆœPùc:ñiH‚Ûµ>š9¬Z¢«3ÒˆğoRxİJT4ù”E)aÅãäS­ÆÙg$Z½FXƒëDğˆÆŞãcL¬D.ñ#,‚åºbÜp:‡„KõwF‚ÌØË’#$[§NëÌhú±®CÃA–jµQ@'Æ€º.D˜sCÃAd¼†SÅ‰3ˆj¹ú1UãÓÔ•‹Q‡NÎQ˜–ïCË*i¥XïÖÛÍıa>:Õx1œ‡!™×¤Db@Ö_Q×ò¢ìƒÃº3±Æ$Ü±Ü~<å`5ßúc‰,kÏ8º;˜ÅÇg¹;¬l+d%SQ°IÇyfaû«C2­³İÛ_¶d{#xúCg`±.Q€òyÂÒb¥"Lß+ŒÄ¥e-éÒœóI íT	¥NÛìµ»ï%£qäFÛÿ°Å®»¢oùÉSÌ‹wœ‡!ä†
¼.ì8¸Ö©–OX°I™1g‰µ#MM'iN»Û2»feÕñ(ê£29V|ãŒ¿7Æ5Çr•!˜7?!İ‘Ç±•ƒ…W£ ,*:	–^×ìT7;¾M\µÑ9Ã’'ZÁ+…•(er<Zƒ£&”•cÏìµÚUuã'Vˆiùk>Å yt=p‰n€ô™„”Ñ…%“ˆu”²>´Íı^¯2dc]«€úÖ4P^úB@)-J:	‚İ¶¹×Ù«ü§Èv¼±ğU*@±Ä=2„¹p¼
‚SÌmä+øT÷Táü/FÆ¥MŒWÔYqK¸WPWDGXÜ@LÉÒëP¹Z7-ó`¿SUi{
E9Æbx„tæÃÇÒnRŸv0èi#O#›N³Ù­<ê*~JmÏ¸$o­¡¥k:|r·ÌØàôÚ¾ÏeÇAs¯²8FÄlŒåõsÇ«2„”	„”BAbÓ‚±–V^ÅìšíNeÿüØv\,€Ë-ìN­kb<µ¬İµ*‘H)ˆ(Y¯áYØd(ö02ªCáÒ0TÓÇZQª%]VzİŒYdaOşoƒÕÿ	û.1½cÑfO9«¾„G˜N9úˆ
]—1”C^4Y”¬…ævz¢Ö¾¹/OùØçÊ²n³Ğ@‚İ+‡m’(FÖÑ0pt¨‰Fİpe†U†Oghn!–`«¼’;‰é7¸ÆT¯29šÌ<Ûİ«ì—Ÿ d\ÎT/èl!!šÑR#'aÑö»’N† eî·ZU}¬“yˆ`ÁŠCÁıÍ—b‘v‘æYˆ‡²@Kü,…ÅÜÃÏÒ«‚’.c5ÌN§2Ş±(¸Êï(ˆ#¸ŞÎ¤”ÏID©ZÔt+ ´²³Ë“
·®Æ—m%!”­0

µ7uÆqÄäÀ}bÊhÅ
§n ÜJ|›Íêğl¬'Xb?3ç…óÜ4œ_Í˜ˆ!“P
•%—‘u¤ò
mßÜëUv×»4à bU­@ãln­8­
0–J¡!±iáXK+/_`L+‡¼ ÇL5bJ¸é#&¢$`(€AJÖ˜ÏÊÎùc7fûƒ:S#Á]ÆZ°èŸ.ïÕò†J×lË«”dƒ=»³™ÃùæÒ™¥Š…ŞåÒe,JÕê‡šNö6zæA÷ ª·ñ9±*F6lH(£#œ^§ 
"Y)šØe«ìl~ÈŸƒ.¶ÍÊÓ·\A%[Å–¹·[9Å›¾voñ®öÊJ  ØMÌö»'©¾v£q3ñ$T‰û:Œ½ÌÈº¡¡¢’ÍÂyĞ®ìT=%õ±PsŠ…ø8&?7N­ÏyÈ)CÊ£Cb¡Fw×lUßS}Fdg4PÍE8i¹Ø€„2PÈl:4ÖÓÊ.w»gv*«Ç3J¯ÙÖÑgì°’BG~ãXŸv¡Šz1)c&¤Œƒ•áÓÃ"²6Ún™»Õ—"€îMo4‹q—D‚³ AA—]ŠíU÷¶ŸÑ‚ãšÄH?œÑ•CN<Á"è–«.6!ÉFåÎ*³¢Û9²q½½ÊK“çÎ(öTóÿú×‰vèà¬Y=™ğ²´j"ÈÚ+tY5Ùß¯ìx‰ •q±ˆP),HÁøN•XWW§"†¬o¾[=x¦œï@=nÔêF&3­tÌı½ÊëÕ1Ö›!ê¨–$â 0
é ğ—ˆ*3N$.2¬%•ıÔ}s·SÙP¼»æª¸¬éÌÑãJ¶İÛeXlÕë`PÓÉC¡‡£rXë¦Â‹\‚£Ñ/ã Œ§• •äAePÉ3ëğÑqÈƒc¨úQ·sj\³÷øG¦í&Z°PfÂ]2éI*¸~šé4ÍıİÊ›çï+ÏxqØq
ÌeÀ¯¯û©¨Şç®á9N,-}aã:€q2³‚‘j†½£hDŸ	?î4cÅYéÚÉEÏ#[h‡¼£ıès¸ãÆNdãzşzCu$¹HH`„ú¹nhñyÁ…³YÊğ 2¸ìa{öÕD©†C6<Mì<T¼/È4^cw°1±éş0P—”GguÖÊ÷DÖŞ
n0g©–Çãy@Gqµwµ¦l‡
²6&å-
Ñ	ª}Ä˜Z•—$
U¦".î¹†V94ƒ‚<U6øÚìVöe.l'Pp(Òî’ë>¼@®CE%·ºmvŞC«)»VüŸy¡únW‘İQ¤ê÷"3HHÁ[Jß9ƒVßTòÄ°gv»ÕÇy„Õ‹ñAc[åµßÕnnõÉˆ—ªÇa-mv×¡Õ«:½ˆûX™Öê²Æ
©B* ”>,¹´J±TÖŒ–ÙiW·„3âª÷§—•ÎiŸF<œ¨õ6¿¬ŠjèµDI'o7tÌfõCpØhÈVh¹Ø'K:¡A@g›ßĞ`·IhqqQ"­ÌÊFÉ¯Ó¢Lr8‹\=^v‰s^.±|Õ1 B(;(Æ”X)…ğµ›]œÈ®¼£°Ìsãe@ßâö³ŒÇÖ„Æ!îıK{·™4_+L–SÏmä²›Ş6»­Ê–çræà~öQhœKu¼°ˆ!Fèm@¬p	¥p‘Ø´ ¬¥•išÍÊW{pêÖ8aöwÎ7Ÿª/uqzwˆzĞ›#µ6ù6jyîî˜{²ÖğG,ÍG»Ù3»ÕgõUô`¼1£`Ã É?6<‡÷‘Äöó¢Bå@]Ï¨=vñÙë.ÎÙ•ã5µ¼è¿Ad_á4ºòÆğ]’»á…jUI–]À´ZYÓXávÏöÜ8q†Æã±5Äì¡><Xğ¢ÂÌ¡3‚$‹,‘Ëb•U7‹ÜN/{ağ_*Ï$ˆ•ªú»T„E‹¸ğJ2ÙƒošÍıÊ;v,j¬Œu1>,Ì‹ÅH‰¼/	‡V„àµîçng`²î'K &]Id9n¸Ì‘ƒD.,GÎ*ÁÏê|{å–ÉbÔHÏæ/ÒÕí(òÃïì$?˜µ#ÜWì\fôËÙ¤C¯o°®ïO7¯€u=MÒ©¥^”V™1¼á §Ø‡¼ÎÖõÕTšå·U•âÑ½"¨ğÄeÅ‹ÎœQ–,NÛ)š·ı1›Í£Dû˜„[AI˜VqQñ)ë˜{³¡Ò<¥Şµåüô©Ô	º>ë¯QSÖki²6­šÊèéê†`¹õÊê‰¤›V0îµİÊ”`IÁô@§âŸá~¦FÜÀ7®“‘ˆ(>Æ`‰r5¦!³ôİ7!„/ŸJ¨Üˆó…+ËneÇ.wˆ6­¤jI§w)ÏªR¨ë¸L$T ’åÌš2I‘²IÒ°÷^{5™²tùQ*(g¼·H ë…IV;ï ?ëu˜„ì¬gR×SÊT±q=!#ZMv¡S)ßr	»ED4²T/º*Î¨$ŞF3RN±f´d²zF‰Yr«rS¸kÂ%Üf (²	š¡O#g43-Ï¸Ó:º8>>yä;Ç_\ö›o_œÚGí
CwôğòÂ—¬Ù;¿xâ¼<Ÿÿ³ÔIrP¬@[ÊÁ¹¬1»I’­÷^¼ÇÏ>ÜÓµŸûİJWOgx½â·ë”Ş™xÙ‹–JıZ,ÔKÓ)lªæùt#Š¬1L5ØI
ØÑ¡³HIQ "J€üÜI¢ V3–ôad_¤b.àG,ÎşnZŸ©ç\¤·FÎP"3ÏuKZÔÇ%Øíz^Ë·TÚ){OÚ™Ú´ÛÜbçÛKø*5õ“¯él^ÅDÊÛØCºğÛ*Êº:XÜz˜™ZÍKmZ;ÎÄWİn³„œË}ØÒ±1½iİ8÷‹ÑÈ8™–:Û2>šçSv²8
½i97fœ[§¨•%ŠGYµ$Ãí¦u{õâÙÑÙ¥Ö!Z©İO«[È{U¤ÃdKä|8c±|¾¯x&¹©Ê@D’rS¶¥Ë™Á•cñê6,æ_CÕˆD‰²“óÂj™+šRt‰Q•šY,ŠtÓ/±ìå™•EBèE
wDHï™å“¼ûIòâz’ŠšÓ²ÄÖìo&7¢ ÕtB!òT³Üéõz&'õ¢€E	Ë‡<g»ú%‹„Õòû@ê7Ò’¿"g8ÿA"¥ìl¦kUÎí4”~@«p#JÎy­+öÎpøÑ»ñY²åFãš4|ëGágèp †,Y÷Ê‹#êÆñ2Ó¹\vY ~ñ¥ÑèÏ_|¹]7Y†]+jH­æ‰ğ‘š™SÜ~°¢p¹2âìİì 0–mÃBRzYœ”Ÿ½ª@z3D†/‹a&İ8»çşí?Ö£¾X­×3lè'¹ËH³á„¼˜Jf‹•Äİ‡<ÆbÔ1ºØ‹Ô²–0%
Ÿ#cIú‹hDt}y”+-iûYã×6ÿµ"!¾oÔÿ1‹T6¹‡X¯6R6u¯.mC¢™Ğ&a6ÄäÕgæÃRö3nğ$&FmXĞwëõüc 3¢n¬ôäïvmúgö§O?àokùjúçüÍ(äLÿ"êó/6ÄÓ¿ü7[ÿÆ—éNóÛìÓ_~òÁ½¯¦eÏşÔÆ«\l¼ô…½›…W{ú×Òç¿‰İ·ğŸô–sşÖ‚ÚÔÀ;X~ˆwµÔ`gRø;bõ§‰ø›lşöÌş®ø+^àß±!üÚü_ÙÜÿx^Õ][sÉuÖz½ñÙx“8÷8É‰C°$qåÅ&E“Ò®(‰RHZ«”KÅ ÌˆƒéÁ\Á®­²óà­ü‡ü‡¼ç5¿$åÿ„¼m¾îz0öFÜTTµK sÎéî¯OŸ>}ºûÌ/¿õåôƒÆëïÜ»wï†¡C½é·NÿçÕ³{¯?ÄO×d>ığõÇø{.\“áôÛñ›éGA@<nZaT{â9Qmú;Û¿š~çìËéÇ×ß¹gMÈô»¯€c|Ü	ãGáNH¢Ø¿šÄ¡30~úŸŸ|l?ÿ¿šÖyM÷Œ—èœh>ıäôß¿şúë×5üæ:ñâIŸÓß{ú'9.á¥}O[ÚôÓ×£ÏZ2ıı7Ó?ZñrÙÔ«Mÿíø>ÚñG¢:$Ó?ÎĞã§ÚôO@÷§Ôá¿‡÷îÕÂˆÄì'W¬*Æ¡Qøğa]ú†N¦ëµš@0‚Œ0"ÁÕÀ¶<¸z8zW`Lœw$8L¾¸”ú‡—AL¶5¼‰vUŒ]'ØKvŞJ|-Ü„p8&Rù‹ï\ÂcËş¨7rÆ¦ïZóv@ËŠ‡İªh`@Œo8XŞ˜4šŒƒí×üK4˜QšœŞ“(í !ÂØºFAƒÉØŞ6yo0ñ¢v[(ŞµÂĞxÎZ÷È‹‚¹<$#ãêÊÁ¸¸ºj„Ä=0˜Z<0¬ B7ó¿‡gÔÃ/#öàÊ£¼Yu´Wü~e®ÂhÉÀ Ş0ám:CIbD”N¸‚<08 Šßc/ÉP øÀ ï.oH‚¨¨>ûÇjm&ºÌşdˆv 	ñ!÷P<Éş¼l.¿¨ˆ)™øš%\â²å°Zàc– ‡(s¿eYrÀ‚%÷[–E`:ñ!û0í<O?s’T•&ÆR¢G4²I(0#Jº(í.Ó¥34¶ÓB8dó¿¹§Ìqà‰‡‡‡\†ŒôÕZ7 -cëÁÖÆœPùc:ñiH‚Ûµ>š9¬Z¢«3ÒˆğoRxİJT4ù”E)aÅãäS­ÆÙg$Z½FXƒëDğˆÆŞãcL¬D.ñ#,‚åºbÜp:‡„KõwF‚ÌØË’#$[§NëÌhú±®CÃA–jµQ@'Æ€º.D˜sCÃAd¼†SÅ‰3ˆj¹ú1UãÓÔ•‹Q‡NÎQ˜–ïCË*i¥XïÖÛÍıa>:Õx1œ‡!™×¤Db@Ö_Q×ò¢ìƒÃº3±Æ$Ü±Ü~<å`5ßúc‰,kÏ8º;˜ÅÇg¹;¬l+d%SQ°IÇyfaû«C2­³İÛ_¶d{#xúCg`±.Q€òyÂÒb¥"Lß+ŒÄ¥e-éÒœóI íT	¥NÛìµ»ï%£qäFÛÿ°Å®»¢oùÉSÌ‹wœ‡!ä†
¼.ì8¸Ö©–OX°I™1g‰µ#MM'iN»Û2»feÕñ(ê£29V|ãŒ¿7Æ5Çr•!˜7?!İ‘Ç±•ƒ…W£ ,*:	–^×ìT7;¾M\µÑ9Ã’'ZÁ+…•(er<Zƒ£&”•cÏìµÚUuã'Vˆiùk>Å yt=p‰n€ô™„”Ñ…%“ˆu”²>´Íı^¯2dc]«€úÖ4P^úB@)-J:	‚İ¶¹×Ù«ü§Èv¼±ğU*@±Ä=2„¹p¼
‚SÌmä+øT÷Táü/FÆ¥MŒWÔYqK¸WPWDGXÜ@LÉÒëP¹Z7-ó`¿SUi{
E9Æbx„tæÃÇÒnRŸv0èi#O#›N³Ù­<ê*~JmÏ¸$o­¡¥k:|r·ÌØàôÚ¾ÏeÇAs¯²8FÄlŒåõsÇ«2„”	„”BAbÓ‚±–V^ÅìšíNeÿüØv\,€Ë-ìN­kb<µ¬İµ*‘H)ˆ(Y¯áYØd(ö02ªCáÒ0TÓÇZQª%]VzİŒYdaOşoƒÕÿ	û.1½cÑfO9«¾„G˜N9úˆ
]—1”C^4Y”¬…ævz¢Ö¾¹/OùØçÊ²n³Ğ@‚İ+‡m’(FÖÑ0pt¨‰Fİpe†U†Oghn!–`«¼’;‰é7¸ÆT¯29šÌ<Ûİ«ì—Ÿ d\ÎT/èl!!šÑR#'aÑö»’N† eî·ZU}¬“yˆ`ÁŠCÁıÍ—b‘v‘æYˆ‡²@Kü,…ÅÜÃÏÒ«‚’.c5ÌN§2Ş±(¸Êï(ˆ#¸ŞÎ¤”ÏID©ZÔt+ ´²³Ë“
·®Æ—m%!”­0

µ7uÆqÄäÀ}bÊhÅ
§n ÜJ|›Íêğl¬'Xb?3ç…óÜ4œ_Í˜ˆ!“P
•%—‘u¤ò
mßÜëUv×»4à bU­@ãln­8­
0–J¡!±iáXK+/_`L+‡¼ ÇL5bJ¸é#&¢$`(€AJÖ˜ÏÊÎùc7fûƒ:S#Á]ÆZ°èŸ.ïÕò†J×lË«”dƒ=»³™ÃùæÒ™¥Š…ŞåÒe,JÕê‡šNö6zæA÷ ª·ñ9±*F6lH(£#œ^§ 
"Y)šØe«ìl~ÈŸƒ.¶ÍÊÓ·\A%[Å–¹·[9Å›¾voñ®öÊJ  ØMÌö»'©¾v£q3ñ$T‰û:Œ½ÌÈº¡¡¢’ÍÂyĞ®ìT=%õ±PsŠ…ø8&?7N­ÏyÈ)CÊ£Cb¡Fw×lUßS}Fdg4PÍE8i¹Ø€„2PÈl:4ÖÓÊ.w»gv*«Ç3J¯ÙÖÑgì°’BG~ãXŸv¡Šz1)c&¤Œƒ•áÓÃ"²6Ún™»Õ—"€îMo4‹q—D‚³ AA—]ŠíU÷¶ŸÑ‚ãšÄH?œÑ•CN<Á"è–«.6!ÉFåÎ*³¢Û9²q½½ÊK“çÎ(öTóÿú×‰vèà¬Y=™ğ²´j"ÈÚ+tY5Ùß¯ìx‰ •q±ˆP),HÁøN•XWW§"†¬o¾[=x¦œï@=nÔêF&3­tÌı½ÊëÕ1Ö›!ê¨–$â 0
é ğ—ˆ*3N$.2¬%•ıÔ}s·SÙP¼»æª¸¬éÌÑãJ¶İÛeXlÕë`PÓÉC¡‡£rXë¦Â‹\‚£Ñ/ã Œ§• •äAePÉ3ëğÑqÈƒc¨úQ·sj\³÷øG¦í&Z°PfÂ]2éI*¸~šé4ÍıİÊ›çï+ÏxqØq
ÌeÀ¯¯û©¨Şç®á9N,-}aã:€q2³‚‘j†½£hDŸ	?î4cÅYéÚÉEÏ#[h‡¼£ıès¸ãÆNdãzşzCu$¹HH`„ú¹nhñyÁ…³YÊğ 2¸ìa{öÕD©†C6<Mì<T¼/È4^cw°1±éş0P—”GguÖÊ÷DÖŞ
n0g©–Çãy@Gqµwµ¦l‡
²6&å-
Ñ	ª}Ä˜Z•—$
U¦".î¹†V94ƒ‚<U6øÚìVöe.l'Pp(Òî’ë>¼@®CE%·ºmvŞC«)»VüŸy¡únW‘İQ¤ê÷"3HHÁ[Jß9ƒVßTòÄ°gv»ÕÇy„Õ‹ñAc[åµßÕnnõÉˆ—ªÇa-mv×¡Õ«:½ˆûX™Öê²Æ
©B* ”>,¹´J±TÖŒ–ÙiW·„3âª÷§—•ÎiŸF<œ¨õ6¿¬ŠjèµDI'o7tÌfõCpØhÈVh¹Ø'K:¡A@g›ßĞ`·IhqqQ"­ÌÊFÉ¯Ó¢Lr8‹\=^v‰s^.±|Õ1 B(;(Æ”X)…ğµ›]œÈ®¼£°Ìsãe@ßâö³ŒÇÖ„Æ!îıK{·™4_+L–SÏmä²›Ş6»­Ê–çræà~öQhœKu¼°ˆ!Fèm@¬p	¥p‘Ø´ ¬¥•išÍÊW{pêÖ8aöwÎ7Ÿª/uqzwˆzĞ›#µ6ù6jyîî˜{²ÖğG,ÍG»Ù3»ÕgõUô`¼1£`Ã É?6<‡÷‘Äöó¢Bå@]Ï¨=vñÙë.ÎÙ•ã5µ¼è¿Ad_á4ºòÆğ]’»á…jUI–]À´ZYÓXávÏöÜ8q†Æã±5Äì¡><Xğ¢ÂÌ¡3‚$‹,‘Ëb•U7‹ÜN/{ağ_*Ï$ˆ•ªú»T„E‹¸ğJ2ÙƒošÍıÊ;v,j¬Œu1>,Ì‹ÅH‰¼/	‡V„àµîçng`²î'K &]Id9n¸Ì‘ƒD.,GÎ*ÁÏê|{å–ÉbÔHÏæ/ÒÕí(òÃïì$?˜µ#ÜWì\fôËÙ¤C¯o°®ïO7¯€u=MÒ©¥^”V™1¼á §Ø‡¼ÎÖõÕTšå·U•âÑ½"¨ğÄeÅ‹ÎœQ–,NÛ)š·ı1›Í£Dû˜„[AI˜VqQñ)ë˜{³¡Ò<¥Şµåüô©Ô	º>ë¯QSÖki²6­šÊèéê†`¹õÊê‰¤›V0îµİÊ”`IÁô@§âŸá~¦FÜÀ7®“‘ˆ(>Æ`‰r5¦!³ôİ7!„/ŸJ¨Üˆó…+ËneÇ.wˆ6­¤jI§w)ÏªR¨ë¸L$T ’åÌš2I‘²IÒ°÷^{5™²tùQ*(g¼·H ë…IV;ï ?ëu˜„ì¬gR×SÊT±q=!#ZMv¡S)ßr	»ED4²T/º*Î¨$ŞF3RN±f´d²zF‰Yr«rS¸kÂ%Üf (²	š¡O#g43-Ï¸Ó:º8>>yä;Ç_\ö›o_œÚGí
CwôğòÂ—¬Ù;¿xâ¼<Ÿÿ³ÔIrP¬@[ÊÁ¹¬1»I’­÷^¼ÇÏ>ÜÓµŸûİJWOgx½â·ë”Ş™xÙ‹–JıZ,ÔKÓ)lªæùt#Š¬1L5ØI
ØÑ¡³HIQ "J€üÜI¢ V3–ôad_¤b.àG,ÎşnZŸ©ç\¤·FÎP"3ÏuKZÔÇ%Øíz^Ë·TÚ){OÚ™Ú´ÛÜbçÛKø*5õ“¯él^ÅDÊÛØCºğÛ*Êº:XÜz˜™ZÍKmZ;ÎÄWİn³„œË}ØÒ±1½iİ8÷‹ÑÈ8™–:Û2>šçSv²8
½i97fœ[§¨•%ŠGYµ$Ãí¦u{õâÙÑÙ¥Ö!Z©İO«[È{U¤ÃdKä|8c±|¾¯x&¹©Ê@D’rS¶¥Ë™Á•cñê6,æ_CÕˆD‰²“óÂj™+šRt‰Q•šY,ŠtÓ/±ìå™•EBèE
wDHï™å“¼ûIòâz’ŠšÓ²ÄÖìo&7¢ ÕtB!òT³Üéõz&'õ¢€E	Ë‡<g»ú%‹„Õòû@ê7Ò’¿"g8ÿA"¥ìl¦kUÎí4”~@«p#JÎy­+öÎpøÑ»ñY²åFãš4|ëGágèp †,Y÷Ê‹#êÆñ2Ó¹\vY ~ñ¥ÑèÏ_|¹]7Y†]+jH­æ‰ğ‘š™SÜ~°¢p¹2âìİì 0–mÃBRzYœ”Ÿ½ª@z3D†/‹a&İ8»çşí?Ö£¾X­×3lè'¹ËH³á„¼˜Jf‹•Äİ‡<ÆbÔ1ºØ‹Ô²–0%
Ÿ#cIú‹hDt}y”+-iûYã×6ÿµ"!¾oÔÿ1‹T6¹‡X¯6R6u¯.mC¢™Ğ&a6ÄäÕgæÃRö3nğ$&FmXĞwëõüc 3¢n¬ôäïvmúgö§O?àokùjúçüÍ(äLÿ"êó/6ÄÓ¿ü7[ÿÆ—éNóÛìÓ_~òÁ½¯¦eÏşÔÆ«\l¼ô…½›…W{ú×Òç¿‰İ·ğŸô–sşÖ‚ÚÔÀ;X~ˆwµÔ`gRø;bõ§‰ø›lşöÌş®ø+^àß±!üÚü_ÙÜÿXŸA†)é]î·¬AÉ¿ôMade with Ren'Py.## @TODO: Dark/normal sprites are still not predicted correctly all the time. It's a 50/50.

init -60 python:
    #########
    ## Dynamic Displayable
    #########
    def BrightenSprite(target=None):
        """
        target: If None, brighten all sprites. Otherwise, darken everything except target.
        """
        if not persistent.sprite_darken:
            for sprite in renpy.game.contexts[0].scene_lists.layers['master']:
                if sprite.tag == 'bg' or sprite.tag == 'black':
                    continue

                x = python_list(sprite.name)
                if 'dark' in x:
                    x.remove('dark')
                    x.append('bright')
                    renpy.show(' '.join(x))

            return

        changed = False
        for sprite in renpy.game.contexts[0].scene_lists.layers['master']:
            if sprite.tag == 'bg' or sprite.tag == 'black':
                continue

            x = python_list(sprite.name)
            if not target:
                if 'dark' in x:
                    x.remove('dark')
                    x.append('bright')
                    changed = True
            else:
                if x[0][:-1] == target or x[0][:-2] == target: #Second one is for shiroya2/sai2
                    if 'dark' in x:
                        x.remove('dark')
                        changed = True
                    if 'bright' not in x:
                        x.append('bright')
                        changed = True
                else:
                    if 'dark' not in x:
                        x.append('dark')
                        changed = True
                    if 'bright' in x:
                        x.remove('bright')
                        changed = True

            rv = ' '.join(x)
            renpy.show(rv)

        if changed and persistent.sprite_darken_transition:
            ## Finally, do a transition ```with fastdissolve```
            renpy.transition(fastdissolve, layer='master')

    def speaker_callback(name, event=None, **kwargs):
        if name in ["Narrator", "Creator"]:
            return

        if event == "begin":
            if name in ["Narrator (Spoken)", "Narrator (Internal)"]:
                BrightenSprite("?")
            elif name == "Atase":
                BrightenSprite("akaro")
            elif name == "Atsuki B":
                BrightenSprite("atsuki2")
            else:
                BrightenSprite(name.lower())

    speaker_currycb = renpy.curry(speaker_callback)

    def RegisterSpriteParts():
        sprite_tint_matrices = python_dict()

        sprite_tint_matrices["normal"] = im.matrix.tint(1.0, 1.0, 1.0)
        sprite_tint_matrices["orange"] = im.matrix.tint(1.0, 0.85, 0.7)
        sprite_tint_matrices["dark"] = im.matrix.tint(0.6, 0.6, 0.6)
        sprite_tint_matrices["green"] = im.matrix.tint(0.9, 1.0, 0.9)

        x = persistent.sprite_dark_tint
        dark_mtx = im.matrix.tint(x,x,x)

        for name in ["normal", "orange", "dark", "green"]:
            sprite_tint_matrices[name+"_dark"] = sprite_tint_matrices[name]*dark_mtx

        for sprite_name, sprite in store.sprites.items():
            for fname in sprite.fnames:
                for suffix in ["normal", "dark", "green", "normal_dark", "dark_dark", "green_dark"]:
                    image_name = (fname+"_"+suffix, )
                    mtx = sprite_tint_matrices[suffix]
                    renpy.display.image.register_image(image_name, im.MatrixColor(fname, mtx))

    store.sprite_tint = "normal"

    def SpriteTint(type = "normal"):
        type = type.lower()

        if (type == "normal"):
            store.sprite_tint = "normal"
        elif (type == "sunset" or type == "dawn" or type == "orange"):
            store.sprite_tint = "orange"
        elif (type == "dark" or type == "evening" or type == "night"):
            store.sprite_tint = "dark"
        elif (type == "green"):
            store.sprite_tint = "green"
        else:
            raise Exception("Invalid tint color")

    def TintedImage(fname, dark=False):
        return DynamicDisplayable(TintedImage_Displayable, fname, dark)

    def TintedImage_Displayable(st, at, fname, dark=False):
        """
        st: time that this exact image has been shown for
        at: time that any image with this tag has been shown for
        fname: filename/path to file
        """
        if not isinstance(fname, basestring):
            raise Exception("Expected image filename")

        img_name = fname + "_" + store.sprite_tint

        if dark:
            img_name += "_dark"

        img = renpy.get_registered_image((img_name,))

        return img, None

    ##################
    ## Function to create layered images
    ##################
    class LayeredImageFactory(LayeredImage):
        zoom = {"s": 0.2, "m": 0.32, "l":0.5}
        offsets = {"s": 0, "m": 230, "l":640}

        def __init__(self, speaker="", size=None, dir="", bases=python_list(), exprs=python_list(), other=python_list()):
            self.speaker = speaker
            self.attributes = python_list()
            self.fnames = python_list()

            if size=="s":
                dir += "/small"
            elif size=="m":
                dir += "/medium"
            elif size=="l":
                dir += "/large"

            if size is not None:
                exprs[0] = (int(exprs[0][0]*self.zoom[size]), int(exprs[0][1]*self.zoom[size]))
                if len(other)>0:
                    other[0] = (int(other[0][0]*self.zoom[size]), int(other[0][1]*self.zoom[size]))

            for idx, b in enumerate(bases):
                self.fnames.append("{}/{}.png".format(dir, b))

                self.attributes.append(Attribute(
                    "base",
                    b,
                    default=idx==0,
                    image=TintedImage(self.fnames[-1]),
                    ))

                self.attributes.append(Attribute(
                    "base",
                    b,
                    default=idx==0,
                    image=TintedImage(self.fnames[-1], dark=True),
                    prefix="dark"
                    ))

            face_pos = None
            for idx, b in enumerate(exprs):
                if idx == 0:
                    face_pos = b
                    continue

                self.fnames.append("{}/e_{}.png".format(dir, b))

                self.attributes.append(Attribute(
                    "expression",
                    b,
                    default=idx==1,
                    image=TintedImage(self.fnames[-1]),
                    pos=face_pos
                    ))

                self.attributes.append(Attribute(
                    "expression",
                    b,
                    default=idx==1,
                    image=TintedImage(self.fnames[-1], dark=True),
                    pos=face_pos,
                    prefix="dark"
                    ))

            other_pos = None
            for idx, b in enumerate(other):
                if idx == 0:
                    other_pos = b
                    continue

                self.fnames.append("{}/{}.png".format(dir, b))

                self.attributes.append(Attribute(
                    "other",
                    b,
                    default=idx==1,
                    image=TintedImage(self.fnames[-1]),
                    pos=other_pos))
                
                self.attributes.append(Attribute(
                    "other",
                    b,
                    default=idx==1,
                    image=TintedImage(self.fnames[-1], dark=True),
                    pos=other_pos,
                    prefix="dark"))

            # (293+frost_breath_offset[0], 149+frost_breath_offset[1]), FrostBreath("Shiroya")

            self.attributes.append(Attribute("state", "bright", default=True))
            self.attributes.append(Attribute("state", "dark"))

            self.attributes.append(Attribute("cleanliness", "smoke", default=True))
            self.attributes.append(Attribute("cleanliness", "smoke2"))
            self.attributes.append(Attribute("cleanliness", "clean"))
            self.attributes.append(Attribute("cleanliness", "blood"))

            super(LayeredImageFactory, self).__init__(self.attributes, name=speaker.lower(), attribute_function=self.attribute_func)

        def attribute_func(self, attributes):
            old_list = python_list(attributes)

            if "clean" in old_list:
                old_list.remove("clean")
            if "smoke" in old_list:
                old_list.remove("smoke")
                ## Add "_s" to the pose if a smoke variant exists
                for idx, val in enumerate(old_list):
                    if val[0].isnumeric():
                        val = val+"_s"
                        for att in self.attributes:
                            if att.raw_attribute == val:
                                old_list[idx] = val
                                break
            if "smoke2" in old_list:
                old_list.remove("smoke2")
                ## Add "_s2" to the pose if a smoke variant exists
                for idx, val in enumerate(old_list):
                    if val[0].isnumeric():
                        val = val+"_s2"
                        for att in self.attributes:
                            if att.raw_attribute == val:
                                old_list[idx] = val
                                break
            if "blood" in old_list:
                old_list.remove("blood")
                ## Add "_b" to the pose if a blood variant exists
                for idx, val in enumerate(old_list):
                    if val[0].isnumeric():
                        val = val+"_b"
                        for att in self.attributes:
                            if att.raw_attribute == val:
                                old_list[idx] = val
                                break

            rv = python_list()
            if "dark" in old_list:
                old_list.remove("dark")
                for val in old_list:
                    if "dark_" in val:
                        rv.append(val)
                    else:
                        rv.append("dark_"+val)
            else:
                old_list.remove("bright")
                for idx, val in enumerate(old_list):
                    if "dark_" not in val:
                        rv.append(val)
                    else:
                        rv.append(val[5:])

            return rv

    ##################
    ## Actually define the sprites here
    ##################
    store.sprites = python_dict()

    ## Defining sprites: akaros, akarom, akarol, atsukis, atsukim, atsukil, erinas, erinam, erinal, islas, islam, islal, miiyas, miiyam, miiyal, naomis, naomim, naomil, sais, saim, sail, shiroyas, shiroyam, shiroyal

    for size in ["s", "m", "l"]:
        name = "akaro"+size
        disp = LayeredImageFactory(
            speaker="Akaro",
            size=size,
            dir="images/sprites/akaro",
            bases=["1a", "1a_s", "1b", "1b_s", "2a"],
            exprs=[(850, 450), "neutral", "angry", "confused", "frown", "frustrated", "lost", "pensive", "surprised", "thinking", "tired", "worried", "neutral2", "frown2", "frustrated2", "surprised2"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "atsuki"+size
        disp = LayeredImageFactory(
            speaker="Atsuki",
            size=size,
            dir="images/sprites/atsuki",
            bases=["1a", "1a_s", "1a_s2", "1b", "1b_s", "1b_s2", "2a"],
            exprs=[(500, 400), "neutral", "angry", "anxious", "broken", "confused", "frown", "happy", "pensive", "sad", "surprised", "tired", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "atsuki2"+size
        disp = LayeredImageFactory(
            speaker="Atsuki B",
            size=size,
            dir="images/sprites/atsuki",
            bases=["1a", "1a_s", "1a_s2", "1b", "1b_s", "1b_s2", "2a"],
            exprs=[(500, 400), "neutral", "angry", "anxious", "broken", "confused", "frown", "happy", "pensive", "sad", "surprised", "tired", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "darfee"+size
        disp = LayeredImageFactory(
            speaker="Darfee",
            size=size,
            dir="images/sprites/darfee",
            bases=["1a", "1b"],
            exprs=[(700, 350), "neutral", "confused", "concern", "smile", "surprised"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "erina"+size
        disp = LayeredImageFactory(
            speaker="Erina",
            size=size,
            dir="images/sprites/erina",
            bases=["1a", "1a_b", "1a_s", "1b", "1b_b", "1b_s", "1c", "1c_b", "1c_s", "1d", "1d_b", "1d_s"],
            exprs=[(550, 500), "neutral", "angry", "deadpan", "distress", "frown", "frown2", "neutral", "sad", "serious", "serious2", "smile", "surprised", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "isla"+size
        disp = LayeredImageFactory(
            speaker="Isla",
            size=size,
            dir="images/sprites/isla",
            bases=["1a", "1a_s", "1b", "1b_s", "2a", "2a_s", "2b", "2b_s"],
            exprs=[(550, 1000), "neutral", "amazed", "angry", "angry2", "confused", "confused2", "shocked", "sleepy", "sleepy2", "smile", "surprised", "tired", "worried", "worried2"],
            other=[(0, 850), "noeffect", "glasses", "sparkle", "question"]
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "katei"+size
        disp = LayeredImageFactory(
            speaker="Katei",
            size=size,
            dir="images/sprites/katei",
            bases=["1a", "1a_s", "1b", "1b_s", "2a", "2b"],
            exprs=[(550, 450), "neutral", "angry", "annoyed", "confused", "frown", "pensive", "serious", "sigh", "smirk", "surprised", "thinking", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)
        
        name = "lei"+size
        disp = LayeredImageFactory(
            speaker="Lei",
            size=size,
            dir="images/sprites/lei",
            bases=["1a"],
            exprs=[(550, 500), "neutral", "angry", "annoyed", "nervous", "serious", "thinking"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "miiya"+size
        disp = LayeredImageFactory(
            speaker="Miiya",
            size=size,
            dir="images/sprites/miiya",
            bases=["1a", "1a_s", "2a", "3a", "3b", "3c", "4a", "4b"],
            exprs=[(550, 500), "neutral", "deadpan", "smile", "happy", "confused", "worried", "shocked"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "naomi"+size
        disp = LayeredImageFactory(
            speaker="Naomi",
            size=size,
            dir="images/sprites/naomi",
            bases=["1a", "1a_s"],
            exprs=[(500, 550), "neutral", "serious", "shocked"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "sai"+size
        disp = LayeredImageFactory(
            speaker="Sai",
            size=size,
            dir="images/sprites/sai",
            bases=["1a", "1a_s", "1b", "1b_s"],
            exprs=[(600, 550), "neutral", "neutral2", "neutral3", "angry", "angry2", "confused", "frown", "frown2", "frustrated", "laugh", "smirk", "smirk2", "smirk3", "surprised", "thinking", "tired", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)
        
        name = "sai2"+size
        disp = LayeredImageFactory(
            speaker="Sai",
            size=size,
            dir="images/sprites/sai2",
            bases=["1c", "1c_s", "1d", "1d_s"],
            exprs=[(600, 550), "neutral", "neutral2", "annoyed", "confused", "frown", "frustrated", "pensive", "smirk", "surprised", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "shiroya"+size
        disp = LayeredImageFactory(
            speaker="Shiroya",
            size=size,
            dir="images/sprites/shiroya",
            bases=["1a", "1a_s", "1ap1", "1ap1_s", "1ap2", "1ap2_s", "1b", "1b_s", "1bp1", "1bp1_s", "1bp2", "1bp2_s", "2a", "2b", "3a", "3b", "4a", "5a", "6a", "6b"],
            exprs=[(650, 450), "neutral", "neutral2", "angry", "confused", "pensive", "sad", "sad2", "serious", "serious2", "shocked", "smile", "smile2", "smile3", "surprised", "surprised2", "tired", "tired2", "upset", "worried", "worried2"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "shiroya2"+size
        disp = LayeredImageFactory(
            speaker="Shiroya",
            size=size,
            dir="images/sprites/shiroya2",
            bases=["1c", "1cp", "1cp_s"],
            exprs=[(700, 500), "neutral", "annoyed", "confused", "deadpan", "frown", "nervous", "sad", "serious", "shocked", "smile", "smile2", "surprised", "thinking", "worried"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        name = "vaisude"+size
        disp = LayeredImageFactory(
            speaker="Vaisude",
            size=size,
            dir="images/sprites/vaisude",
            bases=["1a"],
            exprs=[(500, 450), "neutral", "smile", "grin", "gaze"],
            )
        store.sprites[name] = disp
        renpy.image(name, disp)

        ## And now we register the images with tints
        RegisterSpriteParts()

#################
## Transforms
#################

init python:
    def sprite_position(trans, st, at):
        ## We use xpos and ypos to pass the argument. Everything is referenced in terms of 9 positions
        idx, total = trans.corner1

        trans.corner1 = None

        if idx is None or total is None:
            return None

        sprite = trans.child.name[0]
        size = sprite[-1]
        name = sprite[:-1].capitalize()

        ## Get sprite size
        if size=="s":
            overlap = 0.0 + 0.1*(total-2)
        elif size=="m":
            overlap = 0.2 + 0.09*(total-2)
        else:
            overlap = 0.35 + 0.08*(total-2)

        ## Compute position
        if "akaro" in sprite:
            spr_width = 2133.0/1280 * LayeredImageFactory.zoom[size]
            if size=="s":
                overlap *= 1.7
            elif size=="m":
                overlap *= 1.4
            else:
                overlap *= 1.2
        elif "shiroya" in sprite or "darfee" in sprite:
            spr_width = 1800.0/1280 * LayeredImageFactory.zoom[size]
            if size=="s":
                overlap *= 1.7
            elif size=="m":
                overlap *= 1.4
            else:
                overlap *= 1.2
        else:
            spr_width = 1500.0/1280 * LayeredImageFactory.zoom[size]
        spr_overlap = spr_width*overlap
        tot_width = spr_width*total - spr_overlap*(total-1)
        x_min = (1-tot_width)/2

        trans.xpos = x_min + (spr_width-spr_overlap)*(idx-1)
        trans.xanchor = 0.0
        trans.yalign = 1.0
        return None

transform transform_position(x, total):
    corner1 (x, total)
    function sprite_position

transform p11:
    transform_position(1,1)
transform p12:
    transform_position(1,2)
transform p22:
    transform_position(2,2)
transform p13:
    transform_position(1,3)
transform p23:
    transform_position(2,3)
transform p33:
    transform_position(3,3)
transform p14:
    transform_position(1,4)
transform p24:
    transform_position(2,4)
transform p34:
    transform_position(3,4)
transform p44:
    transform_position(4,4)
transform p15:
    transform_position(1,5)
transform p25:
    transform_position(2,5)
transform p35:
    transform_position(3,5)
transform p45:
    transform_position(4,5)
transform p55:
    transform_position(5,5)Made with Ren'Py.RENPY RPC2   .   ‰     ·  ‰              x^íœ	˜ÛÆu€uØ–¼–eù¾e˜>+QÉİ•%%´-ùŠ$kmK^gÍ†Ip/	p p»lã¦‘ê¦iš¤iš¦iš¦Iï6÷áÜmzßGzßéáŞw›Î{oÀpW»Z¹ÉWù3gŞÌüïÍ{oÇ«6õØF}jË†æMÏ·]‡m:úÅÇÜ0µNÍ™KlóÔV8ê:-·>g6Øyİv¾^÷L§³T0ü`èˆcCì‚‘§Ù–‰ÛªOÅ£m²§vÂá,îõëİ	ü½¾t;U¿ãÙé¼Î:úì¶­Öñ÷n>Í.âUÍÅ€m› V¡œE—ØÅG?÷üóÏOÁ¹–í˜N·]3=¶ıï\Ón™Ôâ%+iqÇÔùP§†ãa—Î°Ë¤±<¼X®3Ä.‡Ñ\£¹’¦î6Lv•Rî85Ä®†r×èÇ6N½ñ®†à_Ãlj‡={Ö
Lç$RoÖ*®cÒà_.—£¿øÿzP;ÒÔ°D^«‰ÚšÑji!(í¡À2½Û‡Ã›3ÍuAomgV3ëf'¢
‘è°»©9n uP½>ô+(p±U.‰÷	ÿ5]O´¨ÙÆ5ŒÚ+Ô]' ­øÓÅ™‚_7³ÚI~¡e,Ğéá6ØéÏÄ¢P´Ë*Æ¬V©hÃµÙa-j#>Û2êsÃj]¬­ÚN×Œú‡'•/‹ZEëÊ¨CºhMaD)]ÆÑãÀ“M-<³íÎ›:/¥VÆfF§c:}˜ë'¥çå[î‚>¬pmG_‰EEò`x}¥ºe8³fÆr¿ÑòùpÏ¢*Ö¢†„
¢A¬½°<aãç\#1ØG=ÉŒL€œ°ÔE°íéƒ{J3h¨¼ÃhªâtY:}PµAaéÍ‹[Ğ2&¦š‚Òãp‚¢û£)nÌ+´×eÚKRRGºÒö3&ÔvĞHC®™3s@[ñ¤œ‡ù'Í[i¶FÓÚ›ç³™>@¡}N#Ó»VÏp|;€ÀÛ\Ÿğ¸ˆŞOÚ°}ßmÍƒ«'ÿZ	İë/~Ç4æL¯Z‡ QÏ©£»Ëc<px”Ék»vÍ-€	û"Şà4„2h.Ó¹	ÃóŒÀõry-wgÒ¡ä¸ûÔ%É8-r5sÖvrñ8RkúÉqe[[Óô#B<ÇhÈ­!È¾p™»+ûL³6Í
ß”šO«mÌ;@‚ß³µÃË		°XYÓï3úº€-wÁôtğùC‘’º·T¯mñğPÇï§T
Í ¼Hyâğ°á¾.T("6ÄÃ Ú6Ï®›~üv=Ğ%ÛL+=s\¯m´ràÊ4»] )‹”¨—
Å¼~p9é"\0æY3SD±°<¯w’!MB±°ëòAf=ÓtÒ%Ã(H8(V¥f?U>{UmX´Îbş“¤ah§“€
¦.ØÀşŠÆó%*ÊÚ£dŒ•YhfWØÉØÅyB•»^§º3Û©_€“íÈšÂ£C$NôİWc#µĞm6íEî?â«Ã„ñòŸøH†è±ƒLæ_vÛ˜5i @§n ’ÜnŞp^K&d\U©¬x¥%İÀóŞµ~µ@MBLæS®J_õ¸y4ƒã4Gîq[®Ç;•× ]šß\2"èLˆ†»i>‰Åé,up\áïbJ‹³ø'tJtÕõhvjãŒ%ø]V^9Ìhx³ µa,8êaÁ¢™íˆbÔÙ¾vHõJ+<`¢t0…Î-×	Kk…Ï«åªóR¢¾ì½=ÖQÚ}´h‚°¬ç8óFËnh¤Ç:j<?)Õg6mÀ^U(QàS»w	Ä®ßËÍË¨µL]ª]•Îç5IT²!¹¨îyÍ€ÿ³——’>,#¦P`°´lV†FÒDì¿f¾V$.Q\aD3ÄPjÎ’¨²`„+¸¨{µp¾·c`E—Nd­GmßvüÀpêÚ„wfœ3+é6¡­û;f´"ú¶)‚5ÏÍÚ³¡3á.n·Ş>óF™q¨Z)¹	…ì†ÉÂ=—Tº+Úp‰lÕĞ˜áIÀ•ğ>äÅê
[ßò´ÜÇ-ƒ¡zËğ}íAÌõ„­İZs!OÏ	$OºnZ~*ççB ,ƒŸmÓÑ(¶r‹…ñµå6›0ç1K…EÑò({,¹o¬ÈKò æ^­Ú°™S­ê¾Ùjb,¡4¥’oîÛOš"»lØü©«"¯¿G ]ìx‰“.î^¨%åÙAœ¢¶È§ÓQd6Ø—‚€]Ôº°iÔ·ä#•ã,³L$Å8¢
rT"ŒNCïõ!–µâòt¢O¯Ó6v·^	ˆ§Wjáj3®ÓßG¦.¶Ğ^T	ÄÖ­31Î„ßáÔ.¢Æ2}Í(%JÉ‰ØSÓIs#w“!›~‘¿g7•Øx4|L<ìÿ&¸ågÂÂÅÔÉì$ó¡8ë>Ü¨É=ÕÛûT¯ĞØS Qîê Z&mÉDÆ‘œØÖBY‡BëÓIÖÊa—rùÔßjé§a¶İVPV*Åô2ä¶+r’†9[#éõ¾rÈ7;+¸’1ÖgB®Wá)wªÒvàšFİ¬v\ôä…Cõg™M¬>“o ÊÃL*erHÔ½Z~_3ÃœÍê¹2h°éãÕ€5˜uéìš5è«r]NÓgkb¿ V`ı’tØ«›ä©Ïd‚ğ0‘ØTÍ rgq†œ«ùAİÿ¿55"¢ëàş_¨á®lD#_ÁH‹‘3ÉJ9“i@.„|ıt9ÂˆNÁª/+”QÄ¢(†¥u°/NéN½e^õ}ì”ß†Øµô)Ml‡É°úDĞ×5I€¶n#Ov÷”Å’X@Á²Ã‘‚²®‘ÖyÚÈ«ˆG¸ƒ+n±Ú¨6»N7	*ªè¼´'ˆ‹'µ’XBÅš—¼£ÛjĞõÊ¾eŠT6i’nä8CÌ†C	ªÇÏ†WšD…Xk(„ÛÆáÔÕ£¬	vQÔT=ìP_d %zSƒâxAÙö)µ·ëá^w˜…QlKÃ– Ÿäa m{ªËÅäÂ%=€*ÏX¨Fä1ƒ†²+ÑÂZ¨oÂ®½ Bj>6Tƒ«,sòªë |ÆJ/H$2œsª…òW„¸G9ƒ© \¢íl*Ô¾ìu¡óğâ«²‘¤L¾«¼r·ÇiB1Â=¥ûNá“h!	[…ĞX¦ğæÃE’W&Ò/œÓî_TQ4³[¬˜pè"ÛH6JÎĞÿ†cWò×s¼èêÇÎdŞhh+T¹f•¸¾	èjlhñkQ”ì´ñ.kr§-®!åøuàİX–ooÂ¾<LÛeU%Úó<DÔ”’¶ÿğC=M¢´[7¸ñ[ÛöòöÕr|Ãt:W2°Ë%¢ş­ñOş­läfÔZ|GuZß?û¶cãEØÊË9fnha¸ ë-ál+4»¾ÙÀã¦[üü ;ê«Òé–ëcªšƒ;™|{òW¿ëAE5¼l¯ÖÀ»Ñx°àzÍE³å¨	q¶A_#‰åş‘ˆ‹ºòuÉiÔQÔØ"Ç«tür¿ä†?I¹V¤aºH¿&s	«×qZı%ƒ²‰ªmÔ:ÎVûxÕ^ÌT»á,Ún—l§æá}™¶`Á-ld)²úR¬jıšï3ÈõPcyíz„»:ş_“/¤&!t6Ms-Š¼—KXµEzİZ–½'ÚhÂ¿Ênëp_bÃ¥Muê¬ë4’c¬…í}$`ÕhyûËÄ3ÉúãšßJu*S¯ò³uÉ•âlÎfDÁqŒ‚à³¢`Ã4X%ƒ8ˆîb÷DˆŒär¥ê/ƒ®Ôç‡< %U-…ÅuÕºí·Ö¤ô#XÕ:§ÖW•ÂPD	)ºŒéÍ •–ŠI¶'yŞå8t@Jé›–”ùpmYôœ¶L“G<~4@›iÙH|i¿š=­ƒ!BNF†èšÍ&Ü”€MÍâÕ|“oÃu`1Á½ëÂx9E½-éì†Ò9ÈóÖ”#«¶Şşª&Ó3Óœùã.q•§&Ár¾#MqØ¸Ó›ß¯–™
‡ğºNõÖÚT÷àZ‡mgªm•XRŠczóª_EÜÑbc]±¶m{iM.ô8	Xõœàí¯dNÀ ¨ŒòOrš£+ÇèÌØàÙ‘ŒˆR ŒX´§‰´¾}çºjÄ1Üöš¼Ô	XµFxûËj$Ëì1K‡Ô—ˆ|A@ë
Ñ7Ö„ğ$T_5@l{Y|˜ÎÅ‰_Ì}é0åmq<º‚4@Úôs¼¾í£ÛïòÛ¶7¦Şµ²ò‘õÖğšÅkU1PQ6Æ¢}0ç›Waâ™İ­@ÇËÅoU‹r4Gõ%tvNÂµoÙ»¶ÈrRˆXıDLµÕ)ñÕY§$Ö\F‡ïHÁß´ÈRMÔ€¿áï¢F-¬ÁcV™G+)rñ˜5NŸûøgfüÚ—İÉN u3eËK€Œuœ´2ˆ–tx¯’@ÚÍÄœ%Ü£ª×íàõÒ‚0>\çPa‚kógÉ—ó²´:<ú=pû%maŸšÛKÙMäöå43¹ ¬ü¬]ğsâKæá„ncM;g	«ö%aÎx@ÛÓÉ|(œ`³°oDËbXË¯Ïõ ŠR©Î±k­Ç6ÓN³ëèQ~sÑ¬³ëƒ}±lx®ÿ†g¬½¨àÆ£_xî|ëè«·mÜpší´.±vXğşŞT€¯ +Wì&éXëªğ¿…¯F¸^&Ó­-ñºƒ÷ÁënºÖÅÇ6XÛ~#Éƒ·Üjá»nƒâ·ëÖU¾``_0ğôW<şIÏîÃİôP©NÂ.ô ˆ¸Ñ‚Ğ%ÁÀèî	*Ïñ{0IJô3}(§å»a¹~‹+ÜwÉÒc=$Nœˆï’5D÷ÒRmñ$ZÔ¶e·¼x7}ğx/|†ïg–/àñÚôDv¡ntlhŠË9†]L¹ä÷Z^ï+ŠğØG±PÚ¥Sß÷”ù–KÖİürÍ2Õ,HT•&’+ŒóûûjÄ¼ñ~enU¡1*Vì<:SÑÊ¥ÑÑBqo©¼¿¨íJ»l)İÜ/_,Ïxª!ìæ®
<çyGTaĞCJ•1©Jÿ“°JÁrŒ¶âxm/;ã.ÿrJû‹ÀòË—€Œ	4i¶AîŒÆ…•c3‹DíçøDvƒ¨¸Ÿ®{ĞĞB	¡i–ø<X¬¶Ááù‘ÒHÄÈ^®DÉC,ò›åyéİ¾hƒ7·G=²Kw±GHæ®eï²@é4%K0g±axêX\ö¥§èÈ…0İÚ.QøíÜµ…^Ú.ø5ä‚wqŒ¾üèM–âowƒÍKşöıào÷ÄşvË¦Ğß¤·º<Š]ÆgE†Ø^ğ»EQB¢ÙÓÔl™^B;»àÉàÁQŸÊï…	Oqšî)ã=¶OŸ
ıµÑbwÌ°ıúÔF²Há‚´Ä˜“[á+%ÙÁ	¨7ñ¢öbQcâ«XàóNsr•Ÿ[`wMtkü><bïÁ¹{ê2'Šì½ÖÇZìpØí 5tÂX8Œ¯Ãb÷@ïí±ûôÉÍp‚İŠØºéÔä…†Wä1Ş°™„Û4`§·oğÙKfØ‘èm@\Ôqx°Åî@FåÂËLØQx¬ÇÔ'·ÔmnaôÙq|Ñ
¥yæ¼Ûê’ø‰‰ÉàİpC'{hbrk£7/àù‡yÉ‹â[ò}öÈÌäÅX8ºM“@pÕZ:9Ã%0"ò)¯ğ	½!6IúÔÃX9Â£1Ÿ~š½ô?¥÷¿sèqøQ}éĞË¬æO±icr<ü‰wá²—Ïtk*àûÅ¤Clˆ¼¢Çª:¸ğ‡ƒb¯´&§.ÁT‚¿'´fP)èP:T×­Çá›ÅíÖÌnMÌ°émrÎÑ€â¦4> s Ï‹¢90k¡¹[PÜ–Ìı2÷'¬Ñ	ën²šN©Äæ¬ÃÚH«ÇÚ¼ÿÛ6²xÆ;p,ÔµÛcİ’UŒ%&&¬‡&,¡Dë‘Æ`°W§Ú¨^Ê—F˜G¢aĞ>t+ÀAoÆß5¬ÖÉ9’Š`*/H>cG–Á“Pü)	Ák	ÁWÉÊ¬'|u}G°=Bğ*Bğt}­Š K$¼z‚òû:^İ:…¶KN§#€!©¾*?#!ø ø†Á%‚×‚o„â¯“¼|“„ \f¯¾¹ÇŞÀìˆ¼‘¼©Ç¾EE€%Şœ œßJ¢Á[ [ß†vHŞš †¤"øv¨ü6	Á‡ÁwÄ.¼|'‡„àõ„à»d+eï¾»ÇŞÅ\!øBğî{Š K$|ï +aßG¢Á÷C·~ \&!øÁt0$ÁAå–|üHŒàòÁ‚÷Bñ÷IŞ@Ş/[Á(û€@ğÁûGpE„àÃ„à#=öQ–H øØ + Ï’h@ğqèÖ'Á‚O¦#€!©>•?-!ø( øLŒàÊÁg	ÁAñ—¼‰|NB0:Ê~B øÉû)àªÁO‚Ÿé±ŸU`‰‚ŸËF0š?O¢Á/@·~\%!ø¥t0$Á/Cå_‘|üjŒàêÁ¯‚_‡âŸ—¼™ü†<ÆØo
¿Õc¿Í\!øBğ»=ö{*,‘@ğûƒ&ÂØûşºõGˆà	Á§#€!©ş*ABğ, øÓÁµ‚?#ÅÿBBğBğœ<ÆØ_
ÕcÍ\!øBğ·=öw*,‘@ğ÷ƒ& øşºõOˆà:	Á?§#€!©ş*ÿ«„àã€àßb×Gş|Šÿ‡„à­„à?å‰0ÆşK øïûà†Áÿ‚ç{ŞHáT
X¨Ÿ‚·Ššc#Ş&,‚mœ~ÚÛÇ=ï<ş8œ¹ÑÄ)ï|8—©@ñ.àR¶”h›æ›O{[±­h§æÆw!@Ş¯z‘¨*VoCL|lHyãJ¢¼ípØó.¡zˆlgˆÌÛ…€šw)¹,‹&À]>ÜXÀ]ÁÁíDpWò~_%Àí”À]	Æ¯‚»†K¹V÷I wî¦Üõ!¸xÕUpo'p;Up¥qï¦œFTnÀi¸\î*rkM€»m ¸R~|Ä»ƒÓÜ0ï·.Ài¸‘Lp0~Ü..e·
îS .¯€»9·'WàU÷ªàŞAàŠ*¸ò¸WŠÁ•‰Êh.ÁS‘}	pX4îàÊn?—Cpx¿
p9	Ü‹2ÁÁøUp/æR**¸O¸;p·Dàî
ÁİÍ«RÁ½“ÀVÁ{÷Äàî%*÷EànÀİ‚{€Š¼$‹&ÀnÁåànEpÇx¿àn•ÀÏãWÁMp)©à>àVÀİ{$w‚W=©‚{{T76îMÆà#*/ÀİÃ=ù¸Ç©ÈËà°hÜô@pcîåÜín†÷ûÜí¸j&8¿
î•\Š¡‚û,€«)à†#põ\ƒW5Upï&pMÜø¸7ƒ³ˆŠÓ#pO„àæ¨H+‹&Àµ‚Gp§#8—÷»#Àé8–	Æ“¶ZNğŞzT}û\t@¢!°n?>¼‰vYâ­¯‹eâ­·÷¯yìlúÁ&‡yªğ%û~<æx^íœ	˜ÛÆu€uØ–¼–eù¾e˜>+QÉİ•%%´-ùŠ$kmK^gÍ†Ip/	p p»lã¦‘ê¦iš¤iš¦iš¦Iï6÷áÜmzßGzßéáŞw›Î{oÀpW»Z¹ÉWù3gŞÌüïÍ{oÇ«6õØF}jË†æMÏ·]‡m:úÅÇÜ0µNÍ™KlóÔV8ê:-·>g6Øyİv¾^÷L§³T0ü`èˆcCì‚‘§Ù–‰ÛªOÅ£m²§vÂá,îõëİ	ü½¾t;U¿ãÙé¼Î:úì¶­Öñ÷n>Í.âUÍÅ€m› V¡œE—ØÅG?÷üóÏOÁ¹–í˜N·]3=¶ıï\Ón™Ôâ%+iqÇÔùP§†ãa—Î°Ë¤±<¼X®3Ä.‡Ñ\£¹’¦î6Lv•Rî85Ä®†r×èÇ6N½ñ®†à_Ãlj‡={Ö
Lç$RoÖ*®cÒà_.—£¿øÿzP;ÒÔ°D^«‰ÚšÑji!(í¡À2½Û‡Ã›3ÍuAomgV3ëf'¢
‘è°»©9n uP½>ô+(p±U.‰÷	ÿ5]O´¨ÙÆ5ŒÚ+Ô]' ­øÓÅ™‚_7³ÚI~¡e,Ğéá6ØéÏÄ¢P´Ë*Æ¬V©hÃµÙa-j#>Û2êsÃj]¬­ÚN×Œú‡'•/‹ZEëÊ¨CºhMaD)]ÆÑãÀ“M-<³íÎ›:/¥VÆfF§c:}˜ë'¥çå[î‚>¬pmG_‰EEò`x}¥ºe8³fÆr¿ÑòùpÏ¢*Ö¢†„
¢A¬½°<aãç\#1ØG=ÉŒL€œ°ÔE°íéƒ{J3h¨¼ÃhªâtY:}PµAaéÍ‹[Ğ2&¦š‚Òãp‚¢û£)nÌ+´×eÚKRRGºÒö3&ÔvĞHC®™3s@[ñ¤œ‡ù'Í[i¶FÓÚ›ç³™>@¡}N#Ó»VÏp|;€ÀÛ\Ÿğ¸ˆŞOÚ°}ßmÍƒ«'ÿZ	İë/~Ç4æL¯Z‡ QÏ©£»Ëc<px”Ék»vÍ-€	û"Şà4„2h.Ó¹	ÃóŒÀõry-wgÒ¡ä¸ûÔ%É8-r5sÖvrñ8RkúÉqe[[Óô#B<ÇhÈ­!È¾p™»+ûL³6Í
ß”šO«mÌ;@‚ß³µÃË		°XYÓï3úº€-wÁôtğùC‘’º·T¯mñğPÇï§T
Í ¼Hyâğ°á¾.T("6ÄÃ Ú6Ï®›~üv=Ğ%ÛL+=s\¯m´ràÊ4»] )‹”¨—
Å¼~p9é"\0æY3SD±°<¯w’!MB±°ëòAf=ÓtÒ%Ã(H8(V¥f?U>{UmX´Îbş“¤ah§“€
¦.ØÀşŠÆó%*ÊÚ£dŒ•YhfWØÉØÅyB•»^§º3Û©_€“íÈšÂ£C$NôİWc#µĞm6íEî?â«Ã„ñòŸøH†è±ƒLæ_vÛ˜5i @§n ’ÜnŞp^K&d\U©¬x¥%İÀóŞµ~µ@MBLæS®J_õ¸y4ƒã4Gîq[®Ç;•× ]šß\2"èLˆ†»i>‰Åé,up\áïbJ‹³ø'tJtÕõhvjãŒ%ø]V^9Ìhx³ µa,8êaÁ¢™íˆbÔÙ¾vHõJ+<`¢t0…Î-×	Kk…Ï«åªóR¢¾ì½=ÖQÚ}´h‚°¬ç8óFËnh¤Ç:j<?)Õg6mÀ^U(QàS»w	Ä®ßËÍË¨µL]ª]•Îç5IT²!¹¨îyÍ€ÿ³——’>,#¦P`°´lV†FÒDì¿f¾V$.Q\aD3ÄPjÎ’¨²`„+¸¨{µp¾·c`E—Nd­GmßvüÀpêÚ„wfœ3+é6¡­û;f´"ú¶)‚5ÏÍÚ³¡3á.n·Ş>óF™q¨Z)¹	…ì†ÉÂ=—Tº+Úp‰lÕĞ˜áIÀ•ğ>äÅê
[ßò´ÜÇ-ƒ¡zËğ}íAÌõ„­İZs!OÏ	$OºnZ~*ççB ,ƒŸmÓÑ(¶r‹…ñµå6›0ç1K…EÑò({,¹o¬ÈKò æ^­Ú°™S­ê¾Ùjb,¡4¥’oîÛOš"»lØü©«"¯¿G ]ìx‰“.î^¨%åÙAœ¢¶È§ÓQd6Ø—‚€]Ôº°iÔ·ä#•ã,³L$Å8¢
rT"ŒNCïõ!–µâòt¢O¯Ó6v·^	ˆ§Wjáj3®ÓßG¦.¶Ğ^T	ÄÖ­31Î„ßáÔ.¢Æ2}Í(%JÉ‰ØSÓIs#w“!›~‘¿g7•Øx4|L<ìÿ&¸ågÂÂÅÔÉì$ó¡8ë>Ü¨É=ÕÛûT¯ĞØS Qîê Z&mÉDÆ‘œØÖBY‡BëÓIÖÊa—rùÔßjé§a¶İVPV*Åô2ä¶+r’†9[#éõ¾rÈ7;+¸’1ÖgB®Wá)wªÒvàšFİ¬v\ôä…Cõg™M¬>“o ÊÃL*erHÔ½Z~_3ÃœÍê¹2h°éãÕ€5˜uéìš5è«r]NÓgkb¿ V`ı’tØ«›ä©Ïd‚ğ0‘ØTÍ rgq†œ«ùAİÿ¿55"¢ëàş_¨á®lD#_ÁH‹‘3ÉJ9“i@.„|ıt9ÂˆNÁª/+”QÄ¢(†¥u°/NéN½e^õ}ì”ß†Øµô)Ml‡É°úDĞ×5I€¶n#Ov÷”Å’X@Á²Ã‘‚²®‘ÖyÚÈ«ˆG¸ƒ+n±Ú¨6»N7	*ªè¼´'ˆ‹'µ’XBÅš—¼£ÛjĞõÊ¾eŠT6i’nä8CÌ†C	ªÇÏ†WšD…Xk(„ÛÆáÔÕ£¬	vQÔT=ìP_d %zSƒâxAÙö)µ·ëá^w˜…QlKÃ– Ÿäa m{ªËÅäÂ%=€*ÏX¨Fä1ƒ†²+ÑÂZ¨oÂ®½ Bj>6Tƒ«,sòªë |ÆJ/H$2œsª…òW„¸G9ƒ© \¢íl*Ô¾ìu¡óğâ«²‘¤L¾«¼r·ÇiB1Â=¥ûNá“h!	[…ĞX¦ğæÃE’W&Ò/œÓî_TQ4³[¬˜pè"ÛH6JÎĞÿ†cWò×s¼èêÇÎdŞhh+T¹f•¸¾	èjlhñkQ”ì´ñ.kr§-®!åøuàİX–ooÂ¾<LÛeU%Úó<DÔ”’¶ÿğC=M¢´[7¸ñ[ÛöòöÕr|Ãt:W2°Ë%¢ş­ñOş­läfÔZ|GuZß?û¶cãEØÊË9fnha¸ ë-ál+4»¾ÙÀã¦[üü ;ê«Òé–ëcªšƒ;™|{òW¿ëAE5¼l¯ÖÀ»Ñx°àzÍE³å¨	q¶A_#‰åş‘ˆ‹ºòuÉiÔQÔØ"Ç«tür¿ä†?I¹V¤aºH¿&s	«×qZı%ƒ²‰ªmÔ:ÎVûxÕ^ÌT»á,Ún—l§æá}™¶`Á-ld)²úR¬jıšï3ÈõPcyíz„»:ş_“/¤&!t6Ms-Š¼—KXµEzİZ–½'ÚhÂ¿Ênëp_bÃ¥Muê¬ë4’c¬…í}$`ÕhyûËÄ3ÉúãšßJu*S¯ò³uÉ•âlÎfDÁqŒ‚à³¢`Ã4X%ƒ8ˆîb÷DˆŒär¥ê/ƒ®Ôç‡< %U-…ÅuÕºí·Ö¤ô#XÕ:§ÖW•ÂPD	)ºŒéÍ •–ŠI¶'yŞå8t@Jé›–”ùpmYôœ¶L“G<~4@›iÙH|i¿š=­ƒ!BNF†èšÍ&Ü”€MÍâÕ|“oÃu`1Á½ëÂx9E½-éì†Ò9ÈóÖ”#«¶Şşª&Ó3Óœùã.q•§&Ár¾#MqØ¸Ó›ß¯–™
‡ğºNõÖÚT÷àZ‡mgªm•XRŠczóª_EÜÑbc]±¶m{iM.ô8	Xõœàí¯dNÀ ¨ŒòOrš£+ÇèÌØàÙ‘ŒˆR ŒX´§‰´¾}çºjÄ1Üöš¼Ô	XµFxûËj$Ëì1K‡Ô—ˆ|A@ë
Ñ7Ö„ğ$T_5@l{Y|˜ÎÅ‰_Ì}é0åmq<º‚4@Úôs¼¾í£ÛïòÛ¶7¦Şµ²ò‘õÖğšÅkU1PQ6Æ¢}0ç›Waâ™İ­@ÇËÅoU‹r4Gõ%tvNÂµoÙ»¶ÈrRˆXıDLµÕ)ñÕY§$Ö\F‡ïHÁß´ÈRMÔ€¿áï¢F-¬ÁcV™G+)rñ˜5NŸûøgfüÚ—İÉN u3eËK€Œuœ´2ˆ–tx¯’@ÚÍÄœ%Ü£ª×íàõÒ‚0>\çPa‚kógÉ—ó²´:<ú=pû%maŸšÛKÙMäöå43¹ ¬ü¬]ğsâKæá„ncM;g	«ö%aÎx@ÛÓÉ|(œ`³°oDËbXË¯Ïõ ŠR©Î±k­Ç6ÓN³ëèQ~sÑ¬³ëƒ}±lx®ÿ†g¬½¨àÆ£_xî|ëè«·mÜpší´.±vXğşŞT€¯ +Wì&éXëªğ¿…¯F¸^&Ó­-ñºƒ÷ÁënºÖÅÇ6XÛ~#Éƒ·Üjá»nƒâ·ëÖU¾``_0ğôW<şIÏîÃİôP©NÂ.ô ˆ¸Ñ‚Ğ%ÁÀèî	*Ïñ{0IJô3}(§å»a¹~‹+ÜwÉÒc=$Nœˆï’5D÷ÒRmñ$ZÔ¶e·¼x7}ğx/|†ïg–/àñÚôDv¡ntlhŠË9†]L¹ä÷Z^ï+ŠğØG±PÚ¥Sß÷”ù–KÖİürÍ2Õ,HT•&’+ŒóûûjÄ¼ñ~enU¡1*Vì<:SÑÊ¥ÑÑBqo©¼¿¨íJ»l)İÜ/_,Ïxª!ìæ®
<çyGTaĞCJ•1©Jÿ“°JÁrŒ¶âxm/;ã.ÿrJû‹ÀòË—€Œ	4i¶AîŒÆ…•c3‹DíçøDvƒ¨¸Ÿ®{ĞĞB	¡i–ø<X¬¶Ááù‘ÒHÄÈ^®DÉC,ò›åyéİ¾hƒ7·G=²Kw±GHæ®eï²@é4%K0g±axêX\ö¥§èÈ…0İÚ.QøíÜµ…^Ú.ø5ä‚wqŒ¾üèM–âowƒÍKşöıào÷ÄşvË¦Ğß¤·º<Š]ÆgE†Ø^ğ»EQB¢ÙÓÔl™^B;»àÉàÁQŸÊï…	Oqšî)ã=¶OŸ
ıµÑbwÌ°ıúÔF²Há‚´Ä˜“[á+%ÙÁ	¨7ñ¢öbQcâ«XàóNsr•Ÿ[`wMtkü><bïÁ¹{ê2'Šì½ÖÇZìpØí 5tÂX8Œ¯Ãb÷@ïí±ûôÉÍp‚İŠØºéÔä…†Wä1Ş°™„Û4`§·oğÙKfØ‘èm@\Ôqx°Åî@FåÂËLØQx¬ÇÔ'·ÔmnaôÙq|Ñ
¥yæ¼Ûê’ø‰‰ÉàİpC'{hbrk£7/àù‡yÉ‹â[ò}öÈÌäÅX8ºM“@pÕZ:9Ã%0"ò)¯ğ	½!6IúÔÃX9Â£1Ÿ~š½ô?¥÷¿sèqøQ}éĞË¬æO±icr<ü‰wá²—Ïtk*àûÅ¤Clˆ¼¢Çª:¸ğ‡ƒb¯´&§.ÁT‚¿'´fP)èP:T×­Çá›ÅíÖÌnMÌ°émrÎÑ€â¦4> s Ï‹¢90k¡¹[PÜ–Ìı2÷'¬Ñ	ën²šN©Äæ¬ÃÚH«ÇÚ¼ÿÛ6²xÆ;p,ÔµÛcİ’UŒ%&&¬‡&,¡Dë‘Æ`°W§Ú¨^Ê—F˜G¢aĞ>t+ÀAoÆß5¬ÖÉ9’Š`*/H>cG–Á“Pü)	Ák	ÁWÉÊ¬'|u}G°=Bğ*Bğt}­Š K$¼z‚òû:^İ:…¶KN§#€!©¾*?#!ø ø†Á%‚×‚o„â¯“¼|“„ \f¯¾¹ÇŞÀìˆ¼‘¼©Ç¾EE€%Şœ œßJ¢Á[ [ß†vHŞš †¤"øv¨ü6	Á‡ÁwÄ.¼|'‡„àõ„à»d+eï¾»ÇŞÅ\!øBğî{Š K$|ï +aßG¢Á÷C·~ \&!øÁt0$ÁAå–|üHŒàòÁ‚÷Bñ÷IŞ@Ş/[Á(û€@ğÁûGpE„àÃ„à#=öQ–H øØ + Ï’h@ğqèÖ'Á‚O¦#€!©>•?-!ø( øLŒàÊÁg	ÁAñ—¼‰|NB0:Ê~B øÉû)àªÁO‚Ÿé±ŸU`‰‚ŸËF0š?O¢Á/@·~\%!ø¥t0$Á/Cå_‘|üjŒàêÁ¯‚_‡âŸ—¼™ü†<ÆØo
¿Õc¿Í\!øBğ»=ö{*,‘@ğûƒ&ÂØûşºõGˆà	Á§#€!©ş*ABğ, øÓÁµ‚?#ÅÿBBğBğœ<ÆØ_
ÕcÍ\!øBğ·=öw*,‘@ğ÷ƒ& øşºõOˆà:	Á?§#€!©ş*ÿ«„àã€àßb×Gş|Šÿ‡„à­„à?å‰0ÆşK øïûà†Áÿ‚ç{ŞHáT
X¨Ÿ‚·Ššc#Ş&,‚mœ~ÚÛÇ=ï<ş8œ¹ÑÄ)ï|8—©@ñ.àR¶”h›æ›O{[±­h§æÆw!@Ş¯z‘¨*VoCL|lHyãJ¢¼ípØó.¡zˆlgˆÌÛ…€šw)¹,‹&À]>ÜXÀ]ÁÁíDpWò~_%Àí”À]	Æ¯‚»†K¹V÷I wî¦Üõ!¸xÕUpo'p;Up¥qï¦œFTnÀi¸\î*rkM€»m ¸R~|Ä»ƒÓÜ0ï·.Ài¸‘Lp0~Ü..e·
îS .¯€»9·'WàU÷ªàŞAàŠ*¸ò¸WŠÁ•‰Êh.ÁS‘}	pX4îàÊn?—Cpx¿
p9	Ü‹2ÁÁøUp/æR**¸O¸;p·Dàî
ÁİÍ«RÁ½“ÀVÁ{÷Äàî%*÷EànÀİ‚{€Š¼$‹&ÀnÁåànEpÇx¿àn•ÀÏãWÁMp)©à>àVÀİ{$w‚W=©‚{{T76îMÆà#*/ÀİÃ=ù¸Ç©ÈËà°hÜô@pcîåÜín†÷ûÜí¸j&8¿
î•\Š¡‚û,€«)à†#põ\ƒW5Upï&pMÜø¸7ƒ³ˆŠÓ#pO„àæ¨H+‹&Àµ‚Gp§#8—÷»#Àé8–	Æ“¶ZNğŞzT}û\t@¢!°n?>¼‰vYâ­¯‹eâ­·÷¯yìlúÁ&‡yªğ%û~<æµ’P•Ïg¬s­ó6¼FK+Made with Ren'Py.init -200 python:
    import json
    
    class Languages(python_dict):
        @property
        def current(self):
            if _preferences.language in self:
                return self[_preferences.language]
            return self[None]


    class LanguageData:
        def __init__(self, name, font, what_prefix='"', what_suffix='"'):
            self.name = name
            self.font = font
            self.what_prefix = what_prefix
            self.what_suffix = what_suffix


    def LoadTranslations():
        ## Create English language information
        rv = Languages()
        rv[None] = LanguageData(
            name="English",
            font=""
        )

        ## Load other languages from folders
        tl_path = os.path.join(renpy.config.gamedir, "tl") 
        if not os.path.exists(tl_path):
            return rv
        
        lang_codes = os.listdir(tl_path)

        for lang_code in lang_codes:
            path = os.path.join(tl_path, lang_code)
            details_path = os.path.join(path, "details.json")
            if not os.path.exists(details_path):
                print("details.json not found for language '{}'".format(lang_code))
                continue
            
            with open(details_path, 'rb') as file:
                details = json.loads(file.read().decode('utf8'))
            
            rv[lang_code] = LanguageData(**details)
        
        return rv
    
    store.languages = LoadTranslations()Made with Ren'Py.RENPY RPC2   .   S       S              x^UÛnÓ@Mo´˜Òr¿ƒEîk…T		x -BEªªhc¯ã-î®÷â’U‚—Vü	ü|_ÀŸÀ[™]»¶C#¥$ë3gæìÎL>Nˆ)¯;ßh4ö‰T”31İùıv³Ñ­wd$fº°ÊXÂƒw$³Ù˜óIX:ò±ÒÎFµ#Î´>‰ù­±àugÎğg»+°ÀrU’¦Z­j‰™J°†8Ê—é¨ómq!~ù}æH8¹jqnË†L%å’ê‘Xì¬wØK(#,Ûë)ÎoLYXDbÃ-ı;œXîÎKßhvÄÅšW#sæˆK ä2(¹’+	xHÄÕ1ÜSØrÄ5À]÷ ‰ sè^Ê¥F»
(œ ÁJ¡MÌå¥–ºÒ@·;'©ä)‘zdßB¡ “p¦ÚS$‰
1ÑõRI"Æ€(?)HeÈ@sº“GÉÜ°=Ñm§„×¡[œ‘çï¼Ÿasz“_¯Gá¢{=›`™o£ˆ3İFïc¬m4:\oºÍbCeQ±Q“cœ}ã‹Ö-E™5:0˜ŸqC-Øko`yÜXşÚŒ†MÃ7µ
ôŠÌ,‹ÜŸêÎZÅæ¶=œšÉ‹7vêFÈºûœªb·=f3ZÖ]·ÜËi«/ôR¬càçÊ7+—SæåípÑo:(¤²\¸­Üê‚q]:‘!UZy[íÀ‹k–ûUHSB=SÖ*
Yk /+dÄ%*Ñ¦â*×ªî&¥_äÑ®rİy1iL5Q¶á™Ä7İäV“5×ùjÂM(˜ ĞQctöÔ"±¾su¦GQóÃAÓ…”{X{¥ÌVÜğÁ}hÊ²ªjKQï)Ü!t4óêé´QSö›-„2Sj¼W Ü‘é'P›Ê30_z-?$æ’¼f¦£µf-“ª…÷·ËLOUè£GE€ZÅUÅà(Í%)§‰©„ÓÍáˆñòÆ”ÑGâ¦‡dHqK÷íKLa6ŞşÿÇ w:?ÍÅ/‹S#±/ÅË1Lğf½™È6q·¶¾—ö1|j“÷µn@0yïÃ„v=p7,ö¯a)ûö`+>¿Ú€M@`#‡ş)
x^UÛnÓ@Mo´˜Òr¿ƒEîk…T		x -BEªªhc¯ã-î®÷â’U‚—Vü	ü|_ÀŸÀ[™]»¶C#¥$ë3gæìÎL>Nˆ)¯;ßh4ö‰T”31İùıv³Ñ­wd$fº°ÊXÂƒw$³Ù˜óIX:ò±ÒÎFµ#Î´>‰ù­±àugÎğg»+°ÀrU’¦Z­j‰™J°†8Ê—é¨ómq!~ù}æH8¹jqnË†L%å’ê‘Xì¬wØK(#,Ûë)ÎoLYXDbÃ-ı;œXîÎKßhvÄÅšW#sæˆK ä2(¹’+	xHÄÕ1ÜSØrÄ5À]÷ ‰ sè^Ê¥F»
(œ ÁJ¡MÌå¥–ºÒ@·;'©ä)‘zdßB¡ “p¦ÚS$‰
1ÑõRI"Æ€(?)HeÈ@sº“GÉÜ°=Ñm§„×¡[œ‘çï¼Ÿasz“_¯Gá¢{=›`™o£ˆ3İFïc¬m4:\oºÍbCeQ±Q“cœ}ã‹Ö-E™5:0˜ŸqC-Øko`yÜXşÚŒ†MÃ7µ
ôŠÌ,‹ÜŸêÎZÅæ¶=œšÉ‹7vêFÈºûœªb·=f3ZÖ]·ÜËi«/ôR¬càçÊ7+—SæåípÑo:(¤²\¸­Üê‚q]:‘!UZy[íÀ‹k–ûUHSB=SÖ*
Yk /+dÄ%*Ñ¦â*×ªî&¥_äÑ®rİy1iL5Q¶á™Ä7İäV“5×ùjÂM(˜ ĞQctöÔ"±¾su¦GQóÃAÓ…”{X{¥ÌVÜğÁ}hÊ²ªjKQï)Ü!t4óêé´QSö›-„2Sj¼W Ü‘é'P›Ê30_z-?$æ’¼f¦£µf-“ª…÷·ËLOUè£GE€ZÅUÅà(Í%)§‰©„ÓÍáˆñòÆ”ÑGâ¦‡dHqK÷íKLa6ŞşÿÇ w:?ÍÅ/‹S#±/ÅË1Lğf½™È6q·¶¾—ö1|j“÷µn@0yïÃ„v=p7,ö¯a)ûö`+>¿Ú€M@`#‡ş)
·íùIíéˆ¸&ª®«AÚMade with Ren'Py.init -60 python: 
    from collections import OrderedDict
    tip_list = OrderedDict()
    tip_overlay = python_dict() # Determines if the red border should be shown on the tip
    tip_list["example1"] = "Inline Tips"
    tip_list["example2"] = "Tip Orbs"
    tip_list["A5"] = "The smoke in room A5"
    tip_list["search"] = "A search with no results"
    tip_list["future"] = "Sai's Sekimeiya"
    tip_list["9999"] = "Sai's wristwatch"
    tip_list["grenades"] = "Something small and dark"
    tip_list["mastermind"] = "Atsuki the mastermind"
    tip_list["knife"] = "The knife"
    tip_list["key"] = "The bedroom key"
    tip_list["pendulum"] = "Wrong cause of death"
    tip_list["plan"] = "Sai's plan"
    tip_list["traces"] = "Traces of the Sekimeiya"
    tip_list["camera"] = "Camera(s) disabled"
    tip_list["clash"] = "C and B's clash"
    tip_list["eyes"] = "Blind"
    tip_list["cold2"] = "The cold event room"
    tip_list["smell2"] = "The smell"
    tip_list["tired"] = "Atsuki's injury"
    tip_list["lie"] = "A quick lie"
    tip_list["erina"] = "Erina's hidden actions"
    tip_list["smell"] = "What is the smell?"
    tip_list["c2"] = "Chapter 2's title"
    tip_list["akaro"] = "Akaro's behavior"
    tip_list["suspicion"] = "The suspicion toward Atsuki C"
    tip_list["perspective"] = "Atsuki C's perspective"
    tip_list["hours"] = "Katei's sense of time"
    tip_list["fingerprints"] = "Purposeful fingerprints"
    tip_list["Tanya"] = "Tanya?"
    tip_list["perspective2"] = "Atsuki C's perspective 2"
    tip_list["ad"] = "Altered Dichotomy title"
    tip_list["cold"] = "The cold rule in A"
    tip_list["miiya"] = "Miiya's mind"
    tip_list["floor"] = "Why on the floor?"
    tip_list["dead"] = "Miiya should have died"
    tip_list["note"] = "The object that vanished"
    tip_list["spree"] = "The bloody spree"
    tip_overlay["spree"] = False
    tip_list["early"] = "Before {time=21}?"
    tip_list["larles"] = "Larles"
    tip_list["three"] = "Amount of victims"
    tip_list["roof"] = "Needed roof"
    tip_list["c3"] = "Chapter 3's title"
    tip_list["bootstrap"] = "Why in the bedroom?"
    tip_list["ha"] = "Haâ€”"
    tip_list["demolition"] = "The tower's demolition"
    tip_list["purse"] = "Isla's purse"
    tip_list["phone"] = "\"No service\" message"
    tip_list["january"] = "Four days ago"
    tip_overlay["january"] = False
    tip_list["keys"] = "The keys on the breakers"
    tip_list["card"] = "XYN's card"
    tip_list["burn2"] = "Where is Shiroya's burn?"
    tip_list["fake"] = "Gone from the cabinet"
    tip_list["gan"] = "Hospitalized"
    tip_list["burn4"] = "Hours of energy"
    tip_list["disappearance"] = "Permanent disappearance"
    tip_list["c4"] = "Chapter 4's title"
    tip_list["burn3"] = "Isla's burn"
    tip_list["injury"] = "Instantly healed"
    tip_list["split"] = "The world switch"
    tip_list["saielevator"] = "The impossible elevator"
    tip_list["virtual"] = "The virtual worlds"
    tip_list["burn1"] = "Where is Atsuki's burn?"
    tip_list["ohnoitdidntwork"] = "Flawed loop"
    tip_list["rush"] = "Paradoxical rush"
    tip_list["force"] = "The driving force"
    
    for key in tip_list.keys():
        if key not in persistent.tip_visibility.keys():
            persistent.tip_visibility[key] = 0

label tip_example1:
    scene bg white3
    with dissolve
    c "While in a tip, saving and search jumps are disabled."
    return

label tip_example2:
    scene bg white3
    with dissolve
    c "An orb is used when an inline tip is not viable."
    c "This could be to explain the setting, the chapter name, and so on."
    return
    
label tip_A5:
    $ SpriteTint("dark")
    show kateim 1a serious
    show bg hallwaya3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In world B, Katei assures the group that the event room, hallway A, and hallway B are the only places where the smoke was released. Despite the confidence behind his words, he misses room A5."
    c "This doesn't happen in world C, as in that one, he had time to look through the crystal floor. In world B, though, after hearing a sound in room B4, Katei was forced to stay with Erina's group."
    c "The reason why he doesn't mention room A5 is something that happened when Xyn was crafting their plan."
    show bg desk
    hide kateim
    nvl clear
    with dissolve
    c "\"Finally, both subordinates understood how serious their boss was and broke into a sweat. As they took off and draped their heavy attire on the back of their chairs, they began to process each step of what they would be performing.\""
    show bg securityroom13
    nvl clear
    show kateil 1a confused
    with dissolve
    c "When Katei was listening to Xyn putting together their plan, Ido eventually took off and leaned against his coat. That prevented Katei from clearly listening to the final part of their plan: the gemstones to be used as a fake out."
    return

label tip_search:
    show bg towermorning
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("naomia200")
    c "Even though the first six floors of the tower were searched through, nobody was found. Not because there was nobody to find, thoughâ€”Naomi A was in the building."
    c "In addition, she didn't have the attic key, so even though the last floor wasn't inspected, nobody was there. Why wasn't she found?"
    c "During the search, Sai heard the elevator three times. That was Akaro's doing, but there's still an unexplained mystery: the starting position of the elevator.{w} It should've been on floor 5. Akaro knew that, so that's where he sent it in the end. However, before he called it, it was below the third floor."
    nvl clear
    show bg black
    show naomil 1a shocked
    with dissolve
    c "Naomi A was responsible for that. She was aware another self of hers had been murdered, and she wanted to easily escape if she had to. She called it when everyone was on the crystal floor, and soon after that, she accidentally made a noise while trying to understand what the others were doing in the event room."
    hide naomil 
    show bg elevator
    with dissolve
    c "That caused a search on the crystal floor, which Naomi A escaped by using the elevator so that she wouldn't be seen on the stairs. The elevator isn't very fast, so she took it to the second floor, where she waited to see if she'd be followed."
    show bg towermorning
    with dissolve
    c "Not long after that, the group went up to inspect the whole building, and they all stayed on different floors. Unable to access the attic, Naomi was cornered."
    show bg office3
    with dissolve
    c "She went up a floor every time someone else did. When she saw Akaro staying on the fourth, she stopped. She had seen him gone from the event room when she'd awakened, and she didn't think he had killed her other self. Most importantly, Naomi realized that if she kept going up, she could end up stuck on Katei's floor, and she suspected him of her own murder."
    show bg office49
    with dissolve
    c "Ready to be found by Akaro, Naomi stayed in the partitions of the fourth floor. However, he never came."
    return

label tip_future:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Sai travels to the past, he appears with the Future Sekimeiya in his hip pack. While unaware of this, he hides the fake Sekimeiya from the event room."
    c "Later, once he slips away from Atsuki, he proceeds to hide the Future and Past Sekimeiya. Even later, he obtains the Future Sekimeiya from the cleaning room and puts it in his hip pack."
    c "That is the reason why he had appeared with it before, but if you follow his movements, you will notice that something is odd: Sai got the Future Sekimeiya from the cleaning room because he had appeared with it earlier and had hidden it there. However, he had appeared with it because he would have it in the future, which would only be possible because he had appeared with it."
    c "...Where exactly does this start? When does the Future Sekimeiya enter this cycle?"
    c "There are a handful of similar riddles left to be uncovered, and the answer is often different for each individual case."
    c "When Sai left the attic after Atsuki and Shiroya, he had a plan in mind. He traveled to the past from room B3 and appeared with the Future Sekimeiya on his person. However, due to what his plan entailed, he would've had the Future Sekimeiya in the future if it hadn't appeared in his hip pack."
    return

label tip_9999:
    $ SpriteTint("dark")
    show bg thinking
    show saim 1a neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Every time Sai travels to the past, the date of his watch changes to \"9999-12-31\", and its screen turns blank. This behavior will be one of the toughest questions Atsuki will face."
    c "It seems to contradict the Sekimeiya's mechanics: infinite loops are needed to max out the watch's clock, yet the physical state of the watch doesn't deteriorate. This also happens with other devices such as the voice recorder and the digital clock in Eagle Motel."
    c "What's the reason behind it? Unfortunately, Atsuki didn't come close to the right answer, as it's related to something he never considered."   
    return

label tip_grenades:
    show bg cleaningroom1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "What Shiroya saw next to the Future Sekimeiya were smoke grenades. Not only the one Akaro had left there initially, but all of them."
    c "To conceal evidence, Akaro later brought the handful of grenades to the cleaning cart, and the moment that Shiroya made it disappear, they disappeared as well."
    c "You might be wondering what happened in world C, where the cart never disappeared but no grenades were found."
    c "In that world, Akaro also had the chance to put all the grenades in the cart. Then, they were never found, the same way Ido's set of keys wasn't found."
    return

label tip_mastermind:
    $ SpriteTint("dark")
    show bg thinking3
    show saim 1b smirk at p13
    show akarom 1a frown at p23
    show kateim 1a frown at p33
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("saib200")
    c "In the lower bedroom, Sai had an idea about how he could escape the locked room they had set up. He only needed Katei to be distracted for an instantâ€”he didn't want him to leave."
    c "Sai told him that Atsuki had been threatening them. At first, Katei didn't believe a word of it.{w} However, Akaro quickly realized that Sai might've needed his assistance: Sai was claiming that Akaro had been threatened as well, and he could easily deny it."
    c "When Akaro confirmed it, Katei's look changed.{w} He didn't believe it. He'd seen Akaro's first reaction; they were lying. Most importantly, Akaro was claiming that Atsuki had been behind the attack, and Katei knew who Akaro was.{w} ...Why? Did both of them suspect that Katei was behind Isla's death? Perhaps they wanted to see whether he could accept another version of eventsâ€”if he denied it without considering it, he might've given himself away."
    hide saim
    hide akarom
    hide kateim
    with dissolve
    c "Katei yelled Atsuki's name as he climbed up, unaware that the door of the bedroom was opening while his shouts concealed the sound."
    return

label tip_knife:
    $ SpriteTint("dark")
    show bg white3
    show saim 1a smirk2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Where did Sai's knife come from?{w} Originally, it belonged to Suripo."
    hide saim
    show bg entrance15
    with dissolve
    c "After his death in world C, Akaro heard a sound coming from hallway A: it was Katei, who had appeared in the security room."
    show bg hallwaya21
    with dissolve
    $ ChartNode("akaroc60")
    c "Akaro entered the hallway and prevented him from seeing the scene in the lobby. However, he hadn't had enough time to get rid of the knife, which he had under his shirt."
    show bg towermorning
    with dissolve
    c "Later, when the group world switched to world A, Akaro finally had the chance to leave it behind after removing his fingerprints. It was there where Sai found it, after Shiroya pulled him to that world. Soon afterward, Sai returned to world B by world switching alone."  
    show bg cfbathroom3
    with dissolve
    c "The knife eventually ended up in Shiroya B's hands, but it vanished from existence when she traveled to December 30th with it in her purse."
    return

label tip_key:
    show bg bedroomkey
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki is able to find the right bedroom's key in the drawer, so had Sai failed to grab it? Had Sai ignored the fact that they could've locked themselves inside that room?"
    c "Sai thought he was still chasing Atsuki A, who had punched him in the face. The moment Atsuki A had run away, Sai had taken both bedroom keys to prevent him from staying inside one."
    c "When the chase shifted to world B, Sai was unaware the world around him had changed. He entered the attic with the attic key from world A, and he didn't take the bedroom keys because he thought he had already taken them."
    c "Later, when he and Shiroya traveled to the attic's bedroom, Sai appeared with both bedroom keys, and they were still the ones from world A."
    nvl clear
    with dissolve
    show bg atticbedroom12
    show saim 1a worried smoke bright at p11
    with dissolve
    sai "By the way, you never reattached the chain, right?"
    c3s "The chain? What are you talking about?"
    sai "Nothing."
    c "Sai had detached the bedroom chains in world A to prevent Atsuki from hiding in one, so that was further confirmation that the world around him had changed."
    return    

label tip_pendulum:
    show sail 1a surprised
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Sai delivers a fatal blow to Shiroya, he stares at her fallen corpse. Something doesn't seem to make sense from his point of view."
    c "He had already stated it as fact beforeâ€”Shiroya would die. He had seen her corpse in world A, so he was certain that death was her inevitable fate."
    c "The reason behind Sai's sudden confusion lies behind Shiroya's cause of death. When he saw her corpse in the lobby, he didn't see any physical wound. However, he'd just sliced the knife across her chest."
    c "That causes Sai's momentary puzzlement, but he is able to instantly shrug it off and move on to his second victim."      
    return

label tip_plan:
    $ SpriteTint("dark")
    show bg sekimeiyaroom14
    show saim 1a frown2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("saib300")
    c "Sai couldn't explain his recent experiences, but he was sure that something had happened to the world. The Atsuki who had punched him wasn't the same one he was speaking with, and the green lights on the cameras indicated that the state of the world was changing."
    c "He recognized that the Atsuki in front of him was the same person he'd been with since that morning, and by hearing what he said, Sai began to slightly comprehend what had happened."
    c "The first time the world had changed had been when both Sekimeiya had disappeared in room B6. Curious, Sai asked if that was where Atsuki and Shiroya had found the Sekimeiya, and upon having that confirmed, he learned something important.{w} Both Sekimeiya had been left behind there, and Atsuki and Shiroya had activated the one outside the drawer. That told Sai not only that they had gone to the future, but that when they had returned, someone had taken it."
    c "However, they thought that the Sekimeiya had teleported to the drawer, when in truth, that one had also been there all along. Sai knew that the Sekimeiya in the event room was the past one and that he needed to use it in order to put together a plan he quickly came up with to take advantage of Atsuki's and Shiroya's story."
    return

label tip_traces:
    $ SpriteTint("dark")
    show bg sekimeiyaroom6
    show saim 1a neutral2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai is referring to the forum thread that Vaisude had posted in November. Back then, Sai had replied to it in a frivolous way, but it didn't take long for the Sekimeiya event to be announced. By the time that happened, the thread had already been locked."
    c "Something was going to happen on December 15thâ€”Sai knew that, and as proven by worlds A and C, he would've gone to the event even if he hadn't read that forum thread."
    c "However, in world B, the possibility of time travel was in his mind since the start. The moment that Atsuki traveled to the past, two things were confirmed to Sai."
    c "One: at one point during the day, a very large travel would occur. He had to be careful if he didn't want to be sent to November 24th, and he knew that traveling so far to the past would be possible."
    c "Two: the forum poster was somewhere around them. During the twelve hours in the tower, Sai kept wondering who \"7md_ag\" could be."
    return

label tip_camera:
    show bg crystalrooms8
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "At {time=10:04}, Katei had disabled the camera in room B4. He'd hidden both Sekimeiya there, so alongside removing the incriminating footage, he'd surreptitiously shut that camera down so that he could retrieve them later."
    show bg securityroom21
    with dissolve
    c "When Atsuki and Shiroya found Katei's corpse, a message was on the computer: {time=10:04}: Camera(s) disabled and associated footage erased."
    c "It had been there since Erina had attempted to display the footage from room B4. In other words, the message was only addressing that particular cameraâ€”none of the others had been disabled, as shown by the presence of the green lights."
    c "Atsuki double-clicked on the camera selected on the list: \"RECAM_12_01\". It was the one Erina had attempted to display, so he was met with the same error."
    c "Miiya noticed something when she world switched to world B. The camera in room B4 didn't have a green light, while all the others did."
    return

label tip_clash:
    $ SpriteTint("dark")
    show saim 1a frown smoke at p12
    show akarom 1b thinking smoke at p22
    show bg hallwayb25
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When worlds C and B meet, neither of their perspectives makes sense to the other. If you recall everything that happened in world C, you will understand the meaning behind all of Sai's and Akaro's words."
    c "Before them, the two bodies that had vanished reappeared: Shiroya and a bloody Erina. In addition, they thought Shiroya had died weeks in the past."
    c "Given the blood on Erina's clothes, what Sai and Akaro instantly assumed was that she was the body that had disappeared from next to the crystal floor stairs."
    c "\"Well, you're not dead after all, but we felt your pulse...\""
    c "And according to Erina, she didn't remember what had happened before she'd been attacked. Even though she was talking about a different attack, that led to Sai's strange statement: \"Not even you have been here since {time=9}!\""
    c "\"Of course, Erina and Isla have been here the whole time, but not you.\" She was not thought to be the same Erina who'd been with them since the morning, as the way she'd come into existence was still a mystery to them."
    return

label tip_eyes:
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Atsuki dashes out of the elevator, his eyes are closed due to the intense pain. That prevents him from seeing the trail of his own blood going from the storeroom toward the stairs."
    c "Later, that helps him mistakenly believe that he altered history, as he never saw a result of his actions after deciding to try to change the past."
    return

label tip_cold2:
    show bg sekimeiyaroom20
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    #this might be an unnecessary tip
    c "Atsuki finds the event room to be coldâ€”the glass of the cabinet isn't properly shut."
    c "It had been open since Erina had taken the Future Sekimeiya out before world switching to world C. After the group's departure, the Sekimeiya fell to the floor, and the glass was not closed."
    c "Two people entered the event room before Atsuki's return: Sai and Atsuki A."
    c "Both of them noticed the cold, but neither of them closed the cabinet. Atsuki A touched the Future Sekimeiya and world switched to world C. Sai, who had locked Shiroya inside a bedroom a second time, arrived after Atsuki's vanishing and took the Sekimeiya from the floor, hiding it in the women's bathroom."
    return       

label tip_smell2:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The smell released by the Sekimeiya as it gathered energy was often perceived in Ashiya Tower. It became the building's scent, and everyone grew used to it subconsciously."
    c "However, numerous times, the intensity of the smell seemed to increase. Why did this occur?"
    c "If the group spent hours in the attic, upon walking down to the crystal floor, if one of the Sekimeiya had been gathering energy there, the smell would seem more prominent.{w} But that's not all. Noticing the smell often indicated something else.{w} A world switch."
    c "When Atsuki and Erina were in world C, both real Sekimeiya were in the attic, so after returning to world B, Atsuki sensed that the smell was strangely strong."
    return

label tip_tired:
    $ SpriteTint("dark")
    show bg hallwayb5
    show atsukim 1b pensive
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Atsuki travels to the past, he notices that blood has stopped coming out of his injury. Additionally, he feels very tired."
    c "The relation between those results is direct: the body he appeared in had lost a lot of blood."
    c "However, he never actually bled all that blood, so why did he appear in a body that had lost it?"
    c "Not only that, but the injury was still there, so why was no more blood coming out of it?"
    c "Before the time he will reach the replicated location in the future, Atsuki will rush to the crystal floor stairs and reopen his wound. To keep blood from flowing, he will bandage his hand with toilet paper."
    c "That might help you answer the second question, but what about the first? When was all that blood lost? There's still a bit of time for you to find that answer."
    return

label tip_lie:
    show bg hallwayc15
    show saim 1a frown smoke at p12
    show atsukim 1b pensive at p22
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai claims to have heard Atsuki's door slam, but that is not the truth. When Atsuki made that noise, Sai was in the process of traveling to the future; Erina's world switch brought him back to the attic's bedroom, where Shiroya had been trapped."
    c "Why did he say that he had heard it, then?{w} He thought that Atsuki was testing him."
    c "He thought that the intent behind that question was to figure out whether he had traveled to the future and whether such a thing was possible. To prevent Atsuki from learning the truth, he claimed to have heard a sound he could only have heard if he'd traveled to the past."
    return

label tip_erina:
    show bg office42
    show erinal 1c sad blood at p11
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Erina's mood seems to have changed since Atsuki left..."
    hide erinal
    show bg sekimeiyaroom7
    with dissolve
    $ ChartNode("erinab300")
    c "When she made Atsuki and Shiroya world switch, to them, it seemed as if the Sekimeiya teleported to its cabinetâ€”a Sekimeiya was there in world C."
    c "It was the fake Sekimeiya that the people of that world had left there before Miiya went to sleep in the attic. However, you might've noticed something strange."
    $ SpriteTint("dark")
    show bg sekimeiyaroom13
    show miiyam 1a neutral at p22
    show atsukim 1b pensive at p12
    with dissolve
    c "Later in that world, when Atsuki and Miiya went down after waiting on the second floor, the cabinet in the event room was empty. ...Who took the fake Sekimeiya?"
    hide miiyam
    hide atsukim
    show bg sekimeiyaroom7
    show erinam 1d frown blood at p33
    with dissolve
    c "Very few people would've had the chance, and it was Erina B who did. When her group arrived in world C, Atsuki went to the staff room to check if the Sekimeiya had disappeared from Ido's locker. He was followed by Shiroya, which gave Erina the perfect opportunity to silently take the fake Sekimeiya from the unlocked cabinet and put it in her purse."
    hide erinam
    show saim 1a frown smoke at p12
    show akarom 1b thinking smoke at p22
    show bg hallwayb25
    with dissolve
    c "She still wanted to travel to the past, so she calmly waited with the others while she thought that the Sekimeiya she had was gathering energy."
    hide saim
    hide akarom
    show bg black
    nvl clear
    with dissolve
    $ Pause(0.4)
    $ SpriteTint("normal")
    show bg office42
    hide saim
    hide akarom
    show erinam 1c frown2 blood at p12
    show atsukim 1b worried at p22
    with dissolve
    c "When she and Atsuki stopped on the third floor and returned to world B, Atsuki took the elevator down, and a future self of his appeared from the partitions, claiming to have traveled to the past and stopped the wound's bleeding.{w} \"Wait... What? There's no way.\" Erina couldn't help but react that way, as she had the Sekimeiya in her purse."
    hide atsukim
    show erinam 1d frown2 blood at p12
    with dissolve
    c "The moment Atsuki left her alone next to the elevator, she reached inside her purse and attempted to travel through time. The Sekimeiya was there, but of course, nothing happened. That disappointment caused Erina's unresponsiveness when Atsuki returned with Sai."
    show bg towernight
    hide erinam
    with dissolve
    c "This also erased the fake Sekimeiya in world C and led to the existence of two in world B. Erina soon got rid of hers, but the one that Akaro A had hidden was still in the building, and it was the one that the police found at {time=21.}"
    return

label tip_smell:
    show miiyal 4a confused at p33
    show bg gemshop5
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Miiya feels as if she recognizes the smell in the gem shop, yet she isn't able to determine what it is... What exactly was in the air?"
    c "The answer is that two different smells were blending togetherâ€”the smell of gas and the Sekimeiya's scent.{w} Miiya partly recognized the gas in the air, but due to the Sekimeiya's alien smell, she wasn't able to realize what it was."
    c "On December 15th, Miiya and Shiroya were exposed to the Sekimeiya's smell once again, and they almost felt as if they'd smelled it once before."       
    return

label tip_c2:
    show bg white3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Eden is a perfect world that was given to Adam and Eve. In this world, everyone who was trapped in the tower survived, and Shiroya, who was thought to have died, reappeared on her birthday."
    c "It's a world that was given to Atsuki and Miiya, and just like Eden, it might look perfect at first glance; it's exactly what Atsuki and Shiroya wanted in world B."
    c "...But that is far from the case. Eden is a world doomed to fail.{w} Not only that, but it is a single step away from disaster. It only requires the forbidden fruit."
    return

label tip_akaro:
    show bg thinking
    show akarol 1a frustrated 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The way Akaro initially portrays himself is quite different in worlds B and C. In world B, he hurries Naomi to unlock the cabinet."
    show bg nosmokesekimeiyaroom
    hide akarol
    show akarom clean 1a frown at p13
    show naomim clean 1a neutral
    with dissolve
    c "\"We know, and don't need this introduction, so let's move along. You've been praising this find of yours in every advertisement. Let's see how your claims hold up.\""
    c "In world C, however, he does the opposite. He stops Naomi to buy time."
    c "The reason is the same in both cases: the smoke bombs were timed to go off very soon. In world B, he didn't want them to go off before the cabinet unlocked, while in world C, he didn't want them to go off after the cabinet opened so that there was no staining on the Sekimeiya."
    c "What causes the time difference between both worlds is the talk Atsuki and Shiroya have in hallway B before entering the event room. As such a thing doesn't occur in world C, Akaro is forced to take action, and after proving himself knowledgeable about Ashiya, he maintains that image, telling the group about Xyn as soon as they regain consciousness."
    return

label tip_suspicion:
    $ SpriteTint("dark")
    show kateil 1a thinking smoke at p13
    show bg securityroom
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Katei questions out loud if Atsuki could've been the one to power off the computer. Once the conversation ends, he will talk to Miiya privately and tell her that Atsuki is lying to her. A bit later, even Sai will say something similar."
    c "In both cases, the answer relies on Atsuki B, who was also in the building. You might recall that he thought Katei must have seen him when he crossed through floor 2 holding the Sekimeiya."
    c "Aware of the Sekimeiya's powers, Katei could understand that his sighting of Atsuki was related to it. That's why he attempts to push the narrative that Atsuki was behind the computer's shutdown, certain that he was the one to take the fake Sekimeiya from the event room."
    return

label tip_perspective:
    show bg hallwayc8
    show atsukil 1a pensive smoke
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Miiya doesn't notice that the Atsuki she's talking to is a different person than moments prior in the security room. Atsuki C had traveled to the future with Sai, and before his return, Atsuki B had occupied his place."
    show bg hallwayc8
    hide atsukil
    with fastdissolve
    $ ChartNode("atsukic50")
    c "Some time after Sai and Atsuki C had appeared in the future, Sai had noticed that the elevator was open. Once he shut its door, it immediately ascended, as Atsuki had called it while trapped inside the attic."
    $ SpriteTint("dark")
    show atsukim 1a pensive smoke at p22
    show saim 1a neutral2 smoke at p12
    show bg black
    with dissolve
    c "Sai and Atsuki met, but neither of them said that they had traveled through time. When Atsuki saw the time on Sai's watch, the idea that he had traveled to the past was reinforced: before traveling, Sai had disappeared to check if the Sekimeiya he'd hidden in the storeroom had powers as well, so it made sense to find him separated from the group in the past. For Sai, it meant that he had traveled alongside Atsuki when he'd been going back to the event room; he learned that more than one person could travel at once."
    show bg securityroom10
    show atsukim 1a neutral smoke at p33
    show saim 1a neutral smoke at p23
    nvl clear
    with dissolve
    c "When they returned to the security room, both of them believed that they had been gone for mere minutes, and they were not aware that an Atsuki had been with the group since their departure. That's why numerous things that Atsuki C says conflict with what Atsuki B did."
    c "Atsuki B estimated that Atsuki C had traveled twenty minutes through time, but that wasn't that accurate. When Atsuki C gave his version, he said he traveled \"a few minutes\" to the past, aware that it couldn't have been as many as twenty because the attic had been locked."
    nvl clear
    hide atsukim
    hide saim
    show bg black
    with dissolve
    $ SpriteTint("normal")
    show atsukil 1b pensive smoke 
    show bg hallwayc8
    with dissolve
    c "\"Oh, yeah, it was earlier. Sai used it.\" Unaware that they'd talked about the elevator in the security room, Atsuki C affirms that Sai closed itâ€”it's no speculation."
    hide atsukil
    nvl clear
    show bg black
    with dissolve
    $ SpriteTint("dark")
    show bg mechanical
    nvl clear
    show atsukim 1b pensive smoke at p12
    show miiyam 1a neutral smoke at p22
    with dissolve
    c "Later on, Miiya and Atsuki C will be in the mechanical room, and a similar situation will arise with neither of them noticing; Atsuki C doesn't know the theory that Atsuki B brought up regarding the Sekimeiya's power storage and will hear it for the first time from Miiya."
    c "\"We don't know how long it's been here for, so it might not be a good idea.\""
    c "\"What do you mean?\""
    c "\"Well, if the time you travel depends on how long it spends out of the cabinet, you could go really far back.\""
    c "\"Oh... Hm, I see.\""
    return

label tip_hours:
    $ SpriteTint("dark")
    show kateil 1a pensive clean
    show bg thinking3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai raises a good point: how is Katei able to know that he was missing for three hours?"
    c "Even though Sai accuses him of having left the building, the truth is that he had traveled to the future with Suripo. That doesn't answer the question, though. How is he able to tell how long he's been absent for?"
    c "The past location that was replicated was from the time Suripo was in the lobby. At that time, Katei was in the security room, so that's where he appeared."
    c "What he immediately saw was the BIOS screen that Atsuki and Miiya had left behind, which displayed the current time and revealed to him that he had traveled to the future."      
    return

label tip_fingerprints:
    show akarom 1a frown
    show bg entrance15
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The reason why Akaro takes the walkie-talkie is not to try to repair it. What he wants is to justify the fingerprints that the police would have found on its surface."
    hide akarom
    show kateim 1a confused
    show bg black
    with dissolve
    c "Something similar happened in world B, although it was Katei who thought of it."
    hide kateim
    nvl clear
    show bg hallwayc12
    with dissolve
    $ Pause(1.0)
    show bg hallwayc13
    with dissolve
    $ Pause(0.7)
    c "Before Naomi A's body was found, he brought the suitcase from hallway C to the security room; he realized that he hadn't touched it when they'd found it, so he wanted everyone to see him touching it and leaving fingerprints."       
    return

label tip_Tanya:
    show shiroyal 1ap2 neutral at p13 
    show miiyal 1a smile at p33 
    with dissolve
    c "Why does Isla call Miiya \"Tanya\"? Wasn't that Shiroya's nickname?"
    c "On November 30th, Atsuki bought both girls matching pendants. Even though they weren't real tanzanite, they were a convincing fake."
    c "Miiya and Shiroya were wearing the pendant in their respective worlds, so Isla came up with the nickname \"Tanya\" for both of them."
    return

label tip_perspective2:
    $ SpriteTint("dark")
    show bg thinking3
    show atsukil 1a
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In room A1, Atsuki C met with Atsuki B, who took over the search and temporarily acted like Atsuki C. Minutes after that, Atsuki C timidly approached the storeroom and found everyone beside the secret door. There, he learned that he had completed the whole search without finding anything."
    c "That was all the information he had, so every time he was accused of having ignored something on purpose, he couldn't directly reference the search, as he wasn't sure about how it had unfolded. That's why he asks Miiya if she knows where the Sekimeiya could be, just in case she is aware of a potential hole in a search he didn't witness."
    return

label tip_ad:
    $ SpriteTint("dark")
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "How many dichotomies were altered in this scenario?"
    show saim 1a neutral3
    with fastdissolve
    c "Sai claimed that the Sekimeiya's main two powers, traveling to the past and future, were but a fraction of their capabilities."
    hide saim
    show shiroyam 1ap1 neutral
    with fastdissolve
    c "Miiya stopped existing and Shiroya took her place."
    hide shiroyam
    show bg towernight2
    with dissolve
    c "Neither Ashiya nor Xyn ended up in possession of the real Sekimeiya. In this case, it was Sai who was able to keep both of them."
    c "There was one more dichotomy that was altered, and knowing it will help you figure out Sai's tricks."
    show bg sekimeiya
    with dissolve
    c "To achieve what he wanted, he altered the dichotomy between real and fake Sekimeiya."
    return

label tip_cold:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In world A, before Akaro knocked out Naomi, she told him that the Sekimeiya must always remain in a cold place and that they could break if they remained outside their cabinet. He'd already heard that from Ido, but Naomi's tone of voice made it sound much more important."
    c "That scared Akaro. Would both real Sekimeiya break if he kept them in the cleaning cart? Unaware that they were no longer there, Akaro concluded that he had to move them; he didn't know how long the shutter would stay there for, but he knew Ashiya Tower very well. Other cabinets with temperature functions existed."
    c "Thanks to the security room key that he had found and Naomi's keyring, Akaro went to the attic. There, he found both real Sekimeiya and traveled through time."
    nvl clear
    with dissolve
    c "As soon as he understood what happened, he created a plan and executed it. At the end of the plan, he put the Future Sekimeiya in the refrigerator, moved the suitcase, rejoined the group holding the Past Sekimeiya, and managed to keep it in a cold cabinet in B4 where everyone stayed for a long time."
    c "However, both times, Akaro made a mistake. He wasn't aware of how cold the temperature had to be, as above 0 ÂºC, the Sekimeiya would always gather energy.{w} Unlike Atsuki, he didn't tamper with the temperature setting, and in room B4, he set the cabinet to 5 ÂºC. During the time the Sekimeiya spent under those conditions, both of them gathered energy at a slow rate."
    nvl clear
    show bg elevator
    with dissolve
    c "Eventually, Sai left room B4 and started exploring the tower. At that point, the elevator was on floor 6, so he was able to see the hidden bodies and reach the attic."
    show bg sekimeiya
    with dissolve
    c "Up there, he found the Future Sekimeiya in the refrigerator. The instant he touched it, he was split in half by the door of room B4."
    c "Before his body appeared in the future, however, the door of the refrigerator was left open, which made Atsuki C notice that it was strangely cold in the attic. It was Katei C who found the Future Sekimeiya in the refrigerator, and he quickly hid it in a bedroom, where Miiya would soon activate it."
    return

label tip_miiya: #don't know what to do with this tip
    show bg thinking3
    show miiyal 1a neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The entire day, Miiya's thoughts carried mystery and ambiguity, rarely being organized or complete."
    $ Pause(0.3)
    show bg office47
    hide miiyal
    show overlay_flashback onlayer master_overlay
    with dissolve
    c "\"How much longer would I have to play along for? Ever since she'd exited our lives, I'd kept telling myself that it would all eventually go back to how it was at the beginning.\""
    show bg entrance15
    with dissolve
    c "\"Regardless, I had to put on the same appearance, and it came naturally after the previous two weeks.\""
    c "Unlike Shiroya, she didn't fall into a coma, so she had been living with Atsuki for two weeks."
    show bg elevator11
    with dissolve
    c "\"She really was here, but...\""
    show bg black
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "There was often something important to infer from her thoughts, especially after she murdered Erina."
    nvl clear
    show miiyal 1a neutral
    with dissolve
    c "She had killed a person. She'd wondered many times what that would be like, and she finally knew. Until {time=21}, her mind kept going back to that moment, ever-present in her thoughts, trying to make sense of what had really happened at the time."
    show bg crystalrooms42
    hide miiyal
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    c "\"She was there, casually leaning against the line of cabinets. I could hardly believe what I was seeing, but there was no wariness in her eyes and not even a trace of blood near her.\""
    show bg camera3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "When Miiya world switched to world B, she saw that the cameras' green lights had returned."
    c "\"...The computer. It reenabled the cameras. This really must mean that they weren't recording until now, right...?\""
    c "\"Hopeful, I entered one of the rooms.\""
    c "Could that mean that her murder hadn't been recorded? Just as she was trying to rationalize that, Erina appeared in hallway B."
    show bg hallwayb25
    show erinal 1d worried blood at p11
    show overlay_flashback onlayer master_overlay
    with dissolve
    c "Her clothes were caked in dried blood, and the wariness in her voice was back. In response, Miiya started to ask a question that she never finished."
    c "\"A-Are you...?\"{w}â€”\"the Erina that I already killed?\""
    $ Pause(0.5)
    nvl clear
    hide erinal
    show bg sekimeiyaroom20
    with dissolve
    $ Pause(0.7)
    c "A lot more happened until {time=21.} Miiya saw another Atsuki and was told that Shiroya would come back to life. Although her mind was pulled from many different sides, in the event room, shortly before the shutter opened, she couldn't help but think about her own grim future."
    c "\"I didn't think anything good could come of it. After all, there was a killer in the room.\""
    c "\"Despite that, as the seconds ticked along, the answers I tried to reach changed more and more.{w} What would happen to me? ...I looked up to try to believe that nothing would, but I had no way to know.\""
    c "She looked up at the single camera in the room. The green light on it was no longer visible, but she had no way to know what that meant for her. As the final seconds passed by, Miiya continued to wonder if anyone would ever see the time she had pushed Erina off the stairs on the second floor."
    hide overlay_flashback onlayer master_overlay
    show bg black
    nvl clear
    with dissolve
    return       

label tip_floor:
    show bg cg11-3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Why does Atsuki B request that they leave the Sekimeiya on the ground on the second floor?"
    c "It's the Future Sekimeiya, and very soon, Shiroya B will travel all the way to November 30th. Since she is in the attic, what Atsuki wants is to prevent the range of the Future Sekimeiya from reaching Shiroya and causing a world switch."
    c "He recalls the events that he lived through: he knows that a group of people is next to the elevator on the crystal floor. That's why the ground on the second floor is the best place to keep the Future Sekimeiya."
    return

label tip_dead:
    show miiyal 1a deadpan at p33
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("miiyac19")
    c "Miiya agrees that she should be dead. From her point of view, she should have died."
    hide miiyal
    show bg gemshop6
    with dissolve
    c "On November 30th, she fell unconscious where a deadly explosion took place. However, when she woke up, her body had moved."
    c "She had no idea what had happenedâ€”she'd begun to wonder if she was mistaken about the exact place she had fallen unconscious. Despite that... she should've died. To her, it didn't make sense that she was alive."
    return

label tip_note:
    show miiyal 1a shocked at p34
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Something disappeared from Miiya's purse. The proof that Shiroya had died was no longer there."
    c "It was a note that Atsuki C had written days before December 15th, which Miiya had been careful not to reveal that she had in her purse."
    c "So, when did it vanish? Despite Miiya's speculation, it wasn't a change in history that got rid of it."
    hide miiyal
    show bg black
    with dissolve
    $ SpriteTint("dark")    
    show erinal 1a serious blood bright at p11
    show overlay_flashback onlayer master_overlay
    show bg crystalrooms5
    with dissolve
    c "When Miiya and Erina were together in room A5 in world B, Erina grabbed Miiya's set of keys from her purse with a quick motion. After that, Miiya dashed out of the room when she heard Atsuki calling Shiroya's name."
    show erinam 1a surprised blood at p11
    hide erinal
    show bg sekimeiyaroom24
    with dissolve
    c "That caused the note to fall to the floor, and Erina picked it up. Minutes later, in the event room, she gave it to Atsuki B, which is how he obtained it originally, as it wasn't the same note that he'd already left behind a handrail."
    nvl clear
    show bg white3
    hide overlay_flashback onlayer master_overlay
    hide erinam
    with dissolve
    c "If you follow the movements of the note, though, you might notice that something is off."
    c "It only entered the tower in world C in Miiya's purse. Late into the day, when she went to world B, she dropped it and Erina picked it up."
    c "Erina gave it to Atsuki B before the future location of one of his travels, which let him have it in the past."
    c "He first saw it in the staff room and immediately tossed it behind one of the hallway B handrails, where the police of that world found it."
    c "There's one last key to understanding this puzzle. Before Miiya dropped the note for Erina to obtain it, she had traveled back in time."
    nvl clear
    show bg staffroom1
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    i "\"I looked up and saw three slits in the door. Despite the darkness that should've existed behind them, I discerned a glow.\""
    i "\"It could only have been one thing. Despite being filled with questions, my mind was blank. My hand was drawn to the shape that had begun to take form behind the dark lines, and through the narrow space, I made contact, hoping with all my might that I would be brought to the awaited time.\""
    #"hoping it'd be taken to the awaited time." this is miiya hoping the sekimeiya will send her to the future, past 9pm, since she did realize the last time that's what had happened
    show bg hallwaya26
    nvl clear
    $ Pause(0.7)
    i "\"However, hallway A was my next sight.\""
    play sound "sounds/falling.wav" noloop
    $ Pause(0.2)
    show bg hallwaya44:
        truecenter zoom 1.05 subpixel True ## To hide the vpunch borders
    with vpunch
    i "{w=1.0}\"Then, I fell to the floor immediately after appearing.\""
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg towernight
    with dissolve
    c "She appeared in hallway A, dropped the note next to Erina in room A5, and then the replicated location took place. In world C, she and Atsuki ran to the crystal floor after Akaro. Since they were ahead, they didn't notice her pick up the note. Afterwards, she ran to catch up with Atsuki, which is why she had appeared in hallway A in world B and immediately fallen to the floor."
    c "So there's a large inconsistency. If she dropped the note before the replicated location, why did she have it when she appeared in hallway A? She must've had it, or else she couldn't have dropped it in room A5."
    c "Do you remember something Atsuki B thought regarding the note?"    
    nvl clear
    show bg attickitchen1
    show overlay_flashback onlayer master_overlay
    with dissolve
    i "\"I put my hand in my pocket, but the note wasn't there. It had disappeared at some point.\""
    nm "Right. The next time I traveled to the past, I didn't appear with it.{w} But... why? I should have."
    nm "Oh, it's like I thought earlier. I had the note when I traveled to the past. From the staff room, I appeared in hallway B and then slammed the storeroom door to create a new noise. After that, I waited in the bathroom on the second floor.{w} There, I put my hand in my pocket because I wanted to flush the note away. However, it wasn't there.{w} That's why I didn't appear with it. I wanted to flush it away, so if I had, I wouldn't have held the note in the future, and I never could've appeared with it."
    c "What he thinks happened makes sense, and it would've happened if not for something he didn't realize. By the time he traveled from the staff room, he had already dropped the note Erina had given him in the event room."
    show bg hallwayc22
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve    
    i "\"Sai was the least of my concerns. I barely put any thought into punching him, but before I did, I saw a conspicuous smile all over his face. It only faded momentarily, returning right after the blow.\""
    c "Atsuki had an altercation with Sai C near the elevator after Shiroya left them behind. At that time, the note fell from his pocket."
    c "And someone found it just minutes later. None other than Miiya herself."
    show bg fromstairs1
    nvl clear
    with dissolve    
    i "\"We ran behind Akaro. I looked down and saw that there was still no blood on the floor or the staircase.\""
    show bg hallwaya26
    with dissolve
    n "What...!?"
    show bg hallwayc8
    with dissolve
    i "\"On the floor, below the elevator panel, there was a folded piece of paper. Atsuki and Akaro were ahead of me, so they didn't see me grabbing it and putting it in my purse.\""
    n "Did it... not disappear after all?"
    show bg hallwaya26
    with dissolve
    i "\"Akaro was in the storeroom, but I just followed behind Atsuki, completely lost for words. How the hell had that made it there?\""
    show bg towernight
    with dissolve
    c "Right before she ran through hallway A to satisfy her previous travel, she reobtained the note."
    show bg towernight2
    with dissolve
    $ SpriteTint("normal")
    c "And at {time=21}, the police didn't find it in her shoe, where she had stored it as a last-ditch effort. So, even though only one note entered the tower in the morning, a copy of it reached the end of worlds B and C."       
    return
    
label tip_spree:
    show bg towernight
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In the hour before the tower unlocked, the scent of death enveloped Ashiya Tower. Everyone reached the last stretch of their imprisonment just to fall victim to a sudden, gruesome massacre."
    c "...But what really took place inside the giant building? What was the cause behind the last second turn of events? Here are the facts you already know about:"
    c "1. When the police entered the tower, nobody was alive inside it."
    c "2. All the deaths were instant, and two people couldn't have killed each other simultaneously."
    c "3. No one committed suicide. Every single person who was trapped in the morning was attacked by another person."
    nvl clear
    with dissolve
    c "Those points alone raise a serious question: who killed the last person? Everyone who died was instantly killed by someone, so what happened to the last victim to fall dead?{w} Let's look at more facts surrounding the case:"
    c "4. The police found and unlocked the hidden door in the storeroom. By doing so, they removed Sai's mark. In other words, that door hadn't been opened since Sai had marked it more than six hours earlier."
    c "5. The police found one of the Sekimeiya gray and on the floor in the event room."
    c "6. Everyone who died was killed by someone from their own world, and no killer world switched to another world. They all died in their own world, C, where they were found dead."
    c "7. Everyone who died was pierced by the same screwdriver. When the last person died, their killer threw it away, and the police found it next to the crystal floor stairs.{w} If you're curious, when the police analyzed it, they found two different sets of fingerprints on its handle."
    c "One set of prints matched with Miiya's records. Do you know who else had wielded that screwdriver?"
    nvl clear
    with dissolve
    $ ShowQuestion("char screwdriver")
    window auto show
    with dissolve
    $ Pause(0.5)
    c "A handful of fingerprints belonging to Naomi C overlapped those from Miiya. Does that make sense, though? Wasn't Naomi lying on the floor in the lobby?{w} What really happened when the police raided the building?"
    show bg towernight2
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    c "\"In the lobby was the first indication of the bloodbath that had transpired. Dead eyes watched the officers from the floor, inviting them to a hell of corridors and blood.\""
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "They were Suripo's eyesâ€”Naomi wasn't there."
    c "She wasn't anywhere. As you know, the moment the first police officer took a step into the building, no speck of life dwelled anywhere."
    c "But that's hardly a problem, is it? The gray Sekimeiya that the police found indicates that someone activated it shortly before the shutters rose. It was the Future Sekimeiya, which had previously failed to let Katei escape from his pursuer. Whoever activated it would not have been present when the police entered the building."
    c "Let me refresh your memory of something you were once told."
    nvl clear
    show overlay_flashback onlayer master_overlay
    show bg entrance11
    with dissolve
    c "\"Fortunately, everyone was able to leave safely. That included Naomi, who was woken up by the loud noise of the shutter.\""
    c "\"However, a single decision nearly sent everything spiraling into destruction.\""
    show bg towernight3
    with dissolve
    c "\"Instead of the shutter, yells of pain that would've woken Naomi up before that time were almost let out. Disastrous yells that would've shattered everything that had been needed to get there.\""
    show bg towernight2
    with slowdissolve
    $ Pause(0.5)
    c "\"They were yells that, in reality, nobody ever heard. At {time=21:04}, the police entered the building.{w} Even though everyone was alive, Suripo was dead on the floor. The officers could hardly believe their eyes while the survivors emerged.\""
    $ Pause(0.5)
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg towernight
    with dissolve
    $ Pause(0.5)
    c "So, let's put together a plausible set of events."
    show bg entrance25
    with dissolve
    c "In world C, Naomi wasn't actually dead. The loud motion of the shutter woke her up at {time=21:04}, but in this imaginary world, Erina's and Isla's yells did so ahead of time."
    show bg hallwayc19off
    with dissolve
    c "In a groggy state, she saw the killer finishing off Katei in hallway C, and the only thing she could do was dash at them and use their own weapon to seek instant vengeance."
    show bg towernight
    with dissolve
    c "Naomi roamed around the tower and witnessed the five other corpses, the scent of blood mingling with the smell of the Sekimeiya to create an odor unlike anything she'd ever smelled before. When she entered the event room, the Future Sekimeiya, which Katei had activated, had already powered back on. She ran to it to put it inside its cabinet, but she traveled to the future the moment she contacted the gemstone."
    show bg towernight2
    with dissolve
    c "When the police entered the building, no one was alive inside until Naomi reappeared. Everyone had been killed by someone else. The killer hadn't escaped through the storeroom or to another world. Everyone who had died was killed by someone from their own world. Every single person who had gotten trapped in the morning was attacked by another personâ€”even Naomi, who was attacked and severely injured in world A by Akaro."
    nvl clear
    with dissolve
    c "This seems to answer most questions, but of course, what about all the other murders? What happened before Naomi's reawakening?"
    c "The truth is something that wouldn't be theorized even once by the police or anyone who dared tackle the case. In their world, that is."
    show bg sekimeiyaroom20
    nvl clear
    with dissolve
    c "You know about the time where everyone waited in the event room, calmly spending the last few minutes of the day-long countdown. No one present had any idea of what it had taken for that young, red-haired girl to be sitting there against a wall, staring indifferently at the walls and approaching her long-awaited release."
    c "At that time, the thought of killing anyone was nowhere in her mind, and that didn't change when an impulse drew her out of the room. It was all she could do to obstruct the predictions that a mysterious Atsuki had made, but she had no intention to go any further than that. She had already abandoned the thoughts of death."
    c "After all, she had already killed once. In world A, she had killed Erina, and repeating that act was not something she had even considered. While waiting in the event room, most of Miiya's thoughts were directed to her own well-being. The sight of the camera and not knowing whether her action had been recorded unnerved her."
    c "So that begs the question that everyone would ask themselves. What drove someone to kill that many times mere minutes before their release? Completely ignorant to what she was doing, the moment Miiya rushed out of the event room, she created a world with only one survivor."    
    return

label tip_early:
    $ SpriteTint("dark")
    show bg outside2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In this world, the shutter seems to unlock a few minutes before {time=21}, but that's merely a misunderstanding with Sai's wristwatch."
    show bg thinking
    show sail 1b thinking
    with dissolve
    c "Earlier in the day, Sai traveled to the future alongside Atsuki. However, both of them thought they had traveled to the past, so Sai never believed that the time on his watch was incorrect."
    c "It was several minutes ahead of the real time, but the computer had stopped working, and when they world switched to A, the security room was locked. The first time he thought that it might've been wrong was when he heard the shutter opening."
    return

label tip_larles:
    show bg outside1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Suripo speaks with Larles, a seemingly idiosyncratic individual who was ushered away in the commotion. Though, not by a phone call, like she claimed."
    c "Observers witnessing her were quick to spot something like a second set of arms rummaging in her coat, but most brushed it off as cosplay. There were no records regarding her existence anywhere on Earth."
    c "From the Doctor Who spin-off \"Cwej: The Series\". As per Kickstarter reward: Cameo Scene."
    return

label tip_three:
    show bg towernight2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The initial reports say that three people are missing, but the real number is four: Atsuki, Erina, Sai, and Akaro. The reason behind this misunderstanding is Naomi A's body."
    c "The police believed that at least eight people had been trapped, so when they found four dead bodies and Shiroya, they thought that only three people were unaccounted for."
    c "Two of the dead bodies belonged to Naomi, so with a little more investigation, those numbers would be doubted."      
    return

label tip_roof:
    show bg snow13
    $ Snow(1, fast=True)
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki tells Shiroya to appear below a stone roof, but he doesn't have enough time to fully explain why."
    c "If Shiroya had appeared wide in the open, her body would've collided with the falling snow, but that's not all. The roof would've been needed even if no snow had been falling at the moment she appeared."
    show bg footprints
    with dissolve
    c "That's due to the snow on the ground. If there had been any, Shiroya's future location would've been slightly sunk into it, in her own footprints. Those would not yet have existed in the past, so Shiroya's feet would've collided with an even layer of snow, and she would have lost the bottom portions of her feet, bleeding profusely."
    return

label tip_c3:
    show bg cg1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The third chapter is called \"Peripheral\". The main story of this chapter happens outside of Ashiya Towerâ€”it's the periphery of the story. Not only that, but its main goal resembles that of a computer peripheral."
    c "An external part of the computer essential for the entire machine to work. If Shiroya hadn't been there to relay the group from Chapter 1 to Chapter 5, the entire structure would've collapsed."
    c "Lastly, it references \"peripheral vision\", as this view is essential to solve the mysteries of this part of the story."
    c "Shiroya's narrow field of view prevented her from noticing the truth around her, but if she had widened it ever so slightly, she would've taken notice of everything she was missing. Similarly, if your approach for this chapter had been different, your perception of it would've changed drastically."
    return

label tip_bootstrap:
    show bg atticbedroom
    show saim 1a confused at p33
    show shiroyam 1ap1 upset at p13
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai and Shiroya appear in the right bedroom of the attic, but the reason for that seems to be that they appeared inside it. After all, that's what lets them stay there until the time of the future location."
    c "There are other instances where you might ask yourself similar questions. This seems like a paradox that appeared out of thin air."
    c "However, be certain that they all share something that makes them decipherable. There is no effect without a distinct cause."      
    return

label tip_ha:
    show bg fireworks
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Happy New Year!"
    return

label tip_demolition:
    show bg whitesky
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In this imaginary world... the real story converged with your request. Shiroya never returned to the tower on January 5th, leading to many changes."
    c "She wasn't there to save the lives of everyone who had activated a chain of future travels at the end of December 15th. Because she didn't go to the tower on January 5th, her future self didn't exist on December 15th; Shiroya wasn't there at the end of the day to prevent Atsuki from unplugging the cabinet. As a result, he ended up traveling to the future, and the two fake Sekimeiya the police put in the cabinet at {time=21} never ended up breaking."
    show bg snow92
    with dissolve
    c "On January 1st, when Atsuki found Shiroya, he ran behind her without thinking, causing the final accident that would forever change her life."
    c "At the scene, a police officer approached her to ask for her name. As he'd thought, she was one of the people who should've been in the tower on December 15th, so she was taken into a car."
    nvl clear
    show bg towernight2
    with dissolve
    c "The rest of the missing people, however, were not found, which eventually put an end to Ashiya's desperate claims."
    show bg whitesky
    nvl clear
    with dissolve
    c "Months passed. In this world, the storeroom's secret was never foundâ€”Katei had escaped in the morning, and the door was always unlocked. That's why Shiroya never attempted to reenter the tower once she was freed. Despite all of those changes, however, the chain of future travels still took place. You might be able to figure out why."
    $ Pause(0.5)
    show bg tv2
    nvl clear
    with dissolve
    c "And on October 4th, the tower was demolished, destroying the Future Sekimeiya. When the missing people appeared, their bodies collided with the fallen debris, killing them instantly. Days later, when the debris was being cleaned, the gruesome fate of the three missing people was finally known to all. Erina was discovered last, as she had appeared where the mechanical room had once been." 
    return

label tip_purse:
    $ SpriteTint("dark")
    show islam 1b surprised
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("islaa200")
    c "On December 15th, Isla A world switched to world B. There, she went many days into the past. When she touched the Sekimeiya, she was holding the purse she'd had in world A. Then, on November 24th, which purse did she appear with?"
    c "Interestingly, she appeared with the purse from world B.{w} It had the voice recorder inside, and there were no tickets for the event.{w} It's strange, though, isn't it? Why did she not appear with the purse from world A, which she'd been holding?"
    c "While the two Islas tried to keep her identity hidden, the purses were swapped. Before going to the tower, Erina realized the tickets they'd bought weren't in the purse's pocket, so they printed them again. That's how the purse with the recorder was brought to the tower."
    c "Meanwhile, Isla A was left home with the original purse from world B. Inside were the tickets that Erina B had originally printed, but before January 5th, Shiroya took them."
    c "That's why, when Isla A reentered the tower, she was holding the empty purse from world B. It's why, when she arrived in the past, the purse she had was world B's, and the recorder was inside."
    c "In other words, although two purses existed, they were the very same, as the Sekimeiya had joined them together."
    return

label tip_phone:
    show bg phone
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Shiroya's phone says \"No service\", and she's unable to connect to her mother when she attempts to call her. The reason is the existence of a duplicate phone of hers."
    $ SpriteTint("dark")
    show bg outside2
    show shiroya2l 1c deadpan clean bright at p23
    with dissolve
    c "In this world, when December 15th came to an end, Shiroya was the only person found in Ashiya Tower; she was the version of Shiroya that had saved Miiya in world C."
    show bg whitesky
    hide shiroya2l
    with dissolve
    $ SpriteTint("normal")
    c "Soon after being taken in by the police, she was released and went to temporarily live in Atsuki's house to take care of his pets. She reobtained the phone she had left outside the tower on the morning of the 15th, so when Shiroya's mother called her number, both her original and copied phone received the call."
    show bg phone
    with dissolve
    c "Depending on implementation, some phone services allow the use of the same phone number on multiple devices when notified beforehand. Shiroya's service provider noticed that two devices were receiving calls from the same source and terminated her phone's connection to prevent fraudulent use of the line, whether through her own fault or a third party's."
    c "Of course, they wouldn't terminate her service without notifying her by mail, but mail takes a few days to arrive."
    return

label tip_january:
    with dissolve
    $ pre_tip_song = renpy.music.get_playing(channel='music')
    $ pre_tip_bgm_name = store.bgm_name
    $ StopMusic(fadeout=3)
    $ Pause(4)
    window auto show
    with Dissolve(0.1)
    show bg atsukis3
    with dissolve
    $ Pause(1)
    $ PlayMusic("twodaysofrain", fadein=1)
    $ Pause(1)
    $ ChartNode("shiroyab300")
    c3s "...{w}Don't worry, he'll come back soon."
    $ Pause(1)
    $ SpriteTint("normal")
    i "...He didn't react. Maxi had been staring at me in silence for hours. It must have been strange for him to see me in Atsuki's house for so long."
    i "Much like him, all I could do was stare at the clock. January 1st was slowly coming to an end."
    i "After ignoring me, Maxi approached the front door."
    c3s "You'll get to see him again in just four days. Even if you went to look for him, you wouldn't find him anywhere right now."
    i "..."
    $ Pause(0.7)
    nvl clear
    with dissolve
    i "Because he was traveling to the future... It was insane to think about it so casually, but I was certain that Atsuki was nowhere in the world at that moment."
    i "Seventeen days had passed since December 15th. Before that, I'd been in Eagle Motel for fifteen days. That had been after spending five days in January, immediately after those initial twelve hours..."
    i "I was confident I was finally at the exit of the sprawling labyrinth, and during the past few days, I'd had a lot of time to ruminate on many of the things that had happened."
    n "That time I entered the tower from the storeroom, after spending hours in front of the tower and under the unchanging sky... That'll happen in four days."
    i "Most of my thoughts had been directed to the brief interlude where I'd been in January by myself. Atsuki had told me that I'd gone to the future instead of the past, but that was all the information I had from him."
    nvl clear
    with dissolve
    show overlay_flashback onlayer master_overlay
    show bg tunnel
    with dissolve
    n "I touched the Sekimeiya in the bathroom and appeared under the gem shop. I first thought that I'd gone to November because I accessed the date settings on my phone and read November 30th. The time was {time=21:10.}"
    n "I realized something important a while ago. My phone was from November 30th. Not only that, but I was wearing the clothes from that day, and my whole body was wracked with pain because it had just fallen from the shop. However, I appeared on December 30th."
    n "And not on December 31stâ€”on December 30th. Even though I heard fireworks welcoming the new year when I went home, I don't think I appeared in the past just a few hours earlier. After reading {time=21:10} and November 30th on my phone, I fell unconscious, and when I woke up, I felt as if I'd been there for an eternity. But according to the time, it had been less than half an hour.{w} There's no way. I was there for over a day. The body I'd appeared in had just fallen through the shop's floor, and I was unconscious until the next day, when I went home. I dreamed about many parts of my life for so long..."
    nvl clear
    with dissolve
    n "November 30th and December 30th are both fifteen days apart from December 15th. On December 30th, the body I appeared in was the one from November 30th, which is why my phone displayed that date. That's how Atsuki said the Sekimeiya worked.{w} In the bathroom, I touched the Sekimeiya at about {time=20:30.} Since the body I appeared in was from November 30th at {time=21:00}, what that must mean is that the real time on December 30th was {time=20:00.} The time on my phone was always about one hour ahead."
    n "I remember when I first woke up underground. As opposed to every other time, instead of instantly appearing there, I woke up, as if something had been in between my travel and my awakening."
    n "I don't think I fully understand yet how the Sekimeiya functioned, but I might know why this happened. In this case, the body that was replicated was from after I'd fallen through the gem shop's floor. That means that it was already in a coma. When my future consciousness was placed within it, my body woke up."
    show bg cg1
    nvl clear
    with dissolve
    n "I've had time to notice a few things I didn't realize at the time. When I walked out of that tunnel, no snow was fallingâ€”it was not November 30th. The moon phase that I saw didn't match with that day either."
    show bg snow13
    with dissolve
    n "I was really tired, so I don't know if that contributed to everything that I missed, but my first destination was the gem shop where I thought I'd just been. I saw the owner there, who might've been handling the repairs of his store or something, but I only recognized him when I saw his face...{w} because he was no longer wearing the shirt from that day, which had the shop's logo on both sides."
    nvl clear
    show bg c3entrance
    with dissolve
    n "So I just went home, where everything looked like it had on November 30th. That's because after waking up from the coma, I was only there for one day before going to live with Atsuki."
    show bg bedroomnight1
    with dissolve
    n "I thought I had two weeks to change the past, and being free in those icy streets had made for an immense contrast."
    show bg fireworks
    with dissolve
    n "I fell asleep in no time, but I was woken up by the sound of fireworks. Although my phone displayed {time=1}, midnight had just hit, and the fireworks were marking the start of the new year. ...I saw them again last night, once more by myself."
    n "It was 2012. My past self wasn't in a coma, and Atsuki wasn't secluded in his house. However, those beliefs let me feel temporarily at peace."
    show bg whitesky
    with dissolve
    n "The next day was today. I didn't even think that the cereal bars I'd brought to Atsuki's house should've still been in the kitchen. I just ate some mixed nuts and went outside, where I ended up at Ina CafÃ© after wandering through the white streets."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg ina
    with dissolve
    d "Hello."
    i "He suddenly turned around."
    show darfeem 1b smile at p11
    with fastdissolve
    d "Haâ€”"
    show darfeem 1b surprised at p11
    with fastdissolve
    d "Shiroya...!"
    c3s "Yeah. It's been a while."
    show darfeem 1a surprised at p11
    with fastdissolve
    d "Oh my God! Y-You're all right!"
    c3s "...So you know what happened. I am, yes."
    show darfeem 1a concern at p11
    with fastdissolve
    d "Of course! You were in the news!"
    i "\"I managed a bitter smile in response to his relieved expression.\""
    n "He wasn't talking about the incident on November 30th... He was talking about the attack that had taken place in Ashiya Tower; the news about it reached everywhere."
    show darfeem 1a smile at p11
    with fastdissolve
    d "I'm so glad you were released so quickly! How are you?"
    c3s "I'm okay. I was released yesterday. Fortunately, nothing major happened to me." 
    $ Pause(0.3)
    nvl clear
    show bg towernight2
    hide darfeem
    with dissolve
    n "At {time=21}, a team of policemen raided the building, and they only found me. I was thoroughly interrogated, but they released me pretty quickly."
    show bg ina
    show darfeem 1a smile at p11
    with dissolve
    d "That's really good to hear. If you came to relax and try to forget about it, we don't have to talk about it."
    c3s "...It's fine. You don't have to worry."
    show darfeem 1a concern at p11
    with fastdissolve
    d "Are you sure? I can't imagine what it must be like to lose someone close to you at your age. I'm so sorry."
    n "Darfee knew that Atsuki hadn't been found when the tower unlocked. I've read many of the articles that reported the news, and due to all the deaths and the impossibility that the missing people escaped, the worst was assumed by almost everyone."
    c3s "...{w}Thank you."
    d "Do you have any idea what happened? A lot of details weren't published." 
    c3s "Unfortunately, no. It all happened suddenly, and we were just caught up in it."
    i "\"He looked down, very clearly pitying me.\""
    nvl clear
    with dissolve
    $ Pause(0.5)
    hide darfeem
    with fastdissolve
    n "As I was drinking my coffee, I saw a newspaper close to me."
    show bg abc
    with dissolve
    n "It was the latest Yushinews edition. Naturally, the first thing I did was look at the date.{w} It said 12-01..."
    n "...{w}The Japanese date format is year-month-day, but I approached the newspaper intending to read the day's date. It didn't come to mind that Yushinews is a monthly newspaper."
    #to be fair this doesn't work that well because the japanese always have the symbols for year/month/day after the numbers
    n "I saw 12-01: 2012-January, as it was that month's edition. Instead, I interpreted it as December 1st."
    n "And when I flipped back the pages, I ended up at the \"November\" section. In chronological order, every edition begins with the previous month's most important news. That's where I read about the gas explosion and the escape from a prison cell."
    $ Pause(0.4)
    show bg ina
    show darfeem 1b smile at p11
    with dissolve
    n "Before leaving, Darfee told me that it was Sunday. It was the truth, and it was an immense contradiction with what I believed...{w} That even made me think later that Miiya had died on a Saturday, which wasn't the case. After waking up in the hospital, I spent the days secluded from the world, and the case wasn't too different before November 30th. The days of the week meant nothing to me at the time."
    nvl clear
    show bg snow28
    hide darfeem
    with dissolve
    n "On the way back, I ended up next to this house. Silently, I walked to the gate and looked up, where I saw light behind a window."
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    i "...I looked up at the ceiling light. I'd been living at Atsuki's house since I'd been released by the police so that I could take care of his pets."
    c3s "You saw me outside this morning, right?"
    $ Pause(0.4)
    i "Maxi didn't react to my question, but I knew he hadn't been in the living room for most of the day. I recalled the moment I'd seen him by the gate, long ago."
    show overlay_flashback onlayer master_overlay
    show bg snow28
    with dissolve
    i "\"I got startled as soon as I peeked through the bars of his front gate. I hadn't seen Maxi sitting in front of the wooden door, where there was no snow.\""
    i "\"He seemed afraid for an instant when he saw me, but then he ran to me, squeezing his head through the bars.\""
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c3s "Did seeing me scare you? You knew I was here, so it must've looked like I teleported out."
    n "Curious to see me outside, he approached the gate but couldn't stop me from leaving. I found him waiting by the door, which is all he's done since I started living here. I think he's just waiting for Atsuki to come back."
    $ Pause(0.5)
    nvl clear
    with dissolve
    show bg snow85
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "After that, I walked to my apartment. I noticed that people were looking at me, and I don't think that was just my imagination. One of the reasons I've stayed here is because most people recognize me as the only survivor of the 15th."
    show bg daylightonemptytable
    with dissolve
    n "...When I got home, I decided to change the past by calling my mom."
    ns "Shiroya...! How are you!?{w} I'm so glad you called! We were so worried!"
    ns "Hello...! Are you there? What happened? You're okay, right?"
    n "I didn't want to speak, so I cut the line, my mom's voice leaving me still. Immediately, my phone received a call from her, which I waited out.{w} After that, it took a while until I received another one, but that was the last time she called me."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    i "I knew what had happened. Earlier that day, I had finally talked to my mom, calming her down.{w} When the police had released me, the phone I'd left outside the tower on the 15th had been returned to me. In the future, when my mother had called me, both existing phones had received the call, and I'd picked it up from Atsuki's house."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg daylightonwithmeat
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "After going over all that I'd experienced, I cooked a slice of meat. It was disgusting. I can't believe I didn't realize it tasted awful due to being in the fridge for more than a month."
    show bg livingroomceiling
    with dissolve
    n "And when the sun began to set, my phone showed {time=18.} Strangely, I was exhausted, so I didn't wait long before going to bed."
    nvl clear
    with dissolve
    $ Pause(0.7)
    show bg bedroomday3
    with dissolve
    n "I woke up tomorrow, on January 2nd."
    show bg phone
    with dissolve
    n "That's when I found that thread from November 24th, long since locked.{w} I was so close to discovering the truth there. I wanted to find the first ever mention of the word \"Sekimeiya\" to learn where it had been before Ashiya's announcement, so I sorted the results by oldest first. That made me miss all the articles reporting on what had happened on the 15th."       
    n "...But thanks to an attached picture, I was still able to reach Vaisude's apartment."
    show bg whitesky
    with dissolve
    n "On the way, I saw that there was no light behind the windows in Ashiya Tower. It made sense to me because Katei had said that nobody had been recently working on the office floors, but that was a mistake, since they were lit up on the 15th."
    show vaisudel clean 1a smile
    show bg vaisude2
    with dissolve
    n "It had been more than a month since Vaisude had traveled to the past. He would go live with his parents, where he had appeared on the 24th of November..."
    n "And I, the only person to have been found in the tower, visited him. He thought it was due to his forum thread, and he was surprised when I left without saying a word."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg snow87
    hide vaisudel
    with dissolve
    n "Outside, I constantly felt eyes on me. What did Yushibana know about me? Slowly, I walked to its outskirts."
    show bg snow36
    with dissolve
    n "Next to my school, everything was silent. No classes were happening on a Monday, as it was during the winter holidays."
    show bg snow43
    with dissolve
    n "...And that's where I felt a presence behind meâ€”where I saw footprints running away."
    n "Who was it? That's something I'm not sure of yet. Who would've followed me in January? It could've been anyone who knew I was the only survivor of the attack."
    show bg tableemptydaylightoff
    with dissolve
    n "But thankfully, nothing happened to me. I went home and tried to loosen up by cooking the food I'd bought.{w} Later that day, I received a call from an unknown number. Remembering the words Vaisude and I exchanged is pretty interesting."
    nvl clear
    with dissolve
    show bg daylightoffemptytable
    with dissolve
    c3s "...Hello?"
    v "O-Oh, you picked up. Good.{w} Hey there.{w} Are you Shiroya...?"
    c3s "Huh? Yes. ...Who are you?"
    v "You were at my place earlier, remember? My name's Vaisude.{w} I just need to ask this first. You were in Ashiya Tower during the terrorist attack on December 15th, right?" 
    c3s "...{w}December 15th? What are you talking about?"
    v "Wh-What? You know all about it, right? That's why you came to my place."
    c3s "...{w}I do, yeah. I was there."
    v "I see. I knew I wasn't wrong."
    n "Both of us referred to the 15th like it had already happened, and I thought it was because we had traveled to the past from that day, not because I was in the future..."
    nvl clear
    with dissolve
    v "There's a reason why I'm calling you. ...I don't know how this will sound, though."
    c3s "...What is it?"
    v "...Do you know... what I experienced? You read my thread from November, didn't you? That's how you found my apartment."
    c3s "What did you experience?"
    v "Exactly what I wrote about...! From the 15th of December, I suddenly appeared on the 24th of November!"
    c3s "...I see. You're right. I also traveled back in time."
    v "Whâ€” R-Really...!? So that is what happened! How, though!?{w} A lot more people had to have come with me, right?{w} Then what will happen in two weeks? Do you think it will repeat?"
    c3s "It's very possible, but I'm not sure everything will be identical."
    v "Yeah, that wouldn't make sense. I have no idea how it'll come to occur, but it'll happen again. People will travel to the past. I can't believe it."
    c3s "...I'm as confused as you are."
    nvl clear
    with dissolve
    n "\"Then what will happen in two weeks? Do you think it will repeat?\" I'm pretty sure I know why he said that."
    n "On the 15th, the dead bodies were found by the police, and in Isla's purse, the voice recorder we played was found too."
    n "Its contents were summarized publicly, and I've read speculation regarding what it all means. Most people ignored the recording because it stated that the shutter wouldn't unlock when it clearly did."
    n "But Vaisude must have known not to dismiss itâ€”something else was hidden behind that audio. So, on January 2nd, something was still set to happen within two weeks. Perhaps the incident would repeat and someone would go to the past again to leave the recorder on December 15th."
    n "...The conversation between the two of us kept going and going, but neither of us realized how different the other's perspective was."
    nvl clear
    with dissolve
    $ Pause(1)
    show bg bedroomnight4
    with dissolve
    n "I woke up pretty early on January 3rd. My phone showed {time=7:45}, but no light was making it through the gaps in the blinds."
    show bg snow84
    $ Snow(1, fast=True)
    with dissolve
    n "I felt the need to go out again, and when I opened the front door, I saw the sun rising from behind the mountains. ...It was an hour earlier than I thought, and light snow was starting to fall."
    show bg snow46-5
    $ RandomizeSnow()
    with dissolve
    n "That was the reason behind that foggy and soulless Yushibana. It culminated when I saw Ina CafÃ© closed, but when it was really {time=7:30}, the shutter rose."
    nvl clear
    show bg ina3
    $ Snow(0, fast=True)
    show darfeem 1a neutral at p33
    with dissolve
    d "So what have you been doing these last couple of days?"
    c3s "...{w}Not much. I went to Atsuki's house yesterday, and I was there for a while."
    show darfeem 1a concern at p33
    with fastdissolve
    d "Atsuki's house? You think being there helps you?"
    c3s "...I think so, yeah."
    d "I see."
    show bg ina4
    hide darfeem
    with dissolve
    n "I could finally rest inside, and I did so for longer than I'd expected. I was only drawn out hours later when I saw someone I recognized in the distance."
    show bg snow87
    $ Snow(1, fast=True)
    with dissolve
    n "It was Isla's friend, the Isla from the world I later ended up in. She had traveled from December 15th to November 24th, and for her, it had been a very long time since nobody had come back from the tower."
    show bg snow73
    $ RandomizeSnow()
    with dissolve
    n "I followed her footprints up to her house, but I wasn't yet certain I wanted to change the past. When I felt a presence watching behind me again, I distanced myself from that place."
    show bg cg1-4
    $ Snow(2, fast=True)
    with dissolve
    n "And I ended up high on that mountain, where I finally made the decision to change the past and do all I could to save everyone."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg snow80
    $ RandomizeSnow()
    with dissolve
    n "On the way back, I felt like the same person was following me, and that time, the police were ready to intercept them."
    n "...{w}Hm, thinking about it, I might actually be able to find out who it was."
    show bg snow90
    $ RandomizeSnow()
    with dissolve
    c3s "S-Sorry, did you just arrest someone?"
    ns "Hm? Yes. What's the matter?"
    c3s "I... was feeling like someone was following me just now. Could it have been this person?"
    i "\"The man frowned and took out a tiny scrapbook."
    nvl clear
    with dissolve
    ns "What's your name?"
    c3s "Mine...?{w} ...It's Shiroya Mirana."
    i "\"He looked at me and silently wrote on the paper.{w} Then, he suddenly smiled, completely shifting his expression.\""
    ns "I see. You can stop worrying, then. If you think you were being followed, there's nothing to be afraid of."
    n "At the time, I thought his smile was a bit strange, but he also recognized me as the only survivor. He had just caught the person believed to be behind the attack, so he told me that I could stop worrying."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg atsukis3
    $ Snow(0, fast=True)
    hide overlay_flashback onlayer master_overlay
    with dissolve
    n "There's a reason why the police released me without further complications. Right now, there's one person believed to have orchestrated the attackâ€”Akaro, even though the police haven't released his name.{w} That's because a recording was found on the computer in the tower, one which showed Akaro's and Katei's movements during the time the smoke was released. Before {time=21}, Atsuki saved that recording on the computer. He brought it from the world where Miiya was saved."
    #i say the police haven't released akaro's name so that it makes more sense he's still wandering around the town and hasn't escaped
    n "So, if the police believed they had caught a Xyn member, what's most likely is that it was Akaro.{w} I guess that's not all, though."
    n "Atsuki also told me that after Sai and Akaro escaped from the bedroom in the attic, Akaro traveled to the future and appeared on January 5th. He couldn't have been following me on January 3rd.{w} Rather, what it means is that it was the other Akaro. The one who killed me in another world and then arrived in ours with Isla."
    $ Pause(0.4)
    nvl clear
    with dissolve
    n "I traveled fifteen days to the future and appeared in the location where I'd been fifteen days in the past. The rule should be the opposite when you travel to the past. Vaisude appeared in his parents' house on November 24th, and by that amount of time in the future, he moved out to go live with them."
    n "That's gotta be why that Akaro appeared in a cell on November 24th. He would be caught by the police on January 3rd and put in a prison cell. In November, the cell was vacant and unlocked, so he was able to walk right out of it. That's why the image looked the same as in the article when I saw the cell on TV."
    nvl clear
    with dissolve
    $ Pause(0.7)
    show bg snow79-2
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "When the evening of the 3rd came, I stepped out of my apartment again. The place I went to had been constantly in my mind, as it was essential to construct the future I wanted."
    show bg lottery
    with dissolve
    c3s "I came a while ago, but I'd forgotten to check if I'd won anything until now.{w} The number I had was for December 1st, I believe. I wonder, by the way, how long would it be valid for?"
    ns "Oh, it's still valid, don't worry. They last a whole year.{w} Anyway, December 1st? Let me see."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    n "30-05-12-31-15-26. Bonus 24. I still remember it."
    i "There was a small piece of paper on the table containing those numbers. I had bought it in the other world before going to Eagle Motel. However, the winning number had been different."
    i "But that didn't matter. Even though it had been bought in another world, it was immensely valuable in the one I was in."
    nvl clear
    with dissolve
    $ Pause(1.0)
    show bg daylightoffemptytable
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "January 4th was the final day I'd set for myself. It didn't matter anymore, but I did the laundry to pass the time."
    show bg bedroomday1
    with dissolve
    n "I noticed that my favorite blue hoodie was missing. It was among the clothing I'd brought to Atsuki's house on December 9th.{w} Similarly, a shirt that brought bad memories and which I thought I'd left out of the washer was in the bucket. There were two versions of it, as it was the shirt I'd worn on November 30th, and I left it there both on December 8th and on January 1st."
    show bg whitesky2
    with dissolve
    n "...I didn't want to spend the whole day at home, so I went to Ina again."
    nvl clear
    show bg ina2
    with dissolve
    n "That's where I learned that a Xyn member had been arrested for the first time. The latest edition of Yushinews was still there, and it would stay there for the rest of the month."
    n "The news said that the identity of the person they caught was unknown. I wonder if Akaro wasn't his real name..."
    show darfeem 1a concern at p44
    with fastdissolve
    d "Are you thinking about the news?"
    i "\"Darfee addressed me after I'd been in thought for a few minutes.\""
    c3s "A bit. It just threw me off."
    show darfeem 1a neutral at p44
    with fastdissolve
    d "I see. Well, it's good that someone from that group finally got caught."
    c3s "Yeah, I agree."
    nvl clear
    with dissolve
    $ Pause(0.5)    
    c3s "...Do you know about the Sekimeiya?"
    show darfeem 1a confused at p44
    with fastdissolve
    d "Huh? ...What do you mean?"
    c3s "Ashiya's event."
    d "Hm? Yeah, of course."
    c3s "Well, nobody stole the Sekimeiya, right...?"
    show darfeem 1a confused at p44
    with fastdissolve
    d "The Sekimeiya...? N-No. ...As far as I know, at least."
    c3s "All right, I just wanted to make sure since I haven't been paying attention to the news."
    nvl clear
    with dissolve
    $ Pause(0.4)
    hide darfeem
    show bg ina6
    with dissolve
    n "From my perspective, what it all meant was that the past had changed, so I could go to Atsuki's house and prevent him from going to the tower in case something happened to me."
    show bg snow88
    with dissolve
    n "I had to wait for him to leave, which would never happen. As I waited, I realized that I could go back to Isla's house in the meantime."
    show bg snow77
    with dissolve
    n "When I rang the bell, nobody opened the door, and after knocking for some time, I noticed the door wasn't locked."
    n "I'm just speculating, but when Isla traveled from December 15th to November 24th, it's likely she didn't appear with the keys to her house. Since Erina never came back from the tower, Isla would've had to keep the door unlocked when she left so that she could get back in."
    nvl clear
    show bg islasentrance2
    with dissolve
    n "Inside the house, I immediately found her purse. I took two tickets for the event on the 15th, which is pretty strange...{w} because if that was the purse of the Isla who'd traveled from the 15th, I'm not sure why the tickets would've been inside it."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    n "...The recording was real. On January 5th, everyone who's currently traveling to the future will make it happen.{w} But what about Isla? She'll be there too, and she's not currently traveling through time. ...The Isla from this world died in the cabinet, and the other Isla should currently be alone in her house."
    n "How will that Isla end up inside the tower on January 5thâ€”the exact day that everyone will awaken? I can only think of one thing."
    n "After taking both tickets from her purse, I walked back home. Even though I didn't see anyone, Isla might have been careful about her situation. Maybe she noticed the strange footprints that went in and out of her house."
    n "If she did, and retraced them to my apartment, she had the chance to follow my footprints all the way to the tower. I entered through the storeroom and left the door open, so that's one way she could've been there on the 5th."
    nvl clear
    with dissolve
    n "...That Isla traveled from December 15th to November 24th. She went 21 days to the past.{w} 21 days after December 15th is January 5th. So her location upon appearing on November 24th may have been from January 5th."
    n "If that's correct, it might be how the voice recorder went to the past, although I don't really know any details. What's strange is that if Isla appeared with the recorder on November 24th, the Isla from this world shouldn't have had it in her purse on the 15th."
    n "An answer that explains two questions at once is that the purses were switched at some point before the 15th. That could be why the recorder ended up in the tower and why the tickets were still inside Isla's purse on January 4th.{w} If that's what happened, before going to the tower on December 15th, Isla or Erina must have realized that the tickets were no longer in the lower pocket of the purse and had to print them again."
    nvl clear
    with dissolve
    $ Pause(1.0)
    show bg nightlightoff
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "Back home, I felt the time rapidly passing. I had no idea what would happen the next day, when I would finally visit the tower."
    n "My thoughts were racing, I couldn't get to sleep, and suddenly it was deep in the night. Eventually, it was clear I was just going to stay awake, so I had the thought of leaving anyway because the tower was supposed to open early. I never turned off the heater before leaving, and I never made the connection that it hadn't been turned on when it was December 8th. I'll have to go turn it off on the 5th so I don't waste power."
    show bg outside5
    with dissolve
    n "Anyway, when I arrived, the tower was locked, and nobody seemed to be there."
    show bg streetlight2
    with dissolve
    n "I really thought that the world had stopped moving. For a moment, I believed I would die there."
    n "The tower wouldn't open. It hadn't opened once since December 15th. The time discrepancy with my phone's clock was what made me think that the day wasn't starting."
    n "Something that added to the illusion was my phone saying \"No service\". I'm still not sure what the cause of that was, but the cold definitely didn't let me think properly. The ground in front of the tower was buried in snow, too. Ashiya hadn't been maintaining the plaza like they tended to do."
    nvl clear
    show bg outside7
    with dissolve
    n "I knew the secret of the building, though. I knew that a door probably existed in its left wall, and after feeling around carefully, I found it."
    n "I opened it just by pushing it lightly, which meant that it wasn't locked. I even saw that the handle inside was already taken off."
    n "I bet the door was actually locked on the 15th due to how easily it opened in January. When the police interrogated me, they inquired about that secret area since they had found it open from the inside. They told me that they picked the lock and confirmed the door was really another exit."
    n "Of course, since they didn't have the rusty key, they didn't lock the door again. That's why it was still unlocked on January 5th and not even properly closed. I got it to open just by putting my hand on it."
    nvl clear
    show bg black
    with dissolve
    n "I entered the tower, which was as dark and cold as the outside world, its temperature no longer regulated for visitors. When I set foot in hallway A, I saw the green lights on the cameras. They were still recording.{w} But it's okayâ€”I don't think it mattered. I was in the hallways, security room, lobby, mechanical room, and event roomâ€”all places that should've still been covered with smoke or that didn't have cameras in the first place."
    show bg securityroom20
    with dissolve
    n "In the security room, I found Katei's rusty key. His body had already been taken away by the police, and I thought the room was all messy, as if someone had tried to find something."
    show bg black
    with dissolve
    n "Then, above the breakers, I found the attic and Sekimeiya cabinet keys... And not only that."
    nvl clear
    with dissolve
    i "\"I tried to move, but the obstacles in the room didn't make it easy. Could the cabinet have been there? While it seemed like a good place, neither the lobby nor the mechanical room had cameras.\""
    i "\"There were chairs and tables on the floor, so I had to move some aside to get to every part of the room. Even though it was impossible for anyone to be there, I kept trying to be silent and failing as I scattered things that I couldn't see.\""
    n "According to Atsuki, the Sekimeiya that sent us to the future was there. While searching for the cabinet, I moved it accidentally, which stopped the chain of travels and made everyone arrive on that day."
    nvl clear
    with dissolve
    show bg entrance32
    with dissolve
    n "As I was walking to the event room, I saw the reception desk lights flickering in the lobby. I turned around because I felt a presence behind me, and I don't think that was just paranoia."
    n "It had to be Atsuki. He had to be there too since both of us traveled back to the 15th when I touched the Sekimeiya."
    show bg sekimeiyaroom19
    with dissolve
    n "I moved to the event room and felt that it was much colder than the rest of the building. The cabinet wasn't closed..."
    show bg towernight2
    with dissolve
    n "When the police entered the building on the 15th, only the Sekimeiya that sent us to the past was in the cabinet. Ashiya said that the Sekimeiya weren't stolen, which means that the police found another one and put it in the cabinet. Of course, it wasn't the one in the mechanical room..."
    n "I remember the rush they were in when they found me. What must have happened is that they didn't close the cabinet, so on January 5th, that Sekimeiya had been gathering energy at an incredibly slow rate. That's why I was able to activate it inside the cabinet."
    show bg sekimeiyaroom19
    with dissolve
    n "But I'm not exactly sure how everything came to happen. There was something else in the cabinet, and I activated the alarm out of nowhere... What matters is that Atsuki and I returned to December 15th."
    nvl clear
    with dissolve
    $ Pause(0.9)
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    i "That was all the time I'd lived in January. The second coming of January 5th was the light at the end of a long tunnel."
    i "I looked at the clock and saw that I was close to entering the second day of the year. After a long yawn, I stood up from the couch. I'd been sleeping in the guest room, just like before the 15th."
    i "I had been there all day, and my body felt weak. As soon as I stood, I noticed a weight in one of my pockets."
    i "I reached my hand inside and took out a rusty key. There was one final use left for it, scheduled to happen in just three days. I gripped it tightly, ready to finally exit the labyrinth that we'd long ago been entrapped by."
    $ Pause(0.8)
    $ StopMusic(fadeout=5)
    nvl clear
    show bg black
    with slowdissolve
    $ Pause(1.5)
    $ Pause(6)
    $ renpy.music.play(pre_tip_song, channel='music', fadein=2)
    $ store.bgm_name = pre_tip_bgm_name
    return

label tip_keys:
    show bg mechanical
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In January, above the breakers, Shiroya finds the attic and Sekimeiya cabinet keys. Why were they there on January 5th, though?"
    show bg atticdoor
    show overlay_flashback onlayer master_overlay
    show saim 1b neutral smoke at p11
    show erinam 1d worried blood at p13
    with dissolve
    c "\"Wait, no. You're definitely lying.\""
    c "\"Me? I don't ever lie.\""
    c "\"You don't have any key on you. That proves you hid them, because you should have the cabinet key.\""
    c "...They were the keys that Sai had hidden after locking Shiroya in the attic's bedroom."     
    return

label tip_card:
    show bg towernight2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "At the end of December 15th, as soon as the shutter unlocked, the police were struck by a very strong smell. There, they saw an unidentifiable gas in the air as its source. It was the lingering range of the Sekimeiya.{w} When they raided the building with protective masks, a sole Sekimeiya was in the cabinet: the Past Sekimeiya. They knew another one had to be found, so they searched until one of the two fake Sekimeiya that existed was spotted in the attic.{w} They put it in the cabinet, but they were in a rush. That's why the glass wasn't properly closed."
    c "As the days passed, the cold temperature led to the effect Xyn had designed: the fake Sekimeiya left behind a card with their name. However, their method also damaged the cabinet's interior."
    show bg sekimeiyaroom19
    nvl clear
    with dissolve
    c "...And when Shiroya tried to open the glass all the way, it had been stuck. As soon as she applied a bit of force, one of the triggers for the alarm went off. However, there was no one for it to alert. Nobody had expected it to go off ever again."
    #i have to say this (that the alarm doesn't reach the police nor ashiya on january 5th) or else the police would enter the building through the storeroom
    return

label tip_burn2:
    show shiroyal 4a smile2 at p25 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. The Sekimeiya was immensely hot, so the burn would not have faded by the time the future position took place."
    c "So then, why does Shiroya not appear with a burn mark when she travels from January 5th to December 15th? The number of days traveled is the same."
    c "There's a key difference that prevented a burn from appearing on Shiroya's finger, and it becomes apparent when you track her movements."
    c "After appearing on December 15th, Shiroya will spend many hours in world A until she arrives in world C and once again travels to the past. She will travel to November 30th to save Miiya in that world."
    c "For her to reach January 26th, almost two months will pass. That amount of time is what causes her to appear with no burn mark."
    return

label tip_fake:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Despite Sai's initial reaction to the attack being different in the three worlds, there's something he always did at the start: hide the fake Sekimeiya.{w} Doing that opposed Katei's and Akaro's intentions, as Sai was not yet aware that three different Sekimeiya existed. Although his motives were slightly different in each world, the main goal was always the same."
    c "In world B, Sai took the fake Sekimeiya from the cabinet and hid it in the storeroom, where no cameras recorded him. In world C, when the group was inspecting the office floors, everyone was suddenly separated. That gave Sai the perfect chance to do the same thing."
    c "In this world, A, Naomi C appeared before everyone. Unlike in the other worlds, she wanted to talk to Shiroya in addition to Akaro, as she had seen her world B self on the crystal floor separated from the group and wearing clothes from the atticâ€”two versions of her existed at the same time, and Naomi, who had experienced time travel once, realized that Shiroya might have made contact with the Sekimeiya during the attack."
    c "The three of them didn't return, so eventually, everyone walked to the crystal floor. Sai hurried to the event room, and as he yelled about the Sekimeiya's disappearance, he put it in his hip pack. Soon after, he hid it in room A5, where Atsuki C would find it hours later."
    return

label tip_gan:
    show bg gemshop1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Akaro A says that one person was hospitalized, and he's referring to Atsuki. ...What about Gan, though?{w} The truth is that Gan was only sent to the hospital in world B."
    c "When Akaro A world switched to world B and then traveled to November 24th, he decided to walk away from Xyn's plan. He deeply regretted what he'd done in the tower, and he wished for history not to turn out the same way."
    c "He knew he was in the pastâ€”he possessed valuable information. One of the things he did was remove the storeroom's handle. However, the first action he took to alter history came days prior."
    c "On November 30th, he had accidentally killed a young girl. It was the perfect chance to prevent that."
    c "He knew that an explosion had occurred while everyone had been unconscious in the gem shop, so all he had to do was make sure that wouldn't repeat: he called Gan and told him to turn the heater off late on November 30th in order to prevent a disaster."
    c "Akaro was confident he had saved the girlâ€”Gan had told him that he would turn off the gas. However, Akaro was unaware that Gan did no such thing. He didn't put any real stock in such a bizarre phone call."
    nvl clear
    show bg night3
    with dissolve
    c "Afterward, the Sekimeiya were found, and mere days later, it was November 30th. The way events unfolded in world B slightly differed from world A."
    show bg gemshop1
    with dissolve
    c "When Gan went to get the second Sekimeiya, he stopped himself in the middle of the shop. The moment he smelled the gas, the strange call came back to him."
    c "He glanced at the heater and approached it curiously just as dense smoke invaded the whole shop. He fell unconscious closer to the source of the explosion, so due to Akaro A's actions, Gan had to be sent to the hospital alongside Atsuki."
    return

label tip_burn4:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The Past Sekimeiya, which Atsuki touches, has been in the storeroom for numerous hours, so why is it that he doesn't have a burn mark on his finger when he world switches?"
    c "That's because of the temperature in the storeroom's secret corridorâ€”the coldest place in the tower."
    c "When Atsuki touches the Sekimeiya, it has very little energy: the one with the massive range is in room A4, and it will remain undiscovered until June of 2012."
    return

label tip_disappearance:
    show bg japan
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Along with Atsuki, almost a third of Japan disappears from the face of the Earth. Not only that, but they never appear anywhere."
    c "In this world, when the police entered the tower at {time=21}, they found a real Sekimeiya and a fake. As instructed, they made sure both were kept cold."
    c "Atsuki was the only person they were able to find, and since that day, the tower spent many weeks abandoned. Each second that passed, the real Sekimeiya that hadn't been found kept gaining energy."
    c "The day that it was activated, its surface could've melted iron. The method through which that happened is a question of its own, but the effect became humanity's biggest mystery."
    c "The range had been increasing every day, and it ended up taking away a third of Japan's population. The other real Sekimeiya was still refrigerated, so no world switch occurred. Given that the people who vanished didn't reappear anywhere, which Sekimeiya was activated? Did everyone go to the past or to the future?"
    c "If they had gone millennia to the past, they would never have been able to exist in the future location, so they wouldn't have appeared anywhere. If they had gone millennia to the future, they wouldn't have existed in the proportional past, so they wouldn't have appeared anywhere."
    return

label tip_c4:
    show bg mountain4
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Calliants are the flowers that compose the flora of Airun's base. That is what this chapter is."
    c "The base of the mountain, which lets it build all the way to the peak. In addition, this chapter is more grounded than the others."
    c "Even though it's based on a real flower that can be found on snowy mountains, \"calliant\" is a made-up word."
    return

label tip_burn3:
    $ SpriteTint("dark")
    show bg thinking
    show islam 1a sleepy2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. ...Why, though?"
    c "This is one of the clearest indications of an elusive rule of the Sekimeiya."
    c "When someone traveled to the past, they were unable to keep feeling the pain of the burn they had noticed for an instant. The difference in Isla's case is the amount of time she traveled to the past."
    c "When she touched it, the Past Sekimeiya was immensely hot, so normally, a painful burn would've remained on her skin. The amount of days that it took her to reach January 5th from November 24th would not have gotten rid of it. That's why she appeared with it in the first place."
    nvl clear
    with dissolve
    c "In other words, the body she appeared in was that of one loop of her travel."
    c "When she reached January 5th, the burn she'd appeared with had healed considerably, but it was still visible. If that body of hers had been the one to appear on November 24th, an instant chain of infinite loops would've made it impossible for her burn to ever appear."
    c "Of course, that also means that she would've died instantly; she would've aged more than a month per loop and been unable to appear in November."
    c "Instead, she appeared in a body that had undergone a single loop. This behavior can be observed in a number of travels, and it's the answer behind one of the toughest questions Atsuki will face."
    return

label tip_injury:
    $ SpriteTint("dark")
    show bg thinking3
    show atsukil 1b pensive
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Why does Atsuki's injury disappear when he travels forty minutes to the past? That's not what happened the last time he traveled back in time after getting injured."
    c "The first reason is the amount of time it will take him to reach the future location. Even though it's minutes away, many weeks will pass until he returns to January 5th. That amount of time, enough for the injury to heal, is what makes him appear without it."
    c "However, there's another reason why his injury disappears, and it's unrelated to the amount of time that it will take him to return to January 5th. It's the same reason he doesn't appear with a burn mark when he travels all the way to November 24th, but that will be touched on a little later."       
    return

label tip_split:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Certain events in this story have a specific characteristic to them: their origin seems unclear."
    c "The handle of the storeroom's door has been taken off by Akaro A, but the means by which that happened are not straightforward."
    c "Akaro world switched to world B, and in the attic, he was told about the existence of the secret door. Afterward, he traveled to the past and removed the handle from that door. It could be said that he was told about the existence of the door because he had removed its handle."
    c "This is not the only instance where this seeming lack of causality takes place, so where exactly is it coming from?"
    $ Pause(0.3)
    nvl clear
    show bg mainmenu5
    with fade
    c "In world A, Akaro knew Xyn had been outsmarted. An alarm had trapped them in the tower, and the real Sekimeiya had vanished when he had woken up. Not only that, but he thought he had killed two people in order to bring his plan to success."
    c "He hated the way the world had turned out, but altering the reality he'd experienced wasn't possible. However, eventually, he world switched to world B.{w} Someone else originally from world A came with him: Isla."
    c "In world A, Isla never expected that an attack would take place in the tower. She followed the adults and hoped that everything would be resolved quickly. ...A lot of time passed, though, and at one point, her mother had been missing for a while after going to the bathroom."
    c "Isla couldn't bring herself to voice her worry, as that would've meant admitting that something could've happened to her mother. However, she regretted the way she'd acted; she wished she could've told Erina to stay with her."
    c "Akaro and Isla world switched to world B. As soon as they appeared in that world, they shaped it in a way they couldn't change their own."
    nvl clear
    with dissolve
    show bg mainmenu5-2
    with dissolve
    c "Atsuki and Shiroya B were able to save Miiya in world C, but didn't that only happen because she had already been saved?"
    c "This behavior of the world switch defined the relationship between the three worlds, instantly shaping three drastically different sets of events."
    c "And when a two-way world switch happened, someone was pulled backward in the order of switches. In those instances, both worlds balanced each other out accordingly. By working like this, the world switches led into the progression between the three worlds."
    nvl clear
    with dissolve
    c "In world A, only Atsuki made it to {time=21}, and he was accused of the murders that had taken place. Not a lot of time passed before a large portion of Japan suddenly disappeared forever."
    c "World B was a step up, but being between worlds A and C, it was filled with many bittersweet resolutions. Despite a few deaths, some people got out safely. Isla returned, but it wasn't the Isla who had died. Akaro was arrested, but it was the Akaro who most regretted what he'd done. Atsuki and Shiroya left happily, but they would never see Miiya again."
    c "World C existed thanks to world B. Everyone who was trapped got out alive. The people of that world faced numerous hardships, but they were all resolved. Naomi seemed to die, but she returned. Shiroya seemed to die, but she returned. Erina seemed to die, but she returned.{w} ...Then, why is it a world so close to world A?"
    c "A step was taken when world C was created, but what direction did it take? A bit more examination is needed to reach that answer."
    nvl clear
    with dissolve
    $ Pause(0.6)
    show bg mainmenu5-3
    with dissolve
    c "In any case, the labyrinth spawned by the world switches always operated under the inherent progression that it had created. Some people from world A ended up in world B. Some people from world B ended up in world C, but their world A selves pulled them back to world B. Some people from world C visited worlds A and B, but they were able to safely return to world C.{w} Thanks to the recording obtained in world C, Akaro A was arrested in world B. Atsuki A was the only person from his world to momentarily reach world C, but he dropped all the way back to world A when his elevator ride to the top vanished out of nowhere, the exact moment Shiroya B traveled to November to make world C the world it was..."
    c "The labyrinth never stopped spinning, and somewhere, it hid the peak that everyone wanted to reach. There's only one place where it would not have moved."
    $ Pause(0.5)
    return

label tip_saielevator:
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "I hope you had enough time to think about this mystery.{w} As you might have guessed, the Past Sekimeiya was involved."
    c "Sai traveled to the past and appeared in the locked elevator. Before asking \"why\", though, it's necessary to ask \"how\". Without the Sekimeiya, in the future location of Sai's travel, he wouldn't have been able to enter the elevator. Hence, traveling to the past and appearing inside it seems impossible."
    c "As long as the past and future states align and the events in between are possible, many elaborate setups can be created."
    $ explanation=True
    show bg chart_saielev1
    nvl clear
    with dissolve
    c "Consider this chart depicting one of Sai's possible journeys. Atsuki and Shiroya have trapped themselves in the elevator."
    c "Sai thinks about his next course of action and decides to use the Past Sekimeiya. After allowing it to warm up, he touches it.{w} But how is his past position determined?"
    show bg chart_saielev2
    with dissolve
    c "The answer is that he continues to live virtually, as if he did not time travel. Movements during this time can be natural or driven with clear intent. Let's say he virtually moves until he reaches room B4."
    show bg chart_saielev3
    with dissolve
    c "When he arrives in the past, he will be in room B4. Right now, this new timeline is imaginary. It will become real once the past state matches the future state."
    show bg chart_saielev4
    nvl clear
    with dissolve
    c "Next, he takes out the Past Sekimeiya and allows it to warm up. He touches it and lives virtually until he reaches the floor 4 partitions."
    c "What's important is that the new timeline does not prevent the first travel from occurring."
    c "This means that the Past Sekimeiya must be in the same location and charge state as it was when the first travel happened."
    show bg chart_saielev5
    nvl clear
    with dissolve
    c "This travel creates another imaginary timeline, and Sai now exists before the elevator is stopped."
    show bg chart_saielev6
    with dissolve
    c "Taking this opportunity, he enters it and traps himself between floors."
    c "Isn't this a contradiction, though? In the real timeline, Atsuki and Shiroya are in the elevator, but here, Sai is alone."
    c "Try thinking about what the original Sai sees and hears from his perspective. As long as the circumstances that allowed the first travel to happen are preserved, this is valid."
    c "In any case, this is the power of virtual timelines. The absurdities will soon collapse into a single truth."
    nvl clear
    with dissolve
    c "Notice that the future position of the third timeline no longer matches the second. Sai can no longer go to the 4th floor partitions since he's stuck in the elevator."
    show bg chart_saielev7
    with dissolve
    c "The result is that the future position in the second timeline is updated to match the third. The past position in the third timeline is updated accordingly."
    c "In this latest iteration of the third timeline, Sai appears midair inside the elevator and crashes down. He repeats the process of trapping himself between floors."
    c "The validity of the third timeline is preserved, so let's see what happens if we look farther into the future."
    show bg chart_saielev8
    nvl clear
    with dissolve
    c "The future position of the first timeline is updated to be in the elevator, which updates the past position in the second timeline."
    c "However, this raises an issue."
    c "Sai can no longer perform the second travel since now he appears in the stopped elevator."
    show bg chart_saielev9
    nvl clear
    with dissolve
    c "This destroys the third timeline, but preserves its effect.{w} The future position in the first timeline is inside the elevator after it closed."
    c "After killing Atsuki and Shiroya, Sai's past and future positions finally match. The virtual timeline stabilizes and becomes reality."
    show bg thinking
    nvl clear
    with dissolve
    $ explanation=False
    c "Perhaps you don't like the idea that Atsuki and Shiroya aren't in the elevator in the third timeline."
    c "That's fine. This merely demonstrates the concept."
    c "Another method might involve Sai falling down the elevator shaft in a virtual timeline and entering the elevator from the top."
    c "As long as the goal is achievable within the travel and the user has the will to reach it, the Past Sekimeiya will turn it into reality."
    c "The key is to set the future state to be within the elevator. The exact method is not important as long as there is at least one valid option in the sea of possibilities."
    c "The concept of virtual timelines and iterative updates can be found elsewhere in the story. I wonder what solutions you'll come up with."
    return
    
label tip_virtual:
    show bg thinking2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki obtains an equation for the Sekimeiya's travel times using hypothetical worlds. We'll call these \"virtual worlds\"."
    c "Through countless iterations, he uses his virtual selves to produce a result that's observed in the real world."
    c "While this concept works for him, Atsuki isn't aware of how lucky he is to formulate the plan the way he does."
    $ explanation=True
    show bg chart_virtual1
    nvl clear
    with dissolve
    c "Let's take a look at a simple travel using the Past Sekimeiya. In this example, we'll pay close attention to the age of the user throughout the sequence. The node {b}t{/b} represents the moment at which the Sekimeiya is activated."
    show bg chart_virtual2
    with dissolve
    # Even though they don't time travel, they'd still keep any burns they may have sustained
    c "The Sekimeiya sends the user twenty minutes back in time. In order to determine the user's state in the past, a virtual copy of the user is created that continues to live as if they had not time traveled. After twenty minutes, their final state is used in the past."
    c "Both past and future locations are equidistant from the travel point, which means that in this virtual world, the user will arrive in the past being twenty minutes older than at the moment the Sekimeiya was activated."
    show bg chart_virtual3
    nvl clear
    with dissolve
    c "And when the user makes it to the future copy point of the second virtual world, they will be sixty minutes older than at the moment of the travel."
    c "In this second world, the user is able to update their future state."
    c "The state {b}t+20{/b} does not account for the user's behavior in the past, but {b}t+60{/b} does. This update stage is essential for convergence."
    show bg chart_virtual4
    nvl clear
    with dissolve
    c "The next step is a third virtual world."
    c "Since the previous stage's final position is copied, the user will age by another forty minutes and will be 100 minutes older at the end of the travel."
    c "This stage exists to confirm the loop is stable. The user must have identical positions and possessions at {b}t+60{/b} and {b}t+100{/b}. The ages of the body and possessions will be slightly older, but everything else is identical."
    show bg chart_virtual5
    nvl clear
    with dissolve
    c "If the most recent virtual world was stable, the next step will apply the final result to the real world."
    c "When the user appears in the past, they are sixty minutes older than the moment they touched the Sekimeiya, and in the copy point of the future, they will be 100 minutes older. When a user reaches the future state in reality, they have experienced five times the travel time."
    nvl clear
    with dissolve
    c "This is how infinite aging is avoided. The update stage is required to account for the user's actions in the past, and the final stable loop is frozen and applied to reality. Of course, every stage starts with the memories from the {b}t{/b} point."
    c "A clear example of this kind of sequence is Isla's burn. Touching the Sekimeiya left a burn scar on her finger that this system didn't have enough time to erase. Naturally, however, she didn't age infinitely."
    nvl clear
    $ explanation=False
    show bg thinking2
    with dissolve
    c "Atsuki is able to successfully execute his plan, but he's not fully aware of how the Past Sekimeiya works. His understanding is that Sai's watch displayed the year 9,999 through infinite virtual loops."
    c "However, that's incorrect. If the loops operated like that, Sai would have instantly died in the process, and the watch would've disintegrated."
    c "So let's consider a different way Atsuki could have formulated his plan."
    nvl clear
    with dissolve
    #charts that illustrate this process?
    c "\"If I touch the Sekimeiya when fifteen minutes have passed, I'll go twenty minutes to the past and appear in the hallway holding a notepad. Depending on what it says, I'll do one of three things.\""
    c "\"1: If it has a formula written down, forty minutes later, I'll be holding it, so that's how I will have appeared with it.\""   
    c "\"2: If I don't appear with a notepad, by using the Future Sekimeiya in the kitchen, I'll start working toward finding the formula. Before forty minutes pass, I'll obtain a notepad from the bedrooms, and in the top left corner of the first page, I'll write a \"1\" along with the progress I made in those forty minutes. In the future location, I'll be holding the notepad.\""
    c "\"3: If I find a notepad that doesn't contain the formula, it will have my current progress along with a number in the top left corner of the first page, which will indicate the amount of iterations that have occurred so far.{w} Using the information in the notepad, I'll start working to find the formula. Before the forty minutes pass, I'll write down the updated progress in a notepad from the bedrooms, increase the number I saw in the top left corner by one, and make sure that I'm holding it in the future location.\""
    nvl clear
    with dissolve
    c "The concept is almost the same as the one he actually uses, but there's a very important distinction. In this example, Atsuki doesn't get any information before he travels. Instead, he appears with a notepad after traveling to the past."
    c "According to what Atsuki believes at this point in time, this sequence should've worked too since it's almost identical to what he believes happened to Sai's watch. However, if he had attempted it, it would not have worked."
    nvl clear
    $ explanation=True
    show bg chart_virtual5
    with dissolve
    c "The reason is simple. In the virtual worlds, the location of arrival would not have changed after the update stage. The same mechanism that prevents infinite aging would've prevented the infinite information gathering system. In the real world, Atsuki could only have appeared with a notepad containing sixty minutes' worth of information.{w} Not only that, but the plan contains a glaring contradiction. Points {b}t+60{/b} and {b}t+100{/b} are necessarily identical in every way except age, so appearing with a notepad that contains different information from the one that will be held in the future copy point is conceptually flawed. Even though it's what Atsuki believes happened to Sai's watch, it's fundamentally faulty, as it breaks the rule that past and future points must be identical."
    nvl clear
    with dissolve    
    c "...So why did his original plan work? Where's the loophole that allows him to manifest this infinitely iterated information without aging infinitely?"
    c "Let's refresh our memory on the method through which Atsuki obtains the Sekimeiya's formula."
    nvl clear
    show overlay_flashback onlayer master_overlay
    show bg atticlivingroom4
    $ explanation=False
    with dissolve
    c "\"If I touch the Sekimeiya when fifteen minutes have passed, I'll go twenty minutes to the past.{w} But before I touch it, I'll open the door to the hallway and find a notepad from the bedrooms on the floor. Depending on what it says, I'll do one of three things.\""
    c "\"1: If it has a formula written down, I'll go twenty minutes to the past, obtain the notepad, write the formula down, and leave it in the hallway.\"" 
    c "\"2: If I don't find a notepad, I'll go twenty minutes to the past, and using the Future Sekimeiya in the kitchen, I'll start to work toward finding the formula. Before twenty minutes pass, I'll obtain a notepad from the bedrooms, and in the top left corner of the first page, I'll write a \"1\" along with the progress I made in those twenty minutes. Then, I'll leave it in the hallway.\""
    c "\"3: If I find a notepad that doesn't contain the formula, it will have my current progress along with a number in the top left corner of the first page, which will indicate the amount of iterations that have occurred so far.{w} I'll go back to the past, and using the information I read in the notepad, I'll start working to find the formula. Before the twenty minutes pass, I'll write down the updated progress in a notepad from the bedrooms, increase the number I saw in the top left corner by one, and then leave the notepad in the hallway.\""
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg chart_virtual6
    with dissolve
    $ explanation=True
    c "As you might've noticed, the reason behind his success lies in observing the information left by the virtual worlds before touching the Sekimeiya."
    c "The Atsukis in the virtual worlds leave the notepad in the hallway so that the Atsuki before the {b}t{/b} point can see it. In other words, stage 2 feeds information to stage 1."
    nvl clear
    with dissolve
    c "That causes {b}t{/b}'s starting memories to continuously update, and the calculations made at the {b}t+60{/b} point are no longer locked to a state of a single round of calculations."
    c "When the sequence converges and the final result is applied to the real world, Atsuki appears in the past having aged only sixty minutes but having spent infinite time computing. This is thanks to the virtual worlds continuously updating the starting point through real Atsuki's memories."
    $ explanation=False
    return

label tip_burn1:
    $ SpriteTint("dark")
    show bg thinking
    show atsukil 1b neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. The Sekimeiya was immensely hot, so the burn would not have faded by the time the future location took place."
    show bg streetlight2
    hide atsukil
    with dissolve
    c "So then, why does Atsuki not appear with a burn mark on November 24th? The Sekimeiya was about as hot, and he will spend even fewer days to reach the future position since he will travel forward in time from December 15th to January 5th."
    show bg atsukisbedroom
    with dissolve
    c "The answer lies in what will happen to Atsuki the night he will arrive at the motel. He will travel to the future in order to duplicate his money, but due to a miscalculation, he will replicate his body from November 24th."
    c "That body didn't have a burn, so he never appeared with one."
    return

label tip_ohnoitdidntwork:
    show bg night5
    $ Snow(1, fast=True)
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The biggest reason why this loop doesn't work for Atsuki is that the box Atase took only contained the Past Sekimeiya."
    return

label tip_rush:
    show atsukim 1a confused
    show bg attickitchen1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "While he's rushing his actions, Atsuki can't help but feel like that doesn't make sense."
    c "He recalls that he returned to his world at {time=19:30}, which is approaching. That's why he rushes Shiroya to activate the Sekimeiya at that time and make the people in the center of the tower change worlds."
    c "But of course, that's slightly paradoxical. Why did the travel happen at {time=19:30} in the first place? His hurry to take this action only existed because the world switch had been lived through once, so why did it not just happen at a later point?"
    c "There's something Atsuki is mistaken about. Shiroya traveling to November 30th isn't what makes everyone world switch back to world B. It is Atsuki A who causes that when he travels from world B to world C, pulling them back to their world. That's why he has no control over the time at which the world switch takes place."
    hide atsukim
    show bg towernight
    with dissolve
    c "Nonetheless, when Shiroya travels to November, she does cause a world switch. Both immense ranges still overlapped in the middle of the tower, and only one person found themselves there: Atsuki A, cluelessly taking the elevator up. Before his ride ends, Shiroya's touch makes him go back to world A, where no elevator is supporting him, and he falls onto the one below him."
    return

label tip_force:
    $ SpriteTint("dark")
    show bg tunnel
    show shiroyal 4a smile at p35 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "That burning touch of the Sekimeiya was the catalyst behind the events that unfolded on December 15th. Shiroya traveled to the future and suddenly found herself in her apartment. It was December 19th, and the first thing she did was call Atsuki's phone."
    hide shiroyal
    show bg towermorning
    with dissolve
    c "During the twelve hours of December 15th, Atsuki B vaguely wondered something. He knew he had to make sure that Shiroya's body wouldn't be found in world C so that Miiya could be saved, but that would only work out because her body had already not been found. Atsuki wasn't sure how that detail had originated.{w} Regardless, he instructed Shiroya to keep her world C self hidden from the world. Yet, in the end, she didn't end up causing that: it was Shiroya C herself who was attracted to the Sekimeiya's glow and vanished from the world for weeks."
    show bg night5
    $ Snow(1, fast=True)
    with dissolve
    c "The importance behind that action was even larger than Atsuki had thought. Due to Shiroya's disappearance, Akaro believed that he had killed a young girl, which developed into the attack of December 15th."
    c "And although it was world C's own flow that made that happen, it was thanks to world B's influence that it occurred. Shiroya C avoided falling into a coma because her world B self shielded her while both of them fell through the floor of the gem shop."
    return

label tip_end:
    # This marks the end of tips for the search function
    return
Made with Ren'Py.RENPY RPC2   .   :Ÿ    hŸ ÜH             x^Œ]|\Åóo‹Jq—£X
å¨aAš¶HKI´@R.É%wôr—{wi\[Üİİİİİİİİùáğÿ~gvßÛ}/òçÜİfwvvvvfvvvö û—û×4,Ğ¯_¿YÙ ’/Ë¶ı}çíú5Ìƒ¢™Ù®ò<â[G±Pjš™m.ÏÛ1½<_MS-¶w¥3•êÀ‰Å|u`yş¡—˜¼yÁš†yQ½˜iË–j„¯­øº~5ß^Ií]ÛŞµÈ‚¹ú‡ç™[¨õ²³«å…'KíA¾ä«]åE¶}ä¿ÿşkˆ²B¾˜-v´5fƒò Iı¥ZK¾ğ‹&Á—7Ì‡*Äµ¼ØôòâÛwUs¥âÀòÀtI`º”bÚTjÎ–—öêGÑÀò2¨·l:m^¸_¿-A©-ÕT*²MU©’Ê·µ—‚jjJĞœ²Í[æ›ª1È…|¥šÚÜ-®*(¼…LşÖ.ˆÌhF“š¡©°ÕîC²³3mí…ìˆ!ÓQkÈÄ"ŸšÊIV©•ğWôÕèÕ»ù[.›ª´•ffSùb*(üÅTÉf‚¦œÖ›Ò_©Î|5—*–RA¶ÒQ¨zp[:ªAVëOÍä×®¤¦fgæÛ²ù®ŒvüãVê@’ÎL]9·‚2ÍÙŠ©YjËVsùb+Î
©L±9Õœ	fº-ÚÀlÙ -_l6(W+3ó©*FéüÉébf1ßbĞ†JúÓı{¶+"Tc¶YHwë´g‹Í…6­¸KPŠM™J6UjI5g3UoPí…LÑºüvz¬™&;äiò`8‚n)Ù.2
p¼|¯©M5ç+™ÆB¶ÙÜTÈTÌLâÃìh¡Ë:]¶óq`-@©ĞlY
è€Ñ›SÙYÙbUÇãš¶l¡àT­ğ·7È<Öƒ;E@%_Ü»#ğ[È›©›*wä›f¦Xàâä‹fè[ñ+€äòÍÍÙb*£0“™¢\¦šÊW„¨‚ÚNññ¹L;˜)5`«ùjÁë:33”Ì øu³¹Ì,H'¯ÓJ{¾	¨8«Í¥ª¥ÎLĞœ«<:Şg© ÒN)2ËRÀTB?íÁöo1r¥À¬”I™j–K¯’-*V±]ğ-XEÙ ²´ˆÕ+¬³}GĞ^ªd[:
)ïNÓ2E,b•(üêÍAÊÏËÇ85ÒÅ#cy  Bg›S¹RµÔÖ•$8¹-"¢ğ^ĞQ±5Ö“ yŠÁ²_Ñ½ˆg -…fIk®+U*
#H©7&,]Ó¥@JU@bt‹YÎbù‹«Xª:b¤Ô¸7&`Ág³2Å|%ç×®´Y§:TQ©¹+¥¥®"Ø}HTsëL¡’u™?Œl—m)ÙÔ¾œæÍGØßEõì’ŞN¿»Ò&b2¶­Ôµv™­“oóêa…·(É&g³Í˜*)p 522È¬šQİ­šÆR©Z€k¨ù#õhõ0Ï™yœùè SÜ¾š³m¥B+<â,¦l€>¿9Øµcm‚O¬ÈZâV¾5Uö2¹„Å€Ù=†¤Ú²•J¦Õ«¼w¦Ø‘°Šl•MÔUIeZK±ùs+ÆgjÄ¬>Q=øey±1Èffb™{†¬ĞşvLÉÍßşAÑ,½]rXMpSsù $k€õˆÛ‚Ü6wJLNDS¦EÕSÃVaM(AšU3…ü>>;øh6Rˆ<”-fƒVOšS'µ·Ã‚È›L×ÛCWg`¼UEaEtùÊ ¶Òxt·|ÿ™é%JîŒr1FS¥š)V]©\6S’•v0VÄU¥ +¾ƒÇ·L*™|¶•©ZAÂ¤µW©ä¡wSá‘ÌÊÕL!n
RÒ‰7×ÄŞXxá\ª<ín*K¹b)_mÎ7« 5Ó0e!Ó‰e
ÉÒîÒ!è°6Àö˜ˆæÒì|S¦ Iê'vŠ8°æ ?‹v—ˆO²+e¯5gÓdßš¡µSø'ß"†LdªXw˜å4kÏÊƒDyP¹ËkÃv=ÖÜà8uÃ–—ËÔ_vsËË‹qm*¯Pm”ĞÿÙòŠGæºÙV”WÚö“/æËm{õ"ıûÍ-¯œ[478‡ıB;î*˜Ëlyçûªs3øÏ±û·Ë4fË)˜ı«a{0D·ÒéêGF›š5A1GkÍõòš²UiÑaÅ‚"åµ&ê-º#Y{z¹Æİ:MmÂRXŠ.×A—ëÖ4Ì@Ï°ÊÃjp/Ó*…¹|5;jÎäÉÓñoµ¼Œû	lŒÒ“så®¬/›·LµPn1™LüñîK`yú‰¾GÕD@® £Í´å¼íÑV³Ûƒåe3†µ])feËaî¦Ì=¸¼1`mRß»ÕNšâïİ6Í6¤’Œ®=C£±¼ÙdÌÚ”¦S3]Ë›Ñ- |ŒÎK'ôo¹®a|İ%‡!¹1C––ªÀTGÓ6›š½;ÚÚ!Á!8­ñœ.„ìè3˜šq‚G±¡U(hqĞbK©“
6xSµ¼ÕBàÎ\©¼uCn"åïø=£»”ò6G4,E&Ér]2#S­ùÆj¶RÀ™ÙãVkFyâä†…8YAkGÖQ¥¼-‰°½PĞi6I&ÒŸÁ³ØaG»HSÒL®h4ŞAg1MĞnÜÑOq8äzĞöZ–³@–ßíw¬É­~d.Áà#ËSs!GOeàãi59²íNh¶sM®W^İ%çrèÒC.äÌi:ß9râ® ·›Ã‰7Jåİsäbì¶Øm'°Ût4Ø³&W;i§\ÄR9á£\2ÎTÛ«&W×0„[L•‚FêPìãšS9n*Š` Ùoƒ…ø'
¸Yyn´ÒåLn\Îa‰›©ÆÜVGäÌìç¶9"'óš›89'ó·s.œ°hÍD`˜–CMbp6¢ÃR
SUÈk©’­VÁ¾ÃTc‹‹şaÊÑ%érÖGéfA©¥W”vqP"Ç´¥œá˜†œË"·´|œEöFƒ™†E¸X(ÇnP.DÌ±›a¶š½,E4(Õä–ÎÑ•ÒNWÊh6{“jvSÍÙã-—1›»Áä ïsóV¦İ*èTŒHİ}¸¢¼ê/Š©¹RçÀrzœ…î;=‘:[ÍäªM¤ëˆŒ¸¾`æK•¹V¼vE½ß&½ïJÔ}eMÚÃ'Ç®öCWû×ä ßˆl.é<™®L$µˆÀŞ.`ÌYpÓ-8.ƒƒ î`gÜ!•I.ƒCA¸=±CƒÃ¹öL,ƒ=Í2à„ÌAµ¹vBà„PPlOFÍğô¨¡å#o†™ˆ£q§ q´™ˆ2¹ùw)§VA`
³åcĞë±èõ8U	t¶ÍP]x¼:ıB|‚+€OŒu—tz’j]Ø—0ñ«\–å“õ!‚Ö”CÖÍÄ>+VË§‰YÚK”vùÔ†ÅDè›K©L–6}åÓ(Ua×Ğ\>]Õ­T“Æ¬Z>cNùL£Õ}7pG¸GÁD|å³0Ò³¥€=GD¼lÊçVö/Ÿ×8§|¾ãœ¼`zùBü•Fé¹R¾hzùb+/Í.u8àn¡ÂeÂtªniô.¦mÄĞòå˜¶Øà
´º’lI°AÆ‘†W¡ÚÕF÷ÒÄ¢©©qÃRâ\He*øùÔ…Ò”:Úu³ËŸ‘KhöÊÂŞ©±*˜ìÏq¢gY¹T„ÁF7„¬)Udg¦c!›ÉÓ©-³Ü|h«¦R±6öôº`à÷AûRĞ\AŸğõaä hü™éò5¾$¼Gum¯’°1&œ¯=®'=´Â¹¹”­×®bPØ¸P5ÇXéÍRŠ`s%(å2Íâ†¡(‡Q>ÙZs: [¸^èƒH§\rƒP [è‹Â†NØ-ñ¶uÚm'†D;İ{« ¾¸k­ƒL&+]¾Á§È½B‘{¥HSŒ"7"7“"-B‘,æ*S3¥>ny¸Æ±æìdPoVBO®H	hµlC@`M†Ì±‚@ù€<•v‹ö}‚ö­½¢İì M1|Ğ¾İÃ\p2Ïíæ;"Ár¿tpg(³Ikq`ù.@¾ïñtÉ½®.9Ü*û sZ(Cíõ€ts¿ïˆ Øƒ5¹ã'çNÈ9’îA©ùPîä#DÂŠüjÍ*R¢8« .8¤ü0¡Ÿ.ê…"QôÌ)?:yNù±DËã9“'¬0yı=å“‡¤£§“êäÈ‘äÈ³hğåH.!GryÕ^ —|$†l/m¡Ğ5,ÕXOB¬aÉ¢6o
ìŒmQ°d#İ/Ô¶fö±±® iô¼üuĞ	{:5VjÂoÈ¥UjiÑÓxš¸„°tfu¥`-cúY`Õï:jÀÊ ¨1Û
{]´%§J*›ÁÉ¶±ílÀ…Öë´&6¯Xwğ5¶¦‡”_ôùôa!æK½òi>Æ§/ƒp¯¸|º¨Ø M<ş¢dÙ¯F¬ôˆtõZÈ±{»Lõ:`¾‘dªG¥Í›SÍL0Õ[ÂT9òÏÛäŸwÈ?ï’¸¬Şè÷İĞz*Xë‰:œ"›¦th>}áü˜ôÿaˆsÁµs>àÆ|\*’dÌOÁ˜m`ÌÏĞàs2f[‚1ÛÆüÕ¾$c~ìàe)ÍF.ã]¶(Â§”¢@jïƒ?[qA	¥a©‰Í°Îyï´™Ç‚Xu”l™V˜î8ôS£;„ÍÛ¡‚jU=@äJ	ñPsñ¤`ˆ“6Â Vµp¶«§H\â–Aö-\1)ºúR¥jºü•Ï–O)¿î•-‹±Á7 Û·fGPòvO
´ïâ;‚ïÑà³# yÇn¹Ë?F»‚²ÙüT#Üô3ıâ2¿Xvtñ¶•NL(¬Øè)Aà!.ıˆ¿;lô´Tş#ÉF‚*`£¿Ğào²Q%ÁFÇ\şÕşµæòIs9è‡½?@VÕbúóg|÷ò‘	ğOê•ªFvsÚ ˜š¼0/>’Ë÷Yi=[«½«j¡+¸;k6˜Ÿ5e-Ÿ™ƒE,Àßçä`âkãœ`!–\0=ÈÏ‹¦ãÓ(Š •A‚J¨ÁeınÍÏ`°’aÖÜƒƒÅÂâ¡vÒ¬}gEô–ĞÊKJeÙ%Kñ;ö%Ë€'àª“±c¨RÌ”Úò™‘Ã‡,­½u¢/ÓÑŸ”—ˆŞéûñ`9ízyéº®á"t·–+V[h¸µ@aTS•ül5İÂ£ZaÕşÃ£ğº¨!1ø†ÁmĞÈãµÔ öÒ©Ép$4fõÌ˜âEm_SË+¿™z‰íq2™#M•Jöü¤#_€&mM+p@/âèŠ,ïÍ1Û·ï‚•tø+›áªû€Ls³œ¼À…F#Ng1q$F!DõÚDç/ş¬BÑ¥Îš«J(¢Î†Š<ÊÌbtU„éçL=ö%´¬’ß‹2¾Uû_Wl|)ßjf|£ñ¹%”«ZœfÚ†¥Ä V·˜¡_Ÿ“™¥gCF–s2Æš£àæ’xgàÌÓéäYl5/1°sŒ',Ñ³?t© ‡­ˆ’Á)‚ØûÛÃ„ô¾û§&‚İärm¼1£¢Òt˜AD QÙNÙ}È,ğĞİ•Œç-yqÍËÈ€À¯Øªe=J”ƒ Ä±`‡ ¨ÌÑÁõÃŒm†‚èn%’˜—dBVïkBöq&„Bn5eBâ†ïËs-Âtmß}ãfJ°6«XK%¨1’l¨‘dëI%¬«ı“ş"·ŒÁ2´:&XCQ÷Š`’f™uÌìçøy‚õìpV|Æ\±¡=$Ş¤œ„JYs(áõñªô1ÒícG›£´ò¬#„_“V°UÜlÈÒÁ“€üİHo,k'¿DfR°‰V®5«„\ñ@;-äĞ‹ÇBd¶4ÎU‚eà ¡ ?)m¦J¶ĞBÆwj`?,ìÛÖ¡ÑQÆu)-Å$¢Ï3SÉÃÊVš`ÈóX‰r@vÒ%í$dRõĞ’‡»xœÉÎÍ¹¾··¶şQüM7Ôf•Pt55Ñ¥€m8zlCØ,'œ«A"ãX£«]Æ 4;î0ì> %#Ä"ã“Õ.¯0@&lšX)¯ËŒmÖ×J9ĞY)Øi›ë¤l!“b6™Êbv“Œ!ÌA“òö™oHwuü“ĞØ
Æ*´q±u@«İŠp)Œ÷ØôM·¥Ë¦»lº•BŞÚgÓ·¤Õ6İ²éeÓCÀ¦µñ¶†MI°é!›NÒÊÛ6ıI\°°E§Â¶§<İ3f›;Ë×Ên`Ï.ÑVXJX‰*¬(›?ê1ØÛ#‹(‡a@Åà¨Œ¼h<r(,òŠÊf‘ıD,ø]¶JF¸3R[úÊÀû¥Nh]kËá@Î§ ¿›ÓA}‚ÁŞZOî‹Áõ7ŸÁ%çö1–èÉ
vğØâétG—-sÙbªBŸæ³Å»Òj§nÙbge‹ÃÁ»hc©Qz`‹Ã¶ØU+ïfØâ<°m­Cô\¹1;©éÎ,YãDfÇvÆÊR1"ûF"ÒË†©o5ç[Z  BíÁtj§"İ¿C?Bh&3'Î.ìj(ÓÁî‰)|Oè²G_S8'6…Óuè{Æ¦ºşD¶„îƒ`†7{ïK{¹³7×½ŒnôgïiÕÔíì5ëìÙËjã3{G$fïgöZµrÎÌŠf1S„­Ø="õÕ¹JÏ"å.u§4"¡¸~*™Ncqº¸¬màBVª0Ë¥Rµ_$š±*YÕ¹|[ªÕ‹’‰|Üªxt-BİÍ¤#3ReÆ>fØêLë	CÜBéÅtª¾ãX†%8Å²¼ªp#ªÊêÀ™Ùö*Pâ(:xšMU((XsäŞJµƒ-ãÓ€õ'”Šğª Qìn›êäT©ÓjãtO°á‡2Á{÷Å†GÆØp¦Îa!Æ†T.Ê†£7	•K›Ç‡I‡E—rù°¤Û}>üXZ•»åÃ@ùğhğaEWàÃ£>ìĞÊ³,÷HWÊ_ºâ¡-Äú¶óf„‚±²éµ£>Ü"¢ØÎºüC3Y$CCsµeÓAgb>‘Îîkñı6A—aƒNëyo>°û¬šöÔ?ØO[î/-åìßºq4Ø;8€ÂÃÿãÕ“(õi_¤ ±€lÙàğñxà3ÁêP—Npyà0}¸ÏŸK«9İòÀ\åÁGhã#œ˜à?ÄQZùh©¬~ˆcø=q>«=œd|ÇñgÜáó…`x¼¡6&ã¤˜ÃçíîDé.¾úRZŸÄÖ®Ãçä>'³¦ãğ9…¿Õás*¾ÂásKàğ9ŸpøœOëğ9SQ9Ë§ñW‚ÃÙ–Æ‰óÆà%Ã) ô¹
á<CèS„>ÅYlçkå¤r]ÃÙÖ;Ë8ÎpgA´[S©]Ì(Úî:ó›']T°[gFó´Æé{Í!p£[;êõEİ¢ˆ?5¯‡‡ŒæR5-Ó0ê>Š‘Œ¤:¸ÃôÜ-_e.byoî–Scîˆ‹uÜ—˜qß‰qo§0„v‰çœTN\ó ’IG±F
ÎrH‘mÊ—4U¶§ç%I:%~,’<š—«ôOwOº(4”Îlª9W%X¸ÅáW‚GİàÒU¾ª\ÖUN‹Qår¥Ê†*_b×›è}ÿÈ‘
[Y‡‰äà¦uÆÀjî*uƒYPnÃ•	©&é¤“ÛUè%Õ·ÑQ%*—š›kÅ!Ô
²[6ëVÖ·gŒŠtøç!óõŒœJYn1pS ®0W=ô0JõÚM‰ºä"/Šjî'¸ÓÑC+9{‡ş
£Vû@3\™˜ÖoeZ¯êkZOMëÕ:­×˜iİÌN§5Ö!“MÎå²¬JõŒQSÎ”v³ÄyÂ=Xºpˆ2&¸6îw‚îu}¡{Fİëİº³õÀ›®şZ›ysR¤’Ç&<¤Ì BíS…l‹ììx Slâı.kÊ> ˆãË€Ì\‚7ÂÛ>Ğ®å‰#<¿¾mÆÑ,‚
,‚ƒú^uS_ƒ:36¨›uP·˜AÑí&&ƒ+ÚÄPººU27:È¤&°<ŒlÈÈù<å /[€_é/¡¬Ö+!QX«Üñ1n”p»¿º]S°b9§FT[´š;d[%.©@èÀ`‡	nWı¤â2êA-ˆ Wuñ€ƒÊÜ¨‡˜%„Û­‰øAfà¶¾fà¬˜Mv»ÎÀ2b“íÙd?
Ø;	6f“İ¥-ï––b“Ñ æÑoÖ÷°Ih‘k,²{¥6b¼‚û´ùıR ÆÌüŞcô]ğ !t1jâÏ¸Qó“ û°A£9Ï1jh>¢İ>*İFWA;$ç\/xŒ`BŸëÏúq–YŸëù®ë	…ü¤…,!V?~¯˜í OBëS^¿HO»=\àZšÏhÏJ!^¿J«çØ*áq}^Iv! ´ñ‹Ò¸vÒ…	èBÇÒ|I+¿ìLÎ+früH¼àUíá"3)¯u7)ÿ_&å¢˜¥ù†v÷¦t·4“Öo±µki^Ü“¥ù6k:–æ;ü­–æ»ø
Kó=–ÀÒ|ŸŸ°4?À§µ4?TT>òiü»àğ±¥qÒÒüDÉp	ı©BøÌú’¡/q,ÍÏµòR¹®á=ß³®„íM
Œf˜N²mfØ¯­2xwêÄ Â5¸Şˆ‘ë1D·Üy˜I„ò8ÑØ8J¬‚*A¾öŞ Pô4˜+ŸUøe!8Ëø¿l–Ê-ˆ›K_rü	ú‡ì+–÷f‚^Ó_+A¾1áa0›²ˆ,à¸à—Äâ•d¦¡9É+vY?ßT©…Ài%õxõDê‹ze Ú2³‰ .5ÒM® â$æWV‹Ûs]¹”­¯D+‡1eÍ¼B«–¨`ˆˆJX¾Hf¶ê[iÎò¨ß9‚£°f•hŞğ³òäÁºòà.jåå&Å‡ªl«L+¶õ¸ÙWHß&ˆü§ù»¾ˆ|YŒÈß+‘0D>Zö7rBGÜŒAk¢ó°zv*Â~­b£4à2ÓoKMğwa«šò­9(/1,4‘ F‰öê=ƒï"WOpä&ü˜ç_2ÎŸúçå1åö³ó§(·+<åö·€ıÕ&×áğ?mù›´ô.ØáÁïl*¸«Œ‚ûCZPÓü© ş’‚HÓPv0¼†»	¡
İ`(ÖÿÜşa™U7W»Êà_ÿŸ/¨ş•VıİTıY:xÒ5QğçÁ•Á5	u£æÕÊóIeÕÔóó{Òí°€öp­Qòg\Cÿ'.Ä?iœÉµ1e0P»[Xº‹+ƒ~ˆù˜,ÂÖ®2¸®'e0ˆ5e°(«2Œ¯P‹±Ê`q~B,O«–TT–TÂ™é/8,miœTË(®¡—UËB_Ÿ ôõ2X^+¯ •ë3ËÒZºâ>f"
»ÎöÀeË¦Ø!Û,.MÊu= §=jMlÚ—y	áÈ#{mé`EÇî„+±¼7á~CLî¬¬\Åğ|îaD¦7ÁÁºÆSCÀ†â`¤%ôÊeg“cÇgia—ï¤Â!cÎF°·æÎZ÷ÑfÃ «0²Ãû&Ü2ü­Ak¸”ŸVMŒ}{ª¯±ßûj:ö!fìmû®Øí·‰¬„ÆíÄ‰
\º›°ÉnLwÎQ'­‹6HŠGB|‚Õ#™WF²F_#¹)6’5u$k™‘œ®A9Bb‰Ğ·ógô¡n{¨›éĞ@0«a/=ïÒìö¤šÃ’#KÄöÈÑ–@Ñ2½nT_º»‹a’c@¢åö²	Ö1c^;1æùdÌ5}ùæ˜&ªc^GÆ,šäO“Ì/`×%ØØ6i˜¶\OZŠ&a-·IQ6 Í†¡.¹Íè’õ¥7KÃÈ)P<’ß{Ş,Rt»Å£ù3.Š¤70HcL·Ç6Kj·I·ş¥!»YŠNğ6&œPH.(°7a™U_w¸»¥Z½©íï–õ
l[>˜É½R°ál(Áäí#F›ëàî„€İBáŒ8µ“î46ÃÛ§A‡ÒB‚ÒX¥;]”Æ)¨ñ%ÍHğ
‘‚û ³(Hmé 5rT°•"uÚZ!mcºËCj‚‡Ô@Aj¢‹Ô].RÛ*¨I.Rş½0©í¤F
ê©»Ôd…4Å u·‡ÔöRR;¸HİíÚ;*¨©*œòE¤Õ4¶JlDwR<î;kã]÷$Tâ=íÁğmTŞU*+ãïÆïIÛcwíá^Ãğ{ğgœá	†Óù'µ=îÙ{jw3¤»¸í±¨´Ş‹­]Ûã¾lk:¶G#«íÑ„¯°=šYÛ#ËOØ-ø´¶G«¢’ói<XpÈ['m½•÷ƒĞ3BÁúş¡ïwİ¦•‹¡K†Ğ¼¹æÄ¸Â§Ñ¨®íÚ×†äåîH¾˜ D$À!9#\+ÚqU:Ö°hnŞè˜4Y9L$½ëğñ!-J*ÓÈ]ïiD'Ï¤¥Ú¦~>Ñ$z’Î¸
qŠEd6…ø®RhSf?âF…±dâP”Tˆyå¦[ƒM&ÇÖ¼I…KØwpˆ‘´¸}Ë{3’Œ©×N%ÈlCFd‹€éf¤K*Z³#ØŠQè}m¨]DÛKYsPæ¡Ná1æU5ªÍ|U‚:C÷¾_’ì$òş‰ˆX,ôhêÑ€«x 5¼NH<	®
ó*ŠA84:%âÎâ™Zæv^D aw0‘ã¡šºä]BÈ»O_ä}(FŞ}•¼ûòÒ(.g¶ÜêÚLĞ©Mb$—åÔ»Ò¬Ä
9ÁÒ8¢­aƒp564”\P›:6MáİE\(İP³/…3n¶çÆAóD% ò²Dß"^ÈŒ
Ğm9ßèƒGˆàí'câÃ5!±:U
B£måb£Ég"iÄÆ¤0Æ©¹ëÅI2"ö©x<ÂÉx#D‰ØèK“¹Or³0&±‚E‡7×XWˆ.gf\Ø˜	qH£±†œ×ŠœT#áœ<Lû'dIaúb‡c*ƒ$‚ÀFk™„aâ IxaKIg‡9G!Î ÉCÖaVdR„ĞWhzĞ–hsbĞæ*´#\hj„ĞThyĞ–hG9Ğpy;8Z¡#ĞB%¾¬Ô=–uJü8•÷C·¯OÆµ“Oè–Ç}í‰Zù$³äÅ¯<Ö…-f=L+ÃôÜz‘
ydSd Ñ°ğ„<¼ŞÛÌ+ã•³	ñ$Ü®7İAñ`]íÈKŒm“-¦^ÄÓ{«éàäÇ,'ƒ?¥/y"¶98UÇwšŒO6Oz›ƒåìéıÃ¸–3´å™ÒR6ŒHáæ@² g±M¸/xÚìÎ–êÜœ£íÏ•5Îã÷÷çë>ctöü7“V|/4øb8ÏÄöi·K·Ñ¾ ™ÿ%¸„@BæZQ _Ê2»)xÖ5v/S¸—[¸ñ#v ›‚‘á	Ê^+IWº<ç®WiWû<¿²´º¦[¿Véõ<xş:m|½áùç<ÿ¼cOİ •otfæ&33±”›µ‡ÌŒÜÒİŒ¬"ŞÍÈ1Ãõ6íîvé.n¸®*­ï`k×p}±'ÃõNÖt×»ø[×»ñ†ë=,áz/?a¸Ş‡Ok¸Ş¯¨<àÓ8%8<hiœ4\R2¼B?¬1„~)Aè—áò¨V~L*×5l­±:’BgÄ’şSÖd „ÇPN“Ú^–Æãªwz*nà´—ÒÁãÄÈ³èV“A<ÁòŞ,º—cåIEñ)A±;ò4!šôŠ'µ‡HgÏ˜9·òÏ*¬çV´ô$‘F çFlº”Ÿgëpù­._`™]~¯º«ãE…ı’?skH«—íÌ¹Ù”‚WtÒ^Ã¤½ª_3“öZbÒ^s&íu­ü†™´}ıXM. ™-v†—ËÀx,å
”M;€é”|`<ÍS<àèGï	‰~a¨‰::İƒtÑ æ³ìÒÁ›‰™^SıV_3ız,Òôm×;İÌÍ²22rø¿ëÍÎZÒå{îì¼áÎÎû
ûvÖ–Vv;;éì¼‰ÙùXbfçÍÄì¼éÈ®OµògRYµÊçü­²´¿÷HÓ†Ü~¡½eÄØ—üW,5‚ìW†¥ÁñrŸ[s³0ıPğµöüá‹+ÉbK`Qßv¶%ú+¼½Ì­‘0Ñğó–Yßb¡ÔØØ•cÒ«ƒZÖ•&=®X3~Æ"Alä’8¢a™Ğ_kŒ¤ÕÃñ\‚‹†Êx¿ë‹‹ŞqÑ÷J…b\ÔãÍ‡=>ZG:ıÉå£w\>úY¡ÿâóÑºÒê×nùè:µï‚~ÓÆ¿>z7ÁGï:«ü­ü§™MüØpB	XW0ó¶¸)Uk	R¶èôËµs&K4A4‘7Yvßc'{
S’«Q¸Éd‘ØD÷)²aaˆ&v¬@Í†B°‡í)¯{ıÈÉğü’½ÁÅºêŸ$Ó™;„qÊvÇ'©S là2ø+Á0Ãdşî‹aŞ‹1Ì?Jècƒ|àıšZ!M)æ"Oí¿¬'}öƒo5Ô
ï»üÒğøpö	ii5[%ö	ó²tğ¤À/óiãù¥qí¤üòÃ/hå¥r]¥q`Ô·“İ dgÀ•mç‰‰¤y<„ J‰²Œ’ŞªTÈÎ–|
8‚°—%¼è°-³MYfoOİcã6v…2ÉÓšâ°<{`}!Â@–÷f|Û/,¬ã\DÆ)û…¼ıÂp;ˆ`c‡	‹jËÁÒRö¼K#û…lW°[„»…OÌnaq©Ìé%´õ’RàÛf(¡í°¡…¶ÃÁii—K>u¹d…½¬Ï%#¥ÕrİrÉòÊ%ŸKVĞÆ+.ù,Á%Ÿ9Úi%­¼²TVí´
¿']Â«jŸ•”âÏ¸J%®fh©ø<fYÑîV—îâ–õhi½[»–õ=YÖk²¦cY¯ÅßjY¯¯°¬kXËz(?aY¯ƒOkY¯«¨ói¼à°¥qÒ²N+¾¡×WÃ¡¿LúKg9ĞÊ#¥r]ÃÕTÆê„¢ÇÏÜ(cZ 'èÃğn“œ•Î y`	"á1b”#jˆ’©­A9d2Áü)ßŠì–FÕ#¸È8¥Ä‡+÷‹èz4Ş]z:áš%ˆô©€¦´Œâ°½åº¡Pj4Ë{[®_Å<†(64t¸t‡¬¤B€õ W}õr=“\×4„‚³&h;bo™‚šÄ\È‘Ğ)¹ i©m+!SĞÂpmEï*¯v©ãÎy@â¢Œ$ĞÕ
2Ì]Dßl” ÈFB‘û¢È×1Šl¢©5yG÷\ªÑIØ¹<Ô¨£Ê‘µÍ:†í…‰©=OíKä9rëi¥›Õ5ü48¼`&zĞ‡&ƒD°‡ZMóHæ„™;ó([…Üµ¼W%ÄÖ ˆM„ÛX·Y_„û&F¸Í•p[ÂQÃ™¢•€¥Ùœ_–K–yB)êG/'˜Ã¹&ªÑ!Â¦&¶‘C¹t0&1ÎMdœu}óÛX…±:Îqİ
ÍZ9^„¦“Bì»D…-Ci‰„OÁVF2nm$ã6dœ ıMô%ã¦ÒÑ¶V2z;×I*¿‡PÜN×¡ø}B(~o„"uèd­<E*G:”gú2=fnFŒõèöì)Ô£›	N;°ÌîÁp]`;*ü©~ä~vÓ€‚Õ¸ËÍ!9Â}$áU£ÄİUy4=ğíyùˆ`'ì<}Uø»˜Áşèó€=BusAuWÕ]•¿›‚Úİ'úÒjn‰>]ñø	xì©g<~Jı'Gí¥•3R¹®a$;Nã™D>òÖŒÆˆğ¬Š+F}0›"I„.c‚Föî)„1‚kËE!àC¶ƒf–$råş[ÌYÅªÅ`µ–1W¥SŞ&bä)±CL'#ËõÌrLĞšÀ¤N0Éy˜4ªùn1ù%†ÉŞŠÉLƒ	Q_|§&}•¾Ú£.vÛ×¯±¾JÚW»éë£):ÑŞŠ[!‡øíª+£ğÔ‰“gò V”|•&kŒ¦(â5UŞGÕÓ¹Œd¦	OzÕ!A91şq2ş ?¶¥ıš’Óı¿˜Õ^ÑWeàbµÿæYíãlÁÆ¬öYÚ²SZzÁ¤öÙ`6›…¦ûÆtï’;û(ˆ}¥ bÇxÆÃt.š¡•Ï©8ùí‚ı5=[
‚û³ÌŠ?]Ñs€öq í»DfugW°Ç"vu+z°õ/WJ¢P¨!.[K«ÃØ*±}<œ¥ƒ'ı)1GÏ•Æµ“şNH‰¿ÁZùH©¬ƒ£ø=¹18Z{øÇláÏøÆ`ÁğX3˜íbƒã´»ã¥»øÆ`‚´>­İÁ¿=mNdMgcpëÆàd|ÅÆà–`cp*?±18Ÿvcpº¢r†Oã‰‚Ã™–ÆÉÁYJ†ÿ@è³Â9†Ğÿ%ıŸ#ÏÕÊçIåº†¹Öü£9ÒŒøó¦˜ó¡ìÈ¢Œ„Mğªë; rËËt°ÙæÈÀ>fy*2ÿD;¶Ùğ«Ø7¶lúVFÿkä>L9}PÈHÜ¸Bó`L¶3œÏ!y2~[¡Â,ïÅè¯ï×?&ç.ÔA^dy*	sÔµår€œYSDq§¢÷<q¨m½zÉõHÌI”ÌAd‡ëÈEİéf¢‰)›mú^õ‡³˜ÔBŠèY¸# Éx÷ ¸81äI2äKúrÿø/Õ!_f†ü´Qhş} =R©tÈíPÍ¨IiŒ¨’0^ zòÅ‚ÌdÂ NFí¸DĞ˜xh…AL°
c
ğÌStôôR…IÊ‹½;˜ÿ®€ºÕãLSÀ„­Ò¯¯¤ƒË„ÚNuE_„'Ô•J¨«¡!”Íôƒ'o„Dº§Ã«
ğí³OA®øªs
8:;h_ïf%t0Ø!LË›Á’"„7ªç*iyôi¤tpub<õ2kúÏ<îxb?¸VÇsŒ‡ª­~Şşn›,€¯'à˜n»A›Ş(M½[€¼ÜÄ&V¯ÕÏÏ—N˜˜áf©Îì[´ı­R Bû6~ïùûv‘Zõ˜X‚;ø;.½§Âw„1 ¤ksÔ@z—v|·tòƒ©HmF¹Ÿ1:´äï!¸P…m/]ÜË2£NëìïêÓû´‡ûmİfK4itšı€×ÃÒÃƒn…=0„ã!íáaé!DlGiö›%të£J¼ı!óÓÖKëZ”Å…>‹ôÍÎÔZıIg¦23;Ñ~Z;YØÎĞ3İÍĞTÁòÙh†vgˆ¹øÓŸ—ã
vš4Í[¿Hÿ4ì‹¬êhØ—ø[5ìËø
û
K a_å'4ìkø´öuÅåŸÒ;	oZJ'5ì[J‰A$÷Û
âCîAIr£("÷»Zı=‡Üïrw9J2?Ğîµ„ÿ°;Âï,H~Q—ğ<…ûX»şDº®k`nVªvñ¾ñ¼Ì>B™„+l¼`"„jÑ¿nğÖ+Æ;Í±,’]À^o0WÆÄ†W_˜½\hn]¿™	î¯ ğ6‹í)d‹E÷Ptÿ˜e‚À(Ÿ<QÉ-	îê•4ûn€ßO|S¢ú'»©OI6Ï¾ØEÈùË{³/ÇuÈçJä/‘éU„‰À­Å(×‡j®È±‰w=ÅØ¡§Ìœbée½™bH:6Y¼dpEÚ$&g±RGR6‹¿^6¡FÎ›3¬0ë8T*È½„£vøá 2Éİ	ÄÕÏI„$_õE’Åâ$ùZIò!É³à;2„QêÉlè2tü„QL¤8ÑÄeL‘©}Ùæšy`Ü†éÔxDz Á»q¤U0ŒpD=äã 9L¦õÀ…})q;Œ’©/ÂĞ×0¦TLfÖæ	¡“ÕÃ&Ü’ÍqIôeBå®VôÉDì­ìpŠ§áŒE$·yg³²¨CŞ$•Àb®o>%d.ŠÙÌò¨d3ËÔ¦ğĞ¬²$“qûêÑ¬=ş¤)«IĞäÀV<©âı6Á*»
«|×«,g•ï•U~0¬Âôa ³X¯n¸´}ÀEÖ,ÓœE¹!ì!…Œˆ¦wĞAAbĞ0–?Lt¿,©7˜N—CØµ€€aÎ[Ÿ-’i8Ãµ+	)H'½¯¦K1ºªÌl*š?E¯	›ÛSax“òml¸63vñdTä8°æ–)ÓÌ‡fğ|$EGléxš%7p)@í‰ÚMfè§¾fh‰¸Mù³ÎĞ/2CbS.éÛ”»à_ò.ßjÓß¤©—íK&~g£Ğª\ÚZ•HÚ**„¿åù·Qİ?íü£ªs«:ÿíNuî!(ÿ©ÎeâVe?yè¸?>’ï&˜G¨iUn•P5²İ¦Kó°Ì•ËzFå¼ÚÁ|¶ƒ¸QIßŸÉ2™•ó{}ì)},àö±œgV.¨},$}„fåi6ÍfåÂ,\¿<íœE´õ i]‹²„Y‰¢ÈÎYT«–êºXŒß“^›Åµ“ì-ÁßqÃ/ÁrIşI®ø zÌo³”v¸´t7+3Ò|6wÍÊ{4+—eUÇ¬\¿Õ¬\_aV®À˜•+òfåJø´fåÊŠË*>¥‰U-¥“feJ)±É½š‚bÈ½R’Ü(RrÓ¶[]«¯!Õëş5î[±äp¬¹Çõ?|¼nÂó0N;gòØø«TGÆ&ñ~qÁù«;‘Nã[&h
Ÿ»ä,•€×LUÊª$ƒ_Oy–
|XE¼÷&\Ã¦©¤À’Ü¨šÊÙM~¦9ÏôN¦ˆ€-X70ÍQ€1œ»³zYÔÀõÜ¨B•Bé`MÓ3éš„şk±¼7“nå¸RZ[i[ch{i:³hPh¶Lîæõ½&
aàÉˆªÌ«ïéUñhˆÜj¼ñ`C‰Cş‚gÄ 2§â®¦VZIö{½aaR
E“éNo:š B³Pa¾¨°Jœ
ë*†*\LÃÖ¦vOpÌ¹Ñ´_ò«}#ÜœzÚ‡$Ac¬-k’Ô{çæî•¨îr>¡³Nò4¨oòcG÷|èšÌäÓÁz	d… é¾°jœ ë+†<L)âb”¾Äe<–ÍQš<ÛŒ‰Ö¬ÌÈÛ5­c°)ÒšğŞNè?TîÇ=iy'İ\q.¥éß%¿>¾Ú¥™9ÚîŠÄAfró›È”0lZ3ÌM”=+dN#Dj"ì‹H©8‘F)‘F"DZgI_!PÎ#¯4ˆ5©Æ¸‰cù”óTB·õ™dK~6áò †J"ÉUëŞ°G†œÚšgdZ‡„\¦ƒ£k•ÑmØ×èV‹?éè6–Ñ‰ñ3Ä7~rx9Ôjµé¦ÒÔ3~hÛá•ÖÍØ(4~Ö°ÆÏæÒ€­-Â)ˆ%ÑGŞhT6M:Bõ|^PË2k‚¬é™ãşx6Û[šmÉf	ó`+–®_‹újkm½´®EYÂ<@QdLĞê¥ºšÛò{Ò<˜¤¬mÍƒíø;nÌ,ëİ1/kÇÍƒÉÚáé0n¤ùölîš5=š;°ªcìÈßjLÅW˜ÓXó`'~Â<ØŸÖ<ØEqáœCé6AbWKé¤y°›Rb(É½»‚ØÃ{h’Ü(ŠÌƒéZ}O©^×ğÄ|¥ö¥nİ|ÄğÚá£÷·÷Ií¾&Ãƒ°g´¿m.DšD’±m¹ÄßÊ‘‡l dkFíRÀuğş({Å(qC}Ç;–ì
IfÜQÇ¹İêA’&ä‘¶'È ¦‰©±=…JŸ‰iÓô"é`‰å©ÿ¢Ğw/–÷¦ş×q=×]Fi×(´óCCÜ7Óœ Mì#\A%é·™evá­ë-¼¬vĞâ³C»4kµìàE¹ä”†‘òÚzoÃ	Ã’œ€¢ˆfjõ‚á„cì!_7u…ØË²z°E†‡i*Üuº/aÀ•„ç¥ƒZ§jSãeŞj*CÃ—¯éS)5åÅa8 E×Í¶¶Ä¼•…Å¾æm½¸**éHÛÍH¿ÅH$î\­–¸)q¥É–ê
¨òÕlã?€	§‘bñtÒLb%àJ»&3„²¦O°1Ş5’—°íiIØİÔÁ\Ê×°‹Nf6óàGˆ©}4\rnñuW±ÅÎ\	~6—&]·h:('HÉ§µ"Ñ)ÓqRV””UCÊ³¢ÑæR$Åz¸Ö)÷òíº\Ã©™àM1Ÿ«MÙq«ñcëgŒ9cøˆ!nà¾˜Q½O…{˜Šãä(hP¼¥ØçğÕ Ä¸+2îY}{ıø¸;uÜ³Í¸ç`Üõù|_oa_×Û†Ÿ÷téaœš¶F’E¯«z]e˜:Çz¶åb
Îƒé’È>rîQáí +1ÆªŒqŸ¾Æ8<nÓì«cÜOÆ(6Íß¦éÀûpÌ¦9@›(M½k®H€SÏƒØ&4iFY“æ`©OÎ!
àP)P+à0~ïù”ğp•|£­50‡¿ãÖÀ,Áx®Á#÷ç¡)Ï®I†ã…ÙW¢`<‰À;Š@mŞÈàhEg
âcæ±³e^Şq¬ê„NÁğx–Y€úÎÃ9'(°CãYk5-«ÉmÃò$Ë‘#ƒ“Ë‰å)
øTƒå†>–§yXÎ,Ow±D}Ë3Ø™Kûú8ÏÍm®Æ‘Ñ­Å³<à]üløFZ<GŸ+ÀCÊí#ÍÎc³„=z¾scóm}¡çÆIµˆ¢È½H«_ìpâ%†c§ —j'›X¼¬;ÜW°¼<âÀMâöèÚá•ÒaÜİOš_Åæ®=ZÛ£=z5«:öè5ü­öèµø
{ô:–À½Ÿ°GoÀ§µGoT\nò)½¿ q³¥tÒ½E)±)É}«‚¸Í{Ó$¹QY!·kõ;¤z]CR$Ò\„g%5^¬„qP¥YÄV³ğzó‘ğeRˆAæµ@D¼ğ,1†‚áCf›+‚šES²ãìTr_ñÈw—‰-LÔî<Ä¥:]ÓÓÛÛhšFOBä¸Æ¼Î'f@:¸“”ñŒÏ„˜w±¼7ãs³¸º[	u!ÔÉ‘ÕwôhìOœ xö‘‘:æÑk“ _<İBãØF’#…‹Æj©	Æ.¾)
W,™èıEï¨Å¶Ò@vf³3Ãİ8:ÒÁ½‰(¾¯¯oğı:àÌ€ù¬Ò6’„Ó (Óš°O#?)ÊqÒ'ç7ogÃ&ø¡†å™ûEV™zŸî5“²UÌéæ)Š©ç&fôŞ{c´_â
LŒı ûC}}‹øØÖ±?bÆ¾Æ>däÒPèµ™1Gy³×!ÁÖêgí„}š-TY×ÚğBRÂ	M`v°`öX_˜‰cö¸bö„Áì#€d¢&&º5ÎO™ïíNlüôöI}èÄ˜Ç íCc˜_‰ğ¦çV_0/¡†3åFZƒy£×°´9Ñ3—L0ïÍcŸ"§ÿÓ‚íÉ¬™â=åJ—‡Äi,N(İè¦x“ıW<™ ß!B¿§ú¢_]œ~O+ı1ô{‹3;¥…ûW\AfŒ^².sòÄñ’Óqy$Œ¨éŒ“0„ôğAD–„§£â-ã)Ô¦/Š@vË‘û5Š$ĞtÁÌÃ¨Ó#äMtç¶ex5
ûA}jÔH_D°=› Û¡B·çú¢ÛØ¸qú¼Òí¡›§ã|ãô0ü"ÇŒÓ—´éËÒÔ‹`Ëvá¬ñ6	mÓ-­múªTç¶ÿ5mÿºDÛ~üôÃ¦ß  Ğ<9\ğy“eÖ°ÛÊ³jŞR°oØ°Ùiö›%¬šwY:¸~kªÙ÷´õûÒºe	/Š"«æ­ş¡TWûú#~OzÙ>ÖN¶±VÍ'ü·«ç
–Ÿbc2¶‰[5Ÿi‡ŸK‡q«æiş›»VÍ„­š/YÕ±j¾âoµj¾ÆWX5ß°VÍ·ü„Uó>­Uó½âòƒOé#‰-¥“VÍOJ‰‰$÷Ï
âCî‰Ir£(²j~Õêÿ“êu|gGséõÊfì‰ £™Ëì×íËğá<„|)WK$ë6”­¾B¡^3\r†Óèaÿw><”Ì É—…pÅa šSªÂ—dÕTz%^vW‰aÔÚo¤ƒgÃ%¤ûå½Ù0ÛÆ…ßJ–?YhÃ˜Ûq&4¢€´cE“Í!¨DŞÑ|v6x"SĞD#Ä"1¼Ä°ã,Jt ´¦f=åÚs/°Ú3PUzQİ(bÃü•ğÑ2à¿ûğ¤¸ÔúGü¯X¤Öv¾Ô:F ÿg’#ÑO4íø–ñ<#ƒøC$¶&[±5Ô§ØšWÌ'½Ä¿ÌO˜¡(:Vp[€eV‚MñÃ´‡…¤‡°ÙqÒl ›%ÃX:¸~{	#ĞÖƒ¤u-ÊENV,ÕM¿wF ì†ğw\‚/X.É?iÁ‰0ípié0.ÁNæË°¹+Ávì9Œ€Uİ0ş6aøÊ0–0Œ€Ÿ#ÀgF ¸¬âSúDAbUKénÂ”S%Œ@A1äš$7Šœ0­¾†T¯kØ9rôñB¸Î•æÔœ	&ÿÖ
¿OøaS¦·ø £KqÖhFãÕÇñ<‘ôÄËI2®µXŞ›xÙ)q<¯8×œï‹ùy™<.áæo'Ÿs£x6Öi<¿G˜Àd<òpš7M®ì›³tìÊSX~|Ls8ğLğEôXfD/nEh¾©ÜÇ¡}‚6'mÖé‹6;'í•6Ãm&éq,ÂJKí0'İKØÎ¬šÑ‡eş§@ØÄ±8\O zŠ šîÑ]‡ëŠèpƒ(Ÿ'—ˆI›ÉÒ:\I´&ğ›±‚=Ï@›UœRI™	SEùÅà¡s¨•H±//nK`p1vZÏ¦«ÁlcèÑ•“¥Àî‹ÍU|l¨õş6T‘¹Ñ¡æzÑ7³ Ï}é
ì¢;t¹=Ê A¦"±·Ÿrô <c/RJ¸Xè¼‰Â{ã&ÎñóqªÌÇÈ¾æ£!®ÂFé|Œ–ù¶«¯ÂNÀpÌğŞP›n$M½“îJVÂÈ`c6
Mïİ­ÛDP‡Õ*„M¥ÀÏO|Õs3BÕĞé‚Öæ,³ÚkO{m¡°Çì°ÙÒ¬ÍÚk,K×O§8§­ÇKëZ”%´Š"íµ¥VßJª«öÚšß“ÚkídO«½&ğw\{)XN44Çœì×^Ûj‡“¤Ã¸ö:KšoÇæ®öšÑ£öªgUG{MæoÕ^SğÚk{–@{íÀOh¯ñiµ×TÅešOé³‰,¥“Úkg¥Ä^$÷.
‚Şm’{¯$¹Qi¯]µúnR]3›ğÈEØïÔdyÄhÏÎ¢ÀayÉ&ÕŠU$&&r‹­HîÄÄ£òtÔVSV–0ŞX¬Y¸Ğ¦1E¯˜rÂ„°Û7¼wËëç%Gmáh§Ï¾‡Qs•FfÃmÒÓn¼ÏÍ‘{*ñ!Ö,ïM%fâÒtºbOCˆİİX­"\aÈË]éÏY´½°ÑZ!ÉxAÓ`‹S{RWı½Ôä1Äc˜Æ3ˆŸ+ˆïÕâqÄ3Šx£A|!>¥¯4iF1¸}™¡Û’ôH&ËğüNã%’8£q=§İ0†V9G­~ô¸¸‚”(—#[˜*„“4€Jn¯Âi"/¤" ˆi ¿‰Y P§ÃG'oµä›ÂìuDY+º«İàãi¬§‘ÒAS‚Ìç	™›û"sSœÌY%s‹!3lq7ªäZã3¢_Ì}ªDÂ=˜<Ü¹Š!	HŒN2³Áø“±¶ƒÙy©‚EŒ ÑÉâ´w¯é(yÅµ$®;Z‹U\ÁÖÄàÏ—Áçú|s\µåuğ{ËàEµe}Õv IÀ1ÕVĞ¦mÒÔ;ğ¬æ!:‚"Û„š­Õj¶’Ôçg»(K*„€ß{>ğ¬¨8ÌYÅPåï¸b¸P0î0cD¹øç,í¸S:öUª=©‹êfP¨/à],³*5ïî£°÷µ°™»,#V—ya£QÒ™ñı4HÑ0Åï~^/K/û»½ìí)î´—¥—¹K¤ÙAl–PÜ+éfR“¢­•Öµ(K(nEŠû0­~¸3OsÌ<Åçj';?Gt7?—
–GFóSˆ+î£´Ã£¥Ã¸â¾LšÃæ®ânëQqËªâ>¿Uq¯PÜ'°ŠûD~BqŸ„O«¸OV\Nñ)}¹ qª¥tRqŸ¦”(’Ü§+ˆ3¹‹Ir£(RÜgjõ³¤z]Ã1yÔÓÛÜº)0g:êáB–*ŞyA¶ø­)xŒ¿ú*_Ü»×aRc››d&É'%Öº%Ë·¿ÍòXİÙ§Œ¯œÃòŞ”q).lÏÕÁg·§±Jäİ<^±oÌ"ÊUO<àáS/Pe .qh!'_<¥Â§÷t,ŸúB4-68ãVIh€l		Ü¯Ü/è÷ö8î*îÜ÷r‰ĞıWŞ¦ÓÇ/­‚C6AFv:Íâ¯ü“7	Æ'°¿J°¿¤/ìËqì/Uì/3Øï
ìWÓ2æÚ¾@d'á›Qúyİ «¶W>óy‹h_@ûjAûŠ¾Ğâh_©h_eĞ~Ş;óÕ“Üı1áŸ ĞgéåB†^{ÅşT9Ëæ£3t»Ï{½HÆ­²Fë>ÓøÅrà&]¯¦•sm7DG2Zub™é•yfM(Ï¶Ë¾Z/­!”	^ <ä‚­«ÄºFˆuM_ÄªÄ‰u­ë:C¬duûô¶\¶Ğ.G}æ9lqpkºûì©9A•´NòôŒl¹y7Õ<ÎÉ÷™ZVİ†sY¹cÇaƒŸ%ÅƒNo¹H†(IrklE"\Ÿıµ2úú}5nËÜ¨£¿IF/¶L‡oË\'€o&à˜-s‹6½Ušz9Gù^ümlZ2Ö’¹]js~‡6¿S
ü¤£Æ hr–ßEp¡Ò¾^º›eÖ¢˜íY÷(ğ{ğÿxÖ}„…gİÏŸƒë»¨’P˜
ÌZ”yáYyŞ >ì"ˆúNàÓ#
ìQ;ú¾Mà15Äd=®¨íCÔPhOÔöñQ{ÊCíFAíi5Ô7¨1yÄ3
ìY’ü&iö›%_“VTö%*/hë*û&7Š";é%­ş²TW{ö~O:8^ÕNö³vÒkü·co,_çŸÔ=¿_ÜNzC;|S:ŒÛI·Hó·ØÜµ“öïÑNz›Uİ7¥ùÛ¼)¯|Sš%|SšŸ|SŸá›ÒŠËG>¥o$>¶”îæMi¥Ä$÷§
â3Cî’äFQd'}®Õ¿êu¿BØI>É$ùB%¢9 œ×WäU„ Z(¼ßÑ¬ñ¼”„Ñ&…Ñò’¦èğb	‰Ç¢ŸF¡`Ã³Kıür¥É½](ÊfÓ0BÇuª†~ò°¯Q.ªJdÀ4	¼M¼R³Ğş…ó%ièYg·	Ù¿byoÖÙqıñµ’ôCÒÄôTu…DëımI ¤e:q ]”'&Tö-Óè	/	/âÃÚ’­Aß&P¾]Pş®/”Š£ü½¢üƒAyq^’!:uœÜÀÍê<~¢jje"j=ç'¹Ü/óªÎQˆ2­bØšúî5ALÏÁÛŒö>Í›¹ÖM(9¬Ä\Ä§ıAöÕ®şµBˆÃŸÉaàTKrOéîf n¼'È}‡û§¾È}p\Çş¬äşEÈ-:ö_ÇŞ)€5RË»ñ®M“¦¿€¦Lğ;Û„Zö0«eÿúòØ´øK
"-ËĞßRK6?££ü}X(ğï¤şa™Õ±‡{*ì_ıŸ]#¹F-“}°ÉäÍÔ|¤böJt?Tt’öçÏÁõs(Îà;`ÎƒêØ9¾"›—5Cïçc™EõE6¿[@€…Íî‘f²YB‘-¤¨Ì%*µõÂ•¹IÉŠ¢H‘-¢ÕIuUd‹ò{R‘ÖN°Šl1ş+²{ËÅù'UdGÄÙÚá’Òa\‘İ'Í—bsW‘Ù£"[šUE¶«"[_¡È–c	Ùòü„"[ŸV‘­¨¸¬äSú~AbeKé¤"[E)qÉ½ª‚Hr•$7Š"E¶šV"Õë6ƒÙÎ6n¯è\šImNqDaâD9«O< ˆ¯ÁòŞTÁÑîBç«nk*Rk	RxÏŸfA„ï°­M ƒê‘ÙyòAé°ÆÌ¶}Òg¨‚[GÀÅï99#6
1Ö%„êCuËì9Ö[ ëiiÚ–fëÛióî×;36B[43v\rÆP-QZ}´T×²¿c,:9‰ŠiÔÌUj‡ÇÛÅ²ÇË#‚ñÆ†| ïñîbavƒM´óZÃ.Œ 5£CÅXéæöškx@]‹ƒ	„=š9Öà±-D§ ~ş˜<Ÿ˜ÓsdÄ7d\—wøÔHäG>ñ+>*CÛ¬/V<!®â7×oaÌ]môÀ	nt#™‚ƒ´MseõåÌÜ¾Ú-f‹ó ¼9Ü×kLæ>y¥ÀM½ëÂwÔá66z4qñÉ¸ê‘e<1úÇdôu}şDwôô’ÕÑsxm¼áµÒ¼l©|v’å³­ºã³Ç­#>;)î%ßF;[²ÉäÑ£+½5û„t±­»fOö´î$ía;Û>ûµq.ÂÇ¨¹•4™^ä9êz3[Zì'ëHOá¢À¶7Kø_İîàaö¤`¶£‹ê;[Ú©
lšÅìÿ±¥İÉAmÄÈ`gEíT9¹Uh”¡´NõQÛÕCí)Am75Ôw,İØ,”OK³él–°öTTN#*3´õ^•Ó’‚E‘jÊhõF©^×À¥'ÑŠº<ì²b4HÙI³ØYQrü¨ç_8šé„Öã{2NœJÉ¤xşjyàÌ‰ø`LĞÄáz:ğ!N3Ë{Ó§Çu`VGß"£7:Pù3Ô­:¨ş_>+æø73sT©y··ç0Uo¦Â;Ó‡÷œÀ+8ğh·)¼¢eR“Ëšiú½ì‘N-y¬ö¼@mwYí,o”µƒÀtàfª5,ù=cvqÅYx¢½ª,x6Y°C¡Î2,x¶¿:=_g»(¢¾³ºØ>şjxQšíÛíjØOQ9‡¨ì¯­0¨œ“\(ŠVÃZı ³öÄ^sgÆú· ”Á¨›0OÿŠ—?˜wûô4yœ¼šÂû«#Ğ[æ\ßÆH¹GÍÖ]mt”,Ÿj¦¥Å<şÍŞ,\	Ï(^ê‰Í%xj%rK“®HşùR‘KHH˜Çwn±¯m¥#E±fÇpZ·ğ!e,!»\G‘¡0)ğ–5°Ã¶4|$¦šÃPë¢‰³A‘òÊ¾hå?Gupb-¿$S{H_kùÜøZ>Tçî0w-‹q­åÃuíç¯½—¥Ã9±µ7WÁ.„/óY…Psù£Ò†,dÃx¤³0 &Rn<ŸÜx´Â<ÆpãùşÂ8Ö[¯VÇ¹õv¼;Á[»ò”axİËÙ,¡gOR,/ –'+àS–øXêaùª`yš‹%ê;X®ÀÎ0XöqgöLøkü,ø…l8[Ÿ#ÀCMùº4;—Íšò<çEçùÚú3Î‹’²E‘l¸P«_$Õë§7R)C¢ÄMÖ#'‘
ÒvÇÅÌ6¬*I^Ï“s"›‹îzûõzÉúÈ?sÅK®Xè’¨stb|Chq	Ë{SŒÇÓ¥:ØËd°İ=öz9Aª¿Ä_JoJwWğoZ¼R]eá³Ÿ2j¨¯Vp—úàŞp×8à¨¯Up×ÅXJİ6p³†Ìë=nz[€İàrÓe!71Só
÷&÷Q¼#­ofkç¹ŸúËé£à³ÅYx6‹¿àÖçßû¹•¿àˆ¸ŸpDÜOëˆ¸C;¼Ógßw¥§»ºeß»•}¯ ûŞ£­ï5ì{E’}QíhïÓê÷KuİÑ>Àï1—Ïè¡ÁƒÚÉ•vwñÇw±ï	–›©ÁÔ]éî.¸­yD;|Ôéğ1Ó!S?OÅ+Õì4\õ©‚§ÒÚ2l ×®¯²]?Ñ]×ïK×OF]_ßØ<¥]?ãnıˆÏxLòÀ~Öe’«C&¡‰÷œ‚~^@w·0^`ÛAõ×øœü¡À}ÑàL °—ØË>ããw­î#÷ªNîğ)¸×Í°“Ö\“8y4[{Ìœ{ƒ°¢£Ä7u"®#£½¥`ß6Œv¯Şñè÷± ö®K?ÔwôÁ{
ì};5=ì»ÌÛP²%üÀAªêCEíz¢ö‘BûØ v½Ú'jŸjŸº¨¡¾ci~¦À>`¡6ùTš}Áf	mò¥¢rQùJ[mP¹!¹Qi“o´ú·R½®aXš¡Ç¹u`ƒ{Ì†
§8ÑÈYH¼Ô††Û'{íNòI™dŒö„9k!ªçÂ`›ĞŒ“Ô=r±l˜[„‰yW-vf"Y€‰”ÅYƒöHÁ }¸\x#M"=‡ìˆM¼. ä·pqÇWÑ0Q»D5ğ,á6c³dd~ “Ùókù&æwœ%O+~&sú=Ë{ÓŠ7Æµâ:i?ÚõÚİşî']°7ùöséñçØ‚ıEáıÚã‚mîyÁşÏ_°¿)+ŞLVü]ÁşaXñfUüé­Š/±¿ÜUúÎªø[ıã¯Š/¥Ù¿İ®Šÿ•[ˆJ?­ûãƒ‘[’«EÑª Õç‘êuó›ÜéşÃ’âŞãfJ öRD7LÉ.$qì’˜-|W3B¸©¯¬Ñ†'†íûÙš¿(r;†Ï-ë¹2ÖŒ½Î£e9´¯˜«š[ûğ2>Œ?‰…·~ÿ"BßÄÍÑ"O—]K¸¬ÅF”Äó‚$>%S0Ë{câ[]&¦–˜_i¼€ĞØe‘\“E†…6Ô‚„
Ã¯¥Ï…Xfô·yêq _X€»‡
‘©·[ª¿İ_ ßäAü›Ã|‹*¸Á.Äâ[©»ë&Dòâ,\™o	m½¤a¾;’Ì‡¢ˆù–ÒêKæûFb«(°ß5a›ûşèh/|åœ"Gùè£ÆE´(q,Ò>ˆ«ğùíVÄ&˜gÚ™òÊ.ğÑ˜ ï‡ÕCù¼<Z½ÖjÙö:†ç‰ı……"[ûŸ2yÿáŞÓü#G¤÷–I°ØwBèeûb±;ãgÈË)%—JÊò]şò÷x…h¶³4‰RàÎµéJÒÔ;C–{-ÁÊl!ßcÏW‘údïU@Ê²7„‘ºœõœwtF2Ié“OÙf10V#LcûÀ•5DYè^²Ğê
mÃB÷ú¢tMoqü ƒZË]¨ïØ>k+°‹šqçŸV æJíQPúPôzô}”^WAóÊOÒl½nJZGy?G¹¾¶nFyr¡ (ÚJŒĞê#¥ºn%Fñ{òôx´vò€µç7àïøVâgÁrCÃ`–â§Çi‡K‡ñÙ/Ò|6wOìñô¸–UÓãMù[O7ÃWœoÎlÚ¶à'6mcği7muŠËXŸÒ¿
ã,¥“§Çã•‘Ü[*ˆ­¹J’E‘\ÚZ«o#Õëæ€]Ôû®aÜz°§úÎ<»¢7—õ"˜‘`0&SlGrÄ¥²¶ŞS¶/`ãÕËlÀ{=š½†~ºŠ5Ñ†—x.ÂDHH4&˜ÀAy–Õÿ„YŞ›Rz8~¸­q’ã×"{€ÃRF‡ë¡Q*ŸÉ„ûïàHZòÖ,£™Ím¥Äo+ÃZ%2ÕQêöæšX¥JSš¼©÷‚®cyWíä«­æÇB<)jÙ¯f2ÏıXBó6^Æ	ÉŒ?§ƒí„üMYß!‰r²rŠ!$½TSbùÙ‡™¡º4Ë¥&<$™8ŒïÊ•¡#3eZå9ZCL¤›*´1–]22…‡Ì]ÌoKĞübÆp4Ô³Øt°}b°¿Ë`wèk°ÆõÌ:Ø©2XÑ3ùzæ<Íˆ7Vi'mº³4=CEQÍ·ÏhìÂ¡’yÂ*ŞëQ%³«¶ŞM
"Š àÆ«f£Óİ	*´\ş|ö`™µŸôäøt¼§/]ş’f3¬tñ‚öRÁòKF[7ÁòTR° (’ãMZ½Yª«Ïò{R·h'O[9ŞÊßq9ş·`™3ÄÆd<—ãyípoé0.Çÿ‘æ3ÙÜ•ãÏô(Ç¬êÈñ6şV9^ÄWÈñK ÇÛù	9^Æ§•ãâRñ)ı¯ Qµ”NÊñ¥Ä³$÷,ÑiÈıl’Ü(Šäøl­Ş%Õëîe-9š˜á‘‹Æq„7µj28Ø~Í\µçMÅY¸–Šôur#Uj‹îÜòÀI6*9êåg¾éY¼×«k×92mlX§‰Kdò;¼:&Ôã¡.·Py<cŒlÿé`ÒÂÿÿ	ùöeyoâÿ¹¸ÔÚOI³¿!_[˜X¥05wB»¡‡æ9¢uPòˆf!xRVÂ_ôf<&3CC“èk\ÈßÁ´)ª¡¯PÉQÓtaƒ×‡”¤æbg:8 A€~‹’ öE€çã8H	p°!À¥  ´¯½\Ká»¡c¦I.'GÜ£!ôÙ–¶ ’(µn. ‰jgÖ¨K8T“aú3Î]+ó›Éeo‰A²x–‰İÊŞ§4êş£%èàcX‡$HĞ_Hph_$x!.ÌS.$aş¢/Ìà9F¾¸Â|®6=Bšz›9fd›P¿låùQRŸòühpŒø§6çl¸#>–ÀB‰> uË¬DÅ?¦SĞ'XĞÔ‚Uøê5¯X‚šŒ,ƒ…FOôú™Wú9ÉíçUOsœ¬ıœ"ı„èÍ'ÍNe³ÄVù4–®Mn0jë3¤u-ÊFQi3µúYR]5ÇÙüÔçh'¯[Íq.Ç5Çü‚åyff1ó¯Ç5ÇùÚáÒa\s, Í/dsWs¼Ñ£æ¸ˆUÍq1«æ¸_¡9.e	4Çeü„æ¸ŸVs\¡¸\éSzAAâ*Ké¤æ¸Z)ñ&É}‚¸ÖûÍ$¹Qië´úõR½®ácsÑªg #ú¼\Jä}é’câÜÅZÇú­ò5â<DW”a„(È<¢PÂëêt©âi&XœÁ¥Rª=Ğ×ûs&ÕLpä‰ÿ…„7²¼7ñÿVÜ%u“ïf_´üxLT,ÉÉºî.Å[ØSÈë¥÷[Yf—âÛsê6íævéÆ8§t)†çw°õ úw|çÔÂùNÃŸ6âõ.w·ÁZ[Ì<#yX§ÃˆLF#1÷”=mÜ«¬ñ.Yã>…z¿aw}ÃŞˆ¼tGŒúÇá!ö°‡b‘“Ú&y(¢’Å#’ø·<âõ7Hú{Ôíï=O=¦ı=î/E¥Ùvixæë“:ô÷9ô§´õÓfèï'WŠ¢UñŒVÖ¬ŠK€>òÇâ] R§ZÍ%îpù¡ZKpÅ¥æI•'‡ò¸¢)O\ã4Ã<€¸+2ÏÚ,©íÈ*h1 şå½Fl$™tVvÁ’è„¯â•s\¢“7ÚN òÅo<\ 	jÍu%d4å«šÈSû\bİ=ß×ºù n5¼ xÑP`kšMv!óU-û`V-_¡×hø¤+Ä£g•7v ¶şÀtğRÇÅÇ—ûÂñÃ8¯(¯—6.}ó»ììyñHr®ê«§4n*z\Ö>JÛÍ>ŸØÉµµ$ï‹ËĞ‰šaæ%6fH,´ÓÈ»ñˆ6`É>BàFf‘zîÛT>0|tañ1´·Ğ¡X8àbºI¹dôÂ=v:x-AòÅ…ä¯÷Eòâ$CIş¦!ù9[Œv—kp¼µk5‚ìÍõV¾L€IKnæw¥gvÿ@+
OÚ w¨‰ÆÙ<r’gÍŞ{Š­!V†{‹Š<É*yu¼¼+F«1fÉˆÔ#!o€šµ+8Bx¾)g.‰ºãê‡Ó¡5+ş½â¬IŒäÊvÈÏ)0¥|›<Çƒ8x½Ô‡šyG6t!°•wa¶4æ0ı8ü1©Œxx“ŞJLŞ2yo÷5yÇÍàwtòŞ•É3øß^R ¿GÀ±;ÎïkÓ¤©˜Á´BèÓ¨tTÚ‘’§T>d»ĞşÌšÂI†m|¬@>‘5í>å÷s¶|¦"üskâ}Îßqo)Áúƒ5Fõy<hãKíø+é˜TPÎ„Iœ-å^âÙ¾&äH£~£8}Aµò­şN ×¢Ì»
ı=k†6ÄÒ‚æ,³6ê;õGö“ÁÒÆ³-\İç‘Bågü2şü—ıUÁÿOÀ‡X-+Í~c³„ÿ»ô+ômı§éWIŠ¢ÈŠÿK«ÿíLõ?fªci_şÕN¾¶Sü_wS¼œ`Ù“dn}·âûãoèp >’VüòÒ|6w­øoz´âçeUÇŠŸ¿ÕŠŸ_aÅ/ÀXñòVüBø´Vü@ÅeaÁ%¤ô
‚Ä"¬OJ'­øAüÓàúoIîEÄ`Q‹²Ä¦	E‘½²˜V_\ª×5ĞÇ-¯M…÷T5Y2Ş•¼BÂ B›$<ÏÃ•SÖŠåc¤J§¦èké,*B=V49Üã8X¤;šáŠ"Ó!TÏŸ ‡œs:zÜ÷(¡
]6úƒŞ±’ÿA^ÿSQòe
pŞ"ò{U5‚·ŸÒÁ¤œ·]XQˆ½$Ë{Û.|×oK)!—6„¼GÍÈvĞìeæì ‰g¸“	A‘ËºÉäd7v|šNÁ4^#ó–†½mã2uÖÚèk’º0÷˜6Ùk˜7RŒàn°XO ;#aôÂ=„HË$(³’PfÙ¾(ó}œ2Ë)e–7”Í?©®Ã³\—¾ğxBG£—½w@xó^¡ML–'iÌHB›ÜOC`ù2÷i¯Ár§±]r¯ 7€áá€Òã,ÂŠ„ù˜V4ŞÃÓ¥&˜ØTºv"ìcöMwšİœÌ‡î2Ç	VH{e!öŠ}û‡¸¦^I‰½²[4õ¾¦^E ¯b¢ë°ZU›¦¤©hj^º¢¦Fè½}ì%X-C]ı³ÕÕC¤İV«+˜5¤ Û4gMÑû˜kZ(èVÜÖb™Ut¿ø‡Õ
»ÆÀ®‘¤fšç,ÔÇ,2yÎü'™dï8Ôë0%®ãvø«„­“C<W“fë±YBõ¥Y:¸şr„­­‡KëZ”%d1Šœ#l­>Rª›#l~ïæ[;ù-<Âæï¸u3D°ÜĞÌ48á·Ä¶v¸±tw`­.Í7asWõıŞó6«ºGØüm°ñ•GØ,á6?y„Ïğ[qëSzAbœ¥t7GØJ‰?ä[AleÈıG’Ü(r°µú6R½®‚¨ê±[ ÍmfNy!+lÊD¤<€1y.!LÄsy²¸Zd'•)bÏ-8_™ÎCØ©nm2¹EfG/4=$}°1WêC0{E
BÊ
ã+Ç	î]ÚùLkàùÄ&l'P¦[Sh;‘å½iº?ã±m•n“„n}-ğí>\8kI—õ,³ü/Ï6YaOØğ†9ë;t‡mÏæƒêÿöİakè·[®ÚQáMõ¹ªFêN³\E;¹8f¨”ğÖq°“2Õ?dªÂ.†©şI2Š¢5Ì@TßUªëŞß“w´Ul5mÀ;Ú»k‡ÿÚõ¼Ç×óPÁzº!(ğ¯»yG{Oí|†áè0.¾’®kİšÆˆ+Ó¹íDe™leö¥ù(ó7ãP!ŒŞ•½¶ÆÂ£w„ÆòÖ6sŞÈaW¾î¾4*Ï@!)o³÷á¥u=.#|LOåõÆItV(Q’b:1Él:Ø+ÁÇë]2}ñññ+ÎJ­&gªšÍTõpÅ9«ÓÔoÀ¶w-²`nnĞÒİ4­+è´FÓÔo ¥â*¹ªõÑæ´ã¼Y@.—{W»ÕbÁŞ„]F©8õ ^-(à6Ã«ıx›Ê"k†Kq˜ Yb™]Š¨ïl*ÛX9Ä2~×°®YÜ®›¸nVQÇª‚í08ğqœåá¸àØéâˆú³X—ÁÑn|“·nöñà¦î¾.ÜyB¸LàµŸÂİ_à†$[_šÀf	µ q^ñ m}°â¼vˆ²İŒ6Š"=tˆV?Tª×5,ç|l•â™Õî“íãê_”»—™y\âÅ»¹…ùVKèoƒ¦Ò§º:3È¹orQã³Ğ®íN+IX½Üù¢ºÃj­V
ÓQiÎªøUPyö¥ûK£Ì$dI­¦_Ç!İPràIz2Aõâ,É'Â·Å#ÎmO…OAèóÆ6‰¿zÑl->8“ÚZY  œŒ˜H~6¹´ŒÒ¶7buSeóÒG}ÜtZ‘u¿)÷’vÉæY––bp¯`Ìİë˜˜oˆYF'¥ƒÃÈVÖ.Lx8Ë{ÓÚóÈMšì.•9ÊescKE¯mÃÕ‰ë´4GFDoÒá­™Òï‘îš™ß[‹GiG‡ò"Òİİ%VˆIŒc‰p×cu9-Àåtœ>Ş,§|‰q‚‡åHÁòDKÔw$ÆI
ìäË¸T#Ö&÷CÅSG
NU$Š§)ÔÓŠú(á¡8JP<ÓEõŠ¼òw–;[€Å­òÑÒú¶v¯ü-4 qåï\Ö	¯üÇ_0½Ïç'Lïği¤µÃ‹¤ÃPÚm =]Ìú	iw‰} Ç~©¶¾ÌŒ}`RÚ¡(’v—kõ+¤z]bsô‘ñcGW‡ä¨Åp¦XÊîs$æyª¸üÓò\XÌÿ‰<ûğ¯ç‹x^…0<P"%5¼8"dåè$&¼k2ßËã„À+Ï×¬ÌK3—!JìÏËÆŸo §
Élähwón¶ÄµZ>+}%ië-ùe&®byoK~awÉÓ¼ZI}!õbt¼¨É5.Å´xmê+qPˆïA˜œ¦ËÒ/ôEO Ú(˜(yj°~2Ãñz—Ÿ»:ÿä¤SØ4Ã_¸çÂğáNÛßóImƒÉ‹¦
Â:ºˆ> 	½Ğ–)ÒÆDL® Îw!P™ÑÓóš
 \› öFBíëú¢ö".µ¹l¯WjßĞí²İX€Ş_¶ƒ’Ëö&oÙŞl–í-fÙŞj–-/jŞ¦Ş.z{¥è^Ël7¨~Q1AÃ¥½‰`s'ÿæÜˆ¾KáİmáYÉn¼îQ`ƒ}`µì^½@÷)°ûX´ILZf°aˆÙ¦ìA–Y«t1Ï2{Há>,pÃf›I³GØ,!«eéàúÅ)«ÓÖKëZ”%2(Š6sOhõ'¥ºnæâwlæz¼-ü´v·„İ#<Ãßñ­Üæ‚ï³†f éñ=ÂsÚõó†~İxº¼Œşİxº^ğ»…ôø¢KØ%=Åø’vørlÂxÜ&Üv¯x°ÇìW]ØKy“öšÂ~İŸ´:iöF·“ö¦RqiNÚ[Úúm3iK''E‘‚yG«¿+Õë.gÆ¶]Ùşo’¡ÀcŠeyUJßƒAÜàÔNEGÊP#1·%=Ì©&¦7¿İ¹sBOŞÏFvÈ€)ôì»ÈæMÉ<3™It'ÏŞñˆv‡f¡OïqÔè+4zŸå½‰şe\aDÙğáC!B~”uPı²şr'=~lX“&…Û'
ïS·IÆK“ÏØÄµI–K
·ÏY'´I¾à/Ø$_ò6ÉWø´{ä¯µÃobì˜”ßz¬¸¥ òËŠË{¬ø½ÂıÁgÅ­¤Ùİ²âOÊŠ+ÖÖ¿V\!ÉŠ(ŠäÇ¯ZıR]åÇoüŞó±õïÚÙŠVzüÁßqé±µ`û§™"LáŠqéñ—vüwŒz<@mË2•#ÒÔÂãà<n#ĞÿuI¸’gŸş§ÀûA4$ya‚´î¿y¼°r’°NÈóğxa^~‚æÃ§å…ùñ. ò>±³èEb”D`!ş\¿
§s ^X ×¢Ìó—,Âš¡Š™(Ä2«™PßÙY,ªÀ‡X†—üşÛŸÅ$‘N`qErU"¹„Â]Ò ¹ªäR’Û
’K»H¢¾swu¶¬ Ç6Iš-Çf	õ¹¼¢’"*+hë*©$û£(’Ä+iõ•¥z]íOMãFûO]íNVñæé‚ğ£ˆSù/68ú“³[|âÉ9F–ŞL€x7µØ‹±'	Å}	{|Ski]üŒÌQ_H.‹7m=c±CrRZE„œDØ˜gÖİsRq=òæ“¸|qA[ÃjàmÃ]ˆøT%¸_& CBÆŸV!y=‘¿LÆª,ïMä¯·öSJíÕµ·3‘‡o(ãdôn§·êÕ‚èÑu :SäbwFx¼<ƒ}ÁÂ›A„à¦õ‚éê}a:$éŠéšÓ%S*Éæ’<Ø@GÌ˜!ÁZ‰'K‡k÷Õáêñk´Ã¡¦Ã¢’†.$“¹L¦EŞŠüÜİ16An—DD“§ÏX½mâa] ±ºpÈëtpvóv}B Ş:‰±L‘±¬Û×XÖˆe˜e=3zªaŞğVäì'òÜı¥ım/ı­ßWkºım…5\û!ıÉòZrSœÍÄx$ÇB¿FiÓÑÒÔ»!¯Ç°Mx”\#JlíéÁ†RŸa_)€¥@õç&üŞ³ş¬%ÈÁõC­şÜ”¿ãúsGÁx3ƒ1F44®?7×·»ûŠ3KÔr¢<†ÀCù:U:¬c™Õëxºc¬ö7ÎôgıØøÙÏ^õˆnï÷`OØ[º°×õDşV
{k¢´“4Û†Í"‚qEşDm½­´®EYbÇ„¢Èâ™¤Õ·sf¬ŞÌX,zk²v²©)İÍÔÎ‚åöÑL­çÎÓ´Ã¥Ã¸aº‹4ŸÊæîvšÆÈb -ÍA,G*ÓÁ<‚XèÁ4Vu°wâo=ÂŞ_q„½K`§0¿í”]ñiıh»).»û”n$ö°”NaOWJ¬Orï© fr¯Ÿ$7Š"»—VÏHu$ìá64Œç;ö*¿%İG­28`4²Æ^ü5úO_W Cï¿Kx¹ª­@bÆ±VÇÄÒST»ÊÀšXŞ›¢—`ÍŠtÖ ı*ÆıAy|‹qIrö7G@G>e$œÖ¦PÆMç¼Ä,éi…¼b^Ç»îıÇôŞîö’Íˆbâ}×‰¢g‰%IÄÌx
É^Â”€4«$"@j¦G¢õÇ-	’í&$kí‹d#â$Ë)Éò†dgƒdÓ€ŒÃ„OM…÷w¨$Å¦=ÿ-§ƒwoÍJ|Í¸ğÔ»§lâÜ­¹bM ¹DWÑ™JÒàv'¼©pªíøî2ğ™}|d|àx›8Ÿ“Kİ¹ÇÊ<Ñ²ñWã&N™Š·_Áº&6Ë¹6©Fg˜[C¼$¼ùFqüX‰.“P~L¹—¤gç’ÖjÔºy#|é¾IÒ}ÔF:(&±‡¢Ô!FÅÕp»¢,„5<ÚWÃÓp@À15\Ñ¦Ui*j˜²q]8,kÍˆMAˆJĞÁ¦¡6ŞĞjãYÒŒ.½N…3[
àÒsnÅï…÷»4T:{
û°ÌêÁ<=¸¯v±ŸíÂ$#¡êÀ\à=Ò¦¬ó¢Õşğü øÆ"<P$ÀCœö’f³YBÂÒÁõ›P2ª­“Öµ(K(BEŠğp­>Gª«é2—ß“±\Gh'µVÉßq“%#Xef³_W„Gk‡ÇH‡qEØ(ÍesWnÚ£"<UEx<«"<_¡Od	áIü„"<ŸV¢¸œêSºI8ÍR:©OWJlFrŸ¡ Î4äŞ,InEŠğ,­~¶T¯k¸ÌHs¡‡ z{ƒ6ôv¼Sœ]OÂ¸˜wDcBîiÂ·#›½‚’NÕ##¹x¥$wºó-Ü/rg­¢(XÌä4Ò‡Š%"·…iç¸¥`tî½·H\Ö9´§W›…Nç²¼7½ºyÜçwÒà|¡{“0:¸€@Õoá»ü²Òá…†¹¬×å"w±€3Ë]n>„îø¼œE`y	Á„««E@_Ê2»âÇx+ş2íårÛ‹YñI?ßÜV{¥·Î[ìW)Ü«}ÌI³k,r aĞ×µÊ}cÉ}×iëë÷MrŠ"î»A«ßh¸oŠ‰»ÒlÖ_a3±9—õq¨U0VñKµËDó&óÌ^i¿)Á&yËÍ}±É¸8›Ü¢ÈŞê²‰ÎkxĞs›²ÉxŸMö–owØ„ø
îN—;3¥É]lâz†·LzïfĞxA¸ÜËO—ûğiùò~íğÇPG„¯F/2=è±MAğyÈe›­<¶yX?â³M›4{´[¶yLÙfk²ÍãÚú	Ã6['ÙE‘xR«?%ÕUG<Íï‘>4xF;ÙÆêˆgù;®#Š‚åsf~0ÛÄ·µÏk‡/ôFºhŸù¢Gº’@É%İt/+ğW|ÒµK³W»%İk:ª‰$İëÚúCº‰IÒ¡("İ›Zı-‡to'H7<½ÑĞàíd[Kºw»#]Y°|/"İ¶.éx–ş¾vøtX×ğ¸mœ¤2×ÑÇrÀ‚5©=$½q[¢3àÆ;¯‘ªAno(·§Ü-AC&+“9¢×œ´—paÑFKšĞ	T©~áÃx0Î¾B-¹l.%È`Ú®„@á±£ùu‡åª²tğ!éá©¦@èôË{SM“âÖëÇJ½O„zb½nç[¯ü©™ ÷VÂgÚôsiê9‘¦á°?|Á6¡Ù:Ùš­_J}š­_)€¯-ÓSèãîePbö=qÈ´”#÷É—o6ºº÷­rÑ²êw
ğ{ÃªS|‡üŞª©Ê¸~tWê;§?)°Ÿ-v±Ì€æ’~.oyµ=øÅÁqR¿*^Û¯ÿ)¨ß^ÛûxıîáÕ!xıáâ…úÎAÁŸ
ì/ªóYÒìo6KËÿ(*;•µõ•’«E‘şìáêıñÁÅ5Vvyx ’×Ã'âÙL	6'CdÚ‡àaàŒÜÓÕÓUO©æ›fâu…ì˜`  ùÜÛ)ØÏÃòŞ¸wÇø&t^Eo¾ÿãì*à¬*¾?
ŠØ+ °’Æ*’* ‹(&n¼Øòî.awwwwwwwwww·ÿï÷{fî½sïƒ÷÷÷ù(ï½ÙÉ3gÎ9sæ„›Ş˜Â—M€‡~s5TÿƒtàaÙİ2ñJLº,•ê#„‚ƒ•5*)B"FNJİ!»'Ú#q1<ñQ[öÀ]}€ı¡Ë¡çtL!Å–Góç8K\ Ô'f¸ -p!·@†òHgl5Güƒwç,æÖã*!,3x,2tĞ™Ê¼µE‰Üâg”Ø¢ÊïS™ÛO)œÒö]åQ÷Üúfk}—Zß¤,ùYÄÖ×Cëù™’Ÿ=Ôñ¢ì8syîiMSÓàòœrŠÂƒ›ÆTh{O…–P3ª²—´~–Rñú¥ù}ÎªìeØeÏÊ)q-ËßY¿§&¾œ›86%Ëó—·WĞÀ¡·F^µ¼";ŠOû^ê|%–yá}‡€x­l}¯âûÎ{cÅoÌ«=ï­ËÒ=ïŸÕ¬ç^ê9Ğ>j¶:›åÈÏ®H~Ö´Ök©uÊrwu%ÂDo«Ş'µ7}İŞà£ËÖ´!ë3 |pßhmdg¿'ëÛ“}5Ë~Éìœ½«÷·Ë5`VfŞOÍ×eóô]}—9ŞÕ°jê®>¿í®>_qWÌˆÓCø	qz(>ı]}=›Ëú!¤÷×$6ğÎßÕ74HìJpWX9pïš7Šj¿±U¦ê#¦¬†gaxÊÒÂ³läÀ”ı¬Ş^„>²
!ÚkÏªí HÌ+áf}¢ŸIMtÍ›_–ƒÈÔyÂq¤Fƒ¯±–-Û½ÁBt«ÿØC˜ˆKTÕ…Ø;Ò\±äô¢ İ¨wÖîÛ©¦é /n ¸ı2à™-ƒËåë"­ØIfÁêt‰,6!¼Yì mÑp–Ï›MÍûş‘üÛ*ö	sª1)İ°©[¥Q?_×mÖ"å]FQ÷\`ŠzÅ qJúÆz$ÎP¤ìŸøúhëŒÅS ‰-7kÀM\£‚b@9q…„l2F¨K|à½cĞÉ™ÁHo¢œ§oûôv'.¸(´|çğªêÀÑÙ=ÚVcnŠÓÇ(”Ñ-­3:Åê±µ:H´¢Ç´Œ`‹`Û†º>Kc‡ÅŞ•Û¯µ_£Kí×nYæ5ÆökSí—˜WUÈ¼RÇ›9z“–7·¦cÕ4ˆ'ZUcƒ˜eÕx–5^•É²¶°Ö[ªÀXV%¿Ï™eM0¢P¿éñw–e¬éní¦‹åÔfYÖ66ğ¶¸Dà»‰ì'f‡¨ïI,ó«ğ•ÉÖõv!µ;TÍ¶÷Ô.PM±5Õ‘Ğí`­wt„®.OèP”ğ•¬úÎ) îâ ˆ4_ÙÕ©÷€›Zp‡i–»%€«Ïò•*°ZfùÊáj^Ãæi¾Ò0G¾RËª)¾Ràoã+uø
¾RÏğ•~‚¯4âÓó•i6—é!¤Ğ$š<¤ó|¥Ù ÑHp·X­Üyp£(á+mV}wU1e0@Ìw;Ù„×â§µ!Æ@ş%ÈBñ†Œ”à—ÖÑ:<Š8ƒ€Ò©I·³|n”vZÖå¦Ã&Ô©	çâ@78~1™Áab„>JCÏd™GèéBÏ²1f‡`>ZÍöğ`Î9¸îiPn"”÷²övPnÊCE	”÷±êû:(ïãœãò>n:ª)N¶ïûˆ¥MüÅÄ½ë©6‰­áY„%2s¾¨©jC¼¿&„,€Ôî—Û°c´üıKmXsV5z€­í@­­X¥ƒØeÊ–P1z¬†;˜Kİì±Îõ»ŸÒ;4{½ÃÀ¬ŞA*ôÃ8N½FÖ °Qàx5;j(p´¡@›<¬¬‡c
´åQ E	
gÕw(0(¾.ú$;Ê1aòKÓ×2§*İ‰9¤ŸÛ¶4åKmÛîÙm;Éæs²ß¶4¤cö)¶uQ¸u'jÈS3[wšuxºß:÷(±0ŸMãl$‰ùŒ`¿NR—g¦÷«=Ø¯³¬÷³Ãı:YÍÎñûğ sm¯:¸WçYëóİ^uä÷
EÉ^]`Õ/t{µ–0Á™GZ2¼{EŠ)&¿lŞÑqV!¬Áü‚:îĞ™f"	{¦°[Õ+Ú‹ö[˜0­ux±¿(·ó§hñ—ÚùÎ¬,{‰­îR·ºZ{ös‘í¨ó”«¥'şÎ¼Ó]‘s	£pè”¡Ît¹hĞW×XO¹“¹ùÈvDP/ä\–[Á©ZÁå¥V0#Ë#®°\™A5(Î’lºñ%úª ÑNÓW§mf€h×Xß×†ˆvºš]WÑ®7D›ED»ÁZßèmVÑP” ÚMVıf·“¸­¸‡54âÖ`‰b´îSOvÈÇü¾‰!‰mÊ£[r ?CºµèggëÛlÆ·kÆ¬÷ë3Õñì8£ºÓšŞ¥¦¬y^¨’èn6‰Eë½¼h}ªS'}¯µ¿ïÿµë÷»~–&õ@z×÷Ÿ°¬ï‡Â]?[Í.ºëØ®ï£',kı˜Ûõ}ò»¢Ô–UBÕİ¿çÍ²AöŸ°ø;{78G³|ÆA;²oVÄ}Ö|NfEÜsÕüy6O‹¸ûÍQÄ}US"î‹üm"îKø
÷e–@Ä}…Ÿq_Å§q_³¹¼Bú<Mâé¼ˆû¦Ab‚û-ëâmîıóàFQrÈŞ±êïªúˆ)¥ÇV	ÿX{‘2SP5º8Šz)d²eşè`ÈW½å$5‹VÅÀ™ôì—Ô¦k.‘ÚØ¶s¡µ0 ³ıå‡Õ'æmm`¯‘ÌVR˜SŒ¥×|UÚàµŒVòî}Ëçˆ¶Hš1).©8¿­Å#_\şÛ¥‡ifÜNQøFj~ 7ÇCù{„n ¾Ÿ¯yŸåsßÈ2—Ø:`oä%í5´r3(Ã:Dbp!ÄÛŸ >½Ğæ"¾:§1™“é 3¤Ì9Ù-b4Ø7]UJ¶µx
¨iê$»ŒĞZ-j0ª6ëıĞé$BÛ)µ£…~fœ‚ğ¯2dÁxò ø9å¸â:a’|¤ıaèD{a}¿§¸R)m0ôoÈHnFi‘ÌÎiøQnc.ĞÆ|\jcÌnÌ'¶1Ÿº9G\¿ª:gì<¥öñ;ı›)ñÈ[<’¡_5<xé<ì»²¨3)µ.¶ßÒAÆù'ÓÑ7¢Ïrk¿Pkÿ¼ÔÚJ¯æ_ØÚ¿,Jÿ.R§_‰ş¦h#'"zpŞÜâë˜ğ1ğ7È}ëˆÜw)"÷½øCHä.ÖH?z"H«?};„ôígkı‹£o‡äéŠúö«UÿÍíl?z¬'¡n±. ÍšM¤ Ñ)ˆiqà¨V…®94´Ã…Yp¯T†PY¸"x‘ÅÌæWÖSS¦gÁfŠ|”Ê°è+T”Q#ÎaÔÁıtÌœzØ½é3'É4ØY»b‹¬¸5MucùÙäNh&à2¤@ÂÓ)%[zGn}’z”ŒâŒlcÅ3,#›0ãª¹ôX„ìßsxv‰6êRxvhöŒıi;ñ—Û‰;e
'àÂ0p@<ğA]®¢ñ8ìÅÛg˜ò‘©¶‘ÉvŠT(ĞJ+x—T¾p³	PöÀˆjjZ9ödyÆ±—…¨~¶²ŠLnI©ûµ©şuT‘.%OéÁÛ8ß<ùÜ€Z¯£†Xxèó9¿˜äPÎ«¼ll¨İ#¨”áá<é%Ÿ1\§H¶¡ö&½®õ)kƒ¶
ihˆqE¥r@¥ 
Ñß¹ı¼TûùO©ı<,K7şµıì‚;l^nºLÎƒ¿tãğ"N›¬“8mò6ùI§M|ÆN›øĞ€¡×;P'ù<Ù>Öy]®Ù,Ä2¯ó:"p»[×«ë¸Ùj¶›å{°´gå‘$I‹Zëj]²Üã ŠRr­úâªn–¥|¾‡ï!\¼,Ä‘üæ¸dÃ`êÜÕYmM­	ª‰&vörË0Ã©!B³®—òğ\˜ß-xØÄÅI‚ÉUšfŸË–şæ"¥-ÁE’Ğ•Ñ’,Ÿ›$tTö’º”Á`éÌ^¿¤.læUrÙôflærÖ÷òáf^­f+İÌm3áf®d­Wv›yL~3Q”læ*V}U·™a3'·yÙ
3æşÿe–qÛ)y*Il˜eQ¦½jJ‘¾®¬Ú,†ùJHäp¦<*ËmÕ5Àj¥¶êØ,İîe+\İ­pĞmg§Æè+²P›S´¿83CzŠüf~Z”aÿ¼ë„èç&7ÓÙµ2äX<ö‰8®ê„+$ub¯fû
7`hşÛFùÆL‘T¦f:Áéˆ¹iu¡Ö¢™£Š¶8ÉW1ôi±‚¡ef»Fn#®ÕF¬Yj#ËjÖ²è­váøP»p:îÃ3Ú…¾Ötm5LŞ”36Z‡mbõÂ‰^½ĞOõ©^èo”9¯y›uƒóz½f5 }^O
l>Zßƒ|ßyƒµŒ)TÚƒƒAnĞ CÒƒœ…¡6Èz!Q¸QÍÖ/J60¢p
‰Â†ÖºÂ…SòDE‰c#«¾±ª›c¿çu›Ø §zÆpşÎê0nÒ,G¸}Å¾ŸšÕaŒ´GiÀ¬ãf5ÍæiÆisÔaŒaÕ”cSş6Æfø
Ææ,›ËO°éqøô:Œñ6—-BHß¢Ilé!×aT$N'¸'X[9pŸ7Š¼µUßFÕGL©q®|[§®¶
LUg”—³GĞ,Déf<ÛæÙLg!á«š«¡EØ:ÈŞ¸ãÔW#!Ì¢zÜ¬÷ 7TgkQmËÜğV-r"ËçÆÏHŸl¾‹O²LNáËvÅñe{ƒÒ™_¦Ã—Û4|93û¾£¸“E)DÚ‡^dÈú±(µ3û‰e¢ÛÕ÷.,ó¢ÔYñAcœ˜]­ë©êÚùŒXbêøád7¶îQyvøpr‡z®r³öB_µuWãgº86—¦:p«›Z×TÕŞ@wxö<…q›•Ôoª«@2QÌşNQHÏşœ€LÔÙpõ!òŞ¥fyƒ»i£íÈ¹ÄÛiÖzºÃÛsóx‹¢o›¬z³ÃÛë±€^z_¦ÊiiŒ­Œ3†™ÇÂ-‹“<BiøÉÀ4u.z0hG((2%Sì&q¡‡RÓ¹ü/Àyæ‘¦‡ÜÔİ‚š”àÀÄPÆğÁ'yŒ9ìşR]¨ol¡®	qZr§ànA«µÔ)8/+¶8vÏ %®Å\õ¢`cïÑ˜íé=?ØØë¼3ÜØ{ÕlFÑi{7v–µí6ö‚üÆ¢(ÙØ=¬úncë¸±Û*ÜGŞÀSÁ]Q©$p)’”Ê):%ÆéíkXŞB˜ö%ÉÃÔ÷ÑÆÖN†¦ƒóm¡€W¤^Ñ^¹İ¸OKÜ»Ôn\˜ûö±5ìëÖ°+[»Ç)U©üu7â:Úyáö÷RHd!‚qÿÎ…ÊÈHZš6¿“Gx<ùh¿ÜÜï×Ü÷/5÷‹²˜t€ÍıÀb˜ÔT€hÖ¸ƒLz@cœÆ¤‹L:Ä:?4Ä¤Õì°¢˜t¸aÒ%Ä¤#¬õ‘“.ÉcŠL:ÊªívaebÒD	ĞÂISãBÅŠˆ½¢cr@|H3;¶/Íñ8úøó~t'ğ{XÃ˜†ßeƒ8Éú=Yı‚AüWŠ~
»îQyyÈ=Ñ°§òo)ŸƒÓl¬ÓÃ½zTuÏ(ºWgÚ^]Á½:ËZŸíöêŠü^¡(Ù«s¬ú¹n¯2OÇˆ•|é±	cü¾@¢ãHPqsâ1„dœ¡ù»e¼´ƒÏ#ÕÜA¿)øs^nËÓÏ/µåWfU:Ø
.Ô
²bäãêô"všV_•Wé\Ì:±Jçş‚¬x)?!+^†OÏİ/·¯ğ8öÿı¯î	Íëª4Â]Ø«mkB$xRÍ®-Š×\C$¸ŞZßààš< (A‚­úM	~¥1“#ƒÈ(Bg%ÁF:D
Ã	U¶SfeR‚š&Ú¢/Øcâ=ƒôS ÀœWXÁ'•r(*;›ÊödÛaƒîMUÕ2nµø~6–4ºµ,–R»?8‰BL0Ë]€~ğ\vÉšùfn!±¡epŠriˆ8‹ØÕÉ¦:¾9‡—O	æ·”ÂËk³¤èVêmMœõ%¾š<Şşpo’ĞÜ ÈÓ÷4Š\Ğ¤;m€»4@q¡õn¶îQy}HvQÏ÷ğo)C­{­»ûü|ÿ+‰»?˜ı³ãôìoÂç=hÃ=¤á²Çö9µ~˜­ÓÇöÆü±}„uâcû(áØ>ÆOÛÇñé¯xOØ€O†'êyôTÑõ´¨›x¢±ÖÏºuSşD¡(9QÏYõçİ‰ºÕ³@ƒÌ&C&µú'Ğ*&/dp4¤<Ò:¥;œ¥Æ¹Wæ
d¼ä!p§·(g:¶/~öpiï˜.±%ŞĞ]»2£êµ`¶Ó•Ò×_ùÁæÖ…±J×ZÄCĞ.Ôs~!w"^Ì^,u"nÎˆ—(/gN%£ªÄéö• ™^Ô€¯¦‘é–à(¼f=¿îÂÅİ7ìœÜ“—4ì›©sÂ¤oÙXo‡xô²ê¾SŞ5<ºxôµ~ßáÑmy<BQ‚GXõí(—@l˜Wß1µ|;ÄSsÔ€H­dóH£Fzk	y3·÷FM“l¥Q ¤k¹sô6ÛêW´¬Kmõí¹·i›÷§nŞíÄˆzT'Ùğ ğä\¨Ó7m³›#ÊÊé£ã!kÆÂ‹×’v¬iµp„â&J/ŒÊÊ•ˆ÷YnA¯jAŸ—ZĞÙ}aúÒ-h-»ö¶ê:>o®ÌÚ™iH]LêóóUn¯i_—šÃÙ9|csøÖÍ6Ç£-]79‘©ä-ï*­ËÜL ¬Bíğ²ñ2pa7£	Ëd¸Vpi(Ôk?“×eyœT¶<ú.·¶×µ¶ïK­í®,møÁÖöc†6ğíÆ«44¾ıü‡74æÏiòpw ¬ıÅ:ÿÕun1{˜®ÏŠÙS+dª×DZdPùÀc¿Şz`ô»æ{x˜ÿ°~ÿt‡ùĞÕø¯`’oj’§'‰ú)şûuö¯‡À¥a]`Ş¨¼ŞÒpó°Ì«¼îÌyñ'×©×Ã·Õ¬›å^çciÏÊû¸òù­õj]²Üë!Š2¶ U_HÕGL9	 KÃ™&ØyW„Hkz©•Sç* š†<Ì¡” ¡%iˆK¿[˜Ú€µu„ˆ¥çGŞïÛ§ƒÇù€fv^ˆü-%)—6â`w.1Ğ¾#€,Ìò¹iGïÏÕElÅ=ÜŠ×'½Ù$˜2,jEœğX Ø½H*ìŒiVãb›0“¼AÄÍMê]Mªg©I=UÙ.f“Z\“2ÿüQñí-i{ı WÙ.ÅßYÿ{šÆÒülz :E1—â‰f:ËØ€ËjÀ¬÷¾š/Çæi!ï¡¼·<ëÄBŞ
ü!oE~BÈ[	Ÿò¨È]Ù\E:™Øz¬È]•ÍzT>òú4™2·Õ[Íºë¥î•3B¶¦ãÂÀw(ĞùAIº˜ÕÙE¬yşPİ®Á2	áš6ÂZ!nö‘šõf³Ü1ìc[ó(a_k½¶ZW ,wQ”<ñ¬cÕû¥ö¿‘ıG¸rä1¿ÿëÛÿ5ËÉş?–Ş†hÒ€#¦0ÁüH(‰y•c°<gµä˜·¿
–ïí0ä—*È¨äg©èuâXfB“Ä<pwNĞô‚"ğÔ75ÖÁg¤-ß/ÙA[§îµR_8×¨:¹_‚0 Ò/Ôîq6É`D¡
æ•¾e`š¶!´Äò&w%I9
° 7q¼±H±ó9dN…ëSóó)ˆáùDÀÂò¹Ç³„g¨|=òHxÆÅ6@6çNkq1-\¯ gA–ÊFJkáKfîQU&‚goTÒÆ^Ñú¹‰ª‰oPjâOd'¾¡M¼ÂMüIN|H:^œ(biŞ™Ú|Ç#7U|WH§F°z(å7sÆz§‰™ĞN6gø"s)E5óÑÉhDÇFˆ›Q=¨ÚÊ!`Ä–„Dó7/a±SbÑ®^¦'‡É*ì‡eÓ¡€Ú(¨Ï¨KêÉ, † 6q€Z‡ŠÚšd®Nâg SXË˜PíÑÙrmROİ,›¿.ºGœíÌmQ^+.+¥ò±¬aTóÖƒYm•4>ñ†!N'¤«ıÓ&Â`vÖé¯.2ƒ§2ğ“r´íŠ8´7÷‘™™Ÿ“{…bœkLÆã÷	¡Š•GÃs[ğ¹¶`D©-x*ëj5Ò¶`”¶àPæˆ=*ŸyĞšÍGO=ÚÔÆÚLcÍ-…Ìæl³/ÕÙX–yÎóL €gıW¿YŞü•ZoÁÖiŞül7oÉ:1o®ä/ğæ	üoŞ
Ÿ^³µ¸ŒçùµFÚ–õs¬n"K{V>GV7ÉZOVë
”åXŠŒÕ1^÷vV}{U—İÉó¡İÉ7wJì›–¡éÖtG5ìN„GÑNlÛ¼èíNvV}ÚìbìšÙ1^:jêìŸ¨9¦[ö­¦´[zË^
„…*ë¸:„àwjVS‚µÁ—	Á‚µ®s|9A%ÂB½UoPuù=o2ÍyÅÓù;+,~¯Y69xc?^É
‹Í6`‹Ì"äjŞÊæi{WçhÒÆª){İùÛìA"|…=H;K€«ü®vâÓãê›ËÌÒ?j³<¤óö ³¯Ü{X{:p¿–7Š’+Ò^V}oU1Å4=.øSœ®,*è“Ò„0dYÖòÖ=ÎÒúÚ"m&\ÓHáğhN47~ÒÚöeùÜä×³Üh?›÷şnŞ_aŞã˜W¡˜õ ]çä?Ñ›3˜ZÀ*$b“Ç¡OûèÂo8D˜Â„·``Š´MÛ’4ré0¥|u–3Õ2”¼á{ÎÎ]ò dru?=Îš)ÔäËëtl¦u+ÈAògAòÀR|#Éƒ’;H¾¤K2µ6ÄZ…Ë¤$%±Ùß+="›ÓY…ñ=,<­ï!ÓµZiEÁ]³b—ØÚÖ!ˆ{”pÌ"B·‘1c9ôœ‘ÉBÓ¾ˆiŞQŞ’¿”G‡ä ö‹ vh)ˆ½™5.<Ì v¸ &"ÿVHäUÇG8¢“	r¤5=JM×E¤ù¨f“˜Æ¿ãiü1ªN¬µ?N.,¬Y™F©J%öÕVÕ¢uÇ³K§GBÈºŒT¼KRq¢uv’#ï†z¤“Y3æ—¿iI§°ÌóuÔOé‘NµÎNó3sïNòÌ¤ø$õh§]ÿ®®ÏHwı^ÀÎ´®ÏR×ñŒşP³³Ù,ÇÁÏ±U¾ÏUk­Ïs«|?OQ”ğŸó­úªnüçB~ÏóŸ‹l<ÿ¹˜¿³üçOÍò‡
@•²üçRğ2˜å?©ùålæ?Î‘ÿ\Áª)şs%ÿ¹
_Á®f	øÏ5üÿ¹Ÿÿ\gs¹>„ôßšÄÒyşs£Aâ#‚û&ëâfîòàFQî[¬ú­)pßæÀ½4Íxwê˜ĞZ[èÓKh^3pC$l¿İÆûØCşbÿG³¾3üÇY5Á]6öİ{Ä”‰ÏŞã%Å4½hÀÈÀ^–y²·Ø[È‹@’<¤êÊŞĞîİÃ)Lï_Mí^–Ïé}’•ÿï³	ß¯	z}€ö¨ü4ñ»ÀWõĞèA/â?dİ=¬îBËÆúB3İ¶^|daÛøìÍ£şe™§ŸGö1ëúñ‘æU³'<"¶OÚ~NzÊZ?ípèó<¡(‘a±êÏº}Üû˜)K ¦€o$Ôµ523£ô*m+,òQÜ…Ë°PL?aW¨³>^àzÛ¹ÙÈªŸwoù¥•GÏå¶»«–ı|©íş"Ë™_°u½èÖEÎìí#p!fb¨ÄºÀ+µ Û5ÛFØvJ«`6¼àúwç(ÆtÔ‰ÅÏ‚!¾c£ş¢K;5,8/ø^¥4#Ìz”`|oïe< ¸(,…³xKYDÄ:p‹Q¢<z)±n‚ØË¥ öe–3¿b{Ugş*äÌó©ã×’ƒ_¿^·¦o¨iÀ™¡l)Do²IÌ™¿ñœù-U'g~ÛÚ¿ãSqó*jÄ™ße—3‰Ş³ğ-ÀûÖÙî |ræƒ³8¿–ôQú,¢~Š3l}âgæ83ã!áí0±ù4èvuûYºÛï‚#ş¹uû…º)Ã‚jö%›å¸òW¶Âï¹Â¯­õ7n…ßç8Š6ñ­UÿNÕ+Ïïy®üƒòƒç?òw–+/¤YşäĞ hòC–+ÿlş¢³\¹»šÿÊæi®üã¹òo¬šâÊ¿ó·qå?ğ\ùO–€+ÿÅOpå¿ñé¹ò?6—CH/¬It7¤ó\yş©gåO÷¼ø.ºâƒjŒŸòàFQBQ»YõùT}Ä´NŒÍñ³?vbJ’é1R^RË‡(ròMiÊI"É3ú>©zN—“˜ä"Zß,Ÿ“ü9K5´¹/äæ~˜n†_‘zS—o<v—â´fFğÈÇ C/8-û˜B8”†-IM’ÁFOÛE€—xŸ¼ÂrÔ$Ï|ìÚÙ¾h¢î¹UöĞ*.µÊ_r}¶Ên•4›ØêX¨.‰ï8b´7i¶÷ëH%½õ±ƒäÆÈRWkÊp%2Öãá$B—.Â¢¹5,ª5ô,µ†_³âÌb¶†Åµ†ââÌì´Gåo¡8ÓS.É¿¥èÜRÖİÒênnËeØ0¦X‹©³eYæe™ßCIëwyõ7[\ÍVğÇ/eV´“÷‡|$­õÊîäı‘?y(Jİ*V}UU7BWÆïsû¸šö§'x½ø;Kğ–ĞlWwDÿL<ò¯5là5ôòÆ
vµlÇ³&$§ÄXAFÕ2~‘İÂZ#±[èm³û‹ ècCôu ø+äjk»²¤&¼NzWP?µÛı¬³ş~·ÿ«İBy0ÜRnİôpÃ°áf?³ÊÄVdPĞÿÒêpºÿ$bı‘l5[¯(’­oı—İÀZoè ûoÉP”÷
«¾‘ª˜òJhŞEµ“™(
JGk=BÉÚœ…	$Q±ªõQU5|=cç1ºïƒ` ¶‡K¦Øs¤‚æÖ@³<¤AhVòm÷øg¶?Feká°$çuäM›!Ü‚×8:NeUJuÆPôx*6&¶²¬@:Œåsc+]º6l1!o›Ì†çÏGœ‘GÙˆµË\¸Ysá±i›7OWlŞ(ëy´Û¼yºyÇx´œf¿iPßZ"lfm®ÎŠ["Œeë•óv¥DÓ³åÕó8ş-uÊÆ[w[dĞ>o‰0$¾)nLxu[™p×xÂ´kœ`#l"şŠj¶uQÄßÆ`×°ÛÖZOt°ëæa'Ëy@Q‚ø“¬úd‡ø_`Ã}™ZVgh"| ™™€po¤öÚ´È†ímö&ÛÙ–D¶F"yİ{Ló¾àC•I Z ÏtHmŠLnÈÁPWã!‘qLP±à:f ½ØK©%] ‘%]bqFW>ÖIâ–]çL½))›Ê£ír‡a%yûR‡a¾ôa ¥MÀqÁ1+¯¬Nwd§éG¼ù»"ï'HËŒ&˜`áôF;±Nüˆ·3AŞ…ŸwÅ§WULµwËà!y$³Bò¶U ß*šKuıÎKu\ëÏËe#;L†‡iU[—:L<›õ6Vƒ+6Lr?5Zw…İ•©»i©îxr¦[wMáÉYMu›‹œ;9İyrZ­u›;9İó'EÉÉÙİªGîäL¡T]ga[›2…HI}%ğn›J	¾X–æfŸâšvt¦Hü|Ø®®<jÏái/-ª£.œÆSuÚ¬g¸YawÖêzœé,§©°¢	SÍ¯^Zv—¦N7§=6Ÿt¢r«+h„=€]‡òèF43·ÎÕµÎY¥Ö¹Hv³m{¸u2Å¶cËy¢“6#2; $‰)¶Í™ÓÚŞÅ`“d—DÍWè:©6-¬aÁ4¨åÑ¹µ¬¡µìUj-=²kÙÛÖ²[Ë‘öe	ÜiZŒ£‹:ÆC„š›µØ'ìnC¨
ø¦,¤cCâ˜4j‰’u¸Ö&â¦¿¾Ú¦úìNåÑ¾¹…®©…îWj¡‹fº¿-ô ·ĞCÅŒ0/œ-¶‘9ÑÓZ}à-¬Ò"asÚ:÷Ø£	·m_ÄÉLéüÙ“eŒ3óluÌÅrTa¡ò«õÓd¼Æ•;Ò¹E®¥ETj‘=³œâ`[ä!Zd–SôV§‡²Ó4§X,Ï)c˜SÎ_àGğœâH|zNq”x´Ln´è¾P„MüYa±ÔGó9–eş*¸xÌ-xI:Î:?Şwş_¹Å	Áp}5Ü‰éá–ˆ‡#›=É†;¹(ğÖVëS²À[2¼Sàæ€wºŞxd)gÚ€giÀ,ëh¤³Y?ÿÒÆÒ•K‘¥œk­ÏSë
”åleP”°”ó­úÿ÷4“Á”=ı÷äKÂDØíˆä?¼[¢DMŠÁ¿ÎFNÁÌª¤] DOp0‹††‰9Oï>Xƒ}ÁRîÂÎ÷Óº/
p¾±aóÃÆN .›Ğ0æÒÙƒ}±-ì·°^°”ë¶cb>"¡R!)5œ’ŒÄË±@uæ©Ë’· j†g
å:™ #~lĞ+ÙŸ+‚¤OˆÉšk¹{`”8R†æT@ùaÅRô!ÉÆ!«Å··á=„ĞSÀ!ZÑáÑ  ­m±·:…fM‘i¸œeyì–§ã3&Z5³JáDrzE—æàß_ğ¿¬ü—É^Õ.7ø_Q„8Ú_5(yÙº28“åóªô™\.8“W[ç×=“ëªõµÙ3¹|şL^œÉëİ™¼ÁÉİ™dÀ“›lÀ›5 i„ná÷ŒêÖÓ·ÚY\¡ëø;Y°áĞè6şÎj‚hŠ·óOf=¿‚dMg=O¡éğN‡¾½y.ã70Ï<GZ¾úÙfÛÑ.ß§^Ñ]¹=¨áî.µ‡+fùÆ=6‰{‹‚y:½O`><‰´¹ÁL)ş°(µ½ôÑ¾.¯s<e3«fô‚X
*Óİï÷@	ØHj-µˆÀ‰d•3 ”‡8‘ÉóÏhmê„]ëÃø5¥+.ÊDàÇäùëp&[¢Gùø.&wÃ.D±‡õ¦,E(™Kô¸mÚJ$ OØ¢ŸÔ¢+PæèänšïS(?|ò	Z‘èiÅ™O ‰á, 
·¥Ğ=Ë&wo¬›êl£çØ¸¾¡øÄ{Ã,ôE~‚…¾„O²PbÜË6W4Ã¸Wù=ƒqƒúF¯ÙäWö÷:g1n°vëşÉ0nå4Æ‘­¾i¾¥CíìDÁğ6{Š™ÓõşËöDÒ–¶ÙåUMİ·­š9ª	omİ£wñ'Œñ>à ©mìŠ¿DØÜWízÈä… )·|KÑ‡‚qwˆ
TÉ«LôJv‰>Æ¿a÷•M9n©•ºGŸØ(Ÿj”Ï4Ê5î¹íÑçÜ(áÄ´Ô İñ\ lÒ¨_h»æ‡·üİ£/õkÁZ„1Ñ_¿ŠÛO^OÔp8âu{ôµfö×±åtéˆ:ñjÁ‹Mô­_Ğê;ï÷oVìĞ
±g@YÕäxªı¨ñ»ã³a–è'ô3;Æí!
c*gù€¡Ñ/©Ñ~µÑ~ËvHô;×¡ôÕm³
M®‹I˜vôGª‹?­‹¿ò]ü¢Âä×œ*ú‡óê¬®ê¬¶×ŞUÕÒ¿ÖMø¾§¤™¡B˜yP(i†—ğmxänˆæeYÏÊ2Å®ø¶İÔ¶e9YE‰,3ŸUŸ_ÕGLN÷œ9°Ù»dz˜3ãƒ´B)¸°XÈ
{W³`Ap6êr=Í|A–ÇªË"òÈjYZºM®»&—•Á×W§³Ó´Ş+Ï²aXïÁ_  ‹ò¤'>½;Ôb6àâğ°S_‚}ö¨\=Ô‚l ™.É¿¥_}l¬¥5VH;’l!±rr¶iÇ†êqY–yy ƒ–³Î—1¨BÍVğ>ı­IZÉZ¯ìphÍ<¡(Óª¯êphOç`‘sß~pW4ıB|ÕóF–vİK”õ±3£]×£ÎN"5ƒ
Z’¹´µKÑ€yK¤,èô•°aõXmºx+.$»Êb(ó—.«‚¢>**pö .D¥ø@G§-r/ HJ`j–³S…Â'1µyÍ®Ã4õ—Ú¢K½YX¸á”¶ÀYº¤'¢‚æÎßFÚ÷Õ‚óW“¿¬•½ô²]İmìz«åŠu×GéªHÏ®´Kb¸ö–šÙğ,5{Ü6§œÀŠl%!"0;`˜¦&ÖT…ÌpW‘¿;/Lz´†TÅt?æö’x–Éª-Ñl%X†à9xm,x­Y
^½³ğZËàÕÛÁkÀkL«´‡Èn`ò‰Ò06Rw‘€P‡ÁÃ|„hj ‡G}rs¦¹õ-5·>YZº¶ÍmÍ-KK7Q§ıØiš–öÍÓÒş¬ÓÒrş-]—Ÿ ¥ğéõmÀAúÖÖE\§+
CK¢Ò¸ášÒ4‰[;Piµş×óıÿW•ÆúÁp#4ÜéáÖ	(ê†6\…†‹	ñH5ÛˆÍr†YÚ³²)ê0k½‰ZW ,Ç•Q”PÔáV}„C$:7@ÃÀ@r¸¸èÎÆ×6eç]{WI[`ŸR†û»°$¶/NwÖĞƒaÌ!Ù(-kT€dEvÿìmóãæÍ Ûê†%Û#ôtI£Ã!U´æÉæ•±¦ßP®z;ï¦D€‹%=G)øÉÄpÔs–­ÔG”G›æ0ZØ,^ MÇZš£ÍYÓƒ”g—1Ö–1Î-ãw0´­ğĞHEÇÃü-|Wf‰À2Ğé¸på*¾Lg†«Ç°XÌµ#r£œNƒœMU$ıöŠç—UPh²e1 ©òo´´â%7|›fÌi-œö»1äõ*^ÄßEğ–J—ÓšÚA	£çGT¡óˆíe]¼ŞU	XB|	GiÊqbNÛ_d¾N o… „…¨ ÏÉJgC’¦ª¡à2è`¸•û\<Fã\H1
r‘x<êEãsÈ5FÈµE¹¶,Š\ëf‘«Òk‚C®×™rªåsıdÆ²S@]5ÖÜŠÈ‡ŠÔß¹ZX>Qcpr`;Jƒğ$P¸›gŠÏÃŸ@™Âe±Ñ©ÙıËl››°FÊRSX^5çßË£­rÀÛTÀÛ: -Ed‘YİØ6¶m3ì$ğ¤fPb:1 î›iÌIiâ>0à%“­óíşW^²}0Üæ±jcé|P ŠÛÁ†ÛQÃeyñXµŞ‰­Ó¼xpïÌ:1/Ş…¿À‹wå'xñT|zCÌİlÀ*3¯q©šõsÌ«†¥=+‡yÕZë‚ZW ,Ç¼P”0¯:«^ïüq2/¥øsşèxAÇ©ÀÀ˜’êlÅëª¶pÌ$7
’ç(¬Ş.uÏ¥h<3vçÄI‘|*Ü–´ğ5´‘oo†K¹©•ö›oOu²‹÷/©ÔGÑúêåÿf:Ævâ@2KEbE|*Ûr=^Plº¯š¥ÓLÓ˜˜œHÈSÅD4L6è.:¢Fâh5&;åÔMÒ;ßÉˆ‚ÏNI¤àÉ7Ç‘Cİë-%Ÿå$J”GM¹n¡6—:±ëeØbluÜœäËàÍÇÿ2i	´ñ6 $ë2E)/£f°Ì"Y@ïãwá'ƒ—Gm¹In©Iî^j’ëgÉJd“l÷'?•³“ 1÷øDFíz¥íLô‚ƒ>ÃzŸYô OPëYÙƒ¾aş Ïúî ïéú^©ƒ¾·¸OxĞ·ÒHû=èûÙA¯àAßßZàzEş £(9èZõƒÜ7ò oo÷^÷xínÖñãX-y(¼e*Ôš˜Ô¯ÀGø‡XD='–XNŠ8&.A3‰Ô¡8ˆçP`k­òRq£,
jË8,ƒ)Î’~u9<À€m4æiØ8¸6inÈ¶jvtÑ9Æ6d7äXk}œÛaùAQ²!Ç[õÜ†Ğf‰¢ÄæÕ†G'æ 6Q³8) XK^<Ş$°“m˜S2 ãpNÏS³A¬¸:5€×$yZ^Ãxn}ŸÂk²šY^g¼F^g[ës¼Fäá…¢^çZõó¼®&Ã+e9‡à%ÎD(¦¶ğO-d"½À’ˆœ¤­Jl9ãùR){¨ë1E”ò]%j%±?cH¯iıãvàz$›T—Z–­Á•Ù,Hxï“U~¯èüÜn'H]PêŒÌë9Pô¢êBÖø¼sQ¼Œ/İ€¯.Î¿½Æ¿¤NÊâÔ¥6şeÿ¿Cxy€TLhyhtE©FHu¥u~UˆT;¨ÙÕE‘êCª1Dªk­õu©Æä‘
E	R]oÕopÜHå¶ŸÆ.º€¿¿ù8b‚f‘Æ/fé•…>ƒŸ¶ª“0BÑ¨«•ğ7&3ŒQlC—ğRª:„D»1·O;jñ7•Â“M³ût³­î–"ûTDk}k°O;iÌÛÒû´Y°O·[çw„û´³šİYtŸî²}Úœût·µ¾ÇíÓæù}BQ²O÷ZõûÜ>Mõº
/YÆ*\gO< Cm‡ş¹½‰H¡	côK§á”¿…Ø"6ÖG÷ç¶a­í`ŠÜ†Æf·áA›üC™m@,Ä.ÅR?ìÃ®ô‘ô>ŒöáQëı±p¦ªÙãE÷á	Û‡ñÜ‡'­õSnÆç÷E‰ãÈÓVıU·GÛgù¶|{«ôÂ$ÜúôBÎñæª&øQ?gÃmáŸoŸçïìóínšïü“=ßn‘5xÑ†~É¡ÀkNBÅJ…ÙN™Öù<<›.=—Âµ·‚’›×äK?c6”¦(oïè\~x(ÔáôB!F§'Å¶{™×Pê•l^ÔÈ“3A .^O À]§-‚Ì"p8ÕËS)ó¿vD
!]½œÃ½*Áç•R¸·e÷*èUƒÚk‚š^/+»6l•²È¯VÇ¯;À§£H¼aMßTÓ TP;NQ!z‹mbgÕ­´_½w‰ŞV}>¸¿c¼›Á{½!Ó¶…·¶Xöx/@ûMëı4Úo ıÖù‡!Ú×ªÙGEÑşcÃÃmˆöŸXëOÚo“G{%hÿ™Uÿ<…ö_8´çj¶¦f­Ï€òÁ}£/mm=²UÙšå×	²o›FvÚä}c~«³J‡:5ÿÍÓ†)yYÓA¢{ÈîeU¤}0ù¾gÕ”cèüm¡?â+5~b	ô?óúˆ_ğéõ¿Ú\~!]¯Iüî!Í—‚1íí­M3‰}£?“î?­‹¿¸'åÁ¢„ÚÿmÕÿQõSîFßx0çdÔã”ÙTw¶Ğƒ
uñ qÏ\×q/´€ÎÃÆ º½.?Jt\®<=
Å–>2‡E"»O¿™—#¯5RCÀÛ¦µ…º»{×È,…³¬´wÖÖò¾†¼7ƒ±··WAÕ[ıKX¯ì_¸¸ÌÕAhrVô›- šyñAĞœĞ@èƒºİœô]Xéä©•©áÃ/ÀÔ72Œ]ugc®†»ğ€NÑcÚa'Ë°¶ÂbÌQÏBpXŒáÈıÊ'WgÊ=l&ùpæÊF-·ÿŠ¨+—,½QKïVjéÛe—>Ÿ-}~·ô‘2Á"D–c‹ê1î"­è	q, &\ 7½išŞ‚¥¦·}vzÙôº»éÑ›ytÒUW!=:ğ€LÀ¹l’îÉév\£ğÔ%§PˆGS®´76Ã7(Ìšf—Gçæ>]s_¤ÔÜ§dçŞÃæ¾¨›{+æ>˜zñ8´Íô\†" Ît@&wv˜äŠ1-y†R:Z¼mêºã§Çú°å¤KrdúØ§.õFÔ3·˜&-f±R‹Ù!ûxº¸-f	-&K;›Õé’ì4­°İ1¯ÇYŠub…íÒü¹?A —Å§'ËÙ€ËkÀXaÛ¢‘V`ıœÂvE–ö¬ÜIöÖzeµ®@YNa‹¢”ı†U_ÕmÕ»ØªIJ@¬BF»M«Â›i’9ÒÆ¶½Ú&‡Zñ)·=°Ôe•b/z‡®ÌmbÖÂØ=§Ô8HÒíŸE=ê(?7Æ?Î×ª-zœcôe>a2yø5*®›W§ú¨"*Ë¡F«`»Z)ÔØ9g#aÀ[İï	 oˆ%`şIŞxÏSŒí4’´[N×ì¥Po5µ ~=€á,P`A ôáPc¡Í0zVo;Æº²"Ö®qäÛYjÛc’å£Y1_Ğ	¨‚•”¬í³ÄÛãWÍhœÚ§5KÁi—œm„Á©·ƒÓ6€ÓĞ"pJ¹»ÄiÏ©±äR0ç®XõÉMwwM·o©éîšîÚ6İuÜt¯Ãt×K1ø ›s8lZucôÔxJ7Úı¦‹lş9éd~é/‚³ É|ÂVvK§ØıÇ-¶)ÚSÔ/HĞè_
S³Ğ(7h¬ë ±Ä×Ÿ4 ‹jìHKt¢¿g;D–™ˆSbb¯:ĞÔsÂt¬Ğˆîòš²‡^³í™rü|ÑZw™ò^Ùæò×˜^ƒ$ì _Î.Õa<Vg3ÿ'ˆ¤”sÙ„ÁMkã`×sD¤Şú=¦å4ÈpÀ|·mAî¿òh@îí‚ûÀRpß-÷A÷ÁîÕÀÂ­@KºÀºüéÈ{ÿYò
(ˆœ’ä'b­l£;¤ãº3Ò$Ù áÑÜü;4ÿ¡¥æ_•å›ëÙü××ü³|³SnÀNÓ|³:Ï77d˜oVğøæFüßÜŸo³7Ñ€1ßœ¡‘†³~o`iÏÊòÍ‘Öz”ZW ,Ç7Q”\áF[õ1ªnš‹Mùš‹2j.pOÚ†áGa©Ø§ÌÙ!n%`†c3ºÖ_ì6çï¬c¦æ>–2-Fmöb7Î¦1¾(g©ùrÊã 0Ç‹İ–1¬O—ÿ@%ÛÅn¾âb·•ƒÿÖşÛ¤à¿­ÍebÿÙšÄ¤¢ğŸl@¨#ü·³ÖÛ;ø×åá¢şS¬ú)øïèàŸ¾B#=ÃN6H½‡ôÎÅ ½‡f¹Kéú¬¾hWpª1…qÍFêÔ3–N–(ğé ~ğp{l-›PÕÚÌÇ[KZëì_)b%qˆxT}ì¾$î˜wBÆÕÊ|è­§&ål+Æ›Z««gK$’UI6y›ì’RTR\Ôü-.Ú0.X{
6U,-¸‹è)²zÊjƒX –9ÏIOYËâc»—-°Ì[97fuÖ{½ïı¿š 6Ãí­áÓÃM^s§ÙpÓ5\–ší£ÖMl¦fÓóÔ¬™ubjÖâNS«;Mm©Ó´»…§i_Ô^ô4u¢7ñ4uZëî45åOŠ’[ÀL«>Ë!÷U|·p*áTl¿aÍPÑ›VØÎg^ï¶4+3–â¼tiU(½Át”Jm¦cXD:ËD‘3¶Br1+[f4êÑµœ6DoLòÆ¼Cµ­hD™@Ãâ-lvi÷ ö(…´Íi¤e¸ƒ={	ÿƒÀŞ±GeKè°¿f³ÿ–J^º¯µ_¸Å¨îşE·ø ÛâVnñÖú ·Å­ù-FQ²Å[õCÜ÷×EÏ›»O„`ÔÖŠ»÷ÑĞÆ¤Ñ¡9¨™V
ÆmYÉæp›Ên*ô!§1·ö?l•j Š/¦Š3s{£"ÆnïB$s	`2£B[öÀ“6*nàZ€é>ğˆùNÊjg«èNë‡ŒÌ-ò -ò¨R‹Ü=»È£m‘Ç¸E…ØLµàì2"(KÔŠÄ°kb€îá.Û®<É(NKçVë¤_;ƒqÄWgYƒ{o#òÛõnÎ9X1HæPŞ4+ßÛû)ğ,ûg.\Úë•ÅÌ=ZaÕˆ,¶5tÚMì‰p„wÅıVå¤fe®µ|WN<Š}†Ò,‹J«ßüF–GÇævé`íÒq¥v)ÊîÒñ¶K'¸]Ú¨mßá$>kÄ@dˆÃØ7‰•%QSú7š±)ÉNytbnb‡hb'•šX{Vz>Ù&vŠ&–å7‡ªÓSÙišßtäùÍi¬ó›ÓùÒóü„ô|&>½ÉşY6àÙÜú¿òÓsØgÌ¾ÓÏe™gßû>Ï†;ßçl¯‚\ğ‰éÕAç‡«óÓÏs.²Î/VçñœP³KØ,w¸”¥=+g’°^f­/Wë
”ån(JëVıJ‡B³É;7Ã3_'rºÃ¦ÑRğšŒ:Kœv;<´Qn¯‚!Œ¤Ï	:š¦N
d¢¾<~¦eà^D´Ev$»U7µvòøP#ç¸o{ŒD”€ôª©U_]
geOÆ5¶¬kİ²¶â²b[nĞXSÖÖ"{µbÓ2ÔAi†µ`ËõC &È´_¡)'’EÁİ$
ÑÓzE×å&{”&{}©ÉÎÎŠš7ØdoÌ`S(j&á–n
ĞéhzsöĞéëıÖQ³ÛŠ¢Óí†N{î°Öw:tÚ3N(JĞé.«~·ƒûı&Š¥‡ÛØD`_ÒH´!ş–I^±‰¸a1râOÃÅ„GtÃ0{¤¦fÚ”’ãur<E°CTñZßaŸíÁrw¦¶8ø¤pl)t§h-C >¢+y¯èÜN+èİ[j§÷Êîô}ûçºÓ‰-øÁN§ALïôŞÁN?d½?îôñjöˆßiD´íÒ[XEé}2zÔv{îöcÖÃãn·÷Éï6Š’kìVıIU75ÂSüÏ2ø´²¯¿Æ>ÃßY…Á	šé³ü“)öÍ^cŸ³Ÿwèõ#Ñ+‘“MWD8¹t€„¹'/ñr…0”a±7”¨0)Éçğhsm^Kñ"=„d‘Aµ‘ãDr¨¨Õ˜Á%×ÆñÁ“d2<›Ñ.´ —²3šÑ8ƒW8âÁi‘†ry¢@÷b)„Ü/Œ;ğ’ôåÔ¾R|_µÜßïàkÅvğ$Mãõd÷Ïª|Ş°ßÔ€YÉàd5‹ÍÓ’ÁyÉàmÖ‰%ƒwø’Á»ü„dğ>½côû6àğ¸}È>{T^‰NÑL?rõRÈÇ6Ö'«¤cô§ló÷SÕãg,ó2ÇAÁéşÜ:ÿBÇÍNS³/Ù,üÛ¶ì`ì¯­õ7j]²œX€¢Tğo«ş]
/¾/?Ø ‡x¼ø±^œ®Yş”àÅ!Ù“ı³ø‹1e oUx@mW”k¸˜¨¸u41CE§N¶—øòèWhÎĞÀ¿±|nÚŸC³„úw›ÎEvCÁN¼¦JRüg°“gjÌ¿Ò;yX°“[çÿ„;y–šı[t'»À’@>œ;9¾£õ¼øàNßI%¹«Uï¦ê#¦\kæ#ö„ƒW˜à®Œ‹%ª·œ¤X×,bl†[J¾áA§ÏŒÒÑE\7Ãæ*FÕÄÄ='É‹~Øôcƒs ¾í–5ÌGè¿®ám>®>ØÖ³«ùY>·m="»­00’J{oÿ=pCéØk!¶s4lw–ù3zd°³[ÿ‹¨ÿ¸Ù¹jÖƒÍrgtQÛÙ£¸³=­õbngÊï,Š’]Üª/áv–j/ì¬²AÕ×C˜e<•tzx$²¼–YjXó³K0öÊ›‰+ü‹•Lûœ,ìÒñLk,Á‚¹ïÒr±MfR}…*äh¦(ÓpÆ¹Ã| ]ã¤Ö#$œ™¢%sÛz µT©m=:»­K$–Élëlë–öô|¹\zO	ötyë|…pO/P³‹îéJ¶§ÇrOW¶Ö«¸==6¿§(JötU«^æöôlè]ì„F­x„®Ç2½Q00k/E!kì`6§¯ƒ,â×¡nlkgt1	ŞÌ¼Tà¶T¯«ßT¡Ùi)ù#¥ÀI<tA ¼¤…]‰ãä²–ıÄÒw²™3o®{1¥iiZ’ÓË±æ¤»1Ì”O™×!ô6A¶ƒSAÀÑI‘!­©ˆsÁ+,ì/9‡ì]e÷Å§Îš*ø'xÏsÎ,ëÏít¦4vA¡×Œ™«§—âòhµ_(ÌèU
‰Ë"ñê¶õkdxNkX|‘]+ÅÇXÜÛzïbñÅjÖ·(¯mX|±xkİÏañ	y,FQ‚Åı­z¹ÃâË€Ås³Ltœ±ª2µß¸Ndmr¼
[/{jæc¶ñ<oÑÀgcãeü9Sû…Q÷çtsMÏØ5&AArÿŸ!ÅœmÅäÜªŒÿ“É´Ş2ÉÎ(_b3y®ñ„ÒOµ±eBĞÊ0Ãä€‘TÎ˜Ç[´n¡/’(…Ğ'f•€	²¢ş¥êt0;M‹ú'åEı!¬‹úCù¢şzü„¨¿>>ıú6à†!_¦‘*ŠâøF†ã'Ç7¶ÖÃŸœÇq%8¾‰Uîp|_½H@Ø·kfÖràN;	´T©h’ŒôDG(—ÈÒ’B)ú9/‰Ô; 8L„R0/5{ï2ï4!ÚgˆM83ájOÃúáÑˆÜÖ]®µ,µu§dÕg£lq£İâ\œ\ f'£Z`‘q éDÅbV[\¢¨ÓE)õ²Sıù÷r­Ä²'¹Œ¦îÂ+/Iˆ™,áDFÓLn‘Wh‘›–Zä©Y‚»™-rs-2!€#åÆtH°fœ‰Abqp,‰åº+5ğ8–yqğ´àÙu¼°EÑp•Zo™=§çO@ep&¸°•;[§NÀ66à¶á	¸Z#M,z&Ù	8ƒ'`²µŞÎ€3ò' EÉ	ØŞªÓÊ7‹Q ò;¸¯Tš3S×ÉÅ$¥3IÇóH‹H*ÑLE,ÿb»G[ÕÁ Ê{Z;E""‚÷§¡ÏRKtc+]ÿ cşè xLÜ†f²Î„< ^9¤	·ğ Bç cÿ_'ë#ER·Ãä×½èRïX…%æ„l8³±éƒ/%qlm…5¸Üì¬b7aHq. N8çŞßGdaFp;äğûmß¥ğûÌì!ŞÉögg·?£±?P{Ù{\ìOïc0qnÊ{ë'd|¼]jçx; MÂ
ıå€öš¦Ãå0Òãl1áĞIK­ZÚÀ±U&HülGz‡ºâ­°n­6»éã°t)@d›v<H¡K6+ŞTÈ:æ²×Ce¡Ób­·
ê:#W²KÓ2eU5ö
Bˆ²-”ƒÔÔ²Z/vÉmĞµÚ ]KmĞYÙšj´›Û M¹A“PX•™˜1HPEëN*º
º\Û.!ZælˆKğ®¼¹ññ2¡à~‘kÅCß¡pµ½tŒ½cÈ­=IV±6 Æ[î9\r†ıµ8D&0+9¡™“âvĞ_Á–M"S[¯W¨Á'ªr¶¦ˆÃäÓı¤ÁráğŞ°¡±´g¶‚£!X#£VyT•Û¢ë´EÕ¥¶èììÕØÕº-Zœéøh"¶³¥CöÌİŠ"'oUûtİıaFFâæˆIÃç3÷èøpë¬y³ˆàxÂRš'ÏÓ¼ÄÍ<Ñ‹áe£[›‘ïYá÷ëácÈ6º™ó©'eX Xàúá °ÔéÌ¦O±ÀLŒ×m¸¦›bìíçÓåQ!îëîºRà>'ë Woàn¸å wnè wƒ:ndÇfŠ'“œfM§«ià §·½¨‰mb½ó½ƒ^³êSŞb´ªÀ3Úø}ÎiÀv7ŞyW}Fü}Ô¸Q3nw3ÆŠ.H«>éØawjà0',6‡Ç1yšÁ~bä&õ=“e^ ¹0¸õÍ²®g«ë¸ÙÍj¶›åôQ{Úš.¢<°—µŞ[­+P–Ó£(ÑïcÕ÷Mp?ÀŒ_àş6ÈÅpÜ-šå	à.Î¾%d¬³Œ[Õü6O›^2GóÑCY5åx›ùèáø
óÑ#X‚»Ç‘üÄİã(|ú»ÇÑ6—cBHß¦Ië!÷<Î q)Á}¼uq‚÷¥yp£(¿N´ê'©úˆ)‡x¿@Fæ4«})uìq=¹–˜+ÎtZ¢rÔ%å;lqùdíC:Dy´¨Ê'\J É“tæcû0{<|;dWÌEúÚÛ‡SX>7}íeYıT[ãiZcx4òÎÙ{ŒãwhÄ3XæÆå	Ç™ÖõY¾kVn‡u%u¯VĞd?sÇâ¿èì`Œ;5Æ9é1®ß¹6Æy!RÜ¥fç{¤bÙ^`øp%ñáBk}‘Ã‡+óø€¢.¶ê—8| Ÿè¦âÏón¥Ğ¡ÍT^ô–ª—¢Ìd«Tø»j\JŸ¦{ˆE~Yæâ!¡Èç`-RÂ¦¸_œÑ¾ô—¼™ai–²	C²FÊ£Ksht· wY)4º*ËÅ/7Ğ\á@óŠ‰BÒ‰ ¨g³ÉË5‰J-*QÙ‡©d<D{’›CÊÇmºy¶SëÌ”İcGà&3ÒÉ]9:f[n?NÃ<vM&2ÛÀ8Ö]k»¹(ÍƒèIÛ53âıGf6–£Rô¥O>¨(pEWæàyàyU)x^eÓW<¯<Å¦¯	Ùô½êøZvœaÓ×YÓëÕTlZZúÆ¶©ÉËÈí7°QÌ§¯ó|úF5 »¼Éz¸¹Mpì2±¼º%8¯÷iV·¦ÏëõÁy½Íº¾=<¯÷«ÙEÏëv^oày½ËZßíÎëùóŠ¢„]ŞcÕïUu“7îã÷|~åûm=»|€¿³rÆšåƒäØ’³ìò!ğa˜e—ªù#lf—7Í‘]>Êª)vù»|_Á.Ÿ`	Øå“ü»|
Ÿ]>msy&„ôCšÄ³ÒyvùœAâf‚ûyëâî›óàFQB_´ê/©úˆ)'óÙì5 l¨BìJ1³-…„ŒQA=ŸH¨<hlmŸİRÃÔ 5ºäÏh¬Å;ilâFAš
z{yZK?a—g©ÊÅÆk}}ËÚäI¬[^Rtnª¥æË\cÀ=X^aùÜ¸ç-Y²÷ª-ù5·ä'éƒU'X<-—FŠLH?L^6,?(ŸìÚ‚+¢=÷xÿw÷è^AÏu6ëqW÷CöSÓÊt¢$—ºV»[s+â­„ª¦™Z´ñÓøL›×W*”4{³TBT!z#gr°5^Ä_ÏêêR€º5¨7Po9@1ÓŞf>´è˜ÖDD¡-0Í[ús½FÏ,L«µmD¡½—Ì½áX¶ H}y  Æe£q±/Äûô;oçfı¨fıN©Yß–¥ÂïÚ¬ßÓ¬E…o©ğcêø}GÒ—¥¬é‡j\–”ù)úˆmb"|§'Â«>‰ğ'ÖÁ§*(íóû‹e³Ç5¯ÏYæe³»:ü…õşeHP³¯<uä¦¯0ÜMÂğµşÖ†»ó„E	şÎª¯êF‡à÷<şÑ¹ÇÓáŸø;K‡ŸÔ,v@Ç¦Ü“¥Ã¿Ø€¿jÀ,~JÍcó4¾wtøwVMÑá?øÛèğŸø
:üK@‡ÿæ'èğ?øôtø_›KØK§.ˆOkó pyîçåŸzVŞGpwÅwtÑM]T ,wKDQB‡ç³êó«úˆ)Œ\Çs“„FĞT¨¬`}Á¤Ô¹0™
Á(¸…j%2™Ä´–N©g¤T¼¬TÄÈœ6‚¨‰g.®#‡D;†jˆ£| mî†ƒ2{‰;g H×Ğçg®Y>7ú|–ì,d èî@q¥…{&	%fH}¶ •™ƒG¬s†.9Êy7`Ä± +ÁÁÅ\uşÂ‰DqœÑG
ì"Ò°¯‘¦œZsDÜÈâYb‘R€x ˆˆE Zø.{=jêæšhJE÷ÖÉ –ŞÖĞX*, œ°è¿Z/?/¹"B%mHÂû1UsĞë×¶vVc=åQÏÜZÓZ+µ–³Tyq[ËZ‹¨òC!U~^/É3²ñRÖti5UÖ%²1.
uÑ2låG<Q^VÕI”—³öË« !ÊL·ÓeêÀÄ„|vÓã4£Yæéñ£1=¦jl%ëxeul$r~÷ª1tŞg`?8×´wcf¡¾ÑªF ó¤²Œ¿³¤òE»šƒ õXšT29b/xuÏ÷%µ[ƒírú«5màÇI™Ö²Ö½Õºe9Ê„¢„ô±ê}S«\Û­2£¿ZÇyÂ¯®_±Õ½¬YöOV÷D–”Û€ëjÀ,#xEÍ°yš<9GF0USŒ`#Œ¯`CXF0”Ÿ`ëáÓ3‚õm.„~U“ØĞC:/W$"¸7².6và~*n%Œ`˜UßDÕGLi K²……>Of>*4ŸÒ-§‚…4¥‡œ¢ºàL -¯…r;¿Ğ¢¸tºB36U'M‘Å6#ó€†ç´şšV:‚ås£áOgI×H[Å(·
QAÄ?w=,9kP)š Ù3
/å°e¢bDÑ˜|hüÄÑ”[sl•å²è•ñ{'µ¯¸B˜Ò€ÀHzIû2èYGöÕEòvâ;vï”Î;Qù‡¼}M4:§×§1¥àôLV“·©Ái3Á)4®kmí°€ñ;ûæì?>ïohÌ±,óôéÙ@^g‘÷M5ÛÂ#o /nixûñ¶ÒZOpxû\oQ”àíVV}k·ã•xr‰ j;…oR¾ÔÎÉö˜P›*½²ì¹Q[„KrQëlÚÀfSCÇX¡ÊÈÆ
ÎÏÇñÎÚSb$Æûp÷.¾®%€$Rá%ÎŠ³™IšN[>;«CD¦’–ÔšFuç€‘x6BáÇ'=x
-e^„eÛxGá^	
¨; æ¢X§—\4"Ş×aàs<nx}ÄÓxHÉk›Ò½¥Ü¶Ò=ŸåÅm«&i«Ä‹_yñÛêx2;Îğâí¬éöj*^L6J^\38¢{aÂ‰_òœxU&'ŞÑZï”Áv¦¯¬©OÔS;hş&³KÍ_Ğ|WëujˆæïªÙnEÑ¼ÊĞü¢yµµ®qhşJÍQ”pÃZ«^Puãùuü¿ÕÛ ¯znØÀßY^ÿfÙè x5Ë§Ù€Ó5`–¾¯æMlæ†¯Í‘6³jŠ¶ğ·qÃV|7lc	¸áîü7Œğé¹a»Í¥#„ôšD§‡tÎ0H¼NpÏ´.f9p¿7Šª2Ûªï¡ê#¦¼ìîx€:mT(à6B­ØC¯­¡whÃ9BPYã Ídn´_”£¯ìî}33ÃÉ³×Dş=ı¶ƒÊ$“×­ëÄÒõ@Y3ÌÆİ¼~‡Æ´´¾U÷¶v¤	ƒîÌnm‚a^²Ü÷ZÕ„¬õ„QÀz?X÷bùÜXïYÖ»·l²û(@€<Í¤	^…QbZàgB3i…àÏfø#Ãd*`%4Ìı¦:_Ô:ÅÅãdFÁQobº¢2æy+< ä>>ÚmÔ@Öğ?†šÖßdö-°¿IlµqÙ7ıJAçÍ,tö7èà 3ĞÙ´.½
»[‡u@±Ö^Ö+ÙÄ¨£;l/tî#PhF#YÁ÷,†µƒôÔšœ9zñ8—†ºáNt`nMkM•ZÓ[Ù5lk:Ä­im¥kôÜ&Ì˜]ÇàPœ¦N×šË0ÄöH™}L=³htVõ¨âW, ÅšB¬;‹G`îX¾cÄfy3J³'sy-<hìGÌzÌİlª5"ÃÍ°Šï¥<¤²sˆ_'.ÄÖeğel\M¡Í»æ0CU,FÂ¾‰·dä&Ç%˜4ûphn>Ñ>VjŞÎòÕÃmĞ>ˆ¯¾òÕOÕñ‘ì8ÃW²¦G«©ø*É(ùj5Ä@ª¶è¶‹/ºïyöz¬Ú½g¯‚D˜¤k«ôU`aÓÚ‹“'°ÃXœüL“;‘e^œ|?x>Éº?Ùwï†›íi¸J·rJQ^©åÓpt
ûZOÙ©ÛNåÏ•œf}®¾*Pæî UzO>#˜ØçšØ™é‰¡~*ñêYÖÙÙ~bJìk Ù2WµTBíN“ÍíœÔÜÎµ¹}È¹gİïæöa8·‚¹}¡¹]˜ê§ÂÁ\d]¬ÎbX©f—°Y>jMå#E-°Ö—»©|”ç–(J„“+¬ú•ªnÂÉUüN®¶A>öÂÉ5üN¾Ò,¯åŸÌñøã¬prx½Ì
'_«ùlN>™£pr#«¦„“›øÛ„“›ñÂÉ-,pr+?!œÜ†O/œÜns¹#„ô7šÄÒyáä.ƒÄ§÷İÖÅ=ÜŸæÁ¢TÂ«~Ÿª˜òßÎğ²ŸÒ#ú+º»UX
*w½OG3PÛRıàÆ†ó2"·[)^Ëüí9váñÉõ|æLTdğC8	1Í4Èk–Ö’#‰½î`Ù›Vyt?H%ß
°|nRÉgYõ Áê!«Ls¢Í´ß|áÈ{Íº–±Xô®/kA’væŠb„c2‰Äy€‚^ìaàŞäÀo«j[gÄb`ÅF}Ø3—GçÖ÷Ö÷H©õ}]ß£¶¾ÇÜúöÂúâÀØ92BìJÎÁvPf¾ÔÜg¼,G 6Œ8$ÍB‚ô/ƒX)tH: c©Cä#Ál.°GE‘bt—GçVö½VöD©•}‘åjOÚÊÒÊÄÕ¾¹ÚêøiG&ÒïiÏXÓgÕ4¸-báÏ±AÌÎ¾öììyU&;{ÁZ¿¨‚„1+ŒA
”GÕÈKì-¦¯?jJ/³Ìó²o²üŠõıjH,~R³×<±T#¯ø–tâkı¦£ßæéŠ²ü–U[Õ,¿Ãïy²ü®ò'Ëïñw–,ÿ¬Y¾ïàıø.K–?°?Ô€Y²ü‹šÄæi²üıÉòÇ¬š"ËŸğ·‘åOñdù3–€,ÎOå/ğéÉò—6—¯BHÿªI|í!'Ëß$~ ¸¿µ.¾sàş!n%dù{«şƒª`LÉ.cAf—M€ä»4¦«E?²÷€®ı¦	ıÄò¹Ñµ³§ãgì¦ÓñSx:~WÇ¿ºİJŸß¬éïjªÓ ’ùj™
¯6¸sD°a|J~ñ§äO5â)ùËzù[¡- ¢e ”ØôÙ±À÷;‹ÉšÙ¿,ó‡ä×àtYB]Ïƒ”ìò§šÍ‹Â¼ìÒ•¥=+ã®u³Öó©uÊrÏ(JÉüV}U·C² ¿çÉB6Èïştçïì!ùK³\˜2Ùå÷ì!YÄì¡³‡äo5_”ÍÓ‡ä9’¬š:$‹ñ·’Åñ‡d	–à,ÉO’¥ğéÉÒ6—eBHÿ£I,ë!?$Ë$ş$¸—·.Vpàş3n%‡dE«¾’ª˜r"ôÅã0_…½'›&R>nq¼II¯[WTÁ?=G$y;GË¿i/“7äg|UK'cí€ŞpÍ¯©Õ,ıÍwnm+s…ÁAıW@Y…ås;¨eôª¶à2·à‡tIskËÄ‡JZN”~¶º¿'°u	¼®©ËS”"@x÷heŒb§ÜĞ{ÒÈé~ V‹Xğ.Í2ïÉÎY8s®éÒHrÍ¤µ&4ƒ6Š÷ ì13'®–¯ò7m€w’: ³¥­©³Ş¢İÒËÜÃeÏ‰B;’Lğ¡êù™´9cW·‰‰0™MèÀÓud› bı[éöäÆJÏØÛaS<Z5°‘Æ¥ğ4ÏaH—Åˆ!½JaÈß9OsÃ5„!ùwâwƒ5ÙwLGçÑxk±ÌÓÑB'së¸OxºçU³¾ştÂÆÚv°ÿ•“¹µîçö¿ùƒ¢”“¹U/wx~4­Û’Ó6Ï2ŠuŠw26{à9O²}ÊÎ‰˜Şè»Ÿ$Lˆ™ª êƒœ½v0Ğ5CÎ]1<'<©sÖUPjÃºtkØb‚¿[hKä–z—Jí‰Fe4WÌÄõÚ$§øâ*®¼kq~-0H†+pƒ3şpê,¨©R™œ	ƒùYŞúØôØápLæ‚ƒ©%ï€dŠ1=XTá628™n‚ÌR™'¦†jYOÉò¶ùÔéúì4íc>o7¤†¢pİ2£	f—“¢X'ö1ß¿ÀÀ*ø	¶>}ˆ§mÀa™³3§(›h~Mhxú uí–V¢Œ°ŞG†h5Uô ¶Ô­Ğk½©;@İºå%h3«¾¹ÃªÈ=9€æÅzs§°tæF ƒ`jÀuœ,3ÛdBG+lUÔÕ"Y.lRM^{nÀB(Bk	¯2³wã›Ã…µÜq¥pa¾4.P@oëÙ"³5¤79qË`_Òˆ•é}™?Ş¢Ùëz«¢hÖ]­·Î¢Ùy4Û&@³mšMth6É¡_&Û€Û…ˆ°°FÚ¾("L1DXˆ°ƒµŞÑ!Â‚yD@Q‚;Yõ"l‰¡áN¡	¯Ã|–0oüŒc‘ÏŠ]Eb,ˆ?æ[*Z(¬À»RÁÅGÛpd#Iè¢Ù(÷‹%¥‚u{œÅÌ¢‹ÒÁ¨Q…‰‹Ñ›ñ.&ƒµÔüö¤ãiÌ†=B4\‹ä^ ŸR«SÄGr'ƒ¥°[Ìy%{NrŠ•—ÑéİÔ7Ğø©uõ”a¨³ÅÉ.94_D›¹k)4_(æ4Æšj»µ›vËîUüºXm(Ñ½Ûø;Y°áĞ¨†¿³÷‡šF-ÿd÷‡îD†U:<É+Ø€u™sEmwÇŒDV¨Ô¢ê¶!}¤T£õ:­è‘ê©ÖÓ³Gj‘ü‘j
T³;R-îHµ¦T›¸{x¤ÓHQÑ#ÕnğëÁ#Õa­;İ‘ê‘?R(JÔ«>Ó©ƒéÚmY€¶‚99%ä!¼$ØjA#y¦Wn?‹5Ûª\	¬”‘”ÊEÒèXèSÒ8›Ïâ†ELãT¨†ë^¿Øû_ú¸8ËO£rÛ§ÏX#Wys‹âòc+ŠsşÕ‘Ğ;+N–û0o¿Ê$Y1Ÿ,Iä«/£&ÙíZœ±Æö&ŸÀ9g$½MÆ¾ñ±m•=ËòI²ÀóÌ7/s¯âEÆ‚€B”G³rçpqaÀìRçpÑô9d2Ñ=l‹÷ÔK!Ò³[Lt	u¼—;Yi…ÈŞÖt5Ìï•;Ú—mb]Èâ:H&ºŸê“ìo £òûœ}•2\^ÂÓ‚ƒù;K–ÔŒq3ÆŠ–ÈÒ‚CmàÃ40®|kjD?÷6V-¹
áLiczç:œ]Æ÷ˆ¥4Ì,ó÷ˆ%cÚ@N~¤r”Å…×N»dÆª£ƒ®—V×Ç¤»^*°µ®©À2jv|Q*p‚AniR­õI
,§(JT='[õSRÛtªÛ¦ŒEéi6È2~{N/¶=Ëj–g$Û³Lz{(§œi¥³âğrj~6›§U=Ë’¨Â Ÿ)õVM©zÎåoSõœ‡¯PõœÏHÊğ’ò…øôª‹l.‡^^“¸ÄC:¯ê¹Ô ±Á}™uq¹÷ryp£(õ*hÕ¯Lû*î¥±>ØcDZk}ze«€TFWÛxË{È_Sò+hÖ×&_>y^Ñ®³±¯×Ø#¦|l·ÑÌ¥ˆ±.l+Ÿ?ÍJF¹§wã=SJ"h/èëô&´ØKÖëhíŒ(ÇAû’»\"û{&"âBÚ‰KÉbÿKÃ üih­T8ƒÄ¡ 9Ã&ÁZ*:glªóğè%P\­(`İÈò¹)®VÈŞro2Şì@ø«4uØÍ8âÙ¢Ræ´.n¡MNÊG%Nsa~ĞfF+Óº`!zÃ->VØ¤¼Ğğ@9¯ˆ±q/4–†2(Í ®ó™˜ö‚†AÌ|±=ÄSYæšÉrlÆ››$|¶¶2ñt›5<º%Ô•Ô[KuÅ,Po3 Şî€
"BñùØÒÔT'™§”™ú‰¤€ì#z¤¤ƒNÊ–îÑEÈ&¨]|—ö™ÊE-U 0KéÄ$‚÷s\\¸ÌaÄ|äºÍ•œ÷IÒ¥xâ8üK¿h³OÕ[¢Ì„­#Äe¦ø~€«©ú7@Çp7]²
,µä¸RÑ–Gwä€½²€}g)`¯”ö]ì»°éÛT	¹HÁ¼û	Ò<ıô÷.Ô;™9(‚¦1H.ìÖòèŒû—÷tëı«‰J£LÒq½ğn°²wà!ĞE'öÈ;Cˆ–G÷ä@±Š@qo)P¬œÅ}Šû(hœ—\äœ$é â®n?süÅ-M¿xÛ£f!wÜítâå:@¦%Æìœ‰í»”¢BÔ·7ı~İu4@£åÑ9è¬*è<X
:«d¡óAça6{”2¢V5™^®Œ‡Tk†ÜaMÊvY3¹"š)[¥³ÛKk‰Óp2ı¡ña´Ë£Gr«)Ój-µšU³’ğc¶šÇµIÂe¡$¼š:~Â±Ï´$ü¤5}JMCI˜NÒÑÓlKÂ½¼$üŒêST|Ö:xN‰.›r©Ü¬c9ñyö‹ ½4£XæEĞÕ9ñEë÷%õ7[]Í^f³œ9Ó+,íY¹—W­õkj]²œ&E‰àòºUCÕMœ“ßóO‚oÙ kziåmşÎŠñkh–ï8pc;ÖÌÊ‰ïÚ€ïiÀ¬œ¸¦š¿Ïæi9q­9Ê‰°jJNü¿MNü_!'~ÌÈ‰Ÿğrâ§øôrâg6—ÏCH¯¥I|á!—¿4Hô&¸¿².¾vàî7Š’Ëù7Vı[U1åbš3Åf¤æœ÷SXÆ"ç7İå!<Ğ$Ö|@hà	éòàà}°…æ).Ä<şõ’ÀgÑ ÓP)(0ÌüuÌ÷whàÄÍ]vÓµmÈ¿Ì»³MÆ<& +ıkd­ŞÓ÷,Ÿ›¬Õ'«DúÁ@ğc
ã~r‡.Á<:
“À@úôªE¾eÈÉ?¼ûzÌû¥æõÑt~M0¯oöù›ü».ìêöŸ½¾êûO–ù#»vpküËºşÛuİÇî¢¶±ƒ\\Ÿš) Î°mU-º½Js!ç¨4 tĞhòâ:şµµ¯C\ë²¤F™<Úëx\3ƒÎyQœLymM¹+Ëü”Q?e4ÙÍ:›OÅ+]GÍæg³•Y€¥=+ûq*Zë…ÜTúåÑE	Úw·ê«úˆ)¥^Â]À(!npgÚšéòco¥8ïšœ\&dŸÚ-ğ.Ø(y2V¥„K@éXüğ)ù"]kÁ“«Éèòh.9Àú~P–Ïëûg_5ôJ˜,ìd¸xz'ËãdæÅ%¬ë%Õ5ÒŒ¸w°×ƒ,ÅzT®«Sïw¹:_šKáÆ2Öã²!n¬«ºËÅå77V°Ö+:ÜÇ%h%«¾²ª;_~Z*Cf°^'ğñµázŠPÆßY^4@ó]Í­k˜½9÷²¡Wwh¹B,Eª
ÓÔ‹ş	1Œ$œH‰. "ƒ½ÂTC´ñA{1j†º`âî1˜)BÔ¼õøRWI#³ Èm¸¸Hò…Öj3:ÉÔqç Ş{ÔÒB¶Fºä•Ÿ4‡H|ófã†sêÑÓ¬\Ô!´3à–Âfú{—VÓŠåHh(¶ µ ×l	 5ÖÈ•‚ÿš¥Ê ìQYËv¥wæ¨äåª>Á9¤áú¦ÏÉà€â­mı®bõ`5ëW«ûš!V—[ëuVÉc5ŠŠ7Àªt¨UÔƒ¨¼ì—Ñ3™”ÓE	 ª®ãû|¢Ó1AL„ñ9ÌHm\à	ôÖS‘Ft•:E“‹!ğIñ)˜s96ÒÓ™äú?"ª€î)qœ4fp÷½ñòg{.»â
Ç¹g-Y=ì“+8Qˆ¾Há;‰Eš+†s‹‹Šëíaê¢ªÎÚÎ&›Ô"XÊ-ü*ô÷º'élZ…å;!¯˜“=f÷†”2(‡„C´½ƒK!áĞì5iˆíßP·•jIèt»Ñ(šƒxÁš¡«7êĞ.è5E>×³é¹óqÅ)Â7Qü0(¢ÔmdyºA–GëåÖ3TëY¿ÔzÖË^”6°õl¨õè¢´~xQZOW8j™¾(mdM7VS]”dr Êif_c«øª´¡¿*m¢|Sn]ŒŞúrdÑ£7Ê^Şhk=Æ½ŠüÑCQÂP6µê›©º1”Íùe}ŞÍ¢ÂTNBp}Ù0 uKÛìòf˜ÛÔ”#ÍÓTFˆÂfõáSNK¡iXoı©wßh¬Íh#ÏsÆñw–çl %wP”7Jó¾Ÿla³Û25»J7»ÕR³«®oJ[ÌP™!Ê}A4Áæ±±ŸÇVÅæ±¡æ±u2³óØÆæ±mjİ<Äv`°’+ïS‡×`6Ã÷&ÙĞÃüĞ“‹]¡¡·K†–z{zJjèÜĞ|gÙšÖõ}†ôv´á6ñÃíTl¸4ÜÎÉp›doœ»Øp»j¸ìsc5ŸÊæéçğ9Ş8wcÕÔ³Š¿íÆY¯¸qÖ°7ÎZ~âÆYÀ§¿qÖÙ\ê5—X
¦I4°>¥îü³Ñ 1‚§ašu1]]T ,wÁG‘j)š¬z³ª‡‚g•b^´'±YZ8L<«M4«V–ù+ÄÈ€¡¶Y×»‡‹®f‘_L`s×në¥gmkİéÖ1*¿%§z†UŸ™BšY9¤Ø7šmCŒöH³G1¤¡9î™ Íè,îeÃín7ÜÄQP	;½ $#ÙF”Èk¸¬ó¼4¶ÃTöµ©ŒñSÙ¯ØTFj*û'S“Ê6•SS9¨ØÊ¶á6õÃRl¸QîĞd¸M³ÃfÃî7ÜráS–»àVÖkÖ‘6üf~ø£Š?ZÃ¿YV&?Æ†?VÃ˜ÒCÂ:ï cZÉkq]Œ k…2:xyãq˜Ú!¶—GÇ±ßàº6FãÏr]×ap{tK6?¬aìåqÆ“%nÕUœh“9)‹“‹ş[ûX¿öS‹­}SÍå´díc³ ?İ†;#5Ü™n¸9^…Î²¡Çù¡Ï.6ôfúœdèqY°ŸkCŸçÀ~œ}ll<­ã–UVÍ²´XÄeŸ`ğxÅ—iÇkdíIg2e\ M§,wOYV©1}•§Íõ`&³ñ-‰uğÃÈ[åÑù¹íİ\ëº Ş^HÙ]óû:>+İ]h«½È­vW¾–à-ÓBbbNP¹½Æ1½Ôó.ëWKÅš]z7·<¶°‡Í¯õ…Ä;Ó½H™ò¢<º87÷±šû%¥æ¾Evî—ÚÜ/ss„¹[ê…áç°ÔÆk£R¦¸²GÈ^d €¹[ytyn>ã4Ÿ+JÍgËì|®´ù\åæ³æ³4O%2¶Íå>ëÑŒX2ø`¡á@8•™Jq‚,1¼İ ‘(Îs7ô/nÃj7vØ2Û¼ÍçF<åÑÕ¹u×º®É‘€k‹’€Êìò®³å]ï–G‚ƒİgsc)øMÈÒ˜›l€›S‡şwèÓ–ë÷nµ£¾•?ê·;ê[j·'G}«¬<t‡x§ÌÊC•j~›§—·Î›¿İÍ:±áò=ü¡ç^~Bè¹Ÿ^è¹ß|@ÆâÅô ëçTÙJ·¡œğ°µ~D­+P–“wP”\¼µê¹ı:ûå}AÌeN^ôÁq¡¹ñê“2{«mDÄ#K’…( EÈ%3c»ÁSç©3ú·l'q?{ì!ÅóÂôx“¶d(…IÛfQõI[úSnéQŒ·4¶ãÕ’”Ûk™‡„:ç5£÷tÎÆŞ6 GvÓ*&­¯lE|4ÑíºF×«½ƒ§BK‰Åy””ÒÙ‘xz	ó…fDn„’€áıÕÀ,b}0ÎäkA;c"8oOç ´µ ôL)(MÌBéYƒÒsJ×Pm»ˆ¸
æba¿½u ÷3š¥HÂæûĞUÍTÆ¢¦ªêÙ|í†ºZÄuvv“4–‰/õMy6´Y?.FâK[B­lnb«EôäbÚ°¡ÏÃV=ŸƒÅ6‚Å¥`1)‹/9XœîÊmnã‚Ì™fÙœ(}¼6Öî·¶ŒdŞØ_Mœ2TyL«Õ"ûg”<z§çc•Â©“˜MD/ç–½­–ıJ°ì–<ûŸœ]ö«¶ì×Ü²_!ûw	…šé½ï/ÅrN:Ÿ'çšBÍ¢
QS'#Ä…ÒçÅ[;Pİ3›ŞdÌû®ƒJZ Ë(Ê;¢lVOu3q.h´ƒõ©ˆi["ûSŸÃ™«[tÆœÈfé±gì_»‰@Õ9˜MÌŞ(…*Ûeİ]Ş4˜½%˜e¹Æ$uú6;Msíó\ãÖ‰¹Æ»ü®ñ?Á5ŞÇ§çØ€jÀ˜kLÖH±~k|ÌÒ•SÈ5>±ÖŸªuÊr\EÉ-ù3«ş¹ªã–‡İ.´üÅ5oj¬”xËà[Šü‡›±…hª«ÀÇ·/8t<Éí4É/YæoÎ;ï…_Ùp_ûáœ•©â¼1ŸTSl;ğMĞñöêøÛtÇ;Wòï¬ãïC MQ³ŠíGÚNÚOÖúg´ò@CQÂj±ê¿¦Ñ8`q£@o
S4f2vIé”KtÀS$·¥³W8±OF‘NB‘>*±±`µóôG¹$q-I*"ÑĞ€~e8‡NmnéÉpLâ. Ë(Ç-e ˆ¿ÏGS1p@ùŞÑo¹c´ƒ@ú{pŒŠ³¤çƒÙŸf]pc'·_Y©%a*ğ>€¨…LªStYÍUÕ·âşå!ÅcYD‘hiÆÍfÖ±§)XP”Îš3-ó³0€<î0œeÃ¨ïİÛ(Â{ˆ»l†&Î38œh>“´ĞÔ“»‡çÀæx{ù´'­ ı•ƒî‚îß¥ »KºÿtÿuĞ­Á¹¢ï­"ƒaq]ƒ‹Pn&vqÆO ¥JhÇÁ`
9±Ã
[ ¯Ÿ-CK>]È”hX^K–$=¦Ö²³[©ıe2YRæø 3DQnX
÷Ö;Æl\ÇDÚ`¬wYÃ\…©Ì0˜b+®·m®c¾ğÚó->¶Øİ·VÆ²ƒ&Œ,éO‡øÛ‘w73@.Ôa€”À'iEÙÜaKB›ÒÎH¬8YŸ€TV<Ü’ÃãáHHi|âr3îqZ©<bliTó¯BÛÅ·F<`H6D
©p<-ÔgŸİ:NÉ#-ß¹„~Id|_’Ÿ:Nl#¯–€pÚÚ™Pï´“x–ÇfEÈÃ®Y.;/Z »â#ÏewV§İØišËNÍsÙùX'æ²óó¸ìü—]ŸË.dv×€1ÛE#-Ìú9.»K{VîF†ÑÃZ/ªÖ(ËqY%£§U_LÕGLù“)æ½Í7Iv.¾’X	0RÒéğ‚El27˜´å;;0ãaC¨ Êã8OH½…4=`^óxñÈ?’’ÉfÀNÈC6/{OrÙ3”L–eĞm–Æò8çšŒ«$,t4`@Å`p#„ğãÕm.ëÊ¯'íè_1`ÀŞ.û³]DIˆšaŠd6aîºg 
)'÷$Å 3Ì(fi>›r©´UÔ¤	eJuU-;6»
ï–(ulª²tIC¬¥b1¹j³¹¸SnÙ­4¡ÃÇG‰ÓİÖ†û§ÑÂ™Ä::—ã±šÃ&ÇS#‘ı˜ÀeMØy|•ûÄå“W…²ğŒ7Î§]-ÍTf™R ©Î‚fYÍr4ëKàÙ“E)Oòë­‘“™éA‚Áu ¦¼dxÃîqÎõ”Şs:%òÓ¯©±ç.³j§¡¥í€oÃla7ã¥»K’ô;"Må½tè)½S<uâ2%ºªj"óTB$…‚­rN+€¸»]Åü‘‰ˆÔÇš¶|µ§–—-ÔvÒÅ5Ë£ås›²›6e…R›R“5qYÑ6e%mJò(—Ò¼2;‰r•[…eşVQøµ®j½–eÕj½Z–yòÌ£WÀ<VwÌcÇ<ÖL1µlÀŞ!ó¨ÑH}Š2¾Æ<êÈ<Ö¶Öë8æQ—g(J˜G?«Şß!òó<ã	¡µÓ¥¸¨&Uq#!úÛ-Y´“²½Ÿm^PXh¢Œ¯#ÔEŒ¹³,¤ºpR.:UØbó9‡dYäÑL+²¶ ¾»ãÃªÖ6\Õ™qQ}t!¦€_L\C±ZAsİR(VŸE±®+’‘cP€e78eÁsˆu<4Üô:5[¯è¦¯o›ŞÈMßÀZoè6½1¿é(J6½Âªoä6ıhQ/#òÜe e˜†BóDMÔ´W Å1‡{´&)Â.´ğÛBfOÏHÄ"è M•*^Lğ´Çëz¼–H´Jb©œ|1î4	',•LÏEÖÀ(&aşDZcIƒÈº …ˆ•hêf‘Ê58ÅÄk›eóJ‘ú]ùâØÇeã:Ğ1{1/jNñLV
¦\K.ƒ|Åu²”GG/ıèh¹ËˆnS+B(1må1ú¥ÀâjãÂÖ†•BØiYÑwÛêáE©Wƒ:‘¥^ÓóÔkd@½F9ê5ÚQ¯1zÑ2bSp³Ì	á£KÍ`\æàpW“8qlœ’FÍglú”4§dœu>><%ÓÔl‹¢§dK;%Í<%•Öz‚;%ÍùS‚¢T^«¾µ;%·RñÏ!¼LİKMO™ŠÍW6:·óÙÓİåÒ~˜^/¢(şÖo,zæÿ‘öÕñYMÛmŸzK©{û¤Ô[HR£u…
ê!@JHè	Rwwwwwww·§îîîı®ëšÙsÎ½áşõış:¹7«3³³³³#
Å Tù•Ÿ­„ lOØî“”üÈæÜ,÷×“m¬8¡§}Í6Oèi´`¶E=zj¯2À!”-+è¥qG‡mç³a‘a«Ãmvë2†;"ocıÓH¹ts£fÛÖÄğv†á±ÄğöÖzÇğØÃ(*0¼£UßÉ1Ü)7¤Î2¥/µ W"$]>ÜM›×4Ç¼Y™A3ã‘˜>Nï-Íğß‡"\pÙËX¯ ßhÚ¥„\”®¿ÙÎ	vÚµŞ]êag·*všlAÃ*Ø©x´9ÂL‡†^ÆLa¦Åúcf¬š¬‰™Q†™Nb¦ÕZïê˜éL1ƒ¢3£­z›cæaFZ˜¦NdKPƒñ¹|]‡×Îíƒ±XÅc»vz à‡Wãúi7Â>¸ÈT¡÷ï\A‚”…;aY}¥dJlc2Ydx 	ê¬Æù)^íş¢AÃĞS·Oe:+^7²1	eì&x·×£ŒqÕK‡t¬”ÁÕüY¶oï>}MÊÙ(Fxûîš ï™öì©Åÿ‰A|¥‘?¦n(´¿/é&m#(çİúÇÊ˜9bğºR2ã‡4·j­ÙnÉR3-5«·Ô®ê&è´¥«l‚ša£º¢=Ğ©Ç—÷ÀøhL°®w÷À85›Xsìa{`÷ÀÖz/ßÒ=€¢bìmÕ÷q”ı¦gDjHMÏfB­ä¤_3)X¹|LAšëğÎ ˜Ãš 
I+Y8MWì‚ŠˆpIH×®n…|m²˜éXù@K±1­»ƒ
Ú‘Š¤pÖp7
©ù†W[äÓœ›×nñàåşÆ9\YJ´}Ì$]Ïú˜(òh$äÑ%¨ïW<v¯JDûXX«OnãÕéì´¬œ˜JD±N®<˜¿ <„_(Å7(³‰f‚F:¢&ÑiD³‰æ(k}´Í)Ñ ¨0è<Æª«êf¦}ÿNƒIoƒìì^Nàïªåõîšå‰ü—“Ú³êÿw’x²Œ/İöó·SØE~é¨nOeY¸tïm´Ó¬×Óc˜í¡fgÔ„Ù™¶œ½	³³¬õÙ³½S˜¡¨ØhçXõsU} \7ÀQÓÑ˜ÇN#ÓÇ=5…óY« ‡§ãûTùï6Æ…>Æü™¿Š7.5kyK³‹’q÷Ò¸GãÖ°ÉÛ·Ê/±q/è‘·dSFœGø¡P'"Ó·(½ÄeÂ=%ûôÉ.7°îG°^a}]é`İ/ö”¼*ÂğŞšïÕe£~ÉîëìÚÃû¨ÙuÃL Â$”P+GMv½MgNçëáFŸÎş)–QT`ù&«~³c€«Ş 	:‡ì–Øûj·ÖCòU`ßfCÜ>`'á”²;b€ßi+<+¼Ëú»ÛWx`ğ{"€ï§9ß[8ê— ~ŸuvğıÕìIüA›ÎAœÎCÖÃÃ>ƒR€£¨ ø#VıQ8İ[ÜQ²Ğ"Ùc	ØĞ\¯öƒ«{ë	èIˆöÔ–·gE‘°Ä|öÜÛ˜=•Œz F}:53?Ã’Ä˜ù*ÎŸµÁŸ›$Î›ÒZÙó1Î_0 J ¿hı½ä@>4ÆùËÎÒÔ_)ãõK8Õ:{-ÆùÁjö¿Iâüu›ÎaœÎÖÃ›>ÃRœ£¨Àù[VımGÅÂ@Å¦£¨ó]¿cø"Ûö¢+Í}!\È¼t‘ì!‡hzïÖ#ƒÃ«dğı¾í6î¸²ÓÎÕÕé²¨£”‚`64Ñ
–
—’YªY|˜ÅG5Éâˆ*Y|l“ùd2dAVŒK Ä³vqŞOc¢øÌ°p$±ğ¹õö…cáÈ˜(¾Œˆâ0Mü«2Q ~‰(¾¶Î¾‰‰âp5ûv’DñMç(Nç{ëáŸÎQ)Q ¨ Š­úO˜EğúQÈ>Y%øáÊÔ¹Hös‚#4Á_ê‘ÅÑU²øÕFÿÍG_£÷À#KS{ÃÀ75C’iZVòäj,Şùe9Æ‹\‘[!VgÂYüŞî=²ß“ù©ùıÍ¯Æ	}Lu~ÚüşòùÑ‹’ß²ÆAƒNÉØúÌ.Í#V'*%XúYC8?V[!p:t'ZC!œõ:Ã5—³®šc¡°Ğ¥Ÿ¢Xš’K2}cöw£"Ôx?¶ºW¦@07@`J|$B&2J“;2ÊT¨Y’QşÃŸİGÒœÚúšF}õGY”kZÖÌ¥Ğ£5ßéX¤PÔ/í”é­³ÔYŞì5›‘ÍøŒŸÈ(3Ùtçtf¶ºùtOw
ŠŠ2‹Uï®ê‡®¨×ou4ŒlÖÌ”_^ÃÌ/Ó&dB ®¶‰‹Ğ,Hû¨5 ›•“ˆ$×c5íÙX>9Éõ„*}ÎnsšÃç4ØçÔ1º°9É§^Š½¤+éz0´B\š"óµÇŞÆ4íJ÷çÀJš Jš3™ëqšë\ù\Ã™<7K’3ùÄªñÿ<6åy5e»ÍÇ¿Óğ;ó®N
— ø»z	:^³Yÿ²KĞIUãÿ…lÀ…5`õNy‚šÿ—ÍËwÊ“Ó;eëäwÊEøwÊüâN¹(¾Áÿp1pqXÜº&µ|‰ˆîOÔ„–,Óı)Qì‹¥¬÷¥Õ;b_”6dùb6ï6èT"ß'©ëeTáÜÓúë¥şòº'«n#ë&æ0Ë^Nãêm­û¨u”%æ0(*öP_«¾¼Óë	 WÄÖö^PíÁ¿¶HÔĞYŒ}¨c‘:@IºeıÑÕª‹¹²F¼¢Y0¾nC«i+ğ/Ù,g#ùêçCã‹’ïRÆ@<mÄ:óÍÚ˜õKhşc…œæéuUƒ{^å+ÚzWª·Lù¾rD§j°UÊ$pFdKÛßz]5ôZ—'¯Æ¾Š{ãê†À3‰À5¬¯À3c<0šØišØšå‰¡~‰'¯e­ÓÒéj¶NMZZ×¦r§²µ^ß§rVJK(*hi«¾¡ÓR›Tpz·ñ—Ò‘2n¡Q£RÌ’E‡;Ì(»»o€åjÁÀŞ[Áñ…Q÷İhD¶¼¤­pŒiÌ6J¨ä-tãˆJjèÎ®rñMl%ƒ|%K`%ÔHs)ğÈ QS3–09…6fƒ“9œ©9lšÏ!pçÍX’pçsª»¹Me‹ÉVU4×–†Ñs‰Ñ­¬·­£çÆÄµMD\giâCËÄ…ú%âÚÖ:Û.&®³Õlû@\É¿ƒMç<NgGëa'ŸÎy)¡¨ °­ú.–]É¬< ‚.· ¯in’.~L\:¨…‡GE™—!<½åÙÇH°ĞÇòQn”&¿’QßòÑ$ë2i¢ÓPÛ” ö-uX=ò:¿J^Í¶á¾±u¤eÂÅKF#˜Eáª‘'_6ª§v™¿Ê¥«^ º ÑEFåe<¯´"È—'á‘’†ónŞ‚ËE¹bhôŒ aL¢AÒ’ü°Vä*ãK‘[çU"¯{Š³²ÂnpoTxzuÑ”ï4Mmcèá-5f-	DÏDGD­ÁÖ/¨Bt¤At”C”ñœÍş Ú} ´1kMF;O£íšlÍÑ5·æ…ÕAÛlĞ1>èúD£Q‘˜­vqNR™RºH@T÷¾Ş‚ğJˆb¢¿ífñï³öd®çk®õhí¢ê$ÇÚ$wóIR İŠÎ:eqSN‡
ĞdÍ juÓm½ª§¤âKe£Ö˜eÉ\/Ğ\;¸«	×‹«Sî²)÷)/Ã;(îjn(0F-=-è§²×0 èÒœq×œLçBMg÷t5îš—Tß>&Ú<öĞ<ªrêEêtOvZ–S/MåÔ½X'—S÷æ/È©ûğ9u_|ƒä·Ÿ¸¿Ì%¿‹5Ò¬ŸH~²´û ËÈL²Ö«u”%’ŠŠ·C¬ú¡ªnbÿaü;}û8Ü¹<ˆıGğwUì¿D³<’ÿ2±ÿò²ØÏqGÙ€GkÀIÈÉÇ°}·AWÄrò¥êûXï;@ë8ëïøZ—©î	ZÉñs¢-æJBì$ëád‡Ø•)ÄPT?§XõSU}àĞUyüĞ¶J„áx’“îÚ»ædm•-.í¡˜!oBçØ&D	,^äNãL¢Kçåšûé,ŸœÅşUUá›Ø™šXüªÔ4¬9U:‹çdu…;›eá>ut¼Ÿc½Ã÷J5;¯&5o°½†°½ÀZ_è°½&…-Š
Ø^dÕ/vØv/î<N˜€¬gÛ.ŠšğÛ¥i\cÃà&<™/4+šñœ]ŸõÌkñ¦éÈï§–Ìå=@ºLäûôíÕ»İ{/Iğq•Özi=|\[e`—Ùb.÷Å\W:Zà~ŒØ›-Œ'ÏGas›¤Õ;ıxzaâ¡^ò1×îJø„‚”x‹²HnJÿãVrhÉ4Sr	 O÷wnÅ(¡ú€Qt~ÄÈM°¤À°`¤y÷Ù	4®4®¬ëªĞ¸Ê qµC£…¨ÕÎäû7Ğ¤¢—;«*„³Ûµº‡:f†%åG,pú¤rwé"É«"í*äIT8bĞRèšd	×h	×Ö[ÂÕ%\gK¸Ş—@út£ş¶V†‚·(0fî„¤–œaÇĞ‰!u-½@&2
†'F3^òÛ;`Ú¨¼-prbDó ğuCx…@QÁ,vuCOß*C $ÑªğØ#&KÉ£Ì®@dR(GGbPÓBü¥•iöL3“:$ÖC&ü³/¼8‘ ôZôÆz ½±ªsºÉ z³ j‡Ï-ü»rø  ×­ÆSnÊNğwõğ¹NÓ¸ÿ²Ãç¦êÃû6à5XdùŞWÄ"¯W·w—YäÍÑ½ÿëõŞĞkİ÷âûØWqï¿ßwæÖ×ƒÎ0o‰¯fE»A{¸<1Ô/]Í±ÎUg9Ë¿QÍc³D’xÜ¦r+§ò„µ~Ò§rkÊ»QTğî§¬úÓ¾;N‚.Æ“"@>c´ÆH£¤ëMätîÛ|.5Rš5»n6YWf¼)­²l	8¼UÛÇ6„ìÍ|
ony¬ˆ2ñ‘A¡|İiê£lNÆ-Ú.UüÃ£’» aO÷Ìc‚Šğ¶€yÑ‹$¸FÆ§ş.È¡M°ÖwÃ›™=@(èDnı•Û©zÄá°çØq>P‚^¶B‚@TÀ<sAû~õì‘hs)÷)F qãrj‹#?ƒì™dûŞ$‚x¶Şö½­*?g^¯JÆ7«ÓØiY2¾=•Œ_d\2~‰¿ ¿Ì/$ãWğÜWmÀ×*Û7xô]9rşm”[4—×ËåHyû†uü¦:„Pú›wtg,”Şª®ßæÿJïëïİxãİ¦ºïÕÜxïÛÆ»‹ïkı¡o¼»Ò‡¢bã}dÕ?ö·Ÿ
M7 WGÑ!$[8(“[ a´¬qŸrAı¬¿wÑg7¨ñônóœØS|œ€ƒ}’ÙíZü§õˆìîªTû™­îó
Îi™˜Dü"ÂúñË2Öï‰°ş•uıuÀú¿µğQÄ½1EÜ©a¿­PÄw6Ö÷1EÜ¥º?Ô¤ˆ"î#Eüd­vŠ¸/¥ñ‹UÿÕ)âDW\8Ìc‡µ@›ÃØ1Ä"uGNÖğzA
¨<
šÅêÉëåÚz·ö¼ÊT#flaËj‡—Î~KˆänÁã÷ˆHjÜÑï¯JfØ‚ÿô/Ik(`H `E€jP|tS¶²¿’IÜ£IüO"¨jÿaI¢ª} *ÔL1·æ2%>A¨™Š§BÍP?„š©ù»*ÔÜ«ÙLÃ™Pó`Y¨aÖ­imÀé4àÀ¡Œ3¥˜k…³™%gÀTIÛq`†{…`8ûrı¢dNŠ‘A'sI–~Ğ¸ı,¼kÁ€,ˆ”HaÖhß<&X”“‡ ë;£Ü2tD6=]yïÓ"g`y~å­÷‡ªÌaF[úLZúÿ!XÊÌ1Œî×,º±,Ü…½Yl¸îa¸R°:æ•ÎŸY£PÇ³•;~$Ôf·çPÇù|T³9Ù,Ôæ2Úy”Üank=Z÷GY¢òAQÁæµêó9½0ÔŒ;FÂPføD(ã*ü<c!VÉ…¡±ì¢İEÌ‚+Ç|åsJ	ˆ
;a*B^RÃ4¯@Û¥8	v¢Xsf”§#ôxó'´ò ²@=Zy¬Ê#´e/äËãúDÌT14UyÌ/Â]«íjGÿ1’ü™ReÌœ®Çx8ıa_µì¡ÀÚ<SíCKY8YÊÃZÊë-åñ*Ù7ØR©ĞaÍ3±GD‰hÄEË”øDt&.f]/®®!	ıÛ3q	vİmĞ“ñ™ø¨†]’ÿ+IIKÙXKÇTÿ˜ê.S“ê—5ªŠTßÓZ÷rª*¥zTßhÕ—sôoK5=SùµÈ‰qã•ÿ€† z×k4­9NâPó7$¾°”ıÕàÿ„WkRÁaÓ˜õNPı¸VÕ'Gu8Tú²$9T®ïò6û~>û71ûµàWÿ"hiîA ê¬hŒ$ÆQ—¤™¼cå^Â¾ßĞìHÏKòæl‚v°ñ³=ìTŞ†¨.R&ª™”*Èäã òã“ !«'Û•KÕÍĞ»ævó'.ºŠ… ºÙ
	 Ÿ WŒöJ7¡gªÇñJ¹•9Ó1¬Â¿Sw#®gÃq¼*Wã'5Õœ’AéÏVíZV·×Ğ€Õ[ÑSj>€ÍË·¢çÒ[Ñ@ÖÉoEkònEkñ‹[ÑÚøø:6àºñ6zZ#­Ws­o+}Ûhk½¡o£çÓm„¢"<ÙFV}cU/”Ìá
¶ò
ùl’ŸeÏh:ƒXÎÖ¢³u°u¼ièøß2Í¢áÕp›—‡{1:q·°á†Ä@{NÍ¶¬	´­h/h[[ëmh/¥@CQÁ{†ZõmU}àĞÏ¨8ôH“
oœşMHSHEäÄ¢Lc[:˜ZCæld@.£+ç"•£iäÑ-´ãĞ¯=‡Ë™¼±aSK©e.ßLÃE?'ğ5l`Æ”ÑIŒ]\m%ıùğ¹Ó·T¦«‘µ^ßÇ·Ç–ö™ğ¥1Ûp‹¤½çåíY>¹—«ÇŞÆ+´ÛI¸gLÔ¼ˆùÇ17YN‰;E¤ñ‚Fß¹L¯D¤±‹Ó“Æ‹j6¬&i4i¼JÒn­[œ4^MIEiŒ°ê#4Ö¶«Ú6È‹2YÇ«…6¬2œ©¸Ô’AS÷w'âÙ¨è/iş­õ€şZõäÙÕ&8Ú'¸&XòH(P.2@*ÛK»",Ò°Ó-QÉ@Ñ¶HÖ–ÌòeÍrL>KJØíY;’SòÕ¹vØ\Çú\ù4gNIğh6"’2™«6zw#{Zhö43ûÙnÉô^Ñô²êô:kNïõêôÆÙôº|z?ë	Äoipè³Õpí„¾Fa$šİ|ÙrĞ`µ8A-‘¯Ù’\èxfQ²UíJ‚$¸¥òÌ¶ˆœ–ÈG9™¼qD/beÎgœ^Í<ò_²á2yu©‰ŠF&Ãá£˜ ö`Çg8FDa"@¿,òÑs|ÙWÙ	õÈó2Lùœ¼»Át¢`úW÷àˆİ½Ë«¯i6{ò.¯2LÃ^6ÖŞ«N‹}Ø6?ış§şöeY8ıŞŠxÎ~Öõşê:oöºšÀfé›?K»z[oşÖú`µî²äˆ¢‚çbÕu:¬P&’wİF¥âñ–Ğ:Rˆ{dWæé¥Å«±£Ú“xVÌyÒÍ4DUâhz²’ı¨´í%[OÏ¬¬dRT!L>±–"Ê3şÌĞL£CP3‹¯ä‘õ47Q*Î)ÑSŒ)õ$§¬-cá’Äb~Æbrc™½Y!èDìÜ˜–Ğ÷Båá}×Ğp¼SÕ±a¸:R¸ªJ“oªÓ£ØiYš|7•&f\š<†¿ MË/¤ÉãğÒäñ6à	1%¾¥‘N¬I‰'%¾GJ<ÙZŸâ”ø^J‰(*¬ONµê§©º	ç§óïT8?Ãy?çgòwU8[³<‹ÿ2]ÙûÕÀ³mÀs4`±…™î³!øš„g”q¹ q.{Ìwå;å<–…ÍüA$Êoƒ\ù·¢ì…Ñpïj¸‹ÊÃ}ñ‹m¸KbŒ½§f—ÖÄØeÌˆ±Ë­õ±RŒ¡¨àWZõ«T}àĞ;rQÖ"©XüLRÿ‹Í‚§e8ª3‡^ë›-ÎKòS0’% ¿ûÁiu$ÄUtEá·Yfœş g–åğY<ÿİM@ä8„<—}ƒq5æˆ¬u8Â˜ÓÊóyOïåÈÑ@@D²éûÛ5,ŸœlúqU6½Öàr]…°ˆz»S‘Š´u”Òrºº>Bôú†2¢?‰}£qSŒèÕìæšˆ¾Åı)}«µ¾ÍıiŠhˆ¾İªßáˆæ«Rnì ]Œ8Ò”`ˆn\9aâAVfœH†0)·S©´ì>
¹µdúo³³ELQ\Ïƒ@9Ù	º>Òâïª‡®Ïªlõn[İ=Z]•­~¬Nïe§e¶úyÊVïcœ­ŞÏ_`«ğ¶ú ¾­>d>ãîôHMÜ=j¸û‚¸{ÌZ?î¸û"ÅŠ
¶ú„URÕ­>Å¿+l‰<¶A¾lõş®²ÕO5Ëgù/c«_VÙês6àó0v­ñGà®Ev¯ØUÎO?S÷/²,ğÓ¯"ºÉz9†İçjöJMØ½jËúš°{ÍZÿÏa÷u
;tÿºUCÕ]TBzÕ9®L$ë˜ÀĞ3yÆ¾Œ>ğ&GŒ8Éšß[,Ÿ'ù¦ÊIŞ¶	¼SeštôİŠ_j¸÷ÊPü6‚âûÖï1¿R³kBñ#ƒâw„âÇÖú‡âw)QT@ñS«ş™C±"¦;k)©İŠ\Iq¨Ø¾ıhû!V`ºE·o×S,„P‚Í>f=!LGì=Á\`#&ùP{
AZWá Â­ÆÒ1»Ñúğ†y°Ñò€U¬LL+RJ0â\Ê\Aq5C¢F¬KîQ`ˆâlp–öğ„EºP(UàÕÆĞ~f¨‚‡ºy
êsüÜnßLöuÄr"î’š[j£s7Ëç	-~-,Q¿¯ŞX¿44~åhÜÒ´ÃÍsÔ|ñ<¥§,}]!›Ğí(RDœ'^±[7µÂ¬œšàBÏ•}ÌøÍø›z3ş¡º{¾µWÙ=5}m o5âåôc´~´®Š7ĞwjösÍô‹m Ÿ¸~µÖ¿ùú)İ@(*6ĞïVı‡ü·‘QG0*NÅ«Yd!j–A†² ”–-)®SÕtuÊµ}ãµÀòƒxøh[{‡BĞæáƒy?¢Éµ9RD:	Âê™‚ Ãú1ÎÛS(Gó5%DFRgÚm*¢ã?ªø^Àş«Uü\¥Š¿šÿ8U,5”ô0Ş(±MÒt"hJuSŸ’çô¸³|ŠyÊ'ÖšÆ”,'Ö/Ñ`*üãıŸª¦ÀGí›SG]ÿ¨®§)wıkD…ÓZ×Ó©ëüıIÍ¦g³DS0K»úT8£µI­û£,Ñ ¨ Â™­z7U8”OÅ ›œ‰ÚÑê{Ü¼æXÚ¸¯YÅ’ãÑé^¦!ˆãY„^Tæq¼Âµå·5ã„(g{áñ@†,âh¹=×Á?*İY>¹#ø÷*Û›Õ–=›/ûR—}74-…tİ¸ÔĞ"–nŒôòQÀ{:ó‹‡ü²à¡ÒŠpªU‡H‰nÑèWEKí@ş%¾Ë®™ú|Ypá ë‚ys+=×ıì”r$$uîT’`jè`1Ü˜Í áaz@ø£*"Ïi@˜K@¨ŠÈ¿ªÓ¹ÙiYDş3‘ça\D—¿ "ÏÇ/Däùñ"ò6à‚1eÿ¦‘ªIÙeÿEÊş¯µnpÊş+¥l"ò"V½‡ª›ˆ¼(ÿN5‹Ù yqş®ŠÈ¿k–Kğ_&"ÿ]‘—´—Ò€5ÎVÊÂÒì%ßÙ¨çeXxÍ?Ñ‹ı²ÖqOuh™µåç½Ø¾Û )¦‰<ÏÿTß>ë€‡å¬ÃŞ1şRİ>5ñĞ×@4å4ÀÃòÖºŸãaÊiƒ¢‚Ã¬`ÕWTõCGóœCX<<u˜¶ vşŞèJŞ‚Lë-– <#Š—M…$ğåÅ0±I,`gË€ŠˆR`Æïk­LŸF#Ô0bØ¬Ä™G<ão­se–OgL5Í¨—•Ã«ØBúO¿Ë¯˜ãwÕ¿ÿh¼ÕÊøıÏ4e+‰Õ­ã5btL1›¨‰†©‰5­õZ©St ¨@ÇÚV}GÇx c°Û‹B…ÚÙ<ª£¦Í¥¸½bP²…%ræô3gF÷#tÙ 	9ûhâ]öí(å¨ƒœB{l$üiU*Îlİ3SjÉëÕÃÌ4UÌ¬okÚ`˜éWÜK7Œ03•ÆÛ¨Œ™i#Ìllocæ?j6¨&ff¦#f6µÖ›9f¦K1ƒ¢3›[õ-3[›(N•¥@ˆÓÁ*W….ğ.âÅiX‹lsÇ´ n[ÙrwDGÇ8œ+8k2˜×!Âœ8ÙòSkI[ÖƒüôeÈÓ2q+›óÖ>çs0çm~œ4Ó:n€åØãEnL‹ûjáíqìéÆÍÓÙ¸ÏùbYÏÓ#:ğœGå’eùu!¸|»eëXğ²ö‰|K`´ó’%Ï$Ÿª-ÖOc¶M²öi´ö¡õÖ>C•ê¶µµoW¡:ØN¡×i½Sç:ç#rö°}D„ÓjøÊD8cD„;Ú8;ÅD8ší\“w1"œ‰DØd­‡9Î”!Š
"l¶êÃ¡_b1ùeP¹;Š°5•€5¼†´TŞ¾òÂ‡ã}@Lõp¸Äƒ@aÓ@“deAÔ3Ò&…×†¿EO‘¥÷MÜI»Úy âq=­¶ğ,¡wŠKá6êæ-»ÛÓ:„8¢}D|Iaø‘÷¹%!éèõÈcæ2y…­1Ò 9J¬JW3¨ÓVvZ–®ºM3êdÆkŒãÔId»²N.]æ/HWmüBºƒo8ÕÛmÀ˜NfÔHckÒÉnF'³N2kİét2KJ'(*¬„ÆYõ®Ä_"ù¦ã#âŸI³›P&şîñïnãLŒ5³šíQsQ{Ú¢få¢ö²Ö{û¢fM…¢‚ø÷±êû:ñJL4 Û/¡ŒnšÅş9e‹¿X’Ø2ÌVåÚhùh(õÚ:1FğH¤‚AÀËå´A‹âwCã¥W|ˆQØjÈNæ8‹æxHD½ãÓÉÍ^Ü¡6¹Ã|róÑĞ¢k'Q»É³ó°Z‡'Ãv×°G$ 9²&hæ¨~”~´~FÏâA&¤éƒ‚´y;ØsøŞÀİíÈ©†SÇï¨ælV‰í-Æ‘š:éÀÉ+™©çÊÑöÊJ”r]3Â-A6®œÒj¹Üªä˜³
ÇÖÃÂœU8gp8ŞáĞÛŠ2‘¹©‹£#s7 ;!™ÍlšÍ‰	rNª‰œ¹ª“:Ù&uŠOŠá0¶Õ‹Âz°«¥Œ.µ ¥²€	â ó7•#t6f§&s]s=­äæ®Nòt›ä>I†Ü4ÈÑ„á-	5x"2rß™ÉØshì³8]NóT§pMá\ŸÂBzg€52Ç-$=ŠÁÀgÏyÉæÔÎ¯·úy«C_`C_èC_ÆSœ‰T qÁ8kÓ!“¡ºÂFÆå¼!§U8áƒñaEµL¯iRz jÚOÊ~EU‰‰¦×6[*y.J 0— pq…†ÁóUOàK
—

Õxnuz;-ŸÀó§'ğå¬“ŸÀWğNà+ùÅ	|¾á¾Ú¼Fæ÷ûy4Òµ¬Ÿhî®ci÷Ağ°ºŞZß ÖıQ–Ü«QTV7Zõ›Ç[ Ç[zîË&·øT¦4šëãAÆÇ±œfGªë´e_cöAêò•‚j0ŠdÙÍ	6æÕrn©G“ViòV›ïm>_æ6Ö9bQp[ÈnOÆšOcİ‘ìÀ;kîÀ…ªCŞeCŞíCò®‹!=v×Î<àîT\²b06f–xâ¦W=Ãs¶œ	ü–C8’­yH¼²™ovO²´ùµ´{ëqáêšî³5İïkbXç\OÂÑ‹uÈHF]@£>˜ ô¡š ıouğ‡mğG|ğ|İİ›šõH`î€`et'%ç—Mæz!I¯˜øO8¹ôÂ½—öÖRş.’=š,eA-å±z l¨®áq[Ã¾†Œ(œ3»‘¨ÌC
¹AÁ­ÀdXLç–=™Li!Mé©ºO×„î"Õ™=c3{Ögv³P‹;}Ã½¶P
2BJ/÷½T¾Ğ’‰«b†k¦º‚JJ|7í¶”ğ¦Ò–7†ëi_n&±B×_ ÅìĞºCÚŸ¾‰ÌíƒªnÖÄ&L}dÏ%YXy¾²zTAò‚äE	Ã+:ŸbfX´²6·K%ŸËUeı•åì`ˆ.¼ƒ6f/%óû¯æ÷r‚¹WjbnÑê4_µi¾æÓ¤;.c­@t–aéôgtÀüà;ŒÌ£uÜ’˜jâÒÑÜÜ…ç>¯Ù?M#‘»±a3÷àê<µgôşRµ­b¯ÿ%ënĞº_¯‡—Åª~Ãü¦/ØÅ+¢ G:tº#öFN†ŠµGñê­dìE4öÛ	Ìß©	óÅ«§û»6…÷4…êéŞC}¿ÏÊ§ûééşëä§û‡ü…Óı#~qºŒo8İ?±?Õ€ùé¾¨FúŒõ“Óıs–v´$O÷/¬õ—jİeÉé¢âtÿÊªí ¦Ö¼÷ÿ¯}ÙC²€k=¤£ ê	Uå©LÂ0ÖË¾I°µ˜ÖùmD)5„°¥ª”ò-ä{_È„â™ÛîL
Á£Ï­A¯lGhärn2(˜Ğ†m4Ä‹4æêÕÌåé´Âˆ:êy“•FÓÌP:à•üC²¨Åµ¨ë-jéê¢~²Eıì‹zTlI„`MøCÊqÄCD,¥NTÄ¿f*ÏäÅ“p„/@sâ”Ğ8%ƒ©¥=Ñ,y‡RÂY$¢*yç´lC7#[´|øàªMG^Œ3HñhD£ºÌ=çCKÒQ?„×ÃSKcöK¤%¤_ëi™*~3 ıî@š‹ábÀÌÂÓ±buŠº'8}dÓ:'_¡8ni³È)xfer˜ óÖ›º†·v4â\¬mÑ@'hõŒ!k˜2Ú¨cÍ“ğæG9k†ÿ™×SWŞŞ²í€CTÑü‘»Ä}áífEa›cJ•<âÙ	È—Èÿ¬òe« ÿË@ş·ƒü`“mÀ7Hš83;ÔBVhÅàÁ™n×ÂÑ-cáå-#_.PÙùÓn)cóëcS›%ë("ØHóÎjÜœ
¤=N)›ğÖóO²Ä¥´Ä) ¿Nö®g•íO‰XâTø¤liuúvZfû½R¶?5ëälşÛŸ–_°ıéğlzp˜³ıe4ÒŒ¬Ÿ°ı™XÚ}P#ÙşÌÖº›Z÷GYÂöQT<ZÏbÕ»«º=ZÏÊ¿ñhÍWßÍ¸Å—ê³t6›±Ü4İ1óô£Æœ¿«OÖËjsğ_öd½œ‡5.„Û™Ó†›KÃOÖÕ¼•ıò§‹¹ÙY„`–…—ëŞ‘öv^ë¾v½Ôlşš°[ÀÖ‡°[ĞZ/ä°ë“ÂEÅ‘¹°Uÿ¯ªºô-Á®ÓO=‹#Z2í\&Jó'Ç”È®y¥şıV@`tm Ú°0*¹¤8™ŸÓD®0’,Ã•`öíÃAõ\LôöÜ¨¥/ÂòÉ½=÷­¾5õ°µ-ZATî”[`h±CËi¼ÅËZ>ÇĞì ®%¬ã%K·”]&†@<XªOO$úí·ú–YWËÒÙÒ†¡~ô–©Ez½5î²éõ+“^ÜÓî“Fµk¬IËÙÀ+4z[ë>N+¤¤¢‚4úZõå4îiè•\+h…™qÈóö€¸æ¥Ù¡Ô8¦§R,ó”/ò/ÓTªa’…Œ\ıE–Æ@ş@ø_â
-.Âëô+YĞ_›ÏBdÕÆ6‚ËÓËï^O[°q…d€`ù	uõôV¨G]+V©kEÏJê"ÇáøıVìU8}¯Ñ×òq•2}­ÑWëzÕ}­æôÕİo•vŒÁi"B[:[İp¼r ®5jW?:  ®•«Ä5ĞF]3&®Ôn­šÄµ¶¼
‰kk½®×*)q¡¨ ®õ¬úúN\|WHºåÎ¼¯#‰eDÇÈ‘ĞIŒÀ£*òç6.2Ü„T;‰q¥”ÛEHÙE{V… Æ•R•›cÆJı—ï&_34kÌ6H(gEfÃz”Ó¿zodkßXk¯^ÂVR§›°Óòi¼jzbü4Ì_87å§ñfø†ksp‹
©N ^…¡ÇˆLWÖL¶,“éj™neİn]"ÓmœLs6Ø;bƒC`V”ºm-J]EãnWPêêÕx{x‡°%XÔŞÒ…K~›2bíÈî<¶äòËg;ÙDÖ åîl½íâ”»F Ü&´Cû&ı5·ae˜ ~)xK³u6\ågşªjÖÂf‰à3Â¦2€Si­GùT¤›EÅ&jµê»ªºåøËõ["©GÙÇp	¨ iÜä}Œx'™ –fE²ÑœDtè®¦)·±<?tkd‡X•¦ÇØœÚ}N›åoHƒ©Tëj¶$E€ìğ 'yµ<çOx;qn€{¡"…Ì{ÉlW×lÇæ³¯Ê»±$yU^³ÊË3›tg‚*§XT—aq-bq¼õ6Á±¸VLP»Gµ†&>±LP¨_"¨=¬³=c‚ f{‚JyïmÓY›ÓÙÇzØ×§³vJT(*ˆj?«¾¿#Ï§±¯iúM‰iN…z_‡]n¤9¥Œ: AĞ@MøÀzä´N•œ²Ùì³aP)møÎğ*™’Œ¸¦F<4!‰Ãj’ÄºÕ·ğ)4šº;;2j-uT½Å­W%»£mŒcÙyà4çË…xzlD2kk´ãÊ$³~N2tş?Şº=AİN"lç‰lŞmĞ±åë:êú$ş¯D‚'[§Ä$¸®êHrO[õ4#¿I~§[ë3œü6LÉEùiÕÏr¸Ë¶Şã%ÂKI¾õ´;b,2YÃz„Æ¬RV9G™c>¤C÷´m†L^®e§><k‚WŠ”‚.ª’Ô4
êĞ1²]ww¿©`™°¾e¦ñ³RXOP9'"…¿ª¤p®-û¼
)äw•ÂúüˆÖ×x”‰aãè¾Ğ:¾HÛåøbşËñ$î*—ò6	‡ô¥ü]½&o q/sJ%mR'/·¯ˆ©fCµ»²&Õ\e"Õ\m­¯qª”RŠ
ª¹Öª_çTó´t‹&]ó	‡gÄ7¹Eá]ÙX ¤ÚĞI JÎç‚!îf‘¿eé™‘ğËã›w)’„¨h"e·¸&{‘÷…ÿ·OÉ…(õULOÙõ	¥m$HŞPÒW)íFÕM“ ´•
qğæˆÒ6Öx·”)mÓˆÒnµo+QÚíNiµn-w¶7dvg-2ÛDƒŞUÙfU2»ÛF½'&³AjwoM2»ÏŞœdv¿µ~ÀÉló”ÌPTÙƒVı!'3>624œßRÛW2†ß5¦2ß†*õÙ0âEàøŒ·ÜÈ³Åˆ†¾ºNWí—'4kV&‡Ü9ÜÁé6nŠOñ-m#J%2kÌNÈi° öH=rÚ¢JNH«“œÇFöéUbGÔ´©†{¢LMC"jzÒú}ªDMO;5å|«ot¹xÆğºe ¨gkÔf÷¹‚ ¶¬Ôó6ğ1Am®v/Ö$¨—là­HP/[ëWœ ¶J	
EA½jÕ_s‚Ú—Â–B–å|h4æÿG>×‹Á¦Ã™(§E{j†NÅ|°ª±È™†[&«<1¢ğ9¡È;õ¿„4¶ĞÚ_¯G[Wï¹oØâŞÔâª÷Ü!êô-vZ¾çn“Şsßfüûáû.¿¸ç¾‡oĞ:¿o~£nKôaMÔ}d¨JÔ}l­?qÔMQ‡¢Bëü©Uÿ¬D Ÿ;Î˜k{7®°tö…²m Ì/kæVšåWan[½õ~m~£k¸JõÎÎß²—üò¹µzşeAá¼]´Õ¾·(­äG_I-Æı“-gû°œŸk-gúK±œí«ûìWõ·YCÕî÷šÈúÃŞÈúÓZÿåÈÚ!EŠŠ}ö·UÿGÕ¥QS`ğâ±–O/»L¶iö(J>oaQCFO>â$÷8MÃÉÓê6Á-{P†òÍ|%BŸA7¬‚ã›ö¶Zò”,Ÿœz{Çêe*´Àšşƒ×4(¿io€hSºéU*·'E¦jiGazÔ%9öÁ	] (Ó3Äœ0³©“©n§©NSoª;U‰imªÓiª)é®Rîôì;'İí5Ş,¤»sDº3ZÇ3©c“ngæßnk‘n7öÔ}Ğ.tgáïªh»ƒíÎÙĞ.UÒÕFM£æ“İQífg»DÉ3‡ÜDÒÓZÏ¥ÖıQ–¼n¡¨ İ¹­ú<æÅ©äé5„YeP'%ì´á÷À‹‘ß\dó&èÛI3œ/G_Ğ’ÌÏ’DK2¬JpØLô™,€™l0Æ­ÛiN=”÷0õnÉd%ãï¬ñÎÇ÷0†ÿ­9|suø~~(…/Ù"ro¶ ½‰"öÓXÈsWV7­›³Ã‚±am½LK8®Q²æ´í> ë‘Ì}Í}Ñv‹Õœüğêä·É/á“_ÎMS˜’ÒÙ>•(á	ã
êAŒ9;›³¦±ÃPØ˜-™Ì©IsZ*ŸóüÖˆÖR=˜—¶É,£ÉTæaêtYvZ>˜G¤sOÖÉæ^ü…ƒ¹‘_ÌËáæŞ6`ŸxÃ4k¤¾57Ìò¶aFrÃô³Ö+ø†™nfE«¾’ƒš±¦œ:•¼”²•`×lV©gÿšøUÅïª6èj>(ããb2ÜÆFY†¹îw‚Ü:ˆüÔÔ˜­L£EÓX#¡³5çÑZÇ@›Çš>NÒüë=.7EHË[bÎ©4A•í©˜P">ù~Ğlª§b¼sSX˜ ^âvŒê˜ÉØñ@Ò:BÏkÜ:°¡ÿ¡è‰ îk%ë¡u­]Vw­.h[Ğº¾ ¦µ-ÌN
ÍBv+Ã°l/À‚˜8Ìò'›š0OvoêÊpaSİŒ^/¥¼@<-è}ÇˆÆl½d#µõ«d²AMôŒ®®fC[ÍF¾ê)Ö´÷T#òçLT ··Ï†a²QR¼0»I¢mKú©IV„Ú°–S”rLnBj(‹W~‡5§…ìáÇ2E•’˜DĞoÌ6N 6J Û$B|X[•I2P¨ªLªUnÊNËLjLÊ¤6cœImÎ_`R[ğ&5ßÀ¤¶´·Ò€ù©¾«FÚšõ“S}–vÔN&5ÔZo«ÖıQ–œê(*nÛYõíUİ—øwhaG¤#È,;ñwUf­YîÌ™ÌÒQ½=ìb6iÀ:QZ‡±Ÿmê»™eA	aÃ­ë–ÒZFøZ&ñ8ÒÖ´[XÓ¨Zk£q[‹5íV^İ»ÚÀ£5ğÿ!Êmûî6(‹•àíwŒ›;ŠÚX1ut¨îØšÔ±›-²S¢ÖºÓ©£3¥GØ8«Ş¥ê‡¾©8aÆª"7mb»u”¢ÆæAPFte2AË†7íØ`R±…®°( íxjpIG‚X‘õ„€]Æ`i¸æè¦/0J#g¾/bey,[”Ã€;ŸYO_?`$0L.+Xe¨~,qş]TĞÇAdÌ“ÑšİIóQ¼±á
Ö¤ÔH*)ûÒRXi_uÇƒ¸›â°a–ÏÌúö1€çb ¢Ä-D‹ÉV¦(^;LNJ®'µóh–YOÆ•ìŸI*ÑóëXÖ–OîR8®zÀìn”3Ñ)ç =	CmAÜ3ÃïXı«	75È0"ô§I(R{
Ö8ñAqÓ#€»¯èH$Q²ÿÚJ5SáµG²Âİ´Â=ë­p|u…{Ù
÷ö®ƒ½áø1¿“ò!Õ¤tCšZEšmƒ§b/0ã¡qº[›sU®†i2;õVv¿ñ€Œ3GÈÓ‰”£ Úƒª-®-U> ]UhÃ\…wn.jÓcˆ<ÊnĞvºyˆÜ^7<•"â? Ä<‰Iï^rdá{Hc¶O‚¡LÚ·†&”1Dó¸ıCû—Îƒü<(kÆ¿ô@c‘»‡sà Zç@§¦qpqì^>5àğPXÆ©ùal^&¦¢Âá¬“‹
GğD…#ù…¨p¾á08Ú<&>º4Ò±5ƒãl¥{ğ08ŞZŸà‡Áéa€¢â08ÑªŸäß¨¸äÅ“Dp™x0ã¥›S×¢Ò¿¬Ã%¤¶QîÆëZL2’XÖ9L–—fHˆ"Ã±ğ$B/{4•¬-¯8 Y°[Ï7º.…3[ÒF¸j<¢É•–ãR{+%ùväüª;
y¼©¯ €(tšéÜNNH{¼PuJ=ÒŞ³Ê|N5\œæ¸X±à‰¤ã ¥>mã å•#× Â"$«-Å}C{gÅqêÀØøVû'"Ag!f”÷ ISJjD5ã›pY23|seğ(Ã¨£|Â¾	\onm(€'¨²:;eÎ”üR™ëJÇdÏY~PÏç‚¥l¹ucvz‚“	ÂÉõp²Wõ¢p¦áä¬š»wuzvu÷ïîşs¢İ®ïşó|÷Ÿ_ÚıØ€Æ»¢Fº¨æî¿Øvÿ>Üı—XëK}÷ï“î~…Ë¬úåªn…+øw´øJdßÀL¯âïêEaÍòjşË.
ûV/
×Ø€×jÀø¢@»Ö•VéUi¼ıä…=Õ÷õ,…ıò‹3EÜ`]ßºş·àoŠ†ÛKÃİ\nÿÈtêîÖO{«Ùm5ñt»ğ âék}§ãé€O(*¸ô]VınU8”iíóäïË¤0˜Ïc—ÛuÁ¾•İ÷Z9Ï‘½ç¶È…á\k²
Ì€ù É/ƒPFN¤NW*1Ëº˜ø’fÙ&Ì„@ÀÙ=\~$†î#`İËòÉ‰¡Vş÷4î¯­2á\¡lbşXõ@„Ô}5àƒe¤!õ!ëùá©û©Ù#5‘ú¨!õ`"õ1kı¸#õà©(*ú„UÒ‘z›#ñ](¤~AæNØÇI
«¼ññµ…Ï#d„4A9ä'Z</KCOz×´y4&¹·¢®Şš²’I§²a¹Ô.;&ÄŒ£°è‡â“á„c‘LKÌ¹
"$“ñğ:Ò¼dO%Èİ_@{:Gnxx†%ÉsÀ!Õ³ğYÎsœù¦óøİ§1W
…M†NÔÚ „8tVÄtk¶OÔJ
›NDGÙ†´•¡éİóÉĞ^È×àO
/Ö\Â¡å%Pğ’-áe-áÿ @x…ÃttX¬@8Psz•ÿ+¥ÉyÍÆú_eKÔÌNùz´'Ro”÷ÄáÑxÓº~+Ş«ÙÛ5÷Ä;¶'àx×Z¿ç{âˆtO ¨Øï[õí}€öå{÷ê½B¯>}{-ß§WŸzõ]—èvxÇõíGj5ÂmˆòDöa‚ÈC4ÛrDò-£†šğÈ*~lÓùÄ§s+šIUâjÓÎ1´vÛŠ°Ìd¿Rpm·ÎÉÿ|ÖìXaéï›zÛfûÉOK˜c«j>†u›F¢ËAP©#ó"Ğ¬Âä0<k¼VÎ}³O * |¥ÆÏQU |n@ùÂBÿaH§Ø æVO6ÜØ°nIyÅp÷e“o•V,‹6… AZ-øäC'€]Ş%Hø0Y‘ÕioÌ¾Lu˜õU½E]•ó¾¶E}£EUoy‡«ÓoÙiù–wL*ç}Ç:ù-ï{şÂ-ï~qËûßpËûÉü9ŞVGh¤_jn«_m[Ëmõ›µşİ·Õ±é¶BQ!çıaÕÿTu“óşâß‘œ×§±÷ÒÙß6ÈqAÎû‡¿«rŞ‘šåóçrŞqU9oJüN…OYÎc$ÆÉ£û;Í…¾£4ĞÔ,Bßñ‘Ğ73mçß
}ÓEÃ­á¦/wBÄg°áfÔpù,Q³™Ø,ÑâÏÌÒîƒN$ÒºYëYÔº?Ê->Š
^ØİªÏªê‡òµ-¨‚‰;83ÉH‹7tÏµ ïÈ6OKÑ¤ Àè#Á`üä mMpÊ‡ı(dÜÌí­İ‚ªÌÆDrÛ±Zïì,ŸœÜvRUn›Ã4g…(fÂÂŠŒ%}rÙm®7ÇiĞ¹Ë¸99ÂÍ<Öû¼1nW³ùjâf~ÃÍ)ÄÍÖzAÇÍ))nPTàf!«¾°ãf¢Ô&QŞPHË#š˜“ZŒamÈ’„0¾§`şªp§glKbG×c¤F’£³k„°¬àÿ®éM}YÊë«@-HgH+ôèL§™F@Pó^†1xRpÏ˜¼¨‡\„!†X9\˜£	Yq·ïa]¸Ü›æ†ç rˆÃa®ì| °;}ù ¼¦c²*’z”52Ë÷fÍ°’fuyñ²ÛaŠVòÍ_¿9ñ’¾¢”HÙ
=AXo¨G¡§V)tCk
…2ì$ 5®¥sôÄâ~ºhDŸ'jÈÅÊôyZDŸ‹[ßKÄôy’š-Y“>—2ú<ô¹´µ^Æéóô”>QTĞç²V½§Ó'3ˆZ±ó)Ï|é¹YLZ&aü"Ø¸x*•àLEGG»2f½pŸ¬E4Ö÷ÕCw9›eoÍ²zè¢Nû°Óò¡{fzèöeüĞ]¿pèöã‡î
ø_ÅmÀ•*øuŸ˜µ+G¨=U3Y¥ŒÚ³"Ôö·nWQ{šš­Vµ«jÏ&j×°Öµg§¨EQÚV}MGí’I£hÔÊœ“Ê¯.…`hæ\¨Ã³B×u†İ4/ }VPĞ2ùÈ-OB¾#a%ôúyàmTãQ•”ÍØwpè\¦c®Ÿğ,pk%DtºÀµv=":'±á0x¬ëğk2:\È1Ó"•Š‹Š7…øÂ>•O‚—FWŒriÅ¸¸
ómúV7¯§’>Ä¸fóÁ×KVs†V³~½Õœ[å@Øj6:	ïÓ²³àFÄ½OûõË66Ò:¤µ‰õ6ÈIë¼ØYppDågjÆ›–©õKZ›Yg›ÇT~–šm¨<qbÓ9ŸÓÙÒzØÊ§s~Jé(*(}k«¾c¶ö,b·bJìá²¡	&ÎÖ·0QÃ×ô‚*]mg£oï£3ĞYuš264Nk${³g@ÅÌæS‰î)v½1·ÒÈñ
½˜;a»´C2¿s4¿£ùÕ¸†]XßN6¿}~:4ä‘T!cÆIÄØ¼›ÂÚh—däs5rS>rPÑcI¢¢¹¨JªÍ6áuHµì(İ“ê£‹ål½rÚ¸8&ÕÖˆTÏÓÄw-“*ê—Hu´uÖ“êùj6f’¤ÚnÓ¹„Óé°Æút.IIE©îfÕ3G#ğº!Ù6x"q½ÕHW—LŒHı%ÈUÉÄ¶î„È$äÆ‘³ÎohãêQô¥UŠé²I÷I2Ş§ÅÄCTÅ‘U`’±.ÔX»'42±&\V=á÷°!÷ÔÕş"õ½{*Ÿğ—§'üŞ¬“ŸğûğNø}ùÅ	¿¾áZ½¿x@Œù‹5Òó‘;éA†õ+ˆõƒ­õ!õ+R¬£¨¸VjÕSu»VÎ¿S;«#l+ÃµúHş®^«/Ñ,â¿ìùäÊòµšÉ¶qÒ4Ÿêùä‡y6½Ù±	Z/ÕPÇ%h=¾&Z¯ªnıl'jxÆ©qJÆ!ì ‚$œÄ®‹cêdƒÈÕû)Öİ©ö«ã½kæ—íË4óÓYT¨_ÚûgXggÆp¹š( 9¦Î¶é\Ãéœc=œëÓ¹&¥{ÿ<«~¾#
ÌbéÂ)Š/Ø´¹] â
ÍìÂÔMÖ8Ÿ®­îæ‹lØ‹}Xz$ä9ù&ÖqI2Ø•ìÒï—ÕÄûuÕ1/·1¯ğ1é0oFúä"ª`š‚€Ù•ÉÀWià«ê­òúêˆWÛˆ×øˆËòåKÕ[a!Ê§å2½{àTZGg×&¹Z¹.Àõ5!pC•òo°ùÜøo(ÿ¦˜òo6R»‘¤v‹uw«“Ú1åßQş5šùíeÊGıåßaİSşµjv×$)ÿn›ÎMœÎ=ÖÃ½>›RÊGQAù÷Yõû9BÑ;ç<DAÃà^ƒaKÄ¼9xyj‚D·iÄ½¦_ÅJ} ÁÓušöƒõææ*Á<dszØçDG5ù@@£t’ŒŠä¤ –/•æ/mA`-6¤¹±éïnº¹…ÍÆì‘dÖ×kÖ&ÔõXMêº¥z\>n“B“¯—7¨ï'ÙSù¸¼5=.Ÿbü¸|š¿p\>Ã/ËgñÇås6àó1ÉÜ¨‘^$—/¹ÜFryÉZ¿ìär[J.(*ËW¬ú«ªnÇåkü»r\Âtë6Èíá¸|¿«ÇåMšåü——·WMxß´ßÒ€“ˆUñ6ÛwtGüÊv³ú~Çûêƒw­¿÷Ô_a½àêƒ"ÛØûl—ŸX·¨¯XN¬;£}û¡uûQŒ„[ÕìãšHøÄàs‘ğ©µşÌ‘pWŠ{ös«ş…ªz-ö‡"‚3åC#Òì3©‹!OCô,`Jó-3î´ì=®.’m"­¤R¥ÌŠ2LÌÌh&’ÜÒ7•¢ğÕÜ„—²"Ph%­Qö%Wi¤o¬¾bùä4ÒwW¹ù×Œo*Íc¬\x½F(½]ã}WFé=J¿·ˆQz‡šıX¥?Jï%J¶Ö¿8JïMQŠ¢¥¿Zõß¥‡êòáaÅ•İ]# rËª<ÓıÚc~»22‘±VïkL IvI5‡Â“D~@°"¯£Ca¦vşHGQÇ~OPu§`ğG=TİWEÕŸ¶È¿&ª•Š&G¨ºKãıSFÕıª¦€«!:ŸÒ›Îİj6
Ó7ÿ°´û ˆª©­õ4jİeÉ›Š
TMkÕ§SõCw†< 4¶‘äXbâM)Î¡E8”q°48B›å„Kìr³ä^>Å;4ºhÔVÎ;›óöÏ=Zí,ŸÜşy°zØÎhË™É—ƒ´ŠS0 µÎØ<’rˆYkpåß…<‘Í‡›ˆã5"è°ÍöÑŒŒ	·Ñ-f£šÇÄ@ˆéë"á^“S¹ÌkDº¹í¼'ÕÄòœw¾{F·´ ÎÇ$ƒe£Yr*z° ]¸.õ|¿1ş«ÏLĞ˜Íœ@û^A»[=h?T•f1hw´«ÒÁ}êtVvZ–N¥ƒÙX'—fç/Hsğé`N|Ãy7—8·,Î;*Z.Ú~l›[
Åù<ì%?ùî×œæeY8ù‰öŞ|6ÀüñŞ{@Í¨¹÷´½÷(÷ŞBÖzaß{¦{EÅŞû¯UopbılRq„a£²¡l†·BıÍ¨
UNŠRpsª„åCË/òã!Ì¬©Øl¥dÚËyíÜÅÎÒñÁi¸WŠN©¡‚ÚÈrTÔ‹ñ®á¯=J³`Âä6»œ¢]9©õÒHf‘„,Ø{Ô#ËÇªvN‹\\ÿvN‹sÄnƒ%°‡4›%ø¿’Ó’6ÖRŠ¬iç´tD‹«¿eÊ´øDD‹ËZ×=cZ|DÍzÕ¤ÅF£Å'I‹ËYëŞN‹O¦´ˆ¢‚ûXõ¾N‹«€qzXğØS‰Çoc¢I”œ@<¬{f€7"+ówƒ^DJ"•[a*ˆ®:²ÂÑIO¤İ=ä@bC6“Q-Lna¦ø|Şí€¢Üzñó¾©9b½¬7$_M9³£È®	Ïày¸³æ¦axTâƒ±?Dš9Ú¹O@1İga…(9£`óÙò	)?*¬õ«GÊOUÏ³-+:Z¤~ƒÙ”ÒC©œÂç4@YkAâl·Ir-½KccÂ…MlÙxô°ªB(ëÉ_G·´#•ª|<ÎœŠ¡Ká:e€ŒÉÉÓW®·À§«\ÅØßø&oÇ’&ÆYm½¹çœzÎüJ9u¶ñ‘8¶ğÊŸ—aNéÉ`Ñˆ³Ø …¿R3 w©“‡€·G—|Gû»i"ÍÓ´,È8ï,ÇÀ2®I®KW1È•HcÕrr«ÕƒÜ3UÈ­n[Ã!÷Oš%ŞÔ|‘¼4ƒ%µj$l—®qAâ)Ãd?”pk‚hÂÈÑ
üÂª¥è^¼tÉ®dCñÂIŒÖ‹]ÉnŠPçĞ‚e-YĞ¥8Õ”Jr©…"¤ngî='¾~sq%ÏßkÛİO0z›eğ=!ğ¬¾g«²Ëš¾µ¾ªìò¤:]›–e—çRÙeÖÉe—uù²ËzüBvYß ÙØÀÜ0fçOi¤j²ó?¯‡Sk=ÈÙùó);GQÁÎ[õM8^5½¼bNÿk×"Š¬ûö‰<¯ä2E¶Êí"‡—³—û²¿¹fu¥µ¸dgÏ9Gá” Ófˆ[")¹Ü_¶YBO¦›×#‰ª;jÚÚ´¼<˜(Ä3İHW!‹Pãà	–†çÕô2fÍÂFØmî1Òêñsµdõˆ|2¼f¹m0Ãõà»ä.¨°¬'ãÊ¬òkFÔ&u+ãø5<;È¨TdÉÌâ7g®e¹±1Û2ñ3‚ñVõ`übÆ[Œ·q_EVòÊNWv í÷e’iwƒ›­ü¸©ší ‡
 l)˜†T: œpµ×Lxÿ"U0YÂ©ùvù­(w_+e*EÄ,¤fVd•ÀGÆŞ~ğ–Ó•Ï^Gš×pNLQR6X>¶@fo©¥{JÈ
ŸğíYdÈ‰õ"‘ÄÍ‰2=……ŠÍ]#	ñ±ôŒËMaLĞçbıº©Ôğvz¸­ÕĞ„%l[^ª2àíŒ¶¯É€ŸS§;TğË)Ş1bÀ;9ŞÙğ.%Üd‹ğó©¹&nø2àk=Âğ+)FQ¡ZiÕG©º©–[ùwjà¼«òjP-æïªjùÍ²ÿ2Õò«Uç16`»Œó´´“])Wì.rb;ËoÆ/j€±,7ã×"Ãæİ¬ÿ,ôÿo›;£á^ÒpãÊÃı/ºütÙpãcd½¬fj"kwƒãëDÖDk½‡#ëõY(*NË=­ú^ª>p(ãR®$JJ™yyä"DUëpğnš%›Ñ¬¶KHÓ§½mŠLÏeÆ@»KèV,KÅ@U`_1Q,=2EÀİ›«‰Tb¯híû°|r*±7ªw_[Ü~¾¸+Áq‘ÌÆM‚œyBJT4!“Éƒ*#amĞ8ùm+ÄFrŸˆáÔE97‰™ğmáörÏ	es	©ár»ìòtáp]}Eƒ¹$gj‡-Û¥rEqÅ‘é_½³-Y1…KåLó ¥I†ß­Aü¦XA~.”:ÓõBhmk‘Ç…Á@;“T…¤æ3’¿Æ…å`®DiœO.ÿÀ>³°ÄŒÌñ%wm¶aMN§m)Ù }ÀF{¬Âş	!¼*B8 !¼YUXh„pP…CPU»6¯E
—ƒ£İúšF<¤¼[ßŠvë¡ÖõañnıŸš^s·a»õmîÖ#­õQ¾[ßNw+ŠŠİz´U?Æ	z^İ—Î÷–Ç}0W$»
/Áœ\x­oA¸NĞ.4fÇ&]9®Äß©Büx›é	ˆÓÖò]K‹1åBYybõ74êIe¨¿Aıdëş”êoªÙ©5¡~šAı=Bıtk}†Cı½ê(* ~¦U?Ë¡NÿG{Œ‘ŠÀìót‚¦Vá~fÀ,zü"hxåz2A­½ìæÉ ÀÆé’ {âÍ'ˆxKk;§"Ş¯òÀsmòçùä/t» ' “wÈXÑ·¸¿uHì´ÇøèfcvÉ:‚º‰ÿp…Fˆ9eËõta¼8X"EĞŸN±Åã¡Z%‡õ1nÌÒ85fç' x[ ¸  >¨àBÀE€%pÉóZØ	äLÌÓ½C¨íRXe9‡ä©ÏÌö Ç`-ÙxÄaêAö6Æ¥à<³®Ö)¥‚ÒMÊ¸ÙÔÉæä£1pÍğœxØcŠó@¨½8c3`@œœ€¦A"6.K°å6ÓÅöÖOU ç>6?zâõp£•™öÜ.
Hy›ïÑ”Â5Û€‰&‘ôâï—ÔÃÁ‡U÷RÃÁeÂAUãğ®:½œ–5¥ï¬“k®ä/h®â‡«ñ¯%×Ø€×VØO‰áo”×E¬ç=Íæú2ëù8b=7X×7Æ¬ç}5»©&ë¹ÙXÏ'22²Ö·:ëù$e=(*XÏmVıv'ŞãÄzFÃâE”ÔÙ‚­—“Ã°®Ö6&;Íc1É¶GUIäönÂÎ‰¸k"v¼ÑL+Ş&¤§BH<wÏš!Ø*ÌíI®)¤„Ã`ø"I¼^Ü‘ÉÆõÈäÓêV½ËV{·¯–*ß<½ÄÉPğ„+ïåÔ)Â	Ù#º»m½&hc)ŠÔutílrˆH ÂbåĞ*õ±ü¿Ú˜Ğ[Ú`³Ö¾'Yà‡Zà½õøYu÷Ùï÷."W5ä-4„šBˆÛl3/ë#ÛLÂµ/°Öje¤.€eà*]=äÉ¤(°¨qŠNuŒTl7c¶í»uµRioötjD­0´şbıèÆ‚‡œ›¨™¿ÚôÜã?
Ë¥–cùüå<H_´FmÍ$„]‹Í¦C58"ƒFi–€ÿ#ÿÁzàÿ<±G3ğ?ìàôµi0”„ ^,ÖY²‰®˜`ÊƒÆª„¦%–ÍåäÈ£x¸PSøçä/ÖñÓ„ÀÁóCÄø>Nˆõ$ZÚŸó‚ä~±	¾Œ!Ê‰sÄ#°I€õ±€õh=`}QåÙ°°ª<ûuú;-óì/Sı$ëä<û)şÏ~š_ğìgğ<ûYğ9X\ã™`b¢¢ŒÎ¯ïÏ³q~}ÿTSyeáúşUÄ°_´~_R¿y³ÏÔìe6K…_ai÷A_“a¿j­_Sëş(KŒJPT0ìÿYõ×ÄîÒ/	\&Ï~¸Û°°)Û‚1ÜÌã×/&öNÇ;%Š[Æ@*hR0—B«…ÔØÌ’ídºNwdR§ê¶Í„Î|ÎÛ‹—É5Ëé9énĞnœ.£t™¡ø2¡ˆÎ
}_ş$š¿YÊ$¤ctÓD<²…kœIxT+ø@‘“ÉïÌ>Eà6]°¹øbÒ¼zØ0l²1-|”A K‹ªœnúü‘ì±r<N¡©uù|bzI=±7#\¹›äR‹ )p¹ò÷ÅæñÆä~çùSŞHöÓç"œ7ëí§oª7¢·Œ2Ş®78¸¶¾Eˆüw":ÿBã¾[¦óo#:Ïx?¦ó/Õìƒštş¡Ñùw¤ó¬õÇNçß¥t¢‚Î?±êŸ:+A‘N£ARa:sVŠ°Ph#¯½-áÜâìğ…‚zS=Û1TÅ­¼™Omvr3!|g'®’‚^Ê	È|ãc„Ü±1û,AğW‚Øçõü}Á_H¾¬Ë¿¾Šğúµ†ûºŒ×"¼~cı~ãõ5û®&^¿7¼şH¼ş`­t¼ş˜âE^²ê?;^w°ë"şÃf*†á”óÔB
d©¢ijŸæ&çà"2(9ø3ã:\oÂyõKşoµ°_ëÿ§êyõ›ÍüwÍ¼z^}§Nÿ`§åóêçô¼ú“uòóê/şÂyõ7¿8¯şÁ7¼jN7?8%>¥så{4
k+²´û _d¬h­§Qëş(KÎ•Œ­útª>pèÀK‡tªf`Äâ†Ù1ihó”ÛÚ#yì	3=øˆë¥åG0–oÈ*'J ÷€s„ÁÉ•Ü4FJ½Ğ¹tâ’p i‡Õ+ƒ‚…Íö«ÂÉ=­.=²é	HÕûƒÀ7ËsUoÌ_ëGƒÏLŸï	n‹€ã\İ[Â&?èF `>L9¥‚ô—ÂÒŞÑ `Ó¨ºKÓË`ÊoÄOğ+8›„Ö±¨9ĞËv¶2Z\OÛ'Ê†¤P¶q÷ŒV¶…³÷Y´~ÍsE¥ÿ¥p'^Œƒ©
ıĞ+é¬5«G6sÏÏnõàù[³<»;<Ÿ¤¦±9ÄmÎÊMÍXlx¿@`ˆ	Ç(õ)Pn9AuBUm‰Í‚Õ^n„6
ôI“÷æf¹Š›bİƒ@»bMTÄÊ%ŞÌ­ÅR4åÖ=¦ÍSkAİÔ˜Íš ê'j¶P5ÂRı^e;³ æ ªlçgu:';-³?R¶3ëälgnşÛ™‡_°yñlg>pş˜íü¢‘¨Év4¶ó§ì4­õÂÎvşLÙŠŒí0ã­zƒª29£ûƒÓå%î"(—°Õ”z°,æEÛ¢ÖùbñJ~S³Åk®d	[Éß\É’Öz)_ÉßéJPT0Ğ¥­ú2NĞwÊEÏg
µd¨Wše1’/¶+5ƒÃ{$ÈË# –à0”:Âäñ?Y§ÚÛ‹+OBüó4Á_×/Ïqª0z%-)÷î}`=¸·"ˆó²	ÿ.¸õ¬GÀÿTwz/L£f%9s'1ne1·óÔ%F5£ßš->Ìm{mD,<x%(´Ïã:Úoş…{Z¶\²¢?´¢ŞõV4Å´£6\6Líc+ê[!Zzev¶Œ†ÒjQ2î>«äWÊå#ÊıS÷+Sî”Ó–½ûV°VŒ)÷/5[©&å®l”;Õ´ ÜU¬u§Ü©¦M~”»ªU_ÍÄ”fA:‹-ÖNf7+Gog6n©Cº\é4J@‚êĞÔÍApı™«"ZcõEkÉkÔCÑª(`kXAÃOI«­GÕ‚±¬¡çºV=SGèYÛz_'FÏ³³Ùº5Ñ³¡g¢g}k½£gš=(*Ğ³¡UßÈÑÓ€Ö•oåû ulîq½³T^¥ P©\×ÇX)Îe^àÉSä¡a¾Ğ–º$QÒš’/¨à(µäA¨óÈˆù¸%õY¡p•öÂ,ƒkˆ€ŒÑ²qBHS
9›Ô#¤iË„D/üAıÁı©¥oÉ#PºîNN)®ÆÀ¤ôTª[+mgi{V2)ÊİÜJ6W¹ÚO¢,3K~ŒÕz”ŒĞc‚</T°Ky`@i›T'CùUFXƒÒ•Y8¢pÜi1Dï†¸u<ª˜ñZnü“mš@x*Ax³z®ºU77oñ/¸éh»şGoYŞ®ÓGÛu+aëx»N­fÛÔÜ®Cm»ÎÀíº­µŞÎ·ëévEQ±]··ê;8Á<NƒšÛã-OZXšˆÔ±IËN™ßâÀÉa‰ÊwwÏóûÍ0òEˆ 9áGöôˆëá(³ëVâÃ	Ñ ñh§w_Ü‘%íY!BŞ+©Û%L%~•ÍvL°> ¸S=¬ÏXÆ:3-ìl`ÚE`ªŠµÓªÓ&vZkgšvÔÉCŸ­}|Øï³a¬“‹µÍü±v8¿k[ğbípdLÓi¤Q5‰ Õˆ`fÁ®Öz´ÁÌ) ¨0Qk³êcTİLÔÚùwÅûy•¥³¤Û´İ1óô£`&ÆßUµé5Ëİø/3QëÆÁF-<j\£3°SÖIÊ4ıäRôê»‹eAŠ%ß=m<Şº ®ÿ.?»³ënƒºkÊù°3jØ‰¾¤€¤=l¬=c$Í¤º{ÕDÒŞ¿Y‰¤}¬õ¾¤YS$¡¨Ø©ûYõıU}àPÆ¶•kĞõqÉAÁC¶“üŒ’t‘ Í´H•½d>í”æ›\˜ÒŸr,Å²6PmÙ\E¤§˜Yk>å“ÓSÌV=¯²Eì‹zHÂ\‘´OWZYMÈÉ'<Uï÷sz>æYã|´¢p¥„âl7˜/‰/dbÓûŒĞL­£Ñ˜\£Q§-ƒÇÌ’Õ[é:Ãl?¦uïiw©Ü‚,ˆöÙ!	„º	B‡ÖƒĞìUf:Ü!4FÊOOdŠ²j&¼€I‹,±wt“rœîì m½t'\3\XàÄ×"œSs 9`£¡‡ìIâˆd)³h)GÖ[ÊÕ¥eK9Ú—òN0Òõ'<Üùé-ÕT‘´¤&/NÖBÌÒ¸DOöÔ0Æg'ûDòİÚÜøËËc)¤B]ÌZe–Ä7ÅğzîOŞÒë–/¯v›m6‘–Ğ¡äáÃ½Æ­xøöÈ"=€zÄµ7;&^wïØzÀ›³<&:Î€w¼€g<úş]áÑ+/h<f®À£Oâï*UÓ8ÙŞ\eÍO±O-xšÈà:C uÓ æ¥F@½„×¹Õ‘ñûtzî0ôµ†MCŸY=wyh¶gÙĞgkèêi;»šŸÃæåÓvô´=—uòÓö<şÂi{>¿8m/À7œGÚ€iÀÉ½µ^ÌÆù©0‡¦r	ËÂa4o$Ê]jı^¦~ófsªÙålÆ·VBÆ…éXgGä«+Šóñ¸Òz¸J=ôGYr9FQq’_mÕ¯)!íÚ„Jú09ûu6ÈüU××BÕ\šéªæ¯RÉ6àM¥oöi]´í¾–Zqéìn0Ü­µ†›[ÃİV·@u¸Ûm¸;JÃİéÃ­‚áp­;±®­ÍĞÅO\
Q=v×:vg$7†!_Qq€­¾¤j,ÙJåáÈŒºzß¥³»l~†ùİ]k~óh~÷ó[°:¿{m~÷•æw¿ÏoÙzÂ»£qØÈ1;3<gÃêŒ:¢ù…¢ì›ÇBaÖšÇ¼šÇCÅ<*Ïcì ‡mhØİ-<í¨MKÍ|êâQïû …{¡M³¦«é¢‡Zl(ÉIòİ*{‚M–‚	½6hà%wÌTuêHŸ²öO« Ö‘¯¹¦év—ïŒù5«gY6Ô"Ñ†zÎ:^çÍP³Ø,1^xÑ Úƒ›é%kı²Z÷GY²™PT

dÕ_-!ó5Gf9ŸÛò
dƒ,°öz-¬-¨Y¾Q`mÑ*ß{Ó|KVùŞBjş6›Ÿx¸ÀÒáÀÀbä{³CH´0œ.d]´ÕÇU-{‡UÅşNuó.Ÿ5êìN„	ÂŸÃÉŞg	Xâü‚%~ˆom?²¹|CzaMâ“ énwg[Kõnì³tö©Abq‚û3ëâs÷â)¸QT¸_Xõ/Uİ|/ğ†î"jí×Vš¯Øf&R÷İ7JW}HåaTª¬ ó€ì+®&tÿ+ |Íò\ĞmN#’.QU|c‹ûV‹+v¯‡š2­óMñ»Ï©»AC~Ï²°)–Ì7wÜÖ÷¡ïëóS4Ü"îçòpKEÃıbÃıêÃ-5”A¦ j3”IhúSÈE­:”æJ25Ç@‹¿±W´Ø§Oö»ËÒ$–?¬×?X–ÄÒ„vã²¿¢)öĞÿ.OõK±ş±Î¦XÈ ½ÔP†Mâ¡É'9\“dj¼k’Ãpë®IN‰Vù$—Ï¦âÏîƒ–á$ÿƒ¿ÑïÔê·?ÊœØ$§aÍm‹j’Ó², õK1ñ¦³Î¦Wgy³ÅÔl6KxÙŒ6•e9•™¬õÌ>•eÓÍ…¢bsu³ê³¨úÀ¡‹ñAx„Rb´ÂÆ†m;º–Ä6(Ya·ñO¨İ9d´×geùäv@Ïªô?›Í`vŸÁ<œÁ ¼§#)¹Û´µòİvdĞ%4èœõíUt.tn´™ƒb±šIoûô¹ÅÉF€X˜î
ÃÃñxgpÌQ–†÷½ğfÅR ‘›D–l;°€y’,©Ì[oÕÌg˜ß°`ñ+
&æá…¤_mjÕİsÆ+±Gcâı™7ØÀ,]-¶£LÄÃõlŸ-Lz)MzÁz“^®<iJÙ¤Ö¤%}ô¥¥ÕñÙ±mˆ\úh°¦‹¨i$}ÀÜzxÖƒMré£o>UuòÂÅ¬ıâ*(øì¤^R–`ùŞ[FÓZ’eaË.mÙ¥¬÷¥Õ{ŞlY5[†Í’-»,K»êÇ-ÛÓZ÷Rëş(KÄâG£U_NÕíÆ×›Wn|?úØ +ñ£/Wo|=5ËåæÀÉ
Uñ£Ÿ¸‚¬Š½Ô|E6/‹+NRüX‰UKâÇÊümâÇ*øâG–@üX•_ˆ«áÄÕm.kÄnÔ$H§âÇ@ƒÄJ÷šÖÅZî•Rp£¨àk[õuT}àĞ¾8ÌÖŒ”`‘rYFuA©"½Ó¨.*©K9FKHn1Š„£iÁ×Äœ$PªƒûÊHXb"¬šg-qƒjjºğÒÕnyF´êcd‘êæ;²êƒ‰j'Û63şSƒ-¶»iÄº-ØT¼.Ó=¼ÊÁÖ´	Ã˜>“(¸à8ú<‚Kiê7ØÀ3¨mé)­˜“³Àşêh3>Íšá¬Ü/ÊOiÅ³º<jš5&e9]-%'bŒ`¸ Š™Mpà…ùXf#ÌùˆÓ…œƒô—(g5Ë_%Ü©xCjvxV$9`G"º˜Mğ±j ­KŒÎËåD³ë±|rçåÊUÎ¿¾ÑãN÷˜…A ”Çô9fDSZÒh­díŠ/ipGŒ 
•ßœĞ†±FëHØa–*€”
Íí/³7azSF‰(¹
Ç´Àø”æªxòŞÄô¸‘ùÎ¹Z´vÀuÃ6½›êÁf•ª4½±ÁfÁ¦àò“3iÄAr–İGfYàôısNOÔ¦6Âf5ya_µŞ\¼ğ°â*¶jª‚Ú"g‚>$âoKgx[•ŞÖ6à61Ã[^#/
w»­ñºÕÈë¶³ÖÛ;¯[-åu(*xİV}G§­ŸMª =ªƒƒ¤ÛSÊÁ…cÄ_Š$ïî\İ9.Ò73”Ô¡ë@$ÌAõ2´´4“,ïjAË*BÖÙ{ BÍĞé(";Or“i€¥ò¥·©­%ƒëùàÜŠD@ü®İ•Ï5}­%iz‹šì'ï\&W¯
=»L›S	=b¡gu<ŒW„fk:\M%ôğ^(½Œ¦úf-l“K=k©g„êSêiŒ
ûtÂÄV›Út+ë×¤+P'òpµôUÌûVöéW±¾+d»1­Ebm½µ91­ßrÆDiE-ª½¼‘P¿tËé°ÎÆÆt½’šíV“®3›ÊÚœJ§µçSY;¥k"S—U¯ê&2Màß©È´»²N™&òwUdZY³ÜÃ1Œ®S™ö´÷Ò€U‘i5ß›ÍË"Óº“™öaÕ’È´/›È´ş„È´?K 2À/D¦ñ"ÓA6—ƒcH÷×$	NE¦CëÜ‡Y‡;¸×KÁ¢‚aÕTõC_…™—#Ó¬ù/c©:§ÀÁ\TÀ/!aİp;£E5=`f—UBò¼œ£:ø d1—ÔÇ†9ƒ®kTúòuFôbª£Ğ’BÃLÙÒJéñÉ½^"ˆ¢C}UAõh–OîP_¿z¨c;Ö!vR4SY!Á¤¦·ÎÀ~i€Q%[†Gç5úVÃa‘!Fë ÍÓ°‚	KŠÈ­eØ)–g|v\²ŞÕ´Şãë­wƒêzO°õèë=ëÕûä‚&İºCXùUâëa¸í´ ò´®((˜ƒ]5äI¾p?‡á	zÃPoë~‡°€Œç{=#àaó¤d•«k•'×[å†ÕUb«<ÕWI#n.3«Ü–m‰e¨]<·hêB²eè„5]ÖöévéŸk{ÒA@OçYnö]
9æAÛ'R¶¨¤Œ<°s*ºwÆ VzÈK? È5¿1;-ÓÓéõÀ´QLg˜Ît0QÁË ò”è ³+Ì2ƒEBß•{±mL³EAæWr6Èİ\e_WÔ ?%®zêçNf O…õâ»Sgèº¼‰ 5ä\¥1;+YÜ -îìz‹Û¸züŸc‹;W‹Óñ¿I|üTÇç±ãÊñ¾5½@M#åóìB6ÉOÿÁáô¿HÕyú_lí/QA¬[Î|sİò¥ì-—ƒ×Ô¤.cYƒ7ïË­ï+ÔwŞl-5»’ÍÇU,í>h3'W[ëkÔº?ÊŠŠãûZ«~ªÛñ}=ÿNïlÍÃñ}#Wïµ5Ë›âÀÈæÕãûfğX=¾×Qó[Ù¼||o1Éãû6V-ß·ó·ßwàOßw²Ç÷]üâø¾ßp|ßcs¹7†ôºšÄ}Òéñ}¿AbÁı€uñ ƒ{H
nÇ÷CVıaU8´Æ¢ë´teZX(uuÃYH§SlÍrŠ\¨ÉO‡áítdÎÁskXævCğ rhôÀ‚¾J9h°_F8úBµê†F
uÒŸŠK?£+¾.ïëXBnoD’Q˜§àEIk¥Aôû¦¢P]Ã*Qêx˜N¤#ÿœÖ‹M4OD^(\™€›LˆÖÈ¼Šc:¨
	Q=ÖB¼~ñ0wQæyÊ#¸v †f¦¥eí#D^$X¬'|?ÊòÉ	[Vyëc†ËÇ—3Ğğ7!kõ,<xzë/lŸÜåMaÿ€©Ù† ®
ZfîÖÁMØ£N²	|¿òA×öøfº5*ƒœj3ö¾<õùÜÆA^g@WX±¼¨Ã¦í)ÂéĞüîÿ2xÉ£JBp —~£ˆZ‹œVÀøCAŠŸHÀ¼¾Àüd=0oUóSæ§ÌW˜1ŒîI_òÁM0°kÀÙ¬ÓŸ²¦EuËklØª]fcİRšyº€cUE xz)—EIyø<AD5¢7]$š)Ì”YâÃZ(hËÃ‹5g±ÑÚà`ó7Ã”‚\zV¥}ÑçT"m#HWR+sÌ „›ZÂ8—MD\H4É‚;.çx~CH¨Œ$†›xÂ(KH”e÷Ë/Ek–WìÁŠ «„TÅ¥`8éÌŒ_5fÏ$t°èàÙzt°u•3:xŞé J/eÅìsS3PÖ•D)¯Dìm
bt¡²_tDİ[¥ÑËÿ=8åğ¶6jıBä’Òõ<¦EFŒíÜ“Õ%(iwTëXUTİ‘ m%U­`ò™]s…À Ü{í"z¡ø…	¯¿ }ß	¸7¸_¬îmªÂÕKî—n	WCcáj#uü
;®W¯ZÓ×ÔTÂ_~©[ÙÔı-rÙj» [½®Ú”­Ş°æoª ¶TÙ2¯€c‹¬ğo±³\FÚXSz›eA´Ú>­Ş±®ßU×y³MÔì=6KD«÷YÚ}Ğ<ë?°Öªu”%¢Š
Ñê#«ş±ª›hõ	ÿNE«OmƒhõWE«AšåçoàcÇªhõ…ø¥¬ŠVƒÕü+6/‹V;MR´úšUK¢Õ7üm¢Õ·ø¢Õw,hõ=¿­~À7ˆV?Ú\~Š!½©&ñs€t*ZıbØ™àşÕºøÍÁ½s
n¢ÕïVıU8ô
Ş•¦yMÜ´$(Š±Î/Ø¦élÕAÙËrÙÎVR„£G¨"÷ÇŞ‡!£m÷õ›À^,Ä JJbEYnvÁ_54†«˜%°›0hqá\«1û“Ä’Í«¿X>9±d—*ŸüÛàğÃáÍ !
À°Cª3DlÇ–']WZcQ<p1¨á-tˆÖ?é¶jA2tVáÅĞƒ‘ü6`Å–±X;¢Ã€S%l‘—iÀ;¼äå)wú8Vp¬Z&r°IAôä7ØQ7aA¢LkÂÀõÙW!·¹ 7%Ë'¹¦*ä¦B@î?ø‚îä°
½ I@ÈƒĞ	Ç1y:\ì-÷óø¦¶.=¶¶cîpŸQö‚MÍ¸[j/
F:7(ƒ[¬)9úGÒàgÁbı»gd÷;{“dI<_@¤ädoUöş3uœ-œiêgX8Óp¦sà´ 8HD)5ìøb$•’Ë|Ãh¨¤[‚VÂÁÈÖ/¯¥—ÓTœyá¸c³é“%Ñf¨·„æêf´%ÌäKø£„_PSrÄ?‡:’ªO¬££YÙFH¸@‘‹ùãKW;¤¡ÎæV¤;’%(Zª l/„¾Ú8LÑĞB:æI&]çãÑàÃÁqq!£ÿ«`FbVùèi)Û´H2I—¯+<ü©®ULô-ÈäpÛ‘§ÚC>È%»Ú˜9ì–l·z€^ì,ØîØgrÖ+ŸZã›z€õ^öbIZÀ>â2íY:,Óø„:¶ï=~0äK;ÃxGéj/İ2Ù!7®Lt<¶;‰X’Eº¤(FÅ%^Ş´p³fäJÖå‹ÙĞúao"“"*­!ÕV‚Õlõ`ÕRuk›İ`5‡`U=¤·V§s²Óò+çˆô•s.Ö)¢5ğ£5ğËhøCûùlÀù5`!NñmJ>ÎËçzªØ:—Š¶Ñ\dY¦FFÂÔBÖñÂê8o6TÍşËf‰0ÕÀÒîƒFñt_ÄZ÷Pëş(K„)§û¢V}1'1jñ¥ï…jÁ_äc_cs¬u÷^ŸÅ%%çÑ±£íb<Ê$ì“¢Œ…ç\®ÆÅ®¢À9ÅsÏÕÆÙâ	™l+p,QLZ«ÏíKÚz—ª`¯Œ‰¼t„·í4â2e¼íámYëºgŒ·íÕ¬WM¼5ŞFoËYëŞ·Ñ)ŞPTJmeÕû:ŞÎÒˆ¤#ŠÛ†gºùÊåˆÔybƒıéZ\ºan–ìg+®!Ğ‚«!m|£aô[;gÍ<‡»Ú¼iCŒªR²åüí °ô«‡¿¶*K\ÁÖ½¢¯û+;kğ–¯»·_Ö…+ÜéXØµ@“eçŒH‡3Â“Ü§ ¯¥YPA®µ}¼ŞÓ¸ Üì[?€\³J§’<öthù2\
PË;U×ÓÅD¾I	Àü™Ñ8jŠ²LÄ5R>à..g+% ÜQ \¹(ÇTo¢«(û”º‰¶Ç7ÑÔñªì¸r]Íš®®¦É+¿l¶Éï¢cÃ]t€êó.:Ğ:X³²i+êù×ŠöáÎšÕÚå}¸[´×±¾×÷á.j¶^Í}¸¾íÃŒûpk½¡ïÃ,İ‡(*.£YõUİ.£›ğïô2:Èé—ÑÁü]½Œ6i–›:È’Îêet3psX=ç†©ùl^¾Œ›äet«–.£[ò·]F·ÂŸ¸ŒnÍÛğ‹#p(¾á2º­Íe»ÒÍšÄöÒéetƒDÁ½£u±“ƒ»+7Š
¶·³UßEÕ½Òa+&z!
†+v,*öÛ(ìwOĞ_t+Âs2’{Aà”âG[—ÏØ¸vÊaÒ$'>jç†ªú¨jÏ¸öZ+A«t'ì5qåÑmt¸€5Œå“»S¯òÁfÄpÄBáiƒiw¸•léª*p¾eXL`&‚jŞ‘y:=E”	¡2ÃÑ ûdcÖ’¬¡EkQoªkikåk87¿Q+.x«ğ&T•Î.iušÙi[ë¸q¼@(Ü†Ù*ñZP¡ÂÔ³“&Ÿv8•íUrÍ~ùS»aqeäóD½÷Ø¢f¯¹Q—]5ûöîÓ·1kM?B‹ßµŞâw¯rßÑ¶ø6-^ÜwbÌ}Gªã1Î
Ê†åíÖ´CMÅ}é&C=`¤ÍÆ²mÎ…÷\x7µ#Î¬£NÄ¾¢»6!ğ.ÁcO¹(:J3ëbY`÷Š8ğxëwBÌZÕl÷À"À‰Æö&KØÃZïé,aï”% ¨àÀ{Yõ½Uİ8ğ>ü;åÀûÚ û¼W9ğ®šåşv eŸ*>À<PV9ğh5?ˆÍËxßIràƒYµÄáoãÀ‡âOpàÃX|8¿àÀGà8ğ‘6—£bH·iGH§øƒÄ~÷±ÖÅqîıRp£¨àÀÇ[õT}àĞıxaÛ¸6±ÜÜÚI¨aº§¸‘ 
í}éfMÑi]<ÂNyp9”hı+³w´œÔLŸc95När"¶:F8‰å“c«ûWYÒÉ¶ºS|u§cu•G±b(„_O"@Sİ“@«÷í³·Á{ä%»*	¨²\–¡)^¡ê¤‘§7Ó»âÕ(
›LïY’ü¹1;5Yv»–}Z½eP]öé¶ì3|ÙŒ]á‡§w4m«kxÁfİ´<Ä,¢Ó¢çSòPëÄÌ0ÒĞ)Yí‚ÿê	--£ğë»Æcèº|kökŠÙN•LÂ+@³£¸”¯È€+¸Ğp¨ˆ¿Ô˜™@¨C:«„¬BèlƒĞ9¡]ğÈ3Îz@ø<…õîDİJXÎÖ¸;É†Ş~¯2£ófÔÂwù™@˜•i`rr£°çFıyGÜ0'?n^£º dŞ¦,@SdœãcğVŠó²1;7ÈXä¼z 9¨
ó 8@VõgC;isEb_!Ø*cbéÄÎc{0N­R’à‘ÖÓâJá]eT|wŒet)~)íÙ#s…,Špüxe€	6£©s#AŒƒºª,ˆåêÇÆ†õ!¸‰˜½ÀwŒ…8ÁWİñ ¡æ®ÙÂh1×	Bflº™ã@Ã:P”åšM¦È*Rg*V¹ı4[ÍÙ…	bvb.ª‡˜ƒ«ˆ¹Øs‰#f¾ğÓ3=Œ¤€ÛiD‹ko°Ë	=mc+n°qÚ"bpØézÏã©›¡iÈzZø¼¨BNÆ9Ç¶¬‘“‘ÆaÜ_)Á‰°†Œ:ÉÌÕ2“šÉ¬¯e2óÈ.MÀ	ì—Õû!Uyîrû»ä¹Ccy®S_É+·é«¬éÕj*yJDÊsÍı²kØ âBÜµªL!î:k}½
b“9‚%öË¹Ø[.ÈÓ”ndYäˆ¹›¬ï›ÕwŞ¬KÍna³Dy+K»:’’ÅmÖúvµî²D‰¢B»Ãªß©ê&ÈİÅ¿SAînä¨ ÈİÃßUAn¼fy¯Ãø8ª*ÈİgŞ¯«‚Ü5€ÍË‚ÜÑ“ädÕ’ ÷› ÷0ş„ ÷K È=Ê/¹Çğ‚Üã6—'bHï®I< 
rO$!¸Ÿ¶.qp“‚E… ÷¬UNÕeî³µ¡½kE82,“9Înä…I2mÕÂ?2¤lÑ°fkÖÅ×ÉaMÿ¯¼¯€²³HÚÆƒw‚C¸ 	Ã$8g2™$C23áI`qwwwX‡eÙe—eaqw—eXü§ªû•¾“û}ç;¿œóŸ““{oOkuWuUu‰G5Œ–«²%‚5Ó$>¥µÁLùÎ¶Ä§MÓŸeùôø´S«Dî9›üó>ù#ü:æ$+ ÔÈÂ%Q^~E¿ŸH`
ì^°J"ñ)­ ZPf´UÎ$é	ÁÑJæä…„õ½¬ï@­ïÅFë;­º¾—l}/ûú&`}LCé/ãX†C\ÙaàİG¾ÒöÊ˜‡Ì:EcP…ÉÃ¦aúF İèCM-÷ºñd5× e¶jÙ+ÉBÒB^m´Ó«dñ5[ÈëZˆÈâe²øuü†£iQÌ}Óš¾¥¦‰’qíìm¶‰”ñ¬@ßQ}†}z×:xOFPŞçw”è­€·ÜÉ­;Á©o•>ÌÓÒgÕìC§³aù¿«„å`Íø#Ÿ1Vtv‘°$l¢Ë–6Šıv(Rä°ŸHZQßŸ²,PäsJá şi]ºf¼‡6ø¨x0ˆf™)ÒÛ49G)šÃç¥1Õ_Ç8·Dõÿec|©1âÔS³¯Ø,¡ú_ÜÎ#ú·µşF­¢,¡ú(Ê©ş·Vı»Â&ıÇ7©™æ{äü°9?ÔÛœÃ5ËóÍ9¿Jõ²Ö€Uª„šÿÂæEªATÿWV-Pı–TF|ÕŸ‰% ú3óT|ª?+¾c.³á£ é#5‰^¬OH§Tvş©÷ˆ	î9¬‹9ÕÅ@”%àFQNõç²ês«úàQ9ıÈÏIv>’- Í<\Dé28Jë—åÓ».ªËŞ¶¦ù|MÌº	7şü2¶”ÂdUä²ì	ë&†¤šaöÂõQˆ_>2Ó£5ÓÍôâêL´™.ä3}4@?ä³‰>LuØr
ÿx§)ş:yŠC?qÁ![¾Ë+$ò×!8¢e«–tßD©‚ÏÔŸë½…·¨{QUœRhš[o’µláHÇH‹4Ò%U -j@ZÌ´H»­±=Â<£½pÕeß|³%J¼ç±¤İ²L4Lc»‘E*zÓQ,7õ/®t÷Íë‰6 åë7'3O@(3¡ºŞ>‡¯Çë’WÕq©ß‘³	:wèK®ù©û`n¾Üzy
«Å˜+˜/Ñæ—V­'–4˜/%˜W‰âqêtivZ´¸,µX†u¢õÄ²Nùšœò-W |}lÀåË”ïx´B |%ñŠFô.'Ñ[ÉZ¯ìDïò”è¡('z«XõUl^´Uwß‹5Z>Mp¤ÌÄ‘¦çv;'ñ»6_VŞµlµdNĞBVo´WTÏ~_›é>Ó¹Šg_^e8£…H·†:Ë˜7ìÿ¢¾´±ŠŸÖhO…gäŒBMqTJaÈÜr ,`=¯­`aË¤åœ‡,43uHÑ:ªÿ:rt‹$&OáœSN\AşAF'w9§ak4Ì2óø`µ¬– úDzÍF€¾²
èµĞıĞL¿ZˆxofkÁ¼£1[N‘b £3-XDJ'NÛĞ\Â²:B²‚D¦†fœU¨OíøPï«‡Èœ;8qàİ¨eı“Õ¤Õ®İhµWUW»­v]_-sLÇÜ‘Õœ4â±ÁøxÕäŞ5+ßÄğº¦lL	2÷AŠÅ,o­ĞÁ$2HHP…,ÊfİÓ\pÑußŞğêñ…g	°¥Èâq:ŠAÈ#ğ²zÏ.Z0¯I*UkÙz	|N|ÖoŸ««RÊŸ‚¤”kÊRÊ)êx ;®(o6´¦©©¤²­TŞ´uì×MË6f£(¦\Ä”MÔ€bÊ ëa°
LLÂï=‹)C^8áaü]SNÕ”7õ)cI×WÅ”ÍlàÍ5pYsÄ”Üˆmv…ÓÔù–,rÊoKrÊpë{«Ğ7Å’f=Y­79¯(©l]åt²Mq”J’Êe¤F‰“;CÍ¶e³DRÙÎ@w#o‘í­õj=e	ëŒ¢\RÙÑªïTØ§}Ÿ*’Ê.6ÈMav­·?gj–£òı¹©*©ìfî®«—òYj¾›%•›{”TödÕ‚¤²›~jo|…¤²K ©ìËOH*Íø’Êh›KKÒgkc¤SI¥Õ qÁ=Öºçà¾%7ŠòK{¼UoSõÁ£®¯ìaìqJ’Ä±üY1Z^ÄXĞCñÑÖÑ=™¦¹¶›1d/A+x3 Wò·ÿBpFÑæsJã•Q­(ø¹1œ| 5¼eeûqÉ%¹æAiË§'×ÜZ¥Úí™ı‰ÅX@>«03°ÒŠï8İÈè%O“h7p6§ôüÍ!ªí«Yî “ /¾È gkşf}Öİ•À1Ÿ0Á¶À™Ôõi‡[d	{ÌçÛÇÀæ`Sğfæ>ï4å¦+W— Çeº(0rGàsàÎF ¾­
àIàıÀ+À[B‡#wö1¾Ş4	’lY9xôĞÅ­.Å\wGÖji{ı¼U„¨˜À)İ"³B¯@r8;•™!Ÿ÷|"c¤éÖˆÇ·ë¨Š=&2X‚eÙ²–4ŒniãîpY²çiºmÁíÕ›w²mA·¶@7ïå›÷|u|€“É¢~pŠ5ª¦%ı`‚4!ù"ÛÄ‹÷Îpñ¨úTÓdüF‚ÌŞâsfuËÂıwWéf:Ôú>¬L//T³Ã½,É7G©¼›¤òHk}”“Ê»SR‰¢üf:Úª£êÆAËïéËÉq6È=áf:¿«œÃEšå	rlÉ=Õ›éDğ$X½™.Vó“Ù¼x3İÛãÍt
«n¦SùÛn¦Óğ7Óé,ÁÍt?q3‰Ïp3es9»éK4‰s¤Ó›é\ƒÄ}÷yÖÅùîûRp£(¿™.°êªúàQûòåáº¨€qwÚJ˜Ÿ•Åf¥Dâ¶P,B†’CFë'í2_CºN<^Ói)YIJ¤¶BtN·t«\ª^Ìòéİ*÷W‰Ş%6ûK}ö‡úÓ‰yGEÃïà%O[:XGÛIKàL·„r£æÜÁÄ%ü¥!•xÛÒXœPHÑÍ –]–,î2-îòF‹{ º¸+lqWúâEw_–¼óœnÛCÂe/±Ÿ~3¹²=;ÃÎ<Él'	OÊb^=èÈtA˜ošÙ˜;Èİ3ê	>\²‘Q8âYº(ö_›“6+˜€jŒ|LÚ¸\vUòËò«üÁ*È¯1_ë ï*h_å`(›L™°èYØÃr2OÈ5Œ¸Xcë^£àØxÌäòH'o™â²QÈáeF¹ü‡ğ”]—,è
-èúFú}qA”Ç~kºA2jz#¿§Ôô&£!jz3W©é•šÆ-ü“%x¨JMoµoÓ€Ujz•šßÎæEåÛRåÛ¬•o¿ã/Ì;ù	’y>ƒëÒİ6à=°b2 *OîuãÕ½ì ^|Wk:÷±,\|—.¾û­ïÔwlvš=ÈfÉf±Ë²ßÿH*üµüƒZDY"¡(§Â[õ?ú¹ûÂLõÜeÁ+äÂ&'Ó0T*p‘]Ã¦CÀÙ(8£å‘·\78°í%“g£<Ç“#¶ŠvBÁä›…SàMåt$uIô÷Ü““Q(Ü©èb8ZÓÄ: ó¶€?]œckÙŸ’3­àüH£3ÿ§*ÿÙ€ùæ æ–$bbE-ÆœWà²¸ §Q9Ì†(Šx,–N²#ÄšõÚ—Ãb<‰8PojÅÏÙŞHÔ)'Ÿ]˜JnTô37$Óƒ¶ávåãF-{4ÙuÙ_ì‘*È3ıÍA†^JçOÍŠ*†îŞ°tÈ,­$£‰Ğ•í'…øùªï‰‘Š¶tèFS¿
i­C\xçbú1PŸ!‰ñD$-fLTH|yx±ÜÂ’gÑÃo¸#?¢aW-Æœlí¢¸2Bbo$Û’û®ËÁÒÈc"¦Eb<÷õ‚÷àıç*¼ÿnğ~Òáıñ0Ö]I/G(¬éÏ†™ĞÉˆ<@&ãókrsı3Øİ1íğ#ˆ™òğNÑl3WPR`)œ^*Qsü€1®“§E¯kˆÍ¦µcßâ26cBáöd`šZ:[<•€ï·ßÓÀ÷—*ø1ğ=ëà;&¾"‘<NdJQpõ¬XÔçöBÄo@ËÜí¤vÒ1-ß(8‚‘¨³»S:jÙsÉ2oĞ2Ÿo´ÌG«Y/Ø2_Ô2«wéêô%vZ¼KÿšŞ¥/³N¼K_á/Ü¥¯òwékøâÇë6à0Şw7i¤7Y?QA¾ÅÒŞ#ã÷¶µ~G­¢,¹óPdw%Öw­ú{ª^N	ÀL]ÜkäÉ•ßçHqN7kN°,\İ+]İZï•—r‹š}\w)ŸØRçRşa­?õ¥<.EùõıO«ş™ŸÇ©¹É9d’4ÔŒŞÃ«w9´£XDçâıãvºw§Ê¼p*Õ<ÑRâ‰Ëü ìóäøİªEÑèø=QÅ²Ùª¾ôUÑºüLâ^Y%{då*q/ÍMÇhtëd˜Ê›hRE_@Kš•ÔÑ#ÀeĞ[Âº—a®‹¦oÙ¤ÓZöU²ŞÛ´Ş¯­÷ïÕõşÛÖû¯wÊ[!ô6èÙ”Î5ˆş¥ÕZJ¶ŞnqÊZ°ğ™å)DÅxb
´€©;'À<‡²‚S.^( z3÷…éƒ!¢;Kßi÷U‡Û6>`á:ªI)—ˆÂ—Q±ÇÔ²ËR1r.Aoœu"ä
n@¨ÄzÚ›ZömİÛİïA÷É*1ûA÷{A·JÌîP§?°Ó"1{*%f?²N$f?ñˆÙÏü1ûŸ˜ıjÎĞT"f¿ÓH3¢0%f3±´÷ˆ§•RßÑzµˆ²„˜¡(§ ³ZõÙT}ğ¨*¼„F÷B‘#ŒEF/¸Ö„È6Gˆˆ"ŒãèÕŞÍsã·½¸Ui-,²˜rfO­2C!¸şÖœá‚r«òÜ{)Æñ‹~v’ñğÀåÕ²^EIEs§ 7;Ë§§¢y¦ŠUsdætÈŒ¦€‡ÀSìEp	°şéF,R>‹]Î£cÁİë şÌ?Ö¢Åˆ³>ñë™ˆô…o	`»Evjˆ´lq3á˜ÙiB§Œ—7,˜i—N`¼"Œêj†[<IÜCÈ]]4. WFœ2öÂcåñåEŒ0Â˜ Xô&«¶ò*h¦È¹=…;B_æ/Z¼7”ş”¦-˜;äş Î•C÷àQ‚=~ş\Éşİ¥ı›»Ñş=[İ¿ylÿæõı÷oX+HÃ ø@åQ¢ô
“M=Ä’¥r‰4À2Õ²±;¡ãâëUÑt”×é£Ew
^[rx5	Ø ÔÄØƒöÇOkr#/+ãŠÆÊ6êRœeòpá¦Ò‰\(‚r2ÂB !ƒ²ŞÉİ­š¯Ñ=Wİ ùmƒğ:œÌ‡!•à.b!ŞYKÒÆ!S½iCÄPE“eTÒ'´„ÀhL!û(¬ àÒÎÇ­ÖVğ^ã‰FµlÁdy÷hy5ZŞóÕ{ca[Ş"Z^õŞ¸W.ÊN‹÷Æé½±ëÄ{cqşÂ½±?qo,‰Ïpo,e.]¾7îÓHËÔ½7–µ{ãEŞMÖz9¿7^Lïå¯}¬úòªnú¹ø½¢ŸC¦Öm—‚~n%ş®êçî×,WæŸL?÷RÕNbpUØ×[J¬Æ®"×ı€º_eë~¹Äu÷µŞ×(ÃîA5«Õ…İš¶¬W»µ¬u?‡İ+)ìP”ß¹ı­úÚª>xÔ#0Å Ãî}”'†îš„äâ 
` Ây`h"äjg†Bê¡­ƒÚZHÖpÍŠSxõäuì¨ÄùµRRŞDßÀ<JPµ‡æ„±¶K&c†ğóP0è±óšRô…05«¯Ç1†5ÑDNÁöŒÍ´ñˆ+´Õísíntú™S±a»)Ó*:cÚÔ9šHf<…›_7¿ß•Å‡áúÓŞ}uÔÓ—±H>ÍnFT_’£ø®‡:Jğ…Ü88a,E¸ IkØz@3^‹hË*r-aFnQ3JV<Px*ìŒI‘‚
åÂ^Ñ´8ÚÏrÎÔ‘ZœséÆÛàÉÖ!J”x¯ßÖeùôx¯W«WÃz†!ë;†Ğœn¦Óá“À+Á’™yÈ%ù*¦ÂÒ-‚mjf´júB \¤’Òu«‹ÀS¦á±M{§hšÒÚ³×i^™!ñ‡‘jÙÉ²Ò²4ZökÕG¶ìDu£:DÙ¶76êóz ª›Ô#ªĞ4åDõõ"QebÅÁ6à¨‡ÿ7Êÿ«‹¡ŞEñá˜5İTMõğÏlYÊİÜÎc¶[Æçÿ·ÂóÿæjEeÊÖÍ–*hà¥3œEšşGMm+–šşv‰¦om]o£®c³?©Ù6K”B#ªï¦ok­·Së(Kä(å÷áöV}‡ÂÖíXgë\q'äİ°u;×ÛºG4Ë]ò­{·ú^µ«8JVÙ‹?«ùnl^|ı¯Ç×ÿİYµğú¿ÛëÿøŠ×ÿ½XÎco~‚óØŸóØ×æÒ\†ô_4‰ÑÒéë‹Aâ}‚{ŒuÑêà~?7Šò+t¬U§êæA3\úxK±ÊhàfädÀIáòß‘|ß½ñÉ#ì›‚ëVàÓı:0Î=ÏE”ˆŞ£ZwË§Gô>¨½ılM|MkB`QTzÙ·çvLt®+ëåÎ¸ß÷ _±0ñÈ´HÙ´¬¦úÏŠ¤4»kåV3Ì#hLŞ5¡©}÷©5íê–^$œÅ¨?¦óÔFÁãœ÷Šåw°©ÚÓ}Éù\z¾è½Î~vùµÅèn
$nŞ0*‹5?…b96ëŒÜl½–ML6ã¯ÚŒöF›ñau3:l3:}3¦á€á”(ÆŠ0èëãûàà€ŒÖÇy`S®ĞÂ-‚•ªÚ_0°.-ıİªÚÆÑdß°¢Éİ0Ío1ÇÑÀ e“’e=¦eíßhYUo˜Ì–Õ¥eÛ>™ßÁ¶3ç;ƒæ5›¤´ñNYwkÖm(úq Vğw•yÿ›&3…2æıã*ó>Õ†¦as*?/†¤Îäpgä±Ïdo‘h?®bY õŸ”Ò+şÆ8XT©áj}[…­¤ÂÖ¡¬…­Ãø$ïp~‚äÏ@ò´Ò€q×HG³~r¹c ü”ÔîXk}œZDYr¹ (§vÇ[õ
‡q˜»’˜	‡€5Ñ¤6Ë…áFü†•á´5í‡˜j­Ó ^ª£¬±ÌÓ…çwçÓ=\YDÕìÄä0>©UŸÔè0ş³Šc'Û²Nñe1¨¹¥á ©fdò¬\]GëTYãàMQ¾‚&í“Z´nip yZVÅzâ,¾àŠzH	ív»Twb“-Â¬Zyå S¨(Ğs?±<&qÓ
Ò]ß+NMàğ”àpZ#8|V„y Óg4ÂüMéÌv<­qÏ*bÇç%Nèlàœòa}FÍÎ­{XÏ³ÃúëùÖú?¬_¤‡Eùa½Ğª_ä»ÊxÉäİİË$×ã+b»uà¢åP«é.Ù,èCHÇ'uìfàîëÕ4"d]C`O·w`Ç¼ëv‚ˆugğÇ‡L4†IÎ ËQë*C>¾%€,×š¶iå%ˆ ú(®œn´úcä9‰†tùBDsÆ¬ºN-»8ÙùgÊKíü¿ª;©Áê²F;Ÿë5./íüs÷ŠâÎYÚù+m€«Ê;ÿ¼š]]wç¯±ÿŠ;­µ¾Îwş«tçQ”ïüõVı·¾ó—açåÖÌİÏ3Í…»ÓØ7s!Ş¦h–HIÕC?Ğzˆ[¾ÀÂ"+0Ôyˆ¤¤HëÖ3õ™iÓ½ä´neˆ®“cÃâu]ËnHöòçÆF{ùuu/o²ÕßÜh/ó80·”öòE{kq/ÿ]ºãn³n× Õ;î%µ¾ƒ­‹wÜ7é÷;Ö‰wÜü…;î.~â»Ÿá»Ç¼·|x^ÖH÷Õ=<÷Ûáù–‡çkı oÓÃƒ¢üğüŞª?ä‡ç‘ ûF¢e‡²#TÜÅ
“¼[ŒĞHÜ28'îº/Heµ2™ÇÅŞ*™Ñ: ıˆgdï1Ù’còŠÀğp£cò]õÒû£­óO¾Î=„$ò!#fhì‘älJ§_é<©È³`¾rEñdGR5Yh¥ªz$™ø«šøŸMü?Õ‰ÿÅ&ş¨Oü@L\¯êçÌôşmjgˆgğ²!ê)ÍÁ¢àÀ-!ë‚g>ÃSR}K;#ü•V­kÙ_“u½¦u=Öh]ßWñöo¶®Çµ®éğ¦¹1æ#ò|¯kÜ¿³,ğ¦?”ğöIà)PÅÛ7Ôúi¶.âí)Ş>Ã:oŸå/àísüŞ>Ï€·/Ø€/jÀ8Ï75ÒK¬Ÿğ¦/³´÷ˆŸˆ·¯XëWÕz ÊŞE9Ş¾fÕ_÷c1:?&ÃĞ^ÎŒ "ñ$İ”vdü@òíi­]‹B"±Â~µìdûßÒòŞl´ı?W·ÿ-›ÿÛ¶½h‹ûNiûßÖ¸ï·ÿ—Òüğ~y7ŞQ³êîÆ‡¶¿r7>²ÖûnüšîŠòİøÄªÿÃwcîF³ÄÉ	Ìs‹	EX7ÓŞüh]î__²İ«%Ó«eŸ& Wkøg#ÏĞküÖ#C
ïÁï~f“üÜ'IÙz¸:k4&ìÀT„Ä7Æ*1›¿ä? ãôİ™"vEl±S}ó¨qóğ_ş"YÖ{ZÖ¿-kÆê²¾´e}åËº•°§fÅƒ¹@£7K®#XÌj>Pe¸M)øSË*ñÛ£‡|s®( ZÚ²–îv7¿1Õ¶îA7b*N:÷É³RAÅp{˜ƒ¸sX~Ú Íú:Æû‚Æ¿Ac¦*4¾1h|ëĞ˜ÈM.?rYp±ƒŠ™ÑÎoæH”•—–gˆáÉ$…L–©ôÆÌ*‡ø«q`¹×Ô^¿x%ªªeß%+ù@+ùO£•Ì\\ÉI8®ßÛJ~ĞJªôûCuú#;-ÒïYz?{éw€T:²ŸX'ÒïŸùôû~‚~ÿŠÏ@¿gXNÎˆışH#Í„Â”~ÏÌÒŞ#fíŠ1‹µU­¢,¡ß(Ê)ÆlV½—ªuæÓÚìzNÓ4•yó	jÛÈ™#À'Õc4Ì-pÛOÖòR4ËkåÑ8±Â™®œåânÊn˜Úän÷ø-ê³Ù¹è’æõch–OOó:[q‡)€Ïi0˜K0˜°~¼ææñjıDãÎÃ²Àôê(^?0¯Ğ»¼£ÿP³ùêîèü¶£³sG°ÖúÎî(Šò]Èª/ì;zéèf,×K¼e5G}`Ò,UIQæê4&øÒjwİa¥İ¦¤&ñ~,ìt½nŠf€Ù"É>~*À,Úhç¨ÒœÅlå‹ûÊ¯4š£[…>³;…ûÎAêb»L±Nì1Íx¸v…s‰ç
3OêÆ °„Ëqå$-ë¤j]ÃP©fî#õoÖ% üS X² æ¬`)ÀÒ€ßzwº‚ÔÇ\Ş3ù ?/DiTV>}FŸ|)d¦(îÈX9!D8Ù¹`•iG©–-“¬å3­eÙFk™«Š”M¶–å!å)û”òs»|)çHIº¾‚°¢¨Òõ/Ôz%¶.ÒõyRº¾2ëDº¾
®¯ÊOĞõÕğèúê6`ß2ø—FZ£.¨˜—T`Mk½–SyS*€¢Bn"«ŞßÂ‘~ª(ï'Â™…‚–¥€ñ¹ø´À!œ§U*¼‡DMi}R‚$DÉùøRë_§Ñùè]=ëëÚ×ó"`1n Î4ü[‘¾P¡ºººq6×OÆşJcoĞhìùªc°±úØ»aìô‚cî?=©aÕ-#±İmwÈÜ8µ	ƒÙí>r…û†É´¿Ö´7j4íù«(µ±M{“F(5 ¢Ô Jı[ã.¢Ô%”b­‹Rß¨õ°*J-˜¢Ô¦%”ÚÌQjsG©-
(µ¥8¼ŒRßj¤­ê¢ÔÖ†R¥¶±Ö#¥JQ
E9J´êÛú®3\•4 ÌÒ³LCƒò¥grG ®”´`¬3–Æİ)å®ü¤Y÷RøºáÒPüvÉaùNÀØ¾ÑaY¸zÆw°Õîè«=«µ·zJò:K%/]Ÿ|qª<ª Ô<r‹a¬C•ç§*ht³ÖšDdº]&•;c-Û)Yâ´Ä-q‘*>ìbKÜµ‚Œ‘„ˆUÂ„ï5ânELX´„	»[×{ÔÅ„ÔzÏ*&,–bÂ^%LØÛ1aÇ„}˜Ğl.cÂ©¥.&Œ1LXœ˜Ğj­Ç:&,bŠrk—qV}¼ªÛ3r¿ã™YpŠÏÈ›#‚[k¶ŸµD¯­î›{öñˆÃÃßÕwäŸ4Ù‰ü“½#/Á1Ç/3~2oPjÚmÜ?“ÌÓº]kÉÖ8ÈZ÷%\»y“bê+	X¹¢'ˆŞŸ%Öµ–u&gîgMvR£3·d­ö·%d¾„ş""ÒÿÒÿÈº!	Ç NÓ‘Ä;|yRlÔ²®d>¿h>“Íg©ê|ºm>ø|!š»®®İÒb˜YòòÑâEòX†­ ç[ÖÑÁ
6ÿr9LğšÈ,…SpPV‹|A&‹µlJ²¶_µ¶©Ö¶tumÓlmúÚãÚÊFã:ñbDePËø6˜PÒn”ï„A€±ë:xã‰ÙbpÈøQqƒÜt¸¾©*1œ1­ºQ±ƒ’UÎ° Wù›F«\¦ºÊƒm•‡ø*ùŒNº:Ô¯ÀÕSP_¾X¾®°ØÜ‡­İ6ÔN ßàñè?P SªÛ B`Âa™÷²$¨ÍæŞI°ì¦™#€ÀSSËMà0£àpX#8,[…Ãá‡#
»Í•8ÎÔU/y¸(É„8Û¥¢"n§{»[€ú:Oo°q’±µd¤è»CB´2óoòA’±ÜqœjÙ‘É*gÒ*j´Ê¦â*i²y´­ò­R&›Ëõ¿íÈ\1³:>Ö©hÑdó8kz¼šÊds.Şt0Ùt\ÍN`«h®¹¼ÈïÊ{e'ª5%'Y'« ~´ÂÜJáö•$³h^§²,(IV()IN³¾OWß±Ù¬jv›%Ïg²´÷ˆyƒe­ÏVë(KÔ^(Êo°s¬ú¹ªn7ØyüÆ9ßY)\]ğwõêšM³¼ĞMY©xuQÚ¼È¼XV¥Í^j~	›í5W&C@»,˜®€Ö65w›a’]Êª{ÍËøÛì5/ÇWØk^Á¢Wò‚èUø‚èÕ6—kÊ]“¸6@:µ×¼Î ±
Á}½uñ[÷*)¸Q”³Î7XõU}ğ(™Ó™âŞÌí%¦µîßmºÉ.™FÛBi“`›¡øã§Mâ£’\mİ# ¦‹­Â>7›‡v¸O¸ˆÌg O-»‰ë()çĞÒofùô‡«VIÎ-¶¬[}Y"½ÈLÃSØ+!(-U@QçÄì— 	J)6„y¹¡¶cº!Ò‘OÊ:2/´G/ÄsO ZN-»-YÌœZÌí³Zu1wØb~ç‹¡òhWÅ–03c=ä±^…Ñ¨ÚÚãóK›Şo,K9ã°N„ÒV†5v	Qf)·ÍP^£f|Ã‡íZvg²–¹´–»­eõâZ>èn[Ë=Z‹¡÷½üŞ“ã}v´û$¿Ÿ¿«H>·&ó ÿdüiß"’“<>hÃş^ÃÖS$ûçv±·HìæÑ`Y ‘k”ÄŠ‡m€?j€*™W­ÿÄÖEU-+a¨³ú3Tü…Ÿ â3Š¿Ú€iÀ8ÏŞéo¬ŸåÇ”k’J<a­ÿ®ÖQ–eåTâI«ş”ŸÀqÍDKáYè-Õ#Ÿ¹ Aig’0d6rPÏú/¨éˆĞ[‰<LÂ©3×FDOJ¢ÂDÂÁ•bâ÷<)\0>é‘¢­²É®°D>hôÁ“ZsôÁÔÿRJƒ_ÎÅ³uÓ3ÔÊŒ©é×Aµz-{:9ùó	ÄÏ4:ùkUeÚg†Ï5:‚ù5ı|éÎ¯q_(Á~¥kúEà¥ò‰X@Í^®{"^±ÑŸ'âUkıšŸˆşé‰@Q~"^·êoø‰˜cFãmó|o 7üÀnÛ-¦]ÏCÍCÅ*h‚°lƒ%gl«‡&Ò'gW-‰Y.Ç´tNŠ
tE¢hŞ¨&d¦öŒfÄˆÉ1†9™?‚›ô{ÀºÊ¬%IàİAº’0'Şyæ“ìçjÙ›É¡YP»ğV£C³N•ô¿m`~ÇÁü
o(£9T9ÁrÇrSğ¬ èëôIú/“™&Yø";ù¡”±t)›ì$ J¬2kÁâbİ¿¾²½L¬\K7íQİq®Ä<È¨€kï&`[H`{¯ØÖ­âÚû¶áZn¾ùa	×Ö¸qm½¹ÿØøDTÉı"jı¶.’ûõSrÿ)ëDrÿOş¹ÿŒŸ ÷Ÿã3û/lÀ•‘{Qôe]äşÊ{"÷×ÖúßÜ¤È¢¹¿±êßú©;SªøvÒf4‹Bl–},t!VØ¨CVÉWËô`1”“Óíj›Z =ğJæ‰%¾KÎËb‚Ç—U4ûŞüƒ/xÓÂû¤?ˆ©+ o	wf5á4ĞKú(‚UË~Lf¸¸føS£¬Îğg›á/>ÃÓ]—`„‘İêı×Ò]-ù”N7òìÄb%@÷”%jJe¸zY/ïÅU^¾<ŒdIÂé…‹™)Õ˜Ø ³Ÿãtóf¿&Ë]BË¡Oş}Ã*ÏˆXîLø˜.¿–ÛìÎÌ1"´¤Æ…e_Û¨„À³Ú ³i€*/¥Ö½ØºˆÀ§<;ëDƒ¿€Àsò<>ÏmÎ£ã<—ÖHó²~Â¯õfiï›ç³Öó«õ@”%üŠr^Àª/¨êƒG­ì§Eş
ä s.{)áe-[ˆ£–d°e4Ç…íá ê‘]Ä&±¨Oâ\¾ÅyşcY:!1F·®öq´%±K5¦¤`3	ÁP’+§÷Álg°@9¨4¥ßZkÅHíFQü*cßÛ’,–,zY-zñF‹\]ô¶è%}Ñ…§(C7¢ÅŞà!Énfe=‘%IŠ1°ºse£+ÿhÌs§ó'.–:;¹$=_…ùgı HÜbÃê•É¤ÚK$Ép—ä-M‚=—‚)*¶$ÅÂÄjÙR	›Ä¥qHû—1 .ÛûsËß¦ö/§q—+bÿĞö÷±–¯‹ı}Ôz…*öK±Åö¯äØ¿²cÿ*ì_Õ\­ŒıËk¤Õëb_ÃşM‰ıkXëšcÿ¦)ö£(Çş5­úZ~Ûx›‰Û¡‚Z}¢„÷bÅìüÂå¤Â¿I“ptÍOƒÄ®~¹w¸Ú£_r
VĞ*û7:›UQim[Æ:¾ôb^+‘©<Ğ›\ ¦Lp<E™¥‡-ıÌ,AÁ§V	l´”§)ç_v.&¡8PzqÂÍ†ÍÁ]©À,E¹Æ_|úBùb`Ø±äºMÃV`åYPËÖM ¾¢ ¾^#€o^µ§\ß ¾A]¬XI¨bÅ)V,aÅ†9Vl\ÀŠMlÀAe¬XY#®‹C+¶$VµÖÃ+¶L±E9VljÕ7óãô] Ì br+I¸èÃwDĞSDHE<"§ÇÆäE.(£Œ…Œ&òÏ®Ïi™;¤|Œƒh˜K2$™Èp@V;çÅ|È'2‰Váeª©‚ËÒÅÛlğÍ†Üèt¶ñ8™Ñ"7Š~Q"¾¼–m™Uó-™áUİÒ€:Üú4%÷åsÍ]6 'ŒİuïEAì)™Í`&}Q®HP°2¤İR·KªF7@6­nËë“ÚC¨KÃ¡r¬<'1óHsAdì3ì¼%4a8/’)>×O¸e[%ĞZUĞÚº´¶ª"Ø6­ul5u:²Š`[§¶m	Á¶sÛŞlG0j[w´wÒ€¦mİ™ß{4ØÅğk› nİ•¿«êÖÕ5ÓQü“©[·©ª[w³qw×¸^£ö`G‘#î«Î÷dYàÜG”Ô\{Yß{—‰Æj¶O]¢±¯-j$‰F³µíDcdJ4P”«>ÆÏ÷cùóHA ôˆãHœ‰;²ujk²)ÅäÁÁÁs)Y¥’>>Uš.¦«Dq£¨ÊapÎh$læ<SdñM‚Lólıhô0`@Ğæ¤-\ùÊ3XËZ“ƒ]Ç6:ØÛVÉÀ8ÓxÓ©e“?s¢ë@'„ó,Š!ÛaåÖ!Í¸ÃiÊ`!}Œù‰C^A£§fÈ›“TƒFŒ^°ĞxœÂoÕ²¶d±kj±û5ZìvÕÅN°ÅNôÅnI¹&˜æ†D’ Xy€Y>¥ø£š¥®Ğªâ»~ÓĞ/µ¬=™åZšeG£Yn_¥56ËIšeUÀí§N÷g§Ew‡”Öd¬Ü.ş‚€;™Ÿp»ñÜlÀ)e¼ì¯‘¦ÖÅËi†—;/´Ö9^î˜â%Šr¼üU?Ø÷àìAğ¸Ã™+³r¦·Û9|†ä]Úƒæ}8ßè÷PÖR‡À¶åÀ.áB+D¯dˆ›hß	ÙºÃ¦087„Åe%3FEAŠÜ¾MjLg{9ƒ57[ÆuÕúd‡$û¿¶ xh£ıß¹zJ3î:ˆê‡8ÿÌ§+[D0µ—¿¦)ÈôÎ|»´êËÒ‚D­”V>k(êÂZiV{t%ÿ«²Á–ÍG–³! *â7ôÉH¶vd£…íR]ØQ¶°£}aÄ‚>ıµ°ángVÎøå›:<ÍŸ§I=67=]Îf8—6¡é ƒöI¬UŒ…<¹SÁ—ÁxhkÅÇcHŸ2ğx¼¼'{MÏÏHÎœnED¹Îö"ÍãYC# ÆD³Ã\°LøR~cp(Ş-·p}úõ‘ßÜ¸œÑ"C—æè£“ØAé–K*ôŞ';&ÙÏuµŸÇ6ÚÏ]«ûyœíçñ¾ŸsÌ„ı\Û÷“ .ÀL¼œ|Óæ«AZØ‹ça;Şán]µXRLÀŒÊÃÜ^M4‚çI·Wó<…]nS`œ©ğÁÜ¾™Ú ÏíÈWÅp&;Ç§QğšLÁ]´ÈŠg¶î)Ô	¬{üü-A;+Ñ40øÄsÒèxâgv=[1âèÆ¹ªFÙÉÄÒ
 p09³Z1
á,èŞkÃWFÜE§›…ôİ†”á1dã„ä˜­§cvb£c6ªzdÇìäº÷áúêô”ê}¸[zZºOóûğt¿Ï(Ü‡gÚ€g•ïÃ4ÒÙuïÃsì>Ü÷á¹Öú<¿wOïCå÷áùVıG¢ºÂ7Ø†È«Vq¢¹OJ”èÖ’´	än±ø.2‚‰Q;3*fñĞJY3·1äË"ÎÏ«S¾
„w|gt–"¨¨¹ûÇ7I…­÷|Ëœ‹û]H —ª'R©ˆ¬–]˜œ“ôEÎÉUrt±Aò‡ä[äøCl|±(˜-FèˆR½JÆµw/¢T3îÃå]Ø‡ybo²÷’ía4&¸b¾ùåªŞ0`G*æZ)…d+‡ÏÚ4¡hŸÄgp^×i˜L›F-»4Ş@ï²FÀÛ³Šd—ğ®¨‹dªÓ+«H¶WŠdW•ìjG²kÉ®u$£€{x½4÷·üŞ“9Ñ†b{ùöFş®Ê·i¢7ñO&ßî]•oo¶aoÑ°Ó1'ÊÔ·²·(än¬ncYr÷)	¹·Û w”‰Ç&jö»ºÄãN[Ù¾$wYë»xì›åÄã«~¯ù%f~©!‡®õDV¡l·ça‘;[¢û¦¬¤.EeµÄ68–rV‘· T35›HS{+«¶uñu˜å!U(Bââ¿#]”ô¼‚À±V‘äŒCœ~³o7-Q\K®º&s&£)Ôln6'HÎ€¨ÓâûõÊdAºÀ³¦ K¿NÂ3‰²4ºóîHpÇ!Ã»-Å[¨5mGêÒ5İGi¾CğHÆ0Î©	¨’i)³´N•Í I0%FrÔ2Ñö32ÍEÚ"l£š‘wI)GîøV 2°hv·Té¹í¢]=c'6#DB|ËuIn„Ğãg…ÚG	¢zn†Í¦e¸=gr>\tËŠ’‡,ñŒ¬c”œü™ë¾„ZZŞßˆZ6W©å†wÖ¥–ƒÕéï«ÔrtJ-*QË?8µ|Ø©åZÒÛıO6à#eª2D#ı¹.Uù‹Q•R•G­õ_ª´¤TE9UyÌªÿÍ©ÊÙ¸H‹š&‰fF Å=ñìt†¼ñÍDŒGxŸè›äÑ¤<e7u´¥ï¸®Ş\cëv½2ÊÊ9ë#ÛÕûQ¿;({<ÙĞ¡‚È6tL•wø»-ùI_òÑL2k‹3„n<êR=OÎØ•õräpcF7ËªX`—¦øTîBgöT2óašùÓfŞZ=ŠÏØÌŸ­{7U§ÏUâØô(>_:Š/øQ|ÑâK~iû²øŠÄJï4D÷Ë ÈÜ„ k<-9r¯QŒEÚìlÍöñ
#÷šœ½Ê>ã}º™føËÂ}:.Ş§îuî0ÜLètô8™ğ+«-âúQÏ-JŞ,±¹†x«8Äø8Y‘·mˆw4„±"ïò{ºö÷·Ú/ò>Wy‘-4ìü“ñ"mE^„Hı¡û‘ÆÙRí>f»Ä°äx?"õ?¬õ§j=e‰a	Š
yÉ¬úg~Â{Qùò¿UïCºĞ4|äh%Cl˜¤Ü¾®±ª9JB¼­‚Ş%`¢Â)ıTwŸ'È8\{ğE#dœP%#ÿ2 é@¦ùİMu×XÙ×İ:L†7mŒA¥((R\¨È|­RÁG‡L-dó¯’o¥İhÁ«ş·-ø_ğá©J¯¼‰¾õÓUØšÚ!7@ÿï(ü,ï²4VøU4ÆÿojüÊ“§4œ=oï·Éön­íı®Ñö¶W·÷?¶½ßûö6øşÿ áØ’¨” ò“YäR†ÓJ$òÌÿ5`Ïóÿª@èpšR A•'—’Ó·NßN_G•µùÉNßÏ:}Õ‡°êôvZ|ëLY›_Y'>„Í°¼=„ÍÈO<„Í„O>„İ‡yf|Ç€³àc•ñş÷Y›YÙç<#&é¢úHÍt6şŒ@HyÚËÆš]cMG‘Iœƒ=Ä^·U¯s²,0Nû—sÙ sk€Øl;5›‡Íîb^–ö‘‘»èm­çSë(K¸å¾Ÿó[õTİX¨ù½'mÎB6TWà æï*µ½æºˆ€íª/XÔ†]LÃÅ´¤ÅÄ+ãş&"òš£R®—xµ31Æ- á€&ñğf‘_`x$*"¸u<cTYCkÖ5ƒ©e‹s%ÃÜ´²%X>=çÈÉUz¼¤­w)_ïm®,6©#Ú+UfgEÏ8UÅ˜B°Ğ²	’"Î1ŒŞåıCíïÜ1L¦(«¦şH°Ø
¢"ğèd«?ö«eK'àØQàX¦8º«bYG“ÀQ%;©ÓåØi‘@ˆ>¬	Äòü±?A VÄgx)_É\¹ŒS;k¤UêâÔªvĞ§§V³Ö«;NMIq
E9ÇŞ×ª¯á›}—6›NQÍòwûbNVˆ«P4 3;eÆ‚‡¥6¤¯Ë-.`ÜB×Q™¹é‘ÑM¬‹vÈ¦—^*"ôŒ(R.LEÂO×LÅŠı×²Z²ã»dk6Úñ©UXË`ÒÏaÒT´,êúàÙ`Ánìõµ`úÊ'•ÜFOÊ¤h›?-‡’’‰î´ *TJÆ²¡ªÂ¡ZÕk‚k=-Š~gû$ä"EipqDV¥qõd™œEmÓıT)n·mPĞ@h†¿8á(Ô²ş	ôwô×nıiEèSP^Ç ¿® oT~=~ïQP^ßNÿÌoÀßU2?J³À?™ |`‘Ì3@Ã@wC« •4ì¦.6ò.Š6¶¦›¨©40„(4Ğ,±_6ˆmbx†ƒCx†ÁªÏ5±†Ö<Ì×¼ í‡&QÛ	û°JŸ1ÍÙ„>«f›Ú¢	‹Ş¬Ş¢w×Œ7Ï}Hõ¥bxKÜ(û‰wüê{+–ÖàĞ’Nekëz›Ğu/)Sxp&‹?C¿Ñ£XÔÑÚG»‰ÇB—ƒ“³¥QöÔ(#‹£Vb@¶µQ¶Ó(qr{©Ùöl–0 ;ä'±ÜÑZï¤ÖQ–0 (Ê­ú.…mÚÕ·iN,e;ÒÌUÖª!YØ(äˆ°=»ÕÛ½5Ëİóí9¢|bpOX½{öQó½Ø¼|âÈƒOìÍª…àûğ·ŸØ_|¢™%¸–Fó×R>Ãµ4ÆæÒZ†ô¾šÄØ é4øÄ8ƒÄQ÷xë¢ÍÁ}T
nåwÓ~V}‚ªõ<@,ƒyeD’'Ø’ÎfS¤Ä’ÍA¿uièÜ‰Ç”¬ ?âÔšoÙğÈ†ÛPe£a{kÊmèüĞÖçD| =W0nÂ»+­+ïXcqÑÅ¬Ÿæ6ÌË¡l»ÀÇİ	R;›H•X·fAµåÓcİ®zÆtÄ:±çä
Ùªåµ“»OâkFkÔıYPú˜ˆl]2ë¾KİCt) 4u±ÂßÉl>ÏˆcËâI‹ºîö£m­¿)å#5Fu§†#Å¨n°)PÆålš¦ãdh­òÓt\zšPT°	´êûiúÌì2)pÒİoÌÑàœ)=¾ËfbÚépTJGkPÓb9pltXBªuEÀ¦åŸÒ‹1C8Nç˜ıåñ¨
G%úº…ˆÊºÊü´¡ä—µ™˜½X‚[5wt3KP¢–’³VAúĞFÇìøê1;Ì@yxå˜Qo¾Ëµ§1å¥ƒ6VãY<h'”¨úQ6ÀÑåƒ1NÍ©{0µƒq"ÆqÖúx?'¦EùÁ8ÁªŸèãM—w<ñQÙôÊèÆc
Èã§ER‚­áKÑ>:·On¨HÃ|Ìv°ìM©0Æ8è†sŞËÍJ¡äZñ8IÆoL·r"6ÃJ®‘¹Î3ò ’E¡¥øt0J¶–”œ„ñíÉNÂIUVùƒİ©»‚ø ¡İaÂ^ÉE+õšLh)l™+ªÿiÉÌÚ4³ÓÍìäâÌÈÎa3;S3;wJ™ÛOŸÅMcÒJ²Ô„¦g[ÓsÔTìÜ‚ÎÎuïèl›ÌuM¦8;—­#cwZ`ìÎSK>,o]]PÁ”ÙÈøğÄä –0d‚&wQCN/=']l_¢K¾”ßÁ%‹cDÚUúÁZ"…2®š]frF`I.çï*›<Qã^á@ĞÎ¨¾']i_¥ãÕÑ®vW³]Âp]cŸIÔ¼ÖZ_§ÖQ–0\(Ê®ë­úo«¼ÁWYa¸n´AÎ
«»©Şê:4Ë›óÕUe¸n±oÕ€U†«SÍocó"Ãuv×í¬Z`¸îàoc¸~‡¯`¸îd	Ó8ñ“iœğÓ8Ù\î-Cz’&q_€tÊpİo8‡à~ÀºxĞÁ}N
nr9Yõ‡Tİ²³’İ6nÁ“)ÁR±ÅËÒb³Ó19XòéE„.ÿNMò4‹ÂÑSQ,ÛP²=kİÅ­r*Ùÿ²?p%–h­ûa–O%:·Jşhkú“Ö$:p^™dêø?E:ğgkú5P„YˆuYw×øìQ6‰ÈA@ş¿ª:‘ÿ1kÿ7€ËÙ¥v“€šÕ!}½$&Š@³ãˆZ]šß,\Ù…%Aëï6Ì“avÇk=^»Íz»ê©Rÿ“ÕÿÓÅş/*]ÆÏXÿÏ–Ïa·š=Îa‰K{ŞàÅ<‚/Xëı^œAåÿ’UYÕ®½Âïi|¿WmKÆ¿ÆßUzv€fùºo.6ÿ’*Æ¿a¾©«?EÍßbó"Æ_Ú#Æ¿ÍªŒ‡¿ãßÅW`ü{,Æ¿ÏO`üøÿ¡Íå£2¤§jH§ÿ‰Aâ2=Ø[Ÿ:¸/KÁ¢Âƒ½UÿLÕ%‹±ã”ÀƒÇÜ X èñr3¸fZÙÃ„k’Xhc'†¾+|³ë¦äTË>ç4K8=M+û‚åÓÃéË“p›õ—>ëg0k0Wğƒ“)ÜÁÕœd¹y +¥²û¸öZ‡PG¦¯Ë:PÖ´grK#­“!˜2FìˆˆÓƒN½Lô-Eğøå¾hØ®§½ÖNF>.ã
¨ãL(@†€ˆÙW	¸¸¾n®+’÷s×7® .fK¥UÉYi¢©Õv… ÈçÒ<¦s*#JĞIİ²dÃo¼kÈIT†e´å37”‰Í-­ƒä¤8îJU­xp–-Ê’Áê*PØÊÌØÀÖ6«fYğ¨ µ²RQ3`nÅÈ†â(ƒÉÌ(¹ígq1,mƒå¥dÖ×ƒ²o¸$¸~×®W&××ï®C¡'Æu)ã´.D‘•×Vá:ÓÎõ3¡6¤C¤Ö	§©˜<;rêk¯5†…g”èañ”d¢ICÊ|Â²U~MÀØoâ!è šzSè›¦g÷´İtOpo,#võ3¬oÓ$¸£ºB¸½©ğP(gÏ¡‚'tƒ_†©0¾!—¯c#t(Ô+ÍßòDêÀÔ²’ıùöçÇFûsUq¨®øÉöçgíOI]ÑÕ¿°×yF\]VW¬åß
¯©3¬ şfÄGQ»BN¦ ­™8ú(òÎ„jù-~ˆzœ™eá¿¦tËÎbÏªÎãå¨šÍÆf	_İ‹¥½G\K²?»µC­¢,á«Q”“ı9­ú\ª>xT7NîHœ*l#Ÿ’&â˜–Ï§”átºC<5&†²ğ, ,üİ…ÎufHèºÆ$J¿f¤§TN‘®g(cˆŞEHšÎDÄ‡ÙÔ^–?˜$ÓñĞ¯‚Ï‚­ã9ï‹ĞİZƒ‘„ôyyºz<PEO<Ò Œùè‡.Å†‹4+•‡¨a-IaETF¯!½WÅHèzäU’>Oµ>Œ¹CÖo‡Ë·Sˆ´µ×²¹¹‡¥;ñ0íø<,ŸŞx]•Ï×¶´·¶T|îõe>÷pu<;®È»ó[ÓÔ´ô|~¾¥5[m"£{C`tR}>_,l,¢cÚå÷ Œ¦Ï‹ÙÙ½10o‹ów•y;B3^ÂgŒİX}¾XÒ^ª‚‘¯‘-±£ubÄÆ¥KØx¤z^¦ˆ7•xêe­ã¦Ğ1Ù[ğB<#öz±Nó¨YYÖf‰Œ{¶;[oÔÌ(œ´öºY[àÍDÎå­³9oÈÙ,…éŠ¥™¥™­Tœê;¢=çÊÖÙ*ê,Ò‰£ÕlU6KèÄj6•[8•Õ­u_ŸÊ-)@QÎ¯aÕk…]Ó7¶"¯eƒÜ6´_½=F³ìŸoè­Un|mpXåÆUóuÙ¼ÈßÖ#7¾«¸ñõùÛ¸ñğÜø –€ÈOpãâ3pãÙ\6.Cú8Mb“ é”d¸àl]qpß‚E9YjÕ‡©úàQ?GmøX]Ã¢MN(Ëï¼e¡2lÿ•`zÂ2jš×·o7ìİ­‹„µ¬*®ò"Æ3tÑ¤Æ]İcàå@w	‘a@¥§qF3S Ò£Â’{ƒÈ•Ñøş’¿’+ë±x#ª¢êŠü–'—:pSÂ²Dø7cùôÈãU^`sí-x"BGf`Kv;Ïˆß•™4äp?µÁ´j+ëpkuX~j3 +~îY$@Û°}Ä×Õç–vàÎš´î·-¾“Ôl»pøJB÷övîîâ¹ÛÁZïèçî®ôÜ¡(?w;YõıÜ­·iwL÷SA&{"rëáğ•^¢<8¹#Æáö…‘Ò+ÈÙ™`é¾'0#6N$™yœ®ŠÇo~Ku¬75ò¾1Î™³¥Ñ”hD[„1óÇb”P0³0Á¢4j\nî¨%åŸd‚ˆÁ#«ä9‘V•Ó$;HÌĞ	G_‹tÓÉ™È;™¡ÌÍ¼Şå„€Mæ¤Â0"tâÚ¡ufŒÂr$ën¡|S'´"Ê¢5‘Õ†Œ\NˆÃ‡˜¼ÎcïÖJÿLÏØÒ%¢ñ5	Ù*È…£Ş<y`ÈÅÆ‘•‚€¢êNë¯99Gbh¹¢ëô²cè³ò„¤å›ÒÚŠ4Ù.	‚¬#ºk#½»ú¦4ÊÎàn|ª£)ß½„I§h¼=Š˜tOIS¾§u¼—:6ædo~ïYS¾aÒ½á.Û—¿«ÌÉ©·Ù©¨Æ½UMùh¸¥ŒÂ§©İ˜º(ÜjßGk­Ç9
ß—¢0ŠroÕÛ…ŸpÕmpË†±Û#Z¾a“¾yô	‡B–ÕN½Ğ8‘^öğ”#)díõ¦Y2ø	ÍóÒÈßÙÃj;ª3ë½:™_t\[61è\Æ òD8hPQÜ'O†cOBejÙ~ÉA;]€œĞè İ_•Ú'¤ÚR?RŒ^Ü<ÑVÙ›Ì,H–ïG|Ù±yìjÌsZîòÁÎÊ%iE5‰„.Üjš!ÖC~å‘äbz&Ï‹[.¼š¹N$§CV€…û$`§¿Hg7šB—qíPÈñ©Ñ“Zè*§K`Æ¡Î‘µ©#ìlg#À>P•@&`÷`%<X–@ÎTÇ™£LQÓŞeM'«©$êÊ©i}ËºÙ"Êùã ó©oŠµšüpyà³4ğ´|àfŞâlz 5=(oŠî‹YyÎVÓßæ|LíeÑêx^”}œ\Eòp„ ‡:äÂ².AB|I ‹†ÑÌİÙlXœîîîîîzrÀá~.‡wØÿû­ê÷^¿÷&ÙßŸy3ÓÛ]İ¯ªººªººúĞ‡JŒíZlÄˆ³³¦\(ö–Üîçİ¶ÑµŠfeKu-oı½İÅô¬l¦´pÿ>¥EÆ¦M¶·o°.Y®ŒÜ¶·PYZtÜa¥Å¦•Ûµ0ª÷&{²¥%ºFáëL|İ¨Rè+×™¾Áíî]jñüÔÇª–Fj½ìœJiÉiÒEŸ)M¡2XZj»Çÿøã®‘(ë.ôf{û{RYSÕ¹€TËº³~é8øÒè®EP%Å±––Ù§´¬3Î+ùbïÈÒréòéŸt¤éb&[Z!To
ŠF–VD½•Æ¢ÓÌ’#FŒÌ™bO"]ìîÎ¦+@R9Qèé+šJb“Éšlf‹Bº2/9£»P®$6u‹Ç“?Şîä şÖ'™‘A“±ã~«½Ædç${úº³cöA­1Ûöòå» scâ•µşŠ¾R¡“ZìßòÙD¹§8+›(ô&LãÇ_HålÒ¤óZwRB%
•|¢·˜0Ùrw%7×_é7Y­?=YX¯œ˜UèÉ“.ØüçV0@É@²‚®œÎg‚’™lÙÖ,öd+ùBïL8ÙİHöf™¤™å¶è³eMO¡7c‡\)÷Ï*$*xKçON³z9;Ü]PIºÏˆJe3‚"p¼[§/Û›éïîïÑŠ»›"†˜Nö—³‰b.‘É&+¡—êëNöº¯.¿+&™ö^yùN0|ƒš˜LƒËMRN‘ïcËã™B9™êÎf\ÀéîdÙRrŠ o2¨£….ëzOk…»3Ka8`ôL";;Û[Æ	qMO¶»Û©ZæïĞK0\a(…ŞıûM±İKšI‰R!=+Áw¬¦Ğk_}K~|!“Éö&’:cc²$Ê'+‰BY*C›Â“ø”|²Ì”hØJ¡Òê:9+iŠöøuRÙ|r6¤S¨Óşr_!¡8³Í+JTŠI“ILRf)Sî£™íaÀVB?}ÁŞßdä‹ıÆÎ”Îd%Ë©WÎö*V0]ğ9Ì¢¬,íÅìÖÙ±ßôËÙ\w"ôG§ƒ]’½˜Ä*Qø5„4gP}Şk…GœhtÇ‘ôx ˆÎfùb¥Ø3G8¹-@¢ğéï±5)$
52Ê©üŠîE8/’ë.‚J:Yóƒ‰b¯0‚”†Ş	S×v)e İ‚ÊYL°ğäê-V1RLíâ,ølv²·PÎ‡k—ûLÖ©¥¨˜Lh©»ì5&¨¹U²»œu™?iº­lšœÍM6q É¼icÃPè-ºQÏ›ÒÛëwWÚäı‘Lê)öc.ƒ]fcÕ)ô„êa†çeÓ²ÙH% t“•AvÖ4Õš5©b±R†€ë°úûV´†F·tÜ&ùá¡§»}e²=ÅîgxÀ˜LYƒ>¿9£ëÃÜ°ß¶ÜM¦Ğ·
Ö[[eï1ÓŠ˜<xÈî=&Ñ“-—“3C•÷Oöö'!¬#[aæa%,'’3‹ú¹£Ä2bgŸ,=øåñbÊd“³0ÍC†¬Ğşºö˜FÉÍßÎøSı¦×N½İó˜MpÓóS”9À¿†›C
nk¼wBT"LA£¨„–aoÁÚ¦iVIv³37+°m(…ÈCÙŞ¬™’æ\“úú A${Ó¶ë±V'¡¼UdÁ
şèò•ìIãæš|…Xş³äåÜw°‹‹UšÊ•do¥{0‘Ï&#‹d¹ŒpÕ@Ñ`Æ—¡ğ„5“r²íÎÎNV<AB
RÛ+—Xwş7™]0•şdw Ü$¤“­9z«áù´TyZ‹”Å|o±PÉ2½€še™²;9€i
ÉÒçâÁô{:À D¦8§NvC’†• ˆD|±Œ)Ì¦Ş¥Å#Gâ“ìJÙë©³udß±ã&ŒLà¿BNş™È*\ İÊu¬=» €åÁP¶›gÍ½ ¤«YZ9?ºs±ª¥?‹r“M—V©¤äÖÿliÕcò5ÌŠÒjÛ}ôé"ùí®[jÕÒêù¥ó£ó°ò°,h”AËliçûšısSIüsôşí“©l÷ÈRjÿZ0Æ¨y şå˜À¨Y»k)óm=u½´˜*}@:´X`¤´î4;‚©ŞÔ"YoŸÒX×tšÆTY‡.×G—ŒíZ€ ¡”ÆíZ¶ÌL)È*Ù¦¹Ó¦íƒÿ+¥å]`OÀ0ª›–_"op½ `#1Ş’•îR½7’iIø}w‡¦?²Ô€¾ÑwÓØ È¤ÙR Ï”ZBæÑ–súÌÈR«c˜Ûåb÷ìl©´Û¡zX©°:ÆFm·	;„m·ó£1bIŞ®/I¥±´É4Pm‡ØH¡*÷B²W€ªM1ÜÍĞÅDw¬÷Ò7b¼]K*^ÅÒæ•Ò$éøÌ~HøÒäiR%Iu¤°JS5K²ÏeÀ uo¥+ §[t­¡òŒdº¡¥½½½±´¥ccnµOik9Ó“ƒ#KÛ`ŒÛbŒÛ)@S(uvµàëîyØ®œ7IN®ñ‰2”JÌ=*ìÖüÚ¿¿§kD¼§æ×•¶—1°=SI0ÑTÁXoâµ»äX¨–ÏPş`-¤+¥VÈK;u-@sWşß3r°§J;İõ'¾h–Ö,V½ÉJÅRı•l¹4<#ïJ£pFi‹A3³¿ˆ*—vPç4ÛMğŸ_[öfBî$u•ö*í9ÖÒ JQ:`~Í¨ºW¥´·î }ç,ìRöû ä¾Àûp'!jÜŠEılİ$ØJZhY2#g~
íÓcó9&›ç¥LŞŸØÓ9fLçìØ<goÍfÍÏwÊæóîD½Yú/äı	º‹²}r€›åLÈ[¤rw¾%™u=˜u»bÖõ¢Aql~Bç®ù`fåe:íjáræô¡ZÉ9·psÅä'OË»b·|l4ÎhÉdZrM¥r|_É“ÑûröØ|gW=p=©7Q4)j'°3‰<Íµ^0¼x2Àòü—Ùš°u¥üÔ¼C§Zš“ßñè¼åÖüÎGç…ó»LË¿í–1XŒ48T:`¨t ¥ûn#É‚m²„ÎCóÁ.n³h8$Š†İk¡¡1ÕXŸË´6–%4G“†]òxÍ´)¼v1ìNZm¸œ­T0éÇ«Ff5jú³Æ«(BQ¬+FX-5_Äì^1s‡JÕ¡ÒÑ1»;ˆ‘WbñÃÙs,Şâ8[¹+ïN—Ûe ÇG§Ë	hp¢.”J\'µ”N
&Êv¢œ<6OÇÛ)hpêØü
yz×N£wm94›sµ’İRkìqûŒ+ÎŞËêgä¡ä¹ò{ÿÎ™v•İ‹}¸«ûYá•nz¾80²t6z<İŸZeÏÓ_³hV÷È‚Ûo(l„B±¿\õVÜóƒŞï”Ş/ğÙ…AGuz²)Ï®.BWÍ¾]Å¹úäáÜH&ƒ…ü’ ì]öÒ¼n4	—ÜåH¸[*_	WqûB$\…WS$ì	ûZ‘@‚\ƒj×z¹¡ĞÜ‘.®±õuMãJ×ŞKˆb„¸G†q£%Ä!D>‚ş]Êé ˜«ÆÈÒMèõfôz‹j	ô¿ÎPõèVõû+İmîJw{€¨{¥Ó;T³K>åIéNáf]Ñl9äş#*{o¥t×1 Ò~²*S"•îîZFV·ŞLq ‘ìÇL…` t×=UK`HfJ÷ª&Õ¤1«–î›[ºß®BêÑ¹3<f¦Â‘ˆ;¸ô ŞôAi `’µT,ÅÒÃå¡Ò#©¹¥G]â±}J‹RîOIÏåÒû”ô…§€³§¸O°ğŒp —Ê-¬*²5Œ+ıdK‚E«¿‘’16H:+Ãs¨ö¼+ï·"ñ…¨HLA$ö§úŒÖ¦ÆÖL{Gºô"…áßE¾`/S>„zÛöª”˜<>!Î«D²\†Y]t3M±¿O)ü¸ÇÃ#s%1I£÷s²hG¬\ì…™ÁJ7*–[ªïd.ìîlô«Kl‘¥q«­ÒÅŞ½4p92¤5†˜)£Oø’F ´şòºÒ+aIL¼TKÿ˜¯$NÕÄ¯•^*½n…kÊ‘Ä‚iHâ7Ü%êM ğ-—Xz¼¥G:LædK2›Ë¶•Ş!=Şz¼`ï“x‹S¦˜-÷®WRa˜s¶4š\Ó[«ó@P’OfÄÍÈ¥Fç,üd›™W|šA˜Üp-ÒÇV—pÉIZ ™£¯9œ’Ğv±ÆõíŞ¦Ääf1H4±CÑ¦bÄ—íÏ,ÌRWú Lb¦Zúp¾I× È?‡J•şe)’v("¸E>v)ò	ø©K‘-E>‹R$¦H{2lnnÌ–>'E¾Š|	`_‘"9¡H¼š,ÃY9 Ÿ%rK
L0©=•ı!‘ĞÓµºHL œ¸
†s*Å×a´qøÕÒ7óE[¦Úş=Túv¨ôE[ÆA› hûŞC—Áğ¦?ºË Å!ö}fù¦ìO`HÆôÌÆ•ım0wG–~äÿòÿBkù/îZ~”·pÿ
™ŸãÂäkK7¿¹ÔıÀşp©ûˆR×Œ€Ñ%ğÌ0ÛZS¹l{»Y€u·ÚÇ,ÈO,sf!|™6dÆÇØü­Óò·åUŒ=TÍ"¬{çÑ²€Êò43·,½³»±ƒƒ9ceŒÿ^Q8P.k†şm1üm®YœıÌ5K°âcû˜‘ü|b³$>­F5Ù ÃCf”<—–1‰Ú2Ó¡¡¼ö^3š ÔŒ£Eb–Ñ7YVZùˆ|T^a9Öš&fy–îÌW3ÒÆ+Hã	ùØJ”V"³¢V^I{òmüÇ,=V®AB˜¹d¦½¡!Õhşlé±
?1íÌª
{5İÙõ)Ğ8f+l.uwO¤Š5Xz± pR
Şœ
ø	¬ßôS#´“* L6.N)£Û¬[oØ¬KL’šØî Ä,ærº©	9Å›ÌKHÄÙƒ	˜Îp~øîa˜øvS5`Ö%”ÊÎ„1….úLk^9‘MbÃŞ·>6 ›Aëx–|n§Ø"™Y7Æ¬N$„¬-¢´jÖ`ùü®B\˜5…‡ò\+à¤B”`à¤1'A ˜¿(Ö–Vv¼´¨Üé~ pímğUd³!ø<÷¸Œz]–yŠòşÎL6ë)ü±şyÂòÏ¸ü3ü³l ÒxóyFƒYßrĞüäŒ¯Ğ7èÑÍ>ª¦uİ=+6£7bÎèıíÌ­gfn?1sñéÎÜ&Át³<[|Ïrğ-/|·Fğİ¦#n÷ğí[;İµC›ZmvÏÜ1!¤?)o6ÁEz·+6ÖN6Q¤{VÚSÒjS¶Š‰‡ÍX:º³âa¢6Ş\Oèì‰‰‡G<LÒÊ“#ä}Ú’wJòö†ÅCS¶1×ĞÔÑh¶°Äİ’Ÿ[)ì­vg×ÇÀ\ô½Vmå\gtG¶WVÖb‚«m_¿Xóø9Ğr‚w|bÛLn¢ck ªjH@zsÙNÎ„_ #ê1 ØØ…ó.+¶CU™5ú„pBƒíMŠ°LÙáF0AUìldX/î"ıâš¡ÜJpŸ(Qì¯Ô™mˆ‚p B«f[–ÏO8ôÖÛ	›vÊsû€Y{frY§:Ì
„™¦Ø!hU¹!‘Qí´òwf'm¹³´÷Kú#Ô³j¦³‘ï¿+©[Âì"õ)—vU »yóÄZíbcrÿ±§hHxOm1»‡&È_e`ô°úRÉ¸d…¾gx‚<+­öª9AöÖ	RÆÙGïk'H96AÊAofhåı¤²øYL’ßc–½Ii5îMš?£–¿É3áP*‰/1«İå¤»¨@|NZÏdk5ÍUÅé‡@¬ex›<kR.æïÏÃx6ş~(cÙì¯©¹fK (»ù	AÙƒOOGéÕ¡Ã8~^ÆĞçá8f)›’¢a6mBÙ"zvÑ³DW´r¿ƒèÙÑ+‚i°©i*ÓàÜ;¦7Yì)$ëëÇŒ3ÚÛ€EúœZHA†< }ÀA:˜æ íú@}S_GzÑ
ÁƒØ2âĞ!¸|hFÌhM6§ÚÚë3fˆõ¡·ÌO
ÂCş¡¿³ëR´ÛòâÄ7ûrĞK*‰ra~~ “Ì•ş!üF&h;b.‡ë7Å`µó ]Õ%¦ÁœÊjDå§Zî¶äD[†êÛ#R`1™˜$•¼è‚şB7¶™uæ0?$Äˆª9œåóbsj±#ĞhÈ)Ï£¢+Ï‰¢Bl®%ùÔ©*öPçï–:ÇÔ Î`œ:õíé††t“9ÖRç8:Ç+ü,uP'K2“‘°	ì*Ñ‚Ä±Ø÷ˆgá"@%3Í[üY%—˜«(‰Y6Ä¢Ä8¤,ïM(T—`d­Ç¾„”Í‰1ôó«æ¤áĞ?Xı'âO‘ç©úô>şÓ"è?]ÑsFı/YôŸYıÄÑßÒØ”îhOu˜³,úÏöĞÂ?×¢ŸJÙP[ÕÚ¶L?> Iñxˆ®ïÇp*d¹‚¸»Ô“•'Ù0³LQv°ı¦“q^•‚ÄCÂ±»˜P=p¹dÍ ®ïğ“ÑA¡ àÅz
u%¶Åd•§õÀ©,èŠJòØ* "$³âù&á@=kòfˆå(È¶¿¼§ï6˜íğybÈ¦$A&ˆ‘…w@P™o‡muXOlƒO D=Eæ¼¿DUsşpür@~¹@8åBy^ğË¿€_.ğË%JÏK#üò²å—ËjğËq~ñ —[~¹‚Ÿ\!¯TøW	üè
É^ªæjÖuM†c&Ã5¬âš×² +áuüÄJx=>]“áÁÅò¼)ÀÈFä‘›ŒPºEG|«´
L4¬†}êë@·±¡¯î¿"ïr;Ë<ËÌßv#Ø;ìXÙÆ¦@÷-ÙwÉKœ¹oˆÜêãÒÇİnC®uöq¯Ó3D^•V÷±UÌ¹Ÿ¥£;Æòÿ€6~POè<8¶üì"iå‡#lóše›Gj°Í!q¶éhnªo©oMšG-Û<ÆO®Á+ü'~gí7wõƒ½Q°‘Ä˜ÎÖ:…éšDô)„>¶Zi“”³İ9
|G-œ¹2ÿ{ú5tİî;JK19¸a™,`idËi¸+óC9/nà¢vâÏrİä¥d¬;·A—!Ç°·¹‰¿©7ØŠ.Mé´^ˆÔƒ˜pX&z‚B€˜¼]ÅZƒËúcèGñ¼	yCH)
)Ÿ¾|ò£—ëÌ“DjH3 ™ªæ)–ÏO38¤†¨yZ¦Ô3òük0±q&–0&Ö³ÎÄ‚ËÒüMiúœ´²ŞJ·Ò<Ï&£:9,_—Ñ¾™¦/*´¿G¦)ÍyOôû3õ¥Ğ,zCà½ìÎ¢ÃÜYôŠBşGx½)­^­9‹^ÓYt8fÑëÚø;‹Í¢ÃYô¦V~+2‹Ş²³èí³èˆ‹us*ÓŞÚš3ïØYô®7‹ŞSøïÛYô¸Ûa`‹Æ	3Ø‹»©Í³`@xØ¼i§³³g6´·Ş{˜öVL™)â£s»l×Z»TCmæÂï¨Q¸8`—uí%q`	ÅtTÅ>»x·«²ô•ÄÎ–n˜@³Ğ©ºä1„õ9Sg>ˆñ?\5ÇÿGÔàÿ
ç$Ïü„ÃÿB>ğÿÇıD©ñi„cçicâÚ·eÌŸ»\{¤Ëµ_(ô/Ã\û´úª&×~­\{¸ömüoËµGÅ¸ö(‡k¿ÕÊßE¸ö]Ëµß×àÚ¹q®mnêhÎu@öÿ`¹öGkRøÿ±\{!¸–†R7OŸ¸â3ØA rÆÔ¢§ºÓ Î4eM$Ââ#æ!n°sÀú™B.
jÌÕ%víå66ÁA<Ó×ìãí|}&øD¸„Ô™ŸcFdTÍ‡ã°¹58ìÂ[¿Èó×€Ãæ:&¨‡ıá°ßsD8ŒŠ\ğˆùÜÊ#àá	T„÷d¸°ÌS^ª.s-ˆ¿ ğBøp‹÷¥ÕÂlS,aéèÎ£Á\‹jãÅ¤ñ„Î£cÌu´Ã\‹kå%´'ß¸ÿÀ2×H‚÷ÇÄ™+™lÎ¦ÚÒ)³$ëÃ¸_ŠŸT,F)ü¥~g½3¢6X‚[P¬YÒuÛ—{\Ü³ˆ\ eI‹>¥O99`r…¢wäÁâ˜üR©RÄ.%š±j"ó…ÄÌP|z°û¯Z…J2è2³¸Åè)Ö¸å±YŞşô,˜I`fª;ÒS—˜Z„e«Gõ$,Üã^ì·J¨»è!‚3+ÛWÁøıŒÎ¤#{)°u8¹Ê•~nÎX‡0l#ÁT0®2ÿˆÑ,ï¦
W¢8à©Zuf4iÒCHÕªY†åóÓC©1K–E£!³œ<—bŠ‡QRaÁ,ùáÛİ<jâ+(¬(­ŸšƒÎ’æ_sX)4M>”ñ®ìN“cİiòg…¼JxšüSZ­Zsš¬¦Óä8L“Õµñvš›&Ç9ÓdM­œˆL“ì4Y«Æ49>>MÒ©Fóu˜1všüÅ›&k+üu¼iÜìŒCCtãëâÊ¨b:{leEª5‘é‘‹Ü÷¡f…+á[Ï`´^Î7¨%=Ù:³nŒMøVU³Şplr|6+2Nëlr¼Ã&‚3°É›Ğ?^Q°aĞê„7ş_2ªº •ïßH[ÖKË7^‘š6ò½ñ'Yo|£Ô'‡6)€æ‡Jt”wèÔgÑ–‹~,£juYôd—EÛt{˜E?‘V5Yt‚²è)`Ñµñ&–EO‰±è)‡xS­¼™TVWüD~»â7×Nµ^áIüuÅ*#œl±™~jÄ?E»ÛBº‹:>“Ö[²µëŠ?m^®ø­XÓqÅoÍßêŠß_áŠß–%p@lÇO8 :ñé¹â·×¡LãøsÃ4ÇqWüŠ†ÓèÂNÑ§Ç}º#vÖÊÓµ;_ü}aeÁ.Y2ÏpdòäŒ¶lCº>‰#!»²>–ÌİøÉ%sw…ÏS.™çyƒtò!Ğp6FOMïf­y‚eÊ&jO[I/ÁI_ªÜöË#,º^®ª´wû{Õz—­¼‚¥ñŠê`²gçŸÎvkgÙƒã-3ÄDÕìÉòù-3gÔ{¡ÑÙ[ûd™9#ŠgÈ}-ozğŠ¶ı"dùÒ’%Yƒ,gÖ Kk²#×Ş‘3)K–´G–ŒÂÏZ²Ü²líR¬ÈE†÷QóèÆéyj°­¸…ª­¥D‘Íáˆ^—FT“w¤OÜGt]B6@xàÑ¼˜ªpç¶6eƒwÜæ¥>!á„‹cl]ˆ5D|“‹xÂîÙpD;³ÑòB®‚<÷ˆv¦C4¡ˆ6+B´nEjO„h_Y¢õÖ ÚYq¢¥ÚSÍÉÆtÖ-Ñú<¢•¾±DãV–XäöÌv8Ê¢N$†¸q&uêkV79ìİÁb¿5u£=H´ ÇSÆË_è>‡JêzA *3™	âªŸ	óªæ$)½=+«ĞÆÆÈzœ#²‘«Tåì:ÍyİCq×şy¼¥îŠyîİË	üï*´è	 Bc~$"Ê‰Vq˜aÖ™rŒëHèª©ÇugÕàº~á·Ùò¸î,‡ë„Àus"\7¨\q@„ë¾¶\w`®;;Îu™\6™jé¨7Y®ò¸î`…ˆåº!*êêêô &Îñ¥yb”Q—"ruKe¢Z9¶´†üf€™İDpÆDsh›|ª9l8l]›‡ç‘6Ïv°)è6Š`s®¾m5‚Ío,6®ÍsâØliÍ6µg›ÚÌ1›ÇzØ<Náo±9GƒXéqæ?pjo†Ù°‚•pn&MÂ€ÿq<=ÑÍ‰G‹q(½iæDñ;q0ô"vÎPá$ù%h‘2ÜûÁ8°šAD”å2”åb8çkVÍ‰Ãáüœ8?I°}²<O	p~ƒsA"p~jç§)NNàüßçgÔÀù¹qœ·¦[“É¦†”9Óâü,çg+üs,Î'üIé¥X%e›W]D6I{VÜæNJH0× æO€0¢—jŒ:	‰zŒ®™²tMnQ–s5&ÌcÎ÷ÅA¦@ÎeúÅ${©ÀĞí¶½'æ¸=)óĞ˜DRM
²â•é?õG[XÏ1iR5çÇ çÖ`ó…5.ç…ƒœë0ˆPr‘Ã ´¦.V^´:/dM}+£º4hå[S—iËË¥¥XS´ÔÛÄ\;æ
6ñm©¬-u¥ÔÆs•6¿Z
Ô¹†ßçyøÊ\Kˆ£;/´æÈuü5G¾“á^o‡ğBÇ¡	wƒv{£tv2ˆçÆ¦º‰`üíºïôÍ,ó|q¹î‹[ò­d9a“ßêÍöƒ¥»ımÄÛB=ü =Üîöp±k#Ş¡=Ü)=øãúQZİÅV1oßİŠ²K`ºÜ£ï•Æ:/‰™.—86â}Zù~‡8Xâ„b™µ‡K-QªE”Ÿd„D¹4b#>¢İ=*İEmÄÿHëÇØÚµ/›—ø8k:6âü­6â“ø
ñ)–ÀF|šŸ°ŸÁ§g#şU‡òlÇ?Ëşæá8n#>§h¸ˆ~^!¼`}yÑ—;6â‹ZùïÚo#ş×Êç—6b#^áÄs¦ÍhîhÉt4§šÌË¬ñ~ÒBü‡BU wvİ®Suv"¥Y6…8y‰i²õ>b™Œa¿64nØÔ0FØeœ;c=#¼‚Æ£:õò©Ú‹E–şU›bªÂª,¤z©OñJÙ%B*çpªÎ¼Æ
™DPÕ¼Îòù™WÔ–o ÑySo	fÄt¼"Š~Ë·-Ëz¦ã;ŠÏw#ÔúŸ¥Ö{5¨ueŒZM©lcSs³yßRëZ*ôZj1›ñ1YDÊéØhƒì`~6Y†|#ù†²$N!]€ÕÁi<UÆ<zf¿Wóç DOr#ku†D•|\ˆl€U’Õâ¾ü`Y2t@ÛTğ+û€2Ì'¼S¨`)ŒÓƒ°WåÔõ-¨»;“eF°F?[3„5»H«Ç`ã;ıŞæ<ø3™éEÇC%`ËäLø¦"ÍQwù(ÆDzÕük8¸²|,´ÿDŸp¥ÃBRpÀgø\iôE„~±ğe¸*ÊÉt&ÓĞZo¾²ğµÇß(ô[8N<:ïDÄY#Ô,ÀØµ6g®à›vâØˆ4öGˆMÆ0ªöd
3óĞIDÕ#u‰h¯{µş1®À÷Ëp‰È¨3ßÆˆÀ÷®šï†#ÂU5ˆğ½ ÿyşá*‡‚Uá'‡ÔYş£hú9huuHgùUFõß •¯³üO[ş"-Cé¼ÌæW6óõ–k­Şò›´ ñ»‚øC
‚KCáéW‘“"¾xÎG«õo2¶Xæi×…vôğ€_Îÿ»´Z˜­â;z,İy=wô´ñbÒxBçõ±¥çzg_\+/!•UÉïq?ğ’ÚÃv_Š?£Š×2ÂQü“¦¹¹!²Æ/­İ–î¢küÿÂ†[»küóZã—eMg_¿u__±Æÿ‰%XãWà'Öøñé­ñ+éPVãxÃŸ=Ç×øU7Ñ«*„Õ,¢oŠ!ú&g_]+¯¡İùkü‚ègùÖ$ØÈ³“áÁãÌÍ­Í¹ö¶LÊ$ØëüZüä:?F{ø‹ôĞÙu¤•…%û¡Ìiê	‚˜ÓW#£åŒ²×FA‹ï†²ƒK¶ÆcÒòL;Ú;Xm
ö¬–náë¢ÑSgÖæ Cë6_ºjÖaùüÖí›kŒuÑhÈ¬'Ï±ò¦²nßE)Æ8Ë†Şº½¾âgƒ²_ƒ·Ô¢@K{[ª±½1e6´¨ó(°‘öPo)p}²d§±¥‹]k=Û-(‡-çA÷Ñe×qNxğˆåIæ_ƒßKÀ£H¢z­%­qj°>ıÜföŒÿ[ÏØ eiˆ‡ø¨šÆáˆsKâ4	YšåÙç‡8‚m‹§MQ×!ÎÂ–85ˆsk-â4¶4t4µÖ'ÍKœ=âl¢=lj‰Óâì'l,‡PGÂ…qõx§—İèÁQ~’ÁnŒºx¥ßj}êÉ”Òóf³ªùvU3q8TßZÕ›’'Ésr€ê[Tî€ê)To¡ˆØ2‚êE,ª·ªêÛj¡º­9lolJš­-ª·ñP½­ö°EõYz
@˜Tò-x3À*ŒêQ¡òJG8ÎZ	¢!Dš‹×$Ş%H‡	$ZH0¬;Ô‚gM^SÆf5”ÛAs“Œ¤rüLrÚÓ–(1¢U³ıpD¹­Q¦
9¦És‡€(·9D,ƒ(;:D¡6³“¢lç Õí!mfQÕô •¯Íì¢-w•–¢Íğ¼*=0Aêa³úúÌVŸÙ]ÚĞÃãÛ ²‡¨°'¿ÏÛ³!î¼Ëª{ógTXL½4Äô]?Ì¾Úíé6œÆóÃAQûïğX\`'Yæ©Pw»˜”‚N{ Ã˜”æÛë)˜YtÃ˜á´Ê!ö¾†&“Õ—»‹|NáÌ8:ï±‹|’©îL>4¤%dHwH÷¸CÚ_AÍò†Ä sIèë'÷á àØè•Au;ƒjl2=:¨{1¨^…T´ƒº74¨¾Ğ FÊ Jî îueTÙT8ãPxPgPMM¦_u5[!ØAİÔœĞ –”AºƒºÏÕPP
(ŸäKI«ƒØ*¦ÿé8îÇ8ÖÆ‡ØqÜSËîwôßCµòaRYÿp~ë¿GhX†?’?£?JFxÿ¤úïıw®vW•î¢úïÒÒúh¶võßç¥ÿÃšş{,«ş{¾Bÿ=%ĞOà'ôßñéé¿'éPNãx´ŒáÇqı÷TEÃC@ôi
át‹è‡bˆ~ÈAôZùLÑgYD3'’s$îRÄ=ñ@âÙÚ×ÃåçÔBù22às”?ì œGŞÎÓÏ×÷ôïeírw[FïG°Ü­¢3Zp"SŸÌ™Ùª÷Eü¤ê}±öq‰ô¡.6Yğè€á®‘M3l^qã;ÈóœH¦è‰a‡  O6hc7Ñ]Yì4@‘Ñ´²1"z¹uìèalİ¾‚FÂtî´çyşB¶S$÷,)Ò«§ğx¤B¢™:éàb»”/RÕ‰¦ª¹ŒåóSÕ©±^FCæ
y^)˜Uı‘(°^eÉç©êW+>¯‰Ğl9K³kkĞìÑÚ4khnokjFÂë,Í®÷hvƒöq£¥£ˆ/”)¾+TW¬3Å?˜Â3r@´³§uƒ8Šó¦^¢ ‹\,+@)I$%}•BE»ù›ëjH‚yP1ôÉˆbÊ-'K`úP‘
¤¥¤¡èŒô}Ì£aì[grÆo òÛŒU~ø¨¦a‚¼º8mSŒˆtìxÇÖà€[„ö·Êó¶€u8@H
¸=Âw(uîŒpÀò–îªÁÕæ€ÖLskG&—6w[¸Çã€{µû,ğT“l[*e$—é±ç½Üö’cJà¥§?Ÿ<’(Et°„{ç'õP2È,Wlì(¯İŒM®¬ã¨AcMÊï3¥õÚMV„k)U"ÈÁIÄÚÛ·4¶DNDê{DŠ2»Œ5×á¤•@aå&¡%%™Ms-·KLL 6Ì$›K&8¡ÅÃ°”Ä÷ë‹5Æê#„Ù;÷e/t‘”İ<U†hÂ¦)¥f— ]‚j(A	ñ>Ê	*`ó'ÇL\U ñÚrŒÑTuæş“mªæáxø±<ü pïCò|8àáÇ¦?âğ0T=ªüõ˜´Â‘*OõT=Î£:§`ôµœ?ÉXŸˆÀzRa=åÁ
tGÚÓ
í‰´Ú3hUhÏºĞTéó¡ıM¡=‚¶¢@{ÎÆLÏ+´t®zW’º/²nL[û;KGw>%â%mü²4ĞùTL‰xÊq¢½¢•ÿ‘
+[©ğj©ğtm©ĞÑœiË¶×çÌkV*¼îI…7´7­T8k¹NƒA8LÀ˜~Bt&F¥#…,Ş]À=@ÄïÇHú‰3<²`·P¼«\ä,"öIÔİÀĞJ‰í!»óèŠ8Œ4“f¤«3oÅ˜šo]5oÇÔO×`êw„ß•ç{S?í0µàLı¾Clª(z>Z=2Tÿ,£úgĞÊ7T?Ò–ÿ’–b¨J^lªrıù˜m|õYk£~"Õi£~ªí?“UÕ?ç÷yÛ¨_(›ıÍê_ògTe_EÆû•/8şoõkíöé6°Qã‰ÏÍ¿	ÄçÿUğ·,óÔç\Ãë;…û½7)ÀÄ@mô~u°štğ£ÛÁó®õ“vğéÀÖêÒêg¶ŠMËÿ*¾^À´üŸ6şEOè|!6-_ptû_µòoe~·”‰
ü¡=¼h)2/£È2Âø'5¢^ŒQâOèn!|Ä¨5¥õÂlíQŸ—µk:FÔ¢ü­FÔbø
#jq–ÀˆZ‚Ÿ0¢FâÓ3¢–Ô¡,%Cñqœ1ŒbıšPÍÒüÓèÎ—€èÑ
a0¡ó¥¢_räß²Zy9íÎ·eÖ²òoy‚Ø2/Cş1±?Ïf´¶´t4¥[ÓæO¬3f~ÒŒYQÁ¯$à;»¶ÒXrIø@-¹VK¦*$D#°&R—Ø[Š^¦:‰åa@İKœì}Å:³2»36ZX>?ÃâåÒk42«Ês5«/G1éµºå"Ò‹Kòú†kJ«ZKr‚Fu¾ZöÆÈX×r`qpŒÂú‹À
ƒ$vç&=„xC‹¿¸6[ûò¸Ë<áğwî®«°×óÕÚÒj¬ÇWî%fœ²Ô«`©õµñ–¥^±Ô«K×ÊFXjËRu5XêµK5¤;2ÍéV³‘e©z¥|£e©œIšrë¨‘¡¯vsI’“xÉXÁlrşüÄ»ˆqĞ²63ÔX÷¤ÜX;Y=mŞ>1¢ëLSŒù¢UÓ<¾Vƒ[„[åÙğák
Á‡íŞéP´L¨Á;^îÆ`óxãï¬+#ŞÄå×]ŞÙTaoæõ¤ÕÄš¼³¹òÎàIÚx²å7b¼ó†#÷§hå-¤²®È[ò;Vd^QáøtÄÍ™n¥Sg+íìM»lÍŸÑEy¬v‹4ÌÇ7#Nmµçí"\;Îrmg®}+ÆµÉ†L.•jj7Û[®êqí4¿ƒåÚkÈµbŒI\µUÌ<^”£~R<º„Uaù‰wx—Š·ƒÑ]L¥cAöš‰Ç95•MiŒÌ}ŒOöÔG‘¾^\½lBçä¶•UqÕOÙ1ÆãDKÕì4¿UƒÇwî.Ï]ËáqA:x|×ï¦HÜ=Âãó<QOû(ëË˜÷p¹üm—Ë÷Tè{…¹|iµwM.ßGïpù¾Úx†åòwb\ş#!÷ÓÊÉ¯·¼–ªÁkïÆx­¾1ÕÑÔØÒjÒ–×2¯e|Îò"(¼“BrĞX7Á˜‰Ü½JWW-AreNÉµÈë¥lŒr°£&î==Ÿ"f¼FaÜg&—¼P»×ï!U¶
WšğbËópüMz²”6¸Bğ¶œûúõ„³:ƒ>«.ziUxé :@\Šâ¾ÂdVußO’qC€OrfŒ‰ùªÉÇÎïÖ`ç‚0òşòœ°ó»;]ÁÎİvîQ:õFØ°HçRXÈ¸Â»UÅ7o(Cîs¹ù=—›K
Ü„¹¹NZ•krsE¹ù}ps¿6m¹ùı7¿ïpó€Váæ,7ÖàæbÜÜÖĞ‘Ê¶5fÍ–›ô¸ù ?d¹™ÁkØ¬µj£“pÇÖÅ^¦Tô¸ˆƒ2Ç£äüTp‰¡JÔìIqŠMbï~èhÀÙt–·ñ&šê¡Ux'²s2¹w¯Îc&¾xÕ23}Pƒ™6:L‡ÌôÃL‚V0Ó3ÑŠ>RÑtTĞêÃ]/£š´ò­èª¶<ZZŠÍ¢İgÍ1láÛĞYúX©Lõ8m}|„‰©³Z× ø:ë	!n1èòğ¿\>IaŸæáFiuJM>Uyøcî%iãÓ-ãáİ½$­|¦TV½ã,~oÚ­=|âí ñgTÙh’kqeã“ˆ½yvw¾tİ´k–Ö°µko~:/{óBÖtìÍ‹ø[íÍ‹ñöæ%,½y)?ao^†OÏŞ¼\‡rEÇ-2†+=Ç7í®R4|D_­®±ˆş,†èÏaq­V¾N»óíÍV+,®'Øˆ½ù9„¨ZœÑÄÍdmíIs+ÃÚ¼‘Ÿ´6oRà7ğÎ®ë¨d©g›;6Å“l:a«–IiˆÚ‹ é16¸s±¬},†*"Æyt‡‹ÑL“Ä­O“İÆş©0÷“YåÖÓ-Ûk’Qƒ[.vã;<ğ+Ï–ğº ui£ Ÿhná{„LZ¢¥jneùüLÚÏkˆ’ÛĞhÈÜ.Ï;!bÒ~E:DÉ–Q½½²»wGhÔfitO}¡î€Èµ6Õ7™{-îóht¿ÀÒèĞH6É$é)4VÍª¦‰ ¡nHê)KD¨%QÖ‡ótL¶JıÀæŸ~I6eCØ¼VBBÓ\lğå¦&ZÑ
ç:l	‰·º·@WÍÛ¦{±4-âÁµˆ ªyh8j}QƒZ‘ç£µ¾p¨%èµ‹PëqEèjµ[j=YƒZ_F¨ÕÑŒü9Méfó”¥ÖÓµQàµÔz[ı7ªC’:0‡ó(nòˆ›o¼Dïp¿„ú‹f	¥’úKªxÛ^Üór!=Ùç'ğó¹*5|%UnÊñwËHPXˆœÎ¡`‡ÇÄ°ïÆŞSœ#hdé³1¢8¢3Q¿¬AÔç„œÏËó…€¨_:D*¨/FˆúwÅûK¢vX¢¾\ƒ¨_EÅdªµ=™lÏ™W,QÿáõUşš%*5*›I@´ `Ğ9F;+)Ä[Âåy¥vø¨dlR9¹¸4$X¦·ÿ…¥àPµÎ¼£_»jŞ_Õ Á›‚ı·äùv@ƒ¯RAƒw"4xWÑô^„,Ş¯Aƒ¯#4ğó¤~`iğ!?™'õŸ
ü#Õ ØÎ °®›'õëXÔYÅÍ“ú	°ÒÊO¬ôŸáÓÍ“ú¹ ây~ ãkò~@ÇW:¸'÷µøE‡·'·±õß¬sşËÒÑß@GøN/'t~Ó¾±:UÊ´òR9|i†0Ÿå¼†F_­ü‰=ùcÚDÆô–y®Ğ»û$?+üÿZøÁ6ª{#„ŒÁ®±êC»\‹–’³.ÆÒığ½ ¿ó‹¾ì·xÙ_şoöe¿…­ıê¦2Ô?Ü¡~ëjÀ#*PàÃAúfÒjAÆ‘¾KGw~‡q,¬‘Æ:¿‹!ı;G1[T+/¦=ùŠÙDËí‹lD1û>ÂíÍ-Í­Y$¦\‚•¡˜ä'³%øR¼³«˜œ¬ñÿ²$3u…Ü2¦‚“ïV›â0Ë¤O4£.¤qtU³4ËE?Â^ÏÆšÑ,‰]¦ù}ù°jâ¦y.'Ã5éû(
0!–'P›WŒa`Ò—Z!‚±Í-ÆV¬±"ƒÅÛ”Êµ7›•,ÆVö0ög¾ŠÅØºÖê„0W”FÁ#æpºÇ‹5òk¢Y5†%¨jVa)İT6«×ÄÒ5°´†àgMy&,ıà`I^XZ+‚¥1ú"‰`i’ÅÒÚ5°ôcK-É††ö®e^Çbi]Kë)ğ±KÜ¾Àé8¤ \ì³jÖqË5ñğc<Œl(Ïº ?:x6Šà¡^‡ÚÁÃd‹‡Æxø)‚‡¦l¶1Ù„3ğMÍZx«ÅÃùV©¦–ƒC•Á|ò4#a#‰€·º”«õZ½YwG
¼m€åz<›(]ï4`r7fqÓ¨¦¤$c÷Cæ«î™¶mˆ‡ªi÷iŸåˆt|
ÿTƒ(B	òÜ8 
nZó¥˜`DÙÄ!
&›*Ş6Zı'ä4™"£š´ò&›kËIÒ2tâ1™şîş3™Í|ÏÉ­çdŠ´à2·…‚ØR
°Ìa ğòóƒëå˜·ÅºWmE¨şR·…pk–yKİÿÜ¥níc[¯œ.äëì
k°€n‚º¥@ít¡şâ®JÛ+Ô©ÊË*°•´šÆV1U`–îü•¹Î´ñNÒxBç¯±UéWÇ/³³V.•Õ/³¿Çı2»j¿Y¿ÌnüõËl-#Üİ’bş·ˆ_†«=ºÛCº‹jeÛHë=ÙÚõËü>/¿Ì^¬éøeöæoõËìƒ¯ğËìËhk3ø	mm?|z~™¤%Æñ¶2†´‡ã¸_&£høˆÎ*„œEô1Dÿá,ÿ3µr^»ó'ÎvV<6¼üO±€s†Çãú¸Å#ÛQŸJ™ıÙJÀ,~R	èÖ.z¤‹Î®ªgKÒ~È ¸•|Ø¢Í%y\wäâl÷ã…â`RBô˜¨¥âÙ^½ĞË¬¼}ğÃb[ ñVŞ}’<á®§Óaâ>«V¦!òÊÙ…ì@éåCš_¼jŠ,Ÿç…8ˆ]ĞmúĞjÈ”äiäm©S°n±HeËŒï¥¢HêĞ¡ÓÒav:,P“õ­¹t[K½°t˜ãÑaP»8ÀÒáĞæ·kË}	˜¤œ§GK³!¢Òó¬k
®LÉ½Ü4·² "Îâ¢~4uì ISÉéB¡»õ,&AqGñlÕ—ÿL`ŒQ…hÀyá¨ŒÄ©2$ô8X‡TAİ€*‚fPåĞUS”¡Êö–*GÔ Ê‚5©Òšmo«O·Õ›#-Uò¨2W»¨Zª<k¾ğá|˜)÷Kz5½Å«.ÃıxZK f`ŒjàqA³McÌi„S»ºp{tÒ“ØD–ifãÍs›D·Ÿ¹$İ‚"ùŠ÷ïçÅHİH½ NUæI¦/Œ”^˜…£Î£%‘W5ÇGKà1NËc…ŠÇÉóø€–¨ĞRˆZ¡å‰Šè“"´œjiyrZ.T“–m-¹tC‡7N±´<Õ£åiÚÅé––Fhéåá/Û¸'õR&‘5¥¯ÿ€º%ŸnS¿Ú´À.l9oú¯ìß¯Éì’‚šIy&Q’æ#56ûëÌ1”ó«æÌáP×£ü,AöÙò<'@9ê(åç:(§šuâãü ÙÂ„ô¬i2°‚f¾u¡6½Hš†²A1¥–¹˜M<kê¢X%ë©ÎÏKµıeR 
Äåü>ïÏ+rôÔÅ°šÄ•üÕ$v_eá¾˜t­·Á‹vwµv|t81x™¸ŸÓW:4û^Œk	ÎW§v”.®c™Uí¦.¾€«Û]¯=Üàõ`õGÿèırô/÷¼1ÔÃNÒÃMnKø=Ğås³öp‹ôàlgiv+›Åô¼Ûy#€şq»¶¾CZO@YTaÑ’Óˆ0RêN­~—C©»-¥"!Ÿ÷h'Kzº·…¦Ë(ï(´¤K!ºàî×£ÊŞ.ÒüA6w”½©K-0/mï!Vu´½‡ù[µ½GğÚŞ£,¶÷?¡í=OOÛ{BÇòdÓ»Ê ò0×öVLŒ"ºŸQµèG7Št?«Õÿæ û9‹î§çšäôÜóÚİÒâ_¨…øİdĞ/ˆ_ÚE<'×®_Ò—õuÍİ­~™M#ºæhJ`ïÖZÎüÉæ¶dsckƒy…Õ¡gşƒŸÔ3_Uğ¯	øÎ.^MS¶âeo‘‰tAÌv€"a €ğ¶¡˜y/’H•Š’”ßfÀkW7Ÿ¼,S6zĞİ¨²çÄıÓäÌ}áu„¬¯âÄáGŒgÕ™‡—î¯à¦!0r# r6i†{r$·’l¸ˆÎÅÃEây8
é¹D:\ë,ŸŸüÇ—„7Ñ
¾uy¾-Ø=u#D¥sİòƒ§ç¾«Dz/Â]–Ş¯ÁËÄx !×ŞŞÔŞÜf>°<ğ¡ÇÿTğYà.#ÔT&‡šÙÜ„@JxÄ¸Î –æ&Ã“Í*%Çş5½#h%WÍ€"²3…­I/Í®½.U	‡À#Ş…ä} ÊU°‘JşµÖĞ™@U¬êFÅ~#6^ì=O.Õ™Å(FUÍÇÃQØŠSì¡Õ§òü, ê€bŸG(ö…¢ôËÅö°ûªÅ–Q,×Ø”ikl®7_[Š}ãQìß
ş[K±ç$S2oûå!7^ôw­ÃàÌšì]ÉÎS0\`…²Â«	>[ëSHÎíşU™Çbq\L#Í˜ÌDBÔâiE¥CZã€ü¾”öı¸¦Œ¹‹ıÓ“ş™?Q­y§1ÃÔœ´ÌŞmr†nr|øÂo’'8”ÇLÈìm£ãÀÙV2Ø¤x8äeıÖØ{£œM¥tDÒh/)w³:_T®,±BÎËÁ¬6Mv'Xã½<Z{zƒŠDÊæ*Ï~ãd²NÕ|?'ƒ‹âœüƒğğòü)àdÔ8YXœüŸ'ÿ¬¬öß'ïi9ù58y¹8''Û›s©ÆFó‹åä_=NşMÁÿn9™oûGt%(ÄÛ‡öåv˜a‘t-Ë+\tSLæ…£Âi<›~®ÒŞC´d>±'t%91/Òä±	¸F@_ÿ¶Ë0×Æïó%ŸäÄ%tÍ$^'çmKÍÏ­ùöl–ÿjp›um¼É¼îƒñyº­7£_&™™CãÉ™b¨úáœıg¹´hpó‘bU3Šî|//Î@ ÕYPái/ÔH8´0{°;?´gÁoPxÑ Ùòa{f/ØbA3ßY\›.!MCw…ğ|}¶lF²‘oÑ¬àY4KJêÉK)„QR ÍÒü>o‹f4Aº¢§¶-ÃßQ‹foò²vÈXÆWŒZ4ËiÇËKÇámÙEÓê4"4ßnØGzXeA³RÈ YQ;XÉë jĞp{ÇfºLš•C}ì+}üÙícåI³Šö±ªôám†4[Íb&ÍêŠ½?SÇ^C[¯)­' ,fÒ (Ğ±Z}-‡Tc,©"&Í_´“U<­]‹DûÉ(×	H´JÔ¤YW;\O:Œš4Ii>–Í]“fÕyš4ãXÕ1iÖço5i6ÀW˜4ãY“fC~Â¤©Ã§gÒl¤c©c:%ƒhğ07i«İM
¢Ù¢{µ8ºQ¤è¦]Ñ¢Õ[µGß®H[¹ŞFÈ»buÊuï¦p3ššRí9æÑlgXü¤e1A;ØX:èìúİn³‰ã¦z-²Šl¸Kû™ñ!F*=wKà¸ÓUWˆƒµÉğpBŒë“qÌM±ß-×)Ë’Ú×,*já7…ÙÅnè-ºsn£š½;Â(QåŞ<½$Õ½;E¯LÑlÉ^œ	ò
“ÅnÃ[ËÉR¦Y¯ì¸ÎaUH$HÙ„¨	ÄvÕlÊòù@|\&o†VCf¢<7$‹AºjB&O²ÓÀ#şd¥Í”ñ3–ø[Ô ş5ˆßÜ–ËeZêÛÍ––ø[yÄßZ;ØÆÿjßßs Æ¨w©Ñ'‰Şè˜óÈZ*¼Ñ=´«‡†¸œ…)¼ÈT,™ÎïªbJL¹Ø\SØ¼ğ·¹üWg¶‘‰x©ší†#P'S§h{yNÈ„º™ï Ó´™vP,î!SÖ’i§dZ³™’õÍ¹¶hÓ;[2M÷È´‹v°«%Óe´ü¼{»ıınÄ(’»õæBw¡2(ç¡ÄÊ«D²Éõyk€oìÙÈC¦n^—Z7 ³J°‡½»7ÈÂ-®d¡Îì£Q‚ÍÊá(ìÄ)ÄX%lcÊsÏ€B¨PHP
í¡ĞŞŠÀ}"ÊY
í[ƒB‰jljmïHB²Í°ÚÏ£PR;HY
=
íĞ‹ô3V™Õ­¹LpÉ|†‚.©wÆâv¨Šô˜tºâÓîB©€CN¿,ïä°ù?œìDúw¹İ_=é›hlöÜ.²‡ao†·qZC¹Îáf÷¾İs. ©3é‰¶ªÉGE`0NÅ¬Ğ/'Ï™Q7 ¢TÌG¨XP$ï¡âLKÅY5¨¸V*Ö·´´eréê¶Tìñ¨Ø«-åÇ@q‚³øÉ"g4œ‚Rj ,Ñ¶‰-"W<”—aàÊ@?3c…™®t5”Ë*İ|šHßÖ“™‘œ9ÆŞZ™Â†a_ı|_äªıxõ8ú ¾,ÏJ€~ÔĞ/øúûôÓB˜­Øš	[yØœ ™o!jÓ¤iÈB e’æ@6ò-„µ=á iÀ­‡!…p°DRI›AlîvÓ	Rn÷õôCÑW†2´CYæééë„tèÃşáÊ[^øÇşÒì6‹éĞG²tôÔu©Ô¥­çJë	(‹éĞ(
tèªV?Zª«¹s¿Ç#@ÕNÖótèãø;jæÌ’Qoñåb½¨}‚vx¢tÕ¡»¥ùIlîêĞcç©CŸÌª}
«}*¾B‡>%Ğ¡Oç'tè3ğééĞgêXÎ
cºGq¶‡é¸}bbÑ}®‚8Ï¢{\İ(
tèóµúÚ£¯C÷Z¹q!!Gtèõ]¹¡<:#—Ã!æTƒ¹ˆ C_ÌOêĞ—h—J]ïÊÄ\{7m¨ŸPß<äå=óœw°ù\6—euâ5Û¬Xöº±ˆïONšJè¸AÄÿåŸOåê÷­a3D®‰Æ\¤‚:mõ(ßrŸiY¶^=§—¾ ‚LpÓ­`zu.|`ØF€£|ÓtÌuæ2¾zHG&6«ær–ÏOGbãRé
´Bö;y^%Hu#Ô‚TºÚ²¹·'yâşZiµà±ŠB"f<×‚?Å‹2îëYæI†B’áíàÆ0¿öI³›<~%™¸YYu<Yõm}«eÕñqVEQÀª·iõÛ#¬Z²¬zGVİ°«6´5vdÛSæNËªwy¬z·vpeÕã½€¥nWu{)İ4²‚JKn§sK²3Ùc3ğ÷÷ƒ1&„˜~BbŠ0ÖØò8ñXÓ«}P.¦âÍµ,šàö¯{cŒÅwÇ¦çpŒ4Äë~a©äù`ÀX¨0–àŒõÃX´¼VL=!…±¤x´)êj¢%×’kÌ5gÌc–{¤xB;xÒ’â+Ê$ŠrªD6d¶„Ôp¦J%ÛÓgı¨@*ö5èÜC¤sãd	òkêí"Ì¯ˆ}ÖÓ‚ ™É MN¥‰Ú/·§ûyë›JXy½Î=4‘‡íÎ‘G[¹'Ù¹ E`÷‰1¸rÙ&ör÷şêÌS1Z¹Uóôp´ã´~F¨üWy>ĞuZñ@ë¿Ehıœ’âù­Ë–Ö/Ô õF5hÊ´ÕçÚÓMæEKë¿{´~I;xÙÒúÜàg¦Øy±!r£ISoB©DÆ±J½Üwãh÷„Ä˜·œ2iêŒ†ÆõcÜ,âÚ?¯¸qk.Î£É¦ ü=EH÷Wb„!&ªæÃH‰æU!Ékò|= ê„Lƒ0oDó¦âí­a*–0o× L}Âds¹dk®Ù¼c	ó®G˜÷´ƒ÷-aæ‚0S…Á¤½qÔİÖòÓÏ+ÅÄdµ íj,é^ô™Üÿ™d²vo\’” 6rrLg\_uæƒøÖUóápD âDø§ ÿ#yş+ êD¬‚;D âÿ‰âèÓ YCXñï—}4óÿÏµéÒ4”Í	Yûõ%Ûøz“§÷%õ¹3ğµøF
TUş7¿Ï{gà[‚=µÙS™¿ãï¨Ê<[Fü½1tæèÎÀÚñÒñycãª°s£¡HÁq*9Cõzg¨Ít8-T~V˜ÿ˜P:Eõ?Öôõ’á/,óôÔ·6´ˆ~U`¿ùÄ—P¢ô”^2hoê‹Œòwg”ØğûCGÙÊQ@ª ^ ekx”¢8ååB,óF‰úÎ(V`‹°pú/›(Õ¤ÿZ4|P€/æo©f‹+ğ%¸¹¤ÙH6‹mK²tôÔv¾çRÚz”}Ïö¸j†¢Àh[Z«–êÊ‰Ëğ{Üh[V;éğ8p9şrà2Êåù'Éß‡ê‘Àı?i‡+H‡Q£í i¾"›»FÛ„ym+±ªc´­Ìßj´ı_a´­Âm«òFÛjøôŒ¶Õu,k„1=$ƒXÓÃtÜhK(&6&º×Rc,º7£E&ü­¾¶öèm[É¿!GŒ¶M(ù½,~"_f¤Z“õíõ)³.ëÃf[Ÿ´ÙÆ*üq¿³‹±Ér
\„{91EÕÉP–²ˆ`íÍbZ”ª1$J˜f`øãJ9lQ0R•ÑøÖ™&‚K³^nJxÔx~İ{®uyŠåµd¬bk5{ì=ä^n"½;Hƒ§%n‚Éğ]½:³>ß3d sU³Ëçg ‰ñÕc<ZáŒ˜<ëcb ¡n„2<$fYÚÛÄ¨WD7Dyˆ%dcBn'd}}¶=•B`r“%d³GÈ…ßj	y9Y"ûÅ`µ[>ğU§Šˆìg²&Á<BŠqÿX™‡2±Á`/(Gºp=š¡V
lq˜^4*Ñ¥¡)Ó|önUñ‚¼Vjİä@6;Ëwù1è Î´ÅBàxØp2âéRLçÆAP7 ˆ`˜Ä"ÙT¶Y„ ‡Z‚L¬AÍâIg²¹–Ö\«ÙÜd’GÉ
Š%È… ÈÖ’šl,(¥:+HÕ;QÓDî’s÷7{ùøi¢”ËıL2®!l¼Ş
LÉ§«%Æ{›WZ}…‰†a[ˆP¬:³EŒ6DFÕl9m€—8m¶ªl-ÏmÚ n@A6h³m„6Û)î:#´9ÌÒfû´™§M{*›¬Ï4µ˜©–6Ó<Úì ğw´´Ù´³;26ËyåõxGb¦p¶ÂK~±¥²°0³İVcš¨nOª«cvŠaC­š‡ÃFÇÜtÁÙ.òÜ5Àê˜T s»E0·»¾ó<¹ëÅás{ÔÀÜæ5Ä®kªoÁ=-æöò0··ÂßÇbîCZpiŞÍi7I…§aa1¼I÷gàœÓl[ö¶,'ÌV±²)ÇÄ¹ÀÍ³œ.’äĞçt÷H4„S¦Ãş<7}´²	}ì©&X…«F?ñ0ŒG^U'»¬\iÄ$‘İoÙÉPoƒ:.;†ÖcöÑ—­šÃÑ¸Ów?¡lR©€¾¨ĞWú¦#ôÍ(ş³úaé›«AßIqúfê[ëÛš;ÌLKß¼Gß‚ÂßßÒ÷MÎŒrô"%ÚxkUS41¹oÆ™/Â’#êtÆp&Åuc°¨¨³Œ%~œœìÙ±Şj´D(W<®^H.s ¦B7‹ô×²dÆ#RoÙßü”CpÙAêÉ]ÆÈs4³bt%"«¦{8º§qºöE{åYèŠº]…P kŸCW—%Å»	šM—GÊÀÊA3ß¸¬hÓ~i:G“DÔÙl6ñmË-<Ûr@ªÓ‚š£í¥ °Mb‰  ß¼8JÆs Ë<“gËUr‚RNõ¶’æJ³ƒÙ,f•ÂÒÑS·¢š|¨¶>LZO@Yl+	EUr¸V?Bª«Ur$¿Ç­’£´“­=«d.G­’ªŒ²j‘oë¨Ur´vxŒtµJ–æÇ²¹k•l3O«ä8Vu¬’ãù[­’ğVÉ‰,Ur?a•œŒOÏ*9EÇrjÓÇÈ Nó0·JNWLlKtŸ¡ Î´èŞ6nVÉYZılíÑ·JµRèBX%Û¹a¶dÌ­©–ö†\›9—Õa”œÇO%ç+ø|g×=ï|&TXŞöaªğ"*ºˆeü tI¡!WCí÷±OúpPÕÆIÛŒ`päÖHÆ‹…£ áŠGW7µJdºÎêÅKEf.µ…ªU]È·
™ DSÕ\Äòù™ ÀX\Æ\ŒV¸;J—
~ÄAİ c.³üë™ —+Z¯ˆPí8Kµ+kP­3FµTª¥!×Šğœ«,Õ®ö¨v‚¿ÖRˆÍ=eCŒ»qû‘ÜÃk‰;…Ö»ÇBNvkÊd ›‘Á"ã%6™dxº5	]¢ÜÌÒDoÈ¹%Ål&›Ö¬”ğ*è5™ºáÅ¹.F" {_ÃÑ¸ˆÓã¡Äò¼) êôƒ7;ô Ì¿EvkĞlû°Ì?^v[ĞÌ—ù·kÓ;¤iØ¡ˆ°ÿFs'ÛøBš'ôï’úúw+€{¤`>gëıP‚{	Óä'ÈØîc™'ÿwÉÿûµ‡”Û<ù¢4{Íbòÿ!–º#ÒÃÚúi=e1ù¢@ş?ªÕ“ê*ÿç÷¸üB;ÙÉ“ÿOòwTşŸ$£|Ê"ók§¨üZ;|F:ŒÊÿ“¥ù_ÙÜ•ÿ;ÏSş?Ëªüÿ«ü_!ÿŸg	äÿü„üŸüÿ»å¥0¦O‘A¼ìa:.ÿ_QLL'ºÿ¡ ^µèG7ŠùÿšV]{ôåÿ©V’¼AÈù¿kH%“ÎÈ´·à”EG›y“õ± ¼ÅO. o+üw~g×nÁ>S|ªÚ§’VêJd€b‹›	¯äµ¸©°‘BşÙ–iŠ "^+»ï_gŞe—!éÌ—¨š÷X>?éŒ÷‰Kƒ÷ÑjÈ| Ïeğ"Q7‚$HƒZîò¤óGúÎÿŠàô4‹Ókàt·8N;šÛ²ÍHş‰Åé§N?SøŸ[œ>ÙgåC±mV?b"vÿ7W_k»EsqûÉÆ§àÆ;‘ËBæ%‡§#“åÆ*N_ªO*8 ÃÛ?6Æš	ç°¤ĞÓ3tY¯3_ÄhGdUÍ—ÃÑx‹Óî+¡Ú×òü& ê´b€vÿĞî[ÅíwÚni÷}Úí§]c¶§^S9óƒ¥İí~Røÿ±´ëÔˆ<¸_‹}0¶ÜôšÎ¬°ÔñOŞè).½Ğ9b6©ÎüC$G^5ÿ‘x‰8"ÿ'(üE¿ˆDİ ‘‚ ò·"×ı#‚È3,"G`+'*XºâˆlÊ5·gêÓfÖ‡`YŸ,áà/ŒÉV‡\r0Ï»Ğ¶©Ÿï‚òÄÚ°!¿w§W:Â…W;J6âIàà~?É]lÖïóÚ7Åli‚D¸6¯°çUµ	jáÕìœ¼òD³B¨±Ä!…ÙŒ,‘çS]ı»’DUy#adÚyZ¬8©Ak^09• ö5³Y0+¨M[_g!:CB“ªšEY>?¡	ZÅùe1´2‹Ës	!ŒMÔøE ü2’=8Çµ–Tz.4Û#¬B)4óU¨¥µéhi
Æ,÷@5šeØÈ×¡öòt¨e¥u¨åÂòR¾Ú?5˜"4_:K†µË<íiïö´¢Â^I`ûÍÎ–f+³YL{ú3KGOİ‡Ëù*ÚzUi=e1í	Eö´šV_]ª«ö´¿Çµ§5µ“}=í)ÁßQíéåZç å¾QíiŒvøé0ª=+Í×fsW{š1OíiVu´§uù[µ§õğÚÓX–@{ÇOhOëãÓÓ6Ğ±Œcú<Ä†¦ãÚSbb?¢{#QoÑ½_İ(
´§­Ş¨=úÚÓùVÈ5rD{JºÑÊŸ3Ú›šÒõ­ÈÇÓÌr-ü¤”kÕÚ¤M–Îˆiû	G•iÛà¤`æ¹ˆJb&¦¹Ø`¸†ÆÌÄMŒoƒLéån_:+2’a„
vˆva ·ß0³=Êê/tSˆğ€'“0èB.û~ÍAäÇ@‡L½ÓOåşoíLk@fiç{„ÄQS5,ŸŸx–ââeZawH›FD¼ nõ/›Zõt²Í‘#”ºÀRjó”JÕ T:×–iÍæšÌ$K©É¥¦h[XJíåiéÅVt&h»ï6hMıŞ¡Ÿ¦Ì‡fÑ‰ÈW’—9¡pS/nÂN+È“Í–1ÌòUªf«á0‹·ŠcvkÁé6òÜ6À,ê˜T³ÛE0Û©/¾}³ZÌN­ÙtÌ&Ó-É\K‡™f1»ƒ‡Ùµƒ,f—ÀJmh_M`ßš7Z»‡$1îääAÿ»Í ÁÀV)íšç	'0|Ğ[öt&q1µSI&–ª½:õœ‰d³ƒW›‚¼¾Ó”60Óˆ>slBÕáXÆè_%@tr9C‚YîOÒ¤ÒQgvñ_5Ó‡ãĞ Î»ì*Ïİ>@İ€„°àƒİ#|Àài\dù`Ï|©ÁÍÙ†úLªµÑìeù`oöÑöµ|pQH_»ëÀÿNèIĞ9¯ÚvlIqnõ"Ë.ŒB·7$Q¿¶Ş'UòpÍê…áæsQúËæ„lNÑ"­ M	R¹ÌˆQ‡è¨šı†£0§NRè’’g: êÔtƒ:‡:ôPey¹ Y6¬^],›4óÕ«¼6-HÓ‡ªRÀêbög_»šéiW³¤>CŞº@¨RÒËïóy+äè©yO9éãï¨rr‰Œ¸dGŒ… y3ÚqY:«u^¬VªU! _?»T€÷³ÌSë
¡8°Ù
{Àƒ;gDR,›Û+%7ô@6•±Ğúw¹Î	õr™ô2èö²Hy<@{9Pzñw¹4;ˆÍbÊã¢nµ™ƒµõ!ÒzÊbÊ#ŠåñP­~˜C§Ã-"'áĞNº=úY‹>WÈ(
èÓUçj‡Ué0ª<^)ÍfsWyì™§òx«:Êã±ü­Êãqø
åñx–@y<ŸPOÄ§§<¤c99Œé«d§x˜+§*&z‰îÓÄéİ½qt£(PÏĞêgj¾òxµ˜grDy,º²Ì¾é¶öl[[C›9›õ¡;ÃOêç*üó~g×!y©ç3å*Ï¥.g™Õp¶Q)ºI‚;D¸3‚ "Ù™¥`´[6ÔH
½û÷#õGb’%âet)—%|9*c­3çsl!}o‹¤‚,ŸŸ>ˆËÃÑ
Yåy±¼¥èƒ¨Á&äá%–=}ğREÎeä_c‘yä÷Å‘ß’Í´µ¶5¶š+,ò¯ô•Â¿Ú"_«¸Ce×Ü©,SjL6±t'¨d¨4‚ëÖàÇ‘nj$†dÁk%²y"4ª3×ÄpË—©šk‡Ã-Ş+Ûë«×Ëó† ·¨àVÜŞÁíMúî7Gp{­Åí-5p[Šã¶½#Õ˜Î45š[-noóp{»Â¿Ãâv?WÕö·˜°Ô/×"ê!‰GG˜• KÎX­ÚÇ¯ænÇ^	¦q”¹3†]¾NÕÜ5vñfqìŞ-x½G÷ØEİ »‚.`÷¾vï×· ‚İë,v¬]Çn[¶£¹ìk²Ø}ØÃî#
ÿQ‹İ=€]FØ¹ÉGª#ì©ß¹
ÊjÅ¹êäUuXåHXv­ÅĞÊ÷¨šÇ‡C+^)Ö'¡OÊó© ­¨ Uğ´>Aë3úÚ õz‹Ögk µGkG¶©%Õj6³h}ÎCëó
ÿ‹ÖBQšÕ€:^¹M5äKø)¹E4 |ˆ*9¼›´úÕóî¥2”†ıeMÚÄ½’b¼¸šYc“ïRÄÑílŸ%’ì…Ãƒ8 ‘9Ş˜RhÊ3rlÆË½Q8ìÁóUp(Ô™cÄ$öªæïÃˆŒó%!ãËò|% &êÄê€˜ÿˆóUEökbŞ`‰ùzbVâÄdlU²¥©Ş¼a‰ù¦GÌ·şÛ–˜‹t‡téaº@à¬»O‚Ñ’½e˜j%ªƒ·ÔDËo+1ˆrCo‘:’F÷†0j“',´DêOä“•|[¤8ä•¤VbB¹lD.…µ6Š¢Î¼£ÑQ5ïG`&N÷„.ïËóƒ€:¨PGĞê|èP‡¶È?{ÍúÃ¶È2°Í|[äcmú‰4]ƒ‰<æS¶ğ-‘ÏùLjÓÏû¹6ÿB
jŞH;w·Ip¾Ò}“ê+–yÁœEğµÿÆÿ¿°ù7al¾åÏÑS©R~§0¿˜P:`óCh€7Ë tˆúÎÑ•ŸØ¼·Şd1?;CÃ©šÿêĞàĞş§Ğ~±C; <´_CC»E†ö›;4Ô·CcãßØÌGù­ÒlîØˆÛ9°tôÔ9”ñ­Â±t`\ñFQ`ç,¬Õ‘êj.Êïq'ùbÚÉA³8GíĞÛd”KğOzğå ¨3R;\R:ŒÚ9·Kó¥ØÜµs†æiçŒbUÇÎYš¿ÕÎ¯°s–a	ìœeù	;g9|zvÎò:–?ÉX|Lß!ƒXÁÃtÜÎYQ1q0Ñ½’‚XÙ¢ûà8ºQØ9Öê«h¾s§Æ«rÄÎ9„ÂØ»N3{üã¸J»-kVcmX9«ó“VÎ
}MŞÙõ#D±$îNzÄ¸‘ˆ`æzõRqrçZ‚å»“8Má'ÊÄÂ¦ñ¬L]ƒÔ6¿]_{’Ş5 ½E\õ\Ÿh—cøû`4i¤‚Vnš1Yª7öO¸Û†‰Ã²h œ*%ÙÅtıİàg¯ã¶ç9‚SÕ†Öôÿ1²­ˆaìŞ°|~¶—ïcĞ
Û:ò\[p+¶êF(ù¾e}Ï¶ZWI²^„àwY‚­AğC£oËµ6"wTÎŒ³_ß#ø
}¼%ø®bÖªƒ\‚½“šÄM	Ï«ËÔŞ‰t¡nÃ2Eº›JNbpu–›ÑR¼a¡|ƒª©¡x™8B7TÖË³!@(ê¡„6é+7Gz·EhK„Eh2ÙÚ”iln7­¡mBÛz‡Eè²L…A‘jûpN;	n¡ºxÚŒb¡Ò1“¹¸©Ï€[iØ´g±û)5M­è£^Í26Û¡Ïèq2ÔÄ_İ¼/6¸íÕ½÷Jõzt›n•š/§¾î¡8s{ìz«©—D§‚¤¡Bèy­ä`ufBŒˆıªÙx8f !âÌ°‰°Á¦òÜ,`Ô˜A¨f˜è0µ§Í•\“‚f‡‡µ§{d`“ƒf¾ö4E›n!MC\nn$Í–lãëOGzúÓVRŸúÓÖ
`)ô'¬Ú#Š¹ÜFÍÁmUÛ˜¿ÀÜ+ƒÚeötTH9éTĞÛ[Ğcå&G–½k+m/ÔÛÅ ”ãÉS	3¸âq:—Õ
sG9e!íi§Ğ ï“îìõeºÛE'¡y¿4Û•Íb®Øİt(Uewmİe‡R¯™(
T”=´úR]U”½ø=®¢ì­í©(ûğwTEy@F¹¯e	Èñ££*Êíp?é0ª¢<(Í“lîª(ÇÌSEI±ª£¢¤ù[U”¾BEÉ²*JŸPQfâÓSQò:–BÓÉ ö÷0WQf)&%º»DE÷±qt£(PQzµzQ{ôU”‡­€í#äˆŠrœk/
ŸÎhohnJ¶àpT‰õ¡¤~RI)+üŠÀïìj{Ç{èá¾a ¬Ø—mŸ•xÌ.j¦Ÿ0CË<GY5³Y>¿e¢´2sä9(£“eu#X€ :À²Éô3^ê@}©ƒ¤Ù/î„=
óÿWÌ›Œšz¼p›?g‘ì€£l9DÁ*àæ“¹¸ÍÄ9Œ|¨
ÔÃYæI˜BøíàÈ0[=&ÍòØŠ¢.ËE$º3s•£N$GUµõÑ–£NŒsŠ‚	|ŒV?Vªë>ß1WDSòˆœœVÌdÇŞIéİÇk‡'y“ùşNæÇeÄ'Zô½'¹“™™~NÒÎOÖ7õÙù	ËÎ§°i„O³s®#•Jåà€=•õÁÎ§ñ“ì|ºÂ?Càwvñ|€8-x²OåÉ—\¥Ê˜ÛÂÖ;N¾jÈcVt[?Ø€gY/ÀCnC€œt7sõ YhÛ·ÎœÉñ†¦
1P5g±|~SÈˆO•³e’œ#ÏsåÍeª nÃ˜*ç9¼M‚œ¯» B'-A.¬ASâiÉ4%ÛÚZÛÍE– {¹Dá_j	Bâx¼ë1rÌ8ì Õ»‰ÄJÄ$o
nÙ_àMŠOzª)dlFÎr7İ…îæ9’¼yù[é€?Øz°»¼(Ì ’Án’#ãZŒ:D2®G`¦FÆ5¡Ë•ò¼* êÔt3ãšCîO_£Ø»Ö™«×Ù¹ÊäÓq¹g%»ôß±c2I3óôz§§zóô†Zóô)yƒyzjtú&íøféx~×O5ù2ï‚óeŞÓÒÅ­,ódŞi!­ê6íáv¯*U=¤¥@6_;7©ÍfÕ)x|îÔ7="ğ.v· ›€²:uOhdÏÈÈîuG†ú3ê>v¿7²ÿƒ3êghæAÚÚC
ía;´3ÂC{$4´¿ÊĞu‡†ú¦÷˜{\€ù¸~Vš=Áf1MïIÊ™ÊSÚúi;”3ãŠÕã­şWíÌ—Õ³¢áYBÈê³â¢¡©½¡¥¹£û¬Yı?)«ŸWø/üÎ.Š9Ë¥Ó×›öŒU† wä¶3ã%rJ#c’HÁí_(¶^mo:¢¡œ vJ#fzÃN1ô˜İqõ’ÂPÍ‹|HpØH`ùü70Sc#­°‘ ÏW"¸Q7‚nn$°Ë
Ôq^Uì½&Í¬£óÇ×q^g“QSÏë8ÏÉ€ßˆ€{SÁ½ås˜Ş‡÷¶Â;'ïy÷:Ó»
ï=÷Ò™ŞM…êîT874K?Ôşi;p”<+@ÔÒFvÙG„jIS“ù—N‘ó8E>V¨ŸØ)r^x¶~â‹2ÄÏÜ!¢¾3[?W`_0¶ş]š}Éf±Ùú•å|åkmıÊùñÙŠ¢`¶ş[««ù³õ%;[¿#äÈl½ >[SõM©Ævó=ëc¶şÀOÎÖşO¿³k_øbvcüDq¶v¹–HC®­rsİØKÛË† NqiÜd¿—Ükº§DŒœİñO¸ArŞF¢]ãezW’¹œ0g!àŒéhÑë›dÿpÛS÷È¹Mû-—‘»±­¨ñÊş•ÁÈ¿ÏL:iuÔŒ’59DA$r‚;vú{&•±ŒİÆ^^Ç%·ÒÈ–YXµñÏñö÷Ú3Ş‘1zšÑÓ† &ú˜¡Îü‡¨É³j~fùüdè—5ÿE«!ó?yş"DYƒºf¬ùÕ™Ì”5¿)í—f®=Èš?ØdÔÔÃ²áeğÄh¹ìøpâãÿ/ßÛBlG-ÌŸ£§^ÄÙ²ˆÂ\T`N@YHXŒ5ıøŠŒjq–yº	ê;À
l¤?Àÿ¯|oK:£„²”òbr”^Úòâğ(G‡Fùå2î(Qßå²
l9;Ê.{9;âjä{[>üUş'ø%!Ùµ‚_Q€û˜{Mš­Äf1Ùµ²¾ç¥|Ï?këUì{^—](
d×ªZ}5íÌ—]¯[Ùµ:!Gd×eqÙÕÖšnhÈut˜5X²kM~Rv%şZ¿³ë$ªÎ"D¸Q=€¤ì]YzwC(ì#´‘T¬³›JS#ÉT(¶I$5³$ëÍçn.ş™IîúˆDm×™1kh²óí«æ/,Ÿßd"â“}m´2ëÈs]yk™ì¨Á.&ûzìÁQ,Æ*²ÆI3Lvï%_XŸFM½<<Õßán6^mè&’®NÁ]÷¦€ÛÈG­¢^Á5DX^İ®Ø¢ò‘Æ·¿%Àš\n¿ÒçvZÁÍ
·%Â€o[l­Á€WÕbÀTc.ÛŞnÚ,¶ó“wÅv(ü	?êÃd/p×³îGËFí]Ç !èàn:eGôÎîÆÎvÌ&¬Cçåş‹cù6×lÊø*7ã'|•ñ	'X’°İé‘˜$ÏÉ tÀò’àƒ)®¹ñ½…yKÅ‰çU~G»ëÆ$ÀÖ,=õjJ€m´õ¶ÒzÊb¾(
œRÛiõN©®N©íù=âUng¦j'×xî4ş:¢Ş•Qî`ßÈ¼Æ5piYï¨îät¸³í÷×º–uoÑô$»a[O×®¯õºŞ¥V×ïI×»]_µ­wÓ®w—®‡Ùªè"ùïì=Xæ-\×ù|Ì…zO½—€®5w÷fÛQS¯O¶î>Ø¾
l†¬ÆÜİOÁİ÷¡€K:à8wS
.m_;®°§ecE¯œì¤d+Xø³JˆÉh9;Ó2Úá%5Âß?e`¨ï,©û+°YiæaúÃ…<ıñJt;CÃjß£C»‰CëUhE;´›ÂCëí#ZÉê;Æ„Q`eæsÄ¿¤Y…ÍbÓ±_‡r3‡2[[Ø¡ÜŸ(
ä9Z}P;óä­<<€#ò-5v2ÈğÖÚÖjd},Èñ“òÂ?Xàwvíiæ»icã^d·µé±‹sÍ'¨ñ‚<£kwô,ŒoÁ{i{äÊ{gVÂnò"ç7ÎWiâ?’Ù×Ô%7»d~¯;·şı\¼¡At…àM¹î’ƒòÆLõ@¢yª^IU”sRcv‡?,Ÿ¤5‡xT$C
3µ5üë¦%d¡ Œ½ônN•+˜ >°µ/*ï
¬ˆCˆóbA*â‚–ÏO± AãŠÅah…«[äy„POÔp	”#Ùƒ£X¥DŸ+Í œj¹ªl3jê­aò‰ŒøhÊ1
ïX;Yky æ)Psf-vÇëT¹Så{¢*·…gíI¡Yû©ìdwÖ¢¾3kOQ`§†gígÒì´š³ötÊí’1K[Ÿi‡r{|Ö¢ÈÉ˜¥ÕÏÌÚÏí¬=§Æ¬½#>kÓÍÍõ­æ\;kÏófíù
ÿ;kµw,÷ğì~ÅóĞ‰‡üÇkS˜Ui\•%.7?ƒWb‰åœ¯Ü­â³¬&„uï^°÷uá2AÉÒÈ€RMÿğ¼İP`Ø1ç
æ´—M~~‰Ûğ2 ÛŒ\šº”w…ÉàÓI9+ìm}ö÷âÜhò€T/ƒ§\¤/vÄë×.ŒM2"ù·†›dÀü[2½.‘ç¥Á$Cİ`’	Q™+2).W]a'…kÊ}X½ÜÿğÕä+CÜü…Œù*—›ï©W+ğkxm?Àµl=jê]á	ü¥@¾Î+5ÌëÜáÉñ•Ô½±æä¸I'Çİœ7kë[ìä¸;>9PL[µúm‘Éñµ·×˜÷ÔØèjhokooh2wØÉq§79îRøwÛÉñ¥^s]áÅÊzåJ-¿Pàç¾wV” ½$·Á‰%¸~YKe‘(±2ÎDh Aˆ×1d±AÈİÛô£K¾êÿÇÙWÖU4oÅ¡w)Å¡„¸!¥-VB°RZîMnÚĞ'iKqÎ‹»»¿¸»»»»»û÷<3»g÷ìŞ$ßûûçœÜÍîì™ÙİÙÙøçŠÕY{k«1âÖã¯¹+³îôºCeq-Ñ~uÃèŸÖÜ´Wd_ZQ^
—‘h
µ¸hj
 Ëñ¸S˜ÿ.yŞí¦ êº) ¤Ã¸Çc+š!İ«”¸Ï5»#k†ô­ì~×,5Cz@›>(M3fHâK<Ä6©Ò]Öéa©Ï=éğ¨@¶OoµÔT¨*'‰˜¿‘ë¦ÓF?®,~7Yü	…ö¤añ»³[ÑS¬™J‚ßÉG=Í2{6@}O¶}F=k‡fÔEÏdØxLéîq§Ïe@/ Ÿ÷Aß“Ùå^PĞ/êÜ²GÅ¤ÙKlÉ¦/ëWŞË¯|E[¿j¾òŞx"£È_Óê¯Ku=*¾Á¿c¤7µ“ûìyí-şŠ?Ê(ß6Ì€¥ë¾Ğ éíğ]é0<¼ÿ$Íßcsß éşŞgUÏ éşV¤ñ'>b	õóCı'x[¤Ou,Ÿe1ı³âs‹éØ éÅÄD÷—
â+ƒîbt£È­›_kõo´Çô(ğ‹Y7¿%äà(ğ ¿nÊÄ™”+¯v®¢,ùõqøo~Pø?
üÆæÃÁzÁ§>šj{¡òBK÷ä®ö½ÅÔ70«˜Ùz[N?¬­Ø˜‹ÒGkW„Œz -Œ;ÔkEpÄñ…`-Ê½4<¢jN~â3’3?~,LrÆ÷Ç+Ú/hyş&+’3êHÅŠö»áFk¶ü‡âèÏ€¿üU„Å4@z†ÚºŠ–ºäoCƒ,şUø³Ì§4øRö.ÚÀŠ“61ÙF¸¹HØBW“Xî2!1'‹q­	‘§(°1M¦ÏÉ®
m6r‹œŠ”æ<r)©uËdkkÒÑèQ”ğ¼x«>ÀLòaíÃ~588ˆê3C-€…R6À¿K“YñİYB³ıÉl,ŒĞ@rLèah…è_òœC0*„F]Gh¡='{0k4õsá71·4sÕ3„‡ÕƒÉöpLèºš¶\[¾º-™—õ1Ùæã›“m~…?ÜšŠğ­‚4Ó£)H.L"Rö‚Ù³;ğfÈ¨tf@óÜdD½Mƒê!›@G'U% }jG5“)Ù†â?8ÑPÍyJ“"bğëû“’¡ˆDÄÄXPÈ°<vÄ@İ » Æ"1(G,ªÈZÌ5{$+Gü.[Ü5Kåˆ%´é’ÒTä
}í=“0n)6H…ˆÇ¬±´T¦±Œ¶^V
œ‚ pÓĞWp67ËTºáş!ãYeVx<³O¯ €G({Ù}úOi¶"›EûôH––4=Ác%m½²´n@Y¤ÒE‘Û§WÑê«Juİ§Wãßñ>½ºvò¤İ§×àïpŸşKF¹¦A6&Ô“á>½–v8J:÷é¿¥ùÚlîïÓO¸O—²ª·O¯ÃßºO—áOìÓå,Á>]Á7öéJ¼í>]¥c©ÎbúDÅt¼O×*&&ºëD½A÷Ó1ºQäöé­¾®ö˜îÓÿš¥c=B–g¸t”¤Œ9©¦­¶¢¢¼¥<YŸ•±nlÀ7×Ñ
|CŞØ|7­„yŒàù&½WœZîğK‘ààÑšC A,'Hµ ©]$Z”ÔåvÑ @Nñê5d|9´2ŸêtÓ…Å»¡7m¬ÓŒñ«`b˜Q^²Q¿oOú¦ xi2†_–ÙÛ‰(ø&°|°%8‹W™qhçyn,8’%uB`•ÙÄp°İÛ7UÔnĞm–°Clˆ¬%Eèöl@7äJÏU¶Tæ“Íİ-İ¶PàM†nÌf?¾YŒŒ¾´±4Ä$Ñ,[²b|iXÃ;ÚaÚ@²‹m¬:C;5e ^…Kúº¨†¾RñJ¢|º¹èı«wºM¶Œ¨CtàBg(ê 31u¶ºl#ÏmuP×QGĞêL¨³"pb@Yu¶/BçêTÖµµÖV¶µ$;ê4[êì¨Àw2Ô¹ÔPj#rqr1g|ªn‘knŞé|ƒÃ q)jCy‘¥ŠE‰—Ñ<¡
ãUu¬dsLj!Ğ©cÖ
‰±'ŞGIaÏi÷¡¢66æ¼ªÚ’iĞ]';Gô!Bú“]†¢pÓgW¡Ìnòœäèƒº>‚pĞgw>Ü£sŠÂ¼kö|vMÖâš¥{t«6-HÓÌY?G}IÒÆ6é6ı¢İ¦'K}nÓS@»dïñl&ÀTÑ¶¥;î0ÔT–Ùú¥ÌY½CAwZĞéÕ›ñ8Êñ^We˜–	c0¤Aœº2ıÌ.ıtûı¼œz´Ÿ=•½­@0‡4KØ,zYZÒô
w¨>m=MZ7 ,Pä‚éZ}†TW`/ş3µ“W­@°7‡Áœ2Ê}e±Ü¾
ûj‡ûI‡¡@0—4ßŸÍ}àµ‚XÕäoÂŸf	‚Cø†@p(ŞV 8LÇrxÓsË ú-¦càÅÄëD÷‘
â(ƒî×ct£È	Gkõc´ÇT ˜Ç,]Çr ¼áŸ%dLª¬¯k-T×´$Ç±>d‚ãù¦Lğ…‚Àol>Ø¹¨¨Â±Æqíè†¦rIn¦df;7¬EX_ú˜»ÉfV²ë/Œ¹å R1D…ôZ7]HªÎ´r[æè‰‚…šÒ©¥¡Æ_/MNäğ2;?—-,lcÇ·ÇKÓÉhoy**;êÅÒtšáD›-ıtÅÏÒÌ-´.èêîíìF"ÃB²°É2ÔrºTœI8é\œWFËìRñfF'¶vstctòBºÔÂæ\¶ŞôVV'?Ÿ@>/õù
î3jÕ`
¼N¹“§!J—è2ËsÎÀVÜ/$({I_™\¤¬û6Y÷b…z‰aİ·³ŠÌK3_<¿Œë2ÿ‹QßSd^®À®È±‹LQdˆ)¾_Wfú.ı]å÷÷Nf‘¼Zû»FúK	³€4»–Í¢Eò:ıôwåšB[_o>ıİxÖ¢È»¦Ğê7jgé¬-1³ö&Bfí{ñ¬…ª­¶._Û’ÜÌú˜µ·ğÍY{«Â¿Mà76_B"+İˆ©]İ3TÔkí¦¾¤Ö*§ã†,én&)P$:Âê@ªëìf‚e\ñM.±#òÙÙÜf=HfcÒ›S~a¬è˜ÊNt8Ÿ¹ñêC°Ş½•ØB ÂÙ
¡RghÚ;$y¾Z+Ùïnçdæ5Q‚ë–6¯"×h…ëyŞ-¨yºÊy½àÍêhîUŞPhAC¡û‹Pèı˜Bp««®n-ä“…´zHá?l(´	ev»"b(PD$Jü£Ön#¡Ñ{!Â ™Ş*™ŸÆ w¸2M‰pÈA#ÉP8Äøc>&Ø{\O8¢®Ã¡ 8|2ÀáSúO8\Èàğ™"8ü —·•—jşYƒÃç,ŸWø/.fnªµ˜qªŒ™¡¤Á“ƒ•Âu¯Æ¶“µ¥y£Ş$öÄÈdr7˜¹Mãòî-Ú¢L*Bš”Š¡×È¸«ù(ÖÜ¦&÷mŞI]ÍkX˜º¼ø°9ƒÄüT]­¸È™8gÌ½)ÑŒMªº+M^ŒX‚4À­ÍP,rÄ,ñ²0Ã+ò|Õ±ê:–ƒ%^Xâu%ÙK,lXâÍ",ñaÌm­e­ˆW•¼eXâmËï(üwKL“#`Jnş•!$R••HD%©‘…AL²bÃ;Hl:µØaV¢6Ğ r%¡±ÖMQògØˆÎ÷±)±òùñ%8§Iv‰¦‰l¤*z+ Fº0¤xhz*cÚ$Œ/ÓM°·¸ºC×:¹ ÷!ÖKc«Ë2Ò	ö ‹={'Â©ÁúY;`ã›!›gÂå
ƒæİ³:·ò¸Hµ/l.L„uÚL”&ïEÌEjÂ«g(æacæú@ØêCy~ä˜us	·€¹>ö˜‹ÇÄO”øŸºfe‰‹ÈÀ>sÍÒcâçÚôi*ÇDJéTåöNëíAœìî®äK¶KŠŸØ£âWÒ†Ö¦_+o¤@>ßòïãG%MŸÚ#Ğ÷ü•Qÿ`FìÓĞÖôGíø'éø¬ÕUœ›Š#c{z’äğ ™ë&d'Ñı¢cúŒbÍ¯
ø7Ü€²Œ¿Åï¬™ŠJ‹É0ÿ`™•aQß“èşT`™QZ£•ù12øñMƒ“ëÌŒˆüwüâşüçî_?àyÜÒlVÆÜl,-iú‚_:£õìÒºeÑ)Eî”;‡VŸSª+©çâßñ)wníäKKâyø;$ñ’2Êyù/áõexÊO;œ_:O¹KIóálîŸr¿ğ”» «z§ÜşÖSî‚ø§Ü…X‚SîÂ|ã”»Şö”»¨e±,¦—–A,n1Ÿr—PL|Mt/© –2èş:F7Šœ¼¼´V_F{LååeÌ¶±,!òò7Ü6ê 3‰'•WÃVG“åØ2óò|Sf^Aû!}èõh#§PeHóDvtOƒ³ÍnbÁ™ÊÅ©)‰J›‚„làİğş¢îm+^ƒiQDŒ^ª‰›UØôğ&“Ö:²ï`á7×¥ÈÆƒ0i7/Wy	G5·;
ûUÇLk¸Ê^ÆH\FÄú¥)É‰”L€3B•çƒ×Â3®H<dDob·?ÉòÁDo :^ÆWB+\"ÉsÁ¨ˆŞ¨PËøª†í­®|5%Äê±—5Ä^£±¿-NìŠêªšÚêª¶dMCìµ,±Gikbß¥â·“5µ‚¹GĞdj$@&£ØF0~{‘!†_u•œ•Œê—ÜiMÏsH9«“
w&p,bHÔN5A$w$ˆ>%§35‡T{è
$ŠÏ“ğJ#ê]p­ŠzÀ\L½2¡[¹<+õP×QOÈêUÔ«RÌVÔ[ÎP¯¦õ¾+N½Ö|y,Z’ZC½:K½zí£ÁP¯RŞdK…[ÀN™‡˜[Šq™®P)µ¢¬Om òÜË›ŸÓ¹MÁZfÛü2jU
 ŒİLşPûU‰œÓ#±oQØLjZ{w!„•/ÀFÕøÌšõ€'â)ÓúÔjYÒ) ™1©`ï­(C:zg²nÄ¤@²ŞPbÄ±¾°ÂòíuC…ÁzA©lŒk¬kö}V*[^6Î5K¥²´éÆÒT¤2{	]¤]HŒ%t¶Lå²­\¶©´¢
33^
Š¦ah©Ks›Z*Ô¬ ckd™j~Ê5[(ì&Û·wOe//ƒ(Óäè™ê©¶Ìt8B:ÜÊïğçŒ˜³µv¸Î/«Ì_QšmËf‘jKKš~á¾»¶(­P‰9(rbÎöZ}©®bN3ÿÅœµ“_­˜³‡bÎHåÎ†ÒØ~Åœ]´Ã]¥ÃPÌYIšïÆæ¾˜óÛ€bÎ$VõÄœİù[Åœş„˜“g	Äœ¾!æ´âmÅœ‚¥-‹é•e“-¦c1gŠbâw¢»]AìaĞı{Œn91gªVïĞS1g³vvr æüÁµsI#æx³bR®6_WWßV•t±n¾)èôh/{J/Ío¤¶xöPªAsRCšxá	± ™tFXòä®ÑéöÙ»èr]PRé‡Õ7iÇ¶eöG+å‹Gšçpœ<mŒï5¾×s¯Ñ®p¹Vóü4üøXÂÓt¬dAï«(Ôa	?;#×ıI/Ë“k€Ùx!ìC+Ü…Ésº PäÔÈ……p†ás{U°—â}¦4jÚ›Óé½ªy–ÙeèÏÌıÀ¾
{?ñºqû³ùğ¦¿²«	è¼±Òhÿ@…wP–÷W—º[ŞÇ{–6\)§ñÊQÖÿ›¬¨B8Ì°şß1ë£È­4‡kõ~©®+Íü;W¦InZª¯ìHíğ»êÅßáª³†Œúhó…ÀÀ?şªCeï1Úù±úµé¼[ÓÌ»ãØ4˜wÿ4ï
øêåÕÉñl…y÷¾9ïNĞ^N”^›Ÿö&`š¨BJu}ABU~ö¹¨7‘÷Y™ÿw™FU%˜zàhÂ=¨Í©ƒZO0ØĞÄbáÑŞ	µg»9_0Ç^«àôÚYÏ(ÂªŸúÀ;ëqêQ™ÏJ““ø±™ÙF$ö''³|°Ù|Æ³í´Â•œ<O´ÉlCİ€H˜m§{LeÌŠí3=†:Ë0Ô AµÎVfše¶Íï˜î)H
SŒ™Ö’Ï9×1Ó,³qPËO9ÍNóó´ãó¥c*c"÷ÒœŸ™)+$²u¡iÖÙ0£.RÀ›5ëleÌ%¬™.£d˜—²Ì.¨ï)c.S`—§£´ ì­F&.—úé¦RKr…7F¸Õ]©cœc¼JÁ^mÆ8[vŒ×dÆ¸¶ŒñZŒ¨ïñ:ö_3F«0Šã \Ÿ[*poğáKárq»QáŞ$pS”­#Ínf³H„ºE?qv~â­Úú6ó‰³ÛOÍÍzäO¹=ıv­~‡v–®-efm¹“ƒµeÙØÓ«««Ûêê*rÉ]l…µån¾¹¶Ü£½Ü+½46Ï«Û`-é,˜Ì)]A
âŞœ¤vÔµƒ‰ıÍ8ãŒ'Î»6]n†Ó¦c×Go<åúZ¦èÙcéğteÜW‹ùÒê«½K•İv‡OC˜kœó0Äd‚1‚²ñ~²RG,%Í1ÁèqëÛµ‡37”Äziî
Æ{™`\©y–êÈmĞul~¥#6„#é–	÷æÆ}7ül¹F•õÒF:Ò£>¬9á¦89‚İçÖ%%Ü´Íü'YmDÔ¢ë–½ôtk)yš\—&÷‘I2k2™®Q,lMÆkòhß)y>$ì&k2êÌ5ùaöàMèG”K&ô¸¼,==–™Ùå2îÇı™=gfÅxB;xÒt0àÚk¶`]{Š€ÖÓ:éçâ¤F?k&ı\Ùuí¹Ì(+d”Ïû£D}/(°ÓQ†k¯gÎñ%oˆ•ÉË:Ä¹9ÄWê«fˆsg‡øZfˆ•2Ä×ı!¢¾ç¢ğ†{S€9ÂV™Uë-¶V­yZµjkLÀ”·Ù
«Ö;|3`Ê»ÚË{ÒKxÚc_¸Eb]?`
º	¦|À:~À”Y€SİG|ãT÷1Ş~À”Oğ÷DòüL:èàSÁÃŸ†îMÇü¥bÆ¿«e°_±nîM‰4/‰ô¶şÖiŞxó@‘îM«¡Æá‡"d˜o 2 upek¾­"ùÑá'¾%è›öò‹ôÒØiÓ`.ı\ø¹77W5rˆ3©MmÎû<¥ÌêœİNÌò†uŠ	‚Š—‘í]P‡C-gü…à—ÅbIN+š<€ÕÍ¬•iº‰4(“.Ä0BQuz{÷/:!¬FMçrÓAÜ\~¨ã¨GL_8jÂãÒ-]½ÅwÌ*z%z]ò+1•YAIÄhcù`+(ˆQ$F›ğİòüÓqê:î
3F›Ç}<©ü­¤ú'`ˆZÃÿaˆùbˆŠº\-W&³@‰Áy9+ßdˆÙğz†bAêWÕ¤{ìf¨èT•¨‡¨ğÏH½3-•S%6O:^Æãµ¥¤æE8Àf³ŒÓÀ|<Îó®D.ÀÉƒY¨M·"ÅH:Î°ıÌ÷ò
;´¹AÈÂš:s]¸^wèÀ™îd#²ƒTÖ¸~¥ÉìDV†'H„şd–Æ GÌs¢Õ~É\òœ[Ğ.+ê:"ƒ'æaŞZ=¯Rk>iæª×˜ŸÕƒµz8ybé"Z#»VO*O†®X€o®Ö%ÚÏ‚ÒO¸Z³·şd!ÖõWkt®Ö³¿Z/Â¬Ö‹òÕz1¼ıÕzqÁÊò\Òá ƒn–òpÃèFKë˜—‘fD#Y–m†7- ¹tE¯—Z.€·¼Â[ÁÂ‹Â¦P`%Y`lEõÒ#ØJÌ)„âóÍÊl˜l]¶
ËìÙnÁÌùfU…»š2„İ¢Ö“f«³Y´E­ÁÒ’¦…¸E­©­×’Ö(‹TÄ(rŠ›QZ}m©®Š›RşÅÍ€!¶ÖÑî¶'í2şÕ6ëËxËÎ€Ó…Ã“v…v]iğWD÷É\D÷^•AìÒcµØE2‚[vXŒáÛŒ)w‘P—=Z`×û°Í­Aa¯›%Ú†Òl½¢D[_±¸‰¶¶mˆ¶XL49¹bC­>F;K¥cÌ’1–ƒ%cñ¶‘šV\©WÊ’ql…md#¾¹l¬½l"½46_F+Ô­p<œYÈái¢OàPÃÔy¥rĞ“ğ,ğ=9bb—·lSaf¨¨?MX˜F}*¦`NuÃã \ƒÇ\p§Ñì\âäÚŞfq_B\&Ş'MÓì¸¥É¦ü†ÌêNÜô'›±|°ÕhŠW÷ñhµ_²¹<²º£n€{¬`[†·Y.š‰[J³4»[±Íğ¦%²‹ÎXñÖ<JÛ(¼mÒ3¤ŸP„ôK¹[T$ÛâOä›»ÅöÚÏÒO¸[°·ş„6V™İ…»Å¬ãï;± »ÅÎ|c·Øo·ØU°¼›<'9\´Ãµ|,ıŒ<ÜpAÎé˜óÒl°¹…Ó•u#ùšV–Ùy©ÌÜ.(Ü6Å¹]7–f“Ù,Z§°´¤iiÎívm½‡´n@Y´ £È-ÈSµz‡T×¹“l…Ö¥-c—ãnş—ãMd´=cà¶eÂåxOí8	°G¦ÎƒD#“lGz²ïÍ pSŞç£pÙÌtšŸ®(LW¬ÍÛÎ`Ë`ÅZnH¶­Löb;¬Y3ù&Ûî­ıì#ı„lËŞ÷u}!…l»ëøl»?À¶ğ¶=oŸmÂo„\“ç!Ò¹, |,C®"Xóa:æÃâ‹h=Ù“~BsQPfXœw¤>ÊpŞòY•ÂÑ
ÜãSõ=­Ç±
ì¸t”ƒæ‚ôÇ{ƒDüÅÿè Wà OP¸'šA®äI™An.ƒ<Ù$ê{§ûSØ©Êfv¦6J³ÓØ,š©§ëPFp(ghë3ÍPFÄ3En>K«Ÿ­¥<½…áés9àéÜ…k‘ø¹º¾29—­ÀÑçñÍ]ø|íåéEsš€‡)µ0ó‚1S#±¼Ø7ó¼ï¦®9ñKà6¼Åno¤96i—Kàï¡çèPÏ,×T8‚¯k×ãÄ³VĞ´\Vmò”B7¬îı“%l«M†J÷iœÄöOÖÌ‡N	³Dk‚h1”Ã!iPñ wgâ¹¬ÉŠé+ß_š\Hde¶{¡?¹ˆåƒm÷ G¼İ_ŒVpƒ’ç¥‚v™Ë¨sù2öàæ.Wj]ğD“á‰+‹ğÄÈxI9*k[Zk“«O\myâíåZÃ[ÿ õ
jĞG‡
kõî–“¯8 ‘©Ò\|Ã©²·ä ¿F"1jıáÇs]„O~@òß¡ğ‰o‰ñy½`òyŞèğ‰ºŸ‚ àó¦ Ÿ7ë—ŞàsKƒÏ[‹às¥ğ	ÛÑÊ|¾²5¹Íàóv‹Ï;´—;>|RØlí–„Ø¼=2¹+BÇÑŸÜ=Z0¤-÷Bî•ç}-¨ëĞ"ß	´Ü åğƒZ¶2hy¨ZV-e--5u•µùäaƒ–G,ZÕ^3héR6ãµ‹Éâ Q2†kPv¨ğh	+‘R4—Rùè9Äà,Æzí·Æı™,ıé™ÊŒøx„q~bòÄPÇ×ÆRpı”<ŸvG]‡qA!0şL€ñgÏßÚ`üù"_e Œ·ÖÕ´”µV¶$/Œ¿h1ş’öò²Á8oºqäb¬Í ¬O;S`å•+FòêPXÁˆb¬¼&øx]o8¬ ®ÃŠ|&°ò¦‡¾¥ã}Û5[u¶)»{j˜md`ï¸f©qà»Úô=išñìGœ¤7yŸmR³ÀÕEZ]m×ä©OÀGR ‚òÇü{`Aù‚,iZÃ
ÊŸòw((o+#şÌŒëş¡ ü¹vü…t\Ü]#4‡ÜÔdğKO¥“	ÒáW,³Ç53’××Úß7¦?{Nµ…u	qÁ†¾ÍÀŞN`çÃ^+#0}¯°Øé&J³Ù,˜~R$¢Àô³¶şEZ7 ,:Ú Èm~Õê¿yûİPŒ§Œ­©³]½¬´räídmK©?‹Qj{å_Rkû”âiàoíğé0<ì Íÿesß±”§æŸc_,b¹iÌƒå,™¾9â¬ü­æˆ³áO˜#c	N	³óSÂx[sÄ9ñ7Æ2^¦›es³>1ÁÌ²‘I	L”¯‘ÌÃ•4­CtÏ« æ(‹Ğ"'ŸÎ¯Õ‡k©|º£Y² ä@>-ã’ÅU‡^2'òå…|myYRÂúLä›’éB
aøà4ˆ‚r†¾Å0·7…Dïmí · jÅmş¹QmhJĞ‰Oç-ºŠ{‰øc£“EØgFÀãW 7
ËğğAñŠ·Z!kŠ<—Ñ‹€‡º–°â-É<o)ıè¥¤îdºL¤–ÇHÍµÕ×´å¾yYƒÔå,R—Wø+¤¾¤""eyñ#«ÜµÃ4q`<Ùœ¸Ú¤‹¼×.>jÇ!y­Óè€Ørd¬5áÉÕÓm0	ßxR MÚMğ’¤nd´"3‘ÕÉÅJ bwª75yiˆ4?:‘”8„–}(’1IG
1W’çÊ¤¨ëH*4IW	Hºª¢|µ€¤;’®^„¤EHÚZ¨)¯Í•%k’®iIº–ÂeHzHº%Áèq¥Ç¯4ÈSRèÁe¦ÜĞIÒ+sR¿×	B?fGw>”xcŒÕŠ^Ñé4óBe·¾ÆY<!x* éÏ·¸[;"1¼õCH‰	³¤Lå0¨ë#˜a*ÂT*âªÂìbS]„0•1aj**ZÚòğ©1„©µ„©Søõ†0W0"õÓüÉ3«ì…­”õå;~«	#z[°4’E)Ó¨ê."nãÈP#[X4Ï4ñ¥qYšH¢4±•,	Ó!üš¬ó˜×ƒY^élENùˆPÄ’ÔE( )&ÔzB¢õå¹#ê:B	æA¨Ñ¡$§¼"rŒkV•w•uÍ\Nymº‘41{/·„¥˜\H`Côdc6M¥Á+n"Í$µ¼ÂÙL
LLg%Œƒ’ÆaO ©Ğ³›Œqs–Y9¬6#‡5j[Ø.¼T^ eÂhjå.:sSø$¾¥¼.#ˆm¥À·V^·š«İ¥Ù6l	bÛ²´¤©’Ám½´n@Y$ È	bµúöR]EçøwìÒ¬4XAlGşEæœŒr'C]ì¤¡ ¶³v¸‹t
byi¾+›û‚Øº
b»±ªç2‰¿UÛBË±‚Xob-x[A¬UÇRÈbºEÑf1b“ëİSD»A÷z1ºQä±=´úTí1ÄZÍ:ÖAÈ ¶>×±¥ŠÌ„I5…ºŠš:œ‘;ÙòXß”Çºµ›é¦±ùR³Ï˜xôyÓàtDSÏ´t)¬->!ŒÆ,Ú F, çñÄXæ…¤AQ)n!Œ¯Ğ-ñÛÛ¨î£bÎMÖÔ|ÈF¢—”“ê(©AéŞ`0²Mœ<öä'dÄ;âÑÍX>˜x4Å+Y/Zí—ôÉsš CÄ;Ôp•lºaZ{]7Cq¸—4ó5¹$Š3ÙdxÓÙÛº‚xoW¥}Ü¾Î¬JâØŸæO#ÍkŞ{‚I6½?ËìÂ4:³0 ½h{1SlˆpPîd{°wÃÌštˆÂ=4;S¦H³ÃìLÉf¼×I2†“¤_[a&É˜x’ ÈM’#µúQÁ$i7“äè"“dì€“¤¼¾¼"×Z…œ1f’k'ÉqÚÍñf’le¼84ıˆÕŠÛ4$^¼K˜ºuÜÜ|!‹‰ˆMdSã¼øŸˆ›ùıÉ	Cq3¾'ææ…O’çÉ›Q×q³ 	Ü|JÀÍ§êÇæs³²_vìtåæqYnŞC|†wÏg*¸³M5$:»‰6D©Yé9†DçòÍSûyÚÍùÒM¸Y°³şäÖõïğĞOx‡w!ëøwx± ›ÂÅ|cS¸oÿïRÁñeò¼Üa ¦å[é+<Ôp¢_©c¾Jš¹«gª5¬iIyEzyz5[§ó»C>é–Ùù½qf^«À¯S¼[Ù Sšı—Í"Ùàz––4mÂyxƒ¶¾QZ7 ,’Pädƒ›´úÍR]eƒ[øwF6(/-[#¹U;ÙÔÊ·ñw(tÉ(o7è§mªÓîĞïuN¿uWuİınu›ePw¿7‹ºiv_QÔİ¯_5¨{@[?hP7>FŠêÒê{¨{$B]YiíÉ£ÚÉæuCİ2ÊÇê6÷QÇ	ù„vø¤~]*X$fB>Å¦`Ñ8à„¬®Ê•Õ—#ôùÓlÁâ¾)X<«İ<'İ46¿¦+àM”Ç1<ßw·jrÙáÅÌÓ^ü‰Ù1I2z—gmà¥qÖÒ3s>o	“Àzø‹
o·úº‡É:³#gØ©\Ñœmœ‚ZÉN’ã@‡GuV„ÀÕë¸fóQŠ/Â”&Ïóã3"	±ÚŸ¼ÀòÁD 8^Ä_D+d—çË‚FIP7 ––WÁ)’ğpõªbÿ5×l‹ìáªWöºk–®ŞĞ¦oJÓŒ};Ìæ’·Ø&=UmiOUoK}I¯ Ş•,kÜì’*é™ëœ³å¹
q‡3.’,ç=‚u‰ŞWfßŠ3êø¡™Q[eoû?bÍtë“ïú˜ev]D}Ï$áö©]ÇÇÄ¾ìÅMwAÆõ™7.¤”ÿ\Çµ5Çõ…‚úÒŒkëì¸¾ÊŒkšŒëk\¨ïY!|£À¾`éçL—fß±Y´^¯CÙ†CùA[ÿh†²M¼è ÈÉM?iõŸµ³t˜aÖ€_9X¶õ•$Â	“êZ+-mÕ5É¯¬Éÿßœü¿+ü?~cóQ’ÌÔ¨†ã{;‘RÔa¤ 9zÄšĞCö”_h¥×Ş2µñüF'zfvq¼Pæ³|°Ù…¡Ç³ëo´‚–_ÿÊ8ev¡n€Ì®Y‚Â×çÎŠßø¼ÙğòÑ·—Aß0VĞ7!F_¡¬®¢º¾¾5™õ¾9ø&úæTøs	üÆæC€>$óØ9;ó0â¨,ëƒ-¥Q"Á0’WòÆfr{‚Ä-°Ô×µŠ7¨<z!´¸§z^Ù\1q¶ëÚ–Z}gÿ	U<ƒÁÕB–9œşJ“¹9¾øÅıÉ<,Œ øø˜ ó¢î%ä9¿|© u£ Àğ€ (‚JÌ4X°¶‹	ĞRY¨¬k²!ÀÂ– ‹(üEÙYÍdr§Ì€ÔÆæ1ø6V483Õ ,1Ae§1 J<X·¤¾-–Ïí|û¡ªñ´)M‹ğÏFü­¡ğoñ¿„`~Iy.åğºÿ‚PàiÿÜ^–Qü,ëšMÌn/{ËÀ–sÍÒíeymº‚4Íèî¼HÉ6Mw™ì.³¢4ãMîH…³’¨È¹2ÿø&w‚,ij¶òÓªüŠûÈÀW3?6‡¢çêÚñÒq6¤C|³º&¥«ù¾|-–ÙÍiÇÌæ4Ja¯ma;7rX&=”f ï'×ñ!ï”Ù^Êr¹@N´¿4«`³h{©TtíÌí¥J[WKë”EÇ9™¶F«×z´©3´	îlëµ“],MŠÑä åº&»„ªÂõ´Ãõ¥Ãğôw 4ß€Í}Uá®ª
G³ª§*Ü¿UU8BU8–%8ã§Âğ¶ªÂu,›d1}bS‹éXU¸™bb7¢{¼‚ØÜ {·İ(r»y£VßB{LwóƒÍjØDÈÁv4É—èı‰7©¾¥:WÛZhK¶d3ìJ[ñÍ]ikífé¦±yE"~šxY)÷,ïáu®ËZ6ršämÆ¦Fy½X7qÃ¡Ñí:FË(£İµğKò‘X½RÈ	â8hâeP>ğzÃmH{+[ö 6ªæø©8»PI?ìó…4†+#¡1$ó,óÌ†~×æ”ñü"Ût€`pL·¡ŸÁÏ¥¥£bs7€D#Ê¡Òd[b/³g’,ıÉ–¶g‚Bñš½Z!’“<·:È‰ºÙ±fï`æ‹±Ç8Z ß—b¸d§"\²û€\’¯m«ª¨Ì×$;.ÙÅrÉ®ÚÍn†K¶• Í&qFÅ£™)67ˆ)¼ÃTäÊÆ¨!ÄåzËÜíë­µf@ÕWûä.œ!l&R`ôLK˜ÁL(—úúµ"Ë‰dÿK
m”vLF¥˜D;ÑN(A©l£çŠÑ#ô1d\"ïáz3×;µ×¯&ƒ!ì½h&JŸ±SËcl’i‡¡ty¢ÕD†Æï_‡\Kİ}¸BV†ûK\Ü*w¡®İŞ§x'ElE:ö'»ÅV iÌV9a¨¼<[[¡®c+á°U«ÇV
Jï6×,—•MvÍRQ`Š6m—¦™\j¹Öd6H€+ L•Ê :´u§¨ ĞÅ¿ º	²¤©Õn6=ü
 ‡Ép÷4ÃÅäj€D;î•‡ÈÓG8év{¸ÀÆ2»ÿ2»ôt=Cç¨UÚõK³½Ø,Ú¥gê7µqÛØ[[ï#­PíÒ(r»ô¾Z}?û»ôÚÉd‹¸‹!îåAq“Ã]ú`íğé0Ü¥”æ‡²¹¿KOp—>ŒU½]úpşÖ]ºb—>‚%Ø¥ä»ôQxÛ]úhË1YL%ƒ8Öb:Ş¥SL´İÇ+ˆÿt·ÇèF‘Û¥OĞê'jé.}´YO"ä`—Şƒë/Êåj;×:©¢­<_“k«KNfeìÍ§ğÍ½ùT~š ol®DZØˆ‹s+L	ºûD[¨xÜãR/“ˆa0
Ûo÷èätÂËìV”ú,l·ÂHãeåL´‚æ_gËÈd·Bİàó±¬œcøÆú·œ«t4Ã$$TQez7>¤Óæú,³³mjf¶]¨}\”åc¥ÙÅ–à]Ÿxv‰²@YàR…p™a˜PäXàr­~EÀÇ¸²t,P_YÛVS†L~W¸Ú²À5
üZÃûË:É·á…gpd™ëCB"û«˜šáñİéEJ³È„ƒ˜§î÷‰¨7'Tx[r=H×Óì@lR×EÜÄ/ÅõÃPÜ„.â |tƒ<otÜ„º›“ôğ¸‰.á7+nn‘f¸¡\¸oeƒáM]Ù­ãe¸·¬y»»Ã²¦§ßì´úÍòP¿)W´wføó?ı.Ÿ?»3üy·vtO–?Of÷ÈŸ÷)ö?ïWşì‰ùE?Ôêüy¢áÏ‡‹ğçVV*Ê*“G>jùó1ş¸áÏŠT§Â¬&ÌYØ«¶"=»µrj`èkÚñ‰ˆ§8ºşäÉ¡x
yê)á¦§åùŒã)Ôu<%_z6à©çô{·<å³AzSú‚òU’å«“dÈ/|õ’|Ùò•¹‘GˆûY$Wf}oÜ}à+f:Y@¾ê3So†™^Sè¯g™éiö†e¦Ì½ü›ÊH}d¤·´õÛ†‘úbFB‘c¤w´ú»#jé½"Œ4-ÜëÊÊkråHuü¾a¤,#}¨À?2Œt ğ³¥‰o¦©/`‘’H2	lH-V9`ÿÊp"ÖŸDtŸ.vš¿”zêª.!ÔMÓÔ¹€‹YÕÜÇ[ò[û“O†bK|vÌ–Ÿ
C~&ÏÏ[¢®cKÁ%Øò‹x½÷¥bç« õ§Ô]õÓÔW¶VW´µÔÖ$ßÔkQÿÿŞ ¾U­…L>^™Iˆ2+p§>^ğ‘Ccÿğ´dîÒŒÃ^G8õ´µOæAŒ'i-×—@ûä‡½üx…^|ZŒŞŸ±?Ëó‡^Ôuè|½¿zèååÖoŠß¥YVû—&}Kut°q*œ.Cş“eV™‘™¢)ì¿•tVú?CšıÃf‘ôÿ/KKšöâ6h=+^”ş÷Š§(ŠÜM«“êî»Ï4|2;ÊCqtfÈ'u…–úªBM2+C“oŠ£s)ğ¹xcóvä“n(w¦0T”F[Jï[åÔnERûØ4=2SEaV/ş<ì0#¯rüÈªÁòÁäU|JÌó¡î"ä9\†.ò*êø_,ÀÌõÁ%úÅºf{gÁgÉÀrÍÒcğÂÚti*Ç`IÜÂ”âP?$‹²IzŞ×„“êdÉÅµıR0K.Ih)o-ƒZŠe–%÷Ë°äÒ
{åË’çH³eÙ,bÉåXZÒ´?Yrym½‚aÉıc–D‘;Ğê+Ju=Ñäß±…éJÚÉö@º2‡'ùse”«Œƒ„ÒUµÃÕ¤Ãğ@z4_ÍıéH×`Uï@º&ët-ü‰é(–à@º6ß8–âm¤ëèXÊ²˜>_Qn1H+İ•
¢Ê û İ(r+@µV¯ÑÓéf¨%äà@z0W€…<îœTV[ß’¯…µÕ±ÔóÍ5 AÁ¯+à›™°!Ív7ÁÔD­K±#0Â–¬ü’ú@ú¡0I ˜_˜P¥nîkSq1š¨dDgÆ9£Â¢‰3gƒœªÇhkÉTãŠJÕ jÇV%,ÇÍ9Šœ{0Éu UèWnLKÄ e|k·6“s·âeŞôn†R—ø¢Ğ$öŠî¹“™Àdwl§¶W®0ú[¸Ê,_D~²>Ë[¾@‡xùÚ ­H
ÖeùBİ€¸X¾Æ˜Ya•Ãc•Xã^¸ĞğÂFExáˆòU…º²êºdcÃ›X^ØTÁofxa]«îm¡ûˆ2ì…•B¼óÌÊfj`Š©…“‚ÏD+?IÊ Ö7:"dÃŠo»^?PË¯œ‡Kî–i3ŞİšU;Å²Èè_³nòrÏ€àÚ¬ æÊÈ/"¦ÍÖiÜÁ!w!P‘M·“A¢éf4Z„éf}ËrĞĞğæ„W"„Æ£4Ô6­KNÙÌ·½mÆG|CBÁa(¾Íb¾iÙBMoP×ñ0øfË€o¶RÂnğÍE†o¶)Â7‡F|ÓRV‰ä~­ùd[Ã7,ßl§à'¾9WäÍ\Ôï48—k$M"¦×PSaÙà“Q¯}(8Ø)Š¼®·Ôgä?J£™{w@Úº;Ê­UÚØ—œl‘†¸èOvŠ4@KLúµàÊF;9Ò ®#à¤Ù9 Í.Š»]Ò\lH³[Ò‘&5¸dH³;ß4¸Í)ø¼€÷Nv‚Üì¬ëÜ~hpÛÊ:¾ÁmØ#ÛøÆ9oßàvŠ £]{8” ´C‰|#P2ÕC	ƒ€wè˜;%Vš¹DÛÅº‘4ÓÍÒ’¦Ã¹½öhë=¥uÊ"õ:ŠÜöšhõŞ ÿ—ü÷Á„ÿò\[Me]òÁüOç›Ûë¿—€olÅx.w#¦†IxÄ*pÓ[{Ş’aåM&î:q•]Øs‰etİ×@dĞ$¿ü“õ¤)ršIÁ&âQæíÈf9Æu[Òu6‡ØQ²ŒšYcÍ9
‹ûpğ5ÅÓÕOqµ5}S!_ŒPd#Æ‹dÆœÊÓ7“¤»½Ù®Y2¶Êx'¦w½\’Ì*œF7Ñ”¹3‰ÈÌŞKÊÀƒåƒí½ R<Q÷~ÜWû9®D]Ç•BypåşWòÄ~€RòÀ€Q.3ŒrPF9"b”ºòŠ|U¶xF9Ä2Ê¡
ş0Ã(	WšiX7âQyu?©%G§jzüHÖasGª±ùx‹‹‘²ÄÃÔÛ©$Œ|7$;¹]EÈ>ì e#¸¹³—¢ºYámrN6@°f2yfé>3öÃî h:dM˜Û—ã¶èl¦üÎ{X¿¹²“]À	²!Œ­ÒØ±¸á÷"ˆpÕWéˆ°{˜Ìjrïœ'côéD¢¿îm!.´B»İ8ƒ¬_A-¦|rcğş¶¨’·Éá»‘¾ıIÿPìRÇìv„0Ú‘ò<Ê±ê:vş»°Û1ÊÇìv¹a·ãŠ°Û‘d7¸±‡ÒI^ÌØãÃı‡oî'h'JáÎÀnú““X×ßĞC¸3œÌ:şÎp
°3œÊ7v†Óğöw†ÓgÈóL‡€vH‘¯RÎòÂ3ôÙ:æs¤YöN×œLµ:ç²mº{\!tËìú¨Ìú|}âÛn:WJ³Ù,Út.biIÓÑÜt.ÖÖ—Hë”E›ŠÜ¦s©V¿, îU†¸—!î1ñ¦“¯®ÌÕW’+i¯ä››ÎU
şj¯Ş‚4-E80ÄàÑ¼RÀL>™‹XHn+…½z:ºİl£ì\Ğ%âƒ.i€OÉdÓe² Ö8#}.-LH£Öùlb’?À€wœêe“üÏ$©¹†ŸYî‰¤"aù`Ë=ĞÏ¿ë„Éş+Ïë«¡®c5Á9Xí†€ÕnTŞ°#³ÄÄ›3¼vµùŸ×ÍğÚ­
û¶,¯]#Ín/Êkw(¯G^»S[ßexí¸˜×Päxín­~OÀk×^»·¯ËşÕõe­m…Úä>Ãk÷[^{@Á?hxíPàgb=¼°*ÿÿJ""Øc_`H9“9ŸÍÁÊÄ×¢ r\MÚFäÕI•–aÜõK—&EœÄ/îOŠ“ğñ1'="<ô¨<sœ„º“£à¤Ç=NOÅĞ“®3xªş ­&_W‘/¯M6xÆàYÿœ!ÀZŒc³‹ïÎ@iª "¨€ácûÂ¡à\–æ«²1D IcõûiéŒe/½æ'35®!Fê4§·ñ0=Tu³D\CÜÜüo|¢òFºç4\= ¬-©´™/´j€¡&áæä/IÓië®Å£óùˆOH8Å' Qg á—äù²ãÔu|"„§3Ç'â¤„|Í5;!«›ş¯ìu×Ì9iÓ7¥iÆ¨“Ÿ¼Å6©rú¤ÔHê‹3xW
†²–~ĞÒ-òzÕû,³;ëÉkéö‡vìÊ8É%üG™NnN>ö;9%³¤~¢|ª“Ìnß7J³ÏØ,Ú¾?giIÓ©â"¤­¿”Ö(‹¶o9øWZık©®ğoøw¬ÿV;9ÍjÀ¿ãïP~“Œò{CWèO5à?h‡?J‡¡¬v³4ÿ‰Í}øéjÀfUOş«üWü	øo,÷;ßáşÀÛjÀÿÔ±ü•Åô-2ˆ¿-¦cø?Š‰3ˆîÄ,PQİgÄèF‘ÛÁfE=TŸMª»yt«Y@‡¡<Ô€Ÿé»‘È˜ÔZÙÖÚR]?Ö§ßâÇ£ğçøÍ-&¸í<yMšƒÈ$kuÇêÄ$H%Ìt–3¡ëƒ’PB¯væq3
5ÎÎ8„aUÊ#L_“ÉĞ|îMı54ˆÆ<~:ì?#ëğ‹à§ÃòÁd|\?´‚Ÿ<ç—/µ2ê£Ÿ{0·b´Ñ\@P"Í”Ÿäß1?/Ä–%MgY~^˜¿C~¾M>cÓ	qVh›¹¨v¸˜t˜•ã‘–jùªÚT_œpÒ}»À^‚evµ9;]hC´¤‚^J@›(Â .ÛæÒl=¼éœ¬µÇy5\—UpËÙ‘òV…Öñˆ÷3©­#×;…Ñ,iGÂh*³tB'RH&™
\Æ–ÏŒşNécôçf–±ÚİŠÊêv»Kšd³h[I)rçÕÊÚziİ€²hC‘›W«jõÕ´³ôfén3¯V'äàféüx^ÕU·ÖW”Õç’5XójM¾9¯ÖRø£~cóõ@ĞH1wä%‹Ñòë¶<^#ˆ0W7•@%F—8F2¦Y8®špÍí:)ˆÿƒéÔˆŒG©Ş6@QÏù†9Y€d(*fJ#FÑAËusbHRR]Sr±PD¾0¹½‹wÈ¹6¿&3K‰„Ìbù`³¨*2­p{(ÏrÁ‹ÌRÔğÏY+V*:«,+£¨:Ãx÷È˜k|Æ» Ãxµ
¼.Ëx÷J³ú¢Œ× Œw!o]m½a¼cÆC‘c¼õµúãİgotÆ»(f¼––úŠòÚÊºdCÃxc,ãUøããµ‘ñ¶•øÔ°-b°U££’T´1qÃuI¤4F{2
*$%byïx$€­&ƒM+âzµwOcb"Dm+` 32Ù(â~T²ñPÜ‚ï‹¹eá“Må¹™ãÔuÜ"H·Œ÷¸…§Íï78Ş¢/q\[¨¬ªª*Ë%MÇ[Zo¥ğ·68Şç>UÇK½6*Á6ú”@w ëî€9Qğÿ.yS»8øI*2En²M„[~R«…[|WŒÛ	‚Õíä9ÑáunYÀíön¹)ì ßÎ+ö0"ˆU‹”—§Øl®åÈ˜wb™İÀ.ÉÌÄø.J8»<(Íve³hØ¥%M—r&NÒÖ»Kë”E[ ŠÜLÌiõ|À%.i)Â%—Å\R_(TÊÊI«á’‚å’6…?ÙpÉrœ‰ä€)³‰k®^óâ
¡G&S""s,ıIûPDÆ°b"ï!ä*ÏGdÔuD–o‘;"wéĞ»"Ç‘—z2ô}X†»§OßË3J¢p{.¼ÿ'‰¢ ‡7]‘•^‘n§yßÀ›´éÚ×Œ,/=*u÷*ÊK3•—®Gm½á¥+c^B‘ã¥}µú~/=fxiÿ"¼tU^*ÏWUV´ä“/hyé …°á¥Àªër—çn–šop‡‡#mO¢w"ÄBÆ<8~Ã™+]Ø¹$uNKp“ cc¨A‘àˆ%ùIp‚Š%ñu1K&Ìx¸<ûK¢®cIAXòœ\ÓT`øqƒá£‹`øê"kºMúyŒÁğ±|óJà8…¼À™ì¥?ùëúWè ¼8uü+Y€ãäI|ã8y2Şş•À)‚SåyšÃ	@;œÈG'§{8áZ|†ùLifÂ°©¼oÓeÓ.œE(éâú„|ÚÙ,³kò5™5ùíä\E¼]“Ÿ”fç±Y´&ŸÏÒ’¦k9.ĞÖJë”Ek2ŠÜ<ºH«_Pù)CåKŠPùº"T®ÌUÔ¶Õµ&—*_Æ7ÅòËş¿±ùWz ˜x*sèu3R:"ÙörÊÜ3p&3B•ä"R/«5²­Ú!2v•›8àd+‹V5¥¸,ìkï±Û®_Q¾•¹È7
?\İÃË Û	×Q^6PC¹6„-	/L­of#œ¡ÜòJ²‡&Š†ØÜ¥ËG‘†}3"¾Ş._Iœd„{b¹?¹Šåƒ	÷@x<µ¯¾F×:6F]ÇÆBE°ñuÿW‰r½ec#ÜóPÙ’@Ç ë6¨4{«œcÁ~ZÆ}£ÏÂÿÍl;7i7KÅÏÅ·°õğ¦ë³;Ë3ùÖ`¼·)¸ÛíxñşŸv±;2£Vú¸Óı™Swiwwsâ93'î)2'näœ`CŞ†ª
È»½×ÌŠûøæÚw¿öğ€ô®}ì§?yuıµ]„kßC¬ã¯}³ kß#|cí{oí{LØåqy>á˜ ÓÈg‚iôˆÀíı)óÓŠ»,=/ƒ}†u£eéY––4İÄeé9mı¼´n@Y´,¡È-K/hõ¼`HğRÜ\LTÌçÛªÚª“—^á›ËÒ«
ÿ5ßØ|«Mxf
‰pù+LÆõSÂÜdØ…2kÖıeæ3„ÓoÜº§ğàGeœ¤@Ö¥a¼^%¨ ³yo­‡2ÂˆàzUœÂLscÉ(ªT#`Ä´è1ßAë.æ3B]±¯ó›2Ë
±–¶¬ añ²ò¦ğÆ[ò|Ûqê:*€CŞñ8„»ã»ŠÔ÷¤™S´qKäÁ6É¹è{ï³iÊD/Ê€?`™İoÉ¬'*äòÿAŒı˜ ‡7İš]l^’n?	øüSíë³,Ÿ¿,u?/Êç_(ŸßF>ÿR[eøü¶˜ÏQäøük­şMÀç¯>ÿ¶Ÿßó9ODù|òáóï-Ÿÿ ğ4|¾H!)½í5UBUƒ5FX±›%cõ8Íxå©•µR°wµ“%fyÏp‚ybeLK`ºUšü±"?¤?ùy(VÄ7Å¬ø‹0á¯òüÍ±"ê:VD÷ˆHáõıî?¼¾jğúW¼Şãµª¾²¾ªGÍ¿^ÿ±xıWáÏ‚\?z¹~àHÉûdêÜa3C\<W´LĞKiƒCŞ;ã¶Ôb´ÎÄP)®ıP\-İšçlšˆ4p’‚ºŸ¨GgH$5+úÏÎ}~a2Ë›ûøØáÃĞj¿dvyÎ!_&úBÔuás²/Å\ø„Ì-Í\õ×Âçaõ@½{gŒğ²ê–¶ºòêòd^Ö‡zw>¾¹`Ï¯ğ‡„¯ªêİBÛ4d‘+u_7Öör­Lëã8¨ş¤d(a|1ì,$Ï…P7øhàh‘ G‹ê7,àèuƒ£Å‹àè®"šÈú¶šªÚê–d	ƒ£%-–RøKÑÛ{œˆË2‰‹‰4,çNS’j 4
˜­Ğ:zÄæâGËA8¹†k0tËuà‚I ÒskæÒßå[š,á7¡¡pïq¿œ`}yy®àpº÷‚Là~„‡{îM+*nFJ³¢quó.æşJlnOoÈ˜Wf™İîÎ\:¯¢ÀW5ÀWoæ­sˆ1çÂVqıÆâÊk<Ii)Û89%«®rY¬ÎŸ%M÷p3YCá®)pPf„¦œ\Z¯•ä›2ÈQş Qßr¹¶+µÀ
ö?	Ñëdº{Kº+ó»»7sŠ-×î*”Ù­¸ø¶4«d³H\¬Ò/¿_^­­kÌ—ßo£(rÛh­V¯ÓÎÒË¥wÌÌª'ä`õ¹?Y5ÕåmÕuuIëcõY—o®>ë)üõ~cóÉ@İftĞè€­¬ Ñ‚#¡˜´Ê]­X¨\BOı(J†::32 ŒH!zêîlä¨Çî
ĞfÌÑùÌÉÙÅó*¿íø…x8#ıÉh–¶ ñ|Û­ŞLcåÓe?@İ Å˜oãØƒ·l¤Û8 È»†"›¡È1EÚ*ÊËËâ(ÙÔPd3K‘ñ
sC‘ZîcÖƒ+t8Ëæ«adõIäë%XŸºn©ú›hc„4²?Ùb(¤aÀ1Òš][Ês+‡4ÔuH, i[{HãÕø6úQÛJ3½ŸÀ¿ƒ«ñê5’ít®<h¯Æ'òwx5ş|Æö¦PîAÿjœbÒÚ!3uùóæ}C¥‹Pé¡ANºÉN†N;óÍ“î.ÚÃ®ÒCxÒe?ıÉn¬ëŸtÑExÒÄ:şIwwà¤›ã'İ<ŞşI·EĞ*Ï‚#@;2Èg‚mx«?YÇ<Eší…®æi‡v6Şôpö@ñ|Ï8n=S\‡€s[Ü´q'…•Š²ô§“ ÒEóCÛÅ2»ÿ<’Yk»µ‡%£]k?’f{²Y´Ö&Ê?r­íÕÖ}ÒºeÑÑEÎišVŸ.Õ•Igğï€Iœ|/íä1Ë¤3ù;dÒe”{œ§…Lºv¸¯~]º¸b˜t?6÷Çã¥¤¢¢¾º¼¢ª-ÙŸõ±¸À7÷şA¿±y1zÍÀb€JA¦´2.2F·JÅÒıì*CRu
U^'Q$¨C„]l´—8!àÚßt´·Á¥bŒÍ	‘j*	 gšhHå.Á„mj“¸uXı‘aw
ÆÒQlL^f¤LâÎ8Óú‰´©¤³·4&Ş”"-Ğ)Q"•ÒECaà:£‡=xÚÚ<Qc™İ…4èOaù`»È/”‡ÊÜ<L‡îewAİ€Æ˜¡ıŞ”âºu„’ìÈ€%>5,qT–x¢ˆ$DNÊ'G–8Æ²Ä±
ÿ8Ã;swŸzœ(L8GÍw¬ÄBXMŞ1bŒÜİC$¯&Fn„ì:H…£v œö8¢!–_‚û¡‹Š{‚ ôDyä‹º±‚) öä ±§è‡Ÿ ö3ƒØÓŠ öÉ"ˆ-Ô×·òeÉé±gXÄ©ğÏ2ˆ}’ˆİrÌlÌy‚óFÜsèVƒ¿aqËKé¨é°¦DÌpFQ­…Zö·À”ş`2mÅAˆó$²Éƒèñ&*üÂèÆcªw³xœ¹ŒEV}'³—³[ÌHdÕß©Q‡èî$Ã€AÈ³#BsıÉ9CHŒ	y®ğ<yï‰ºBò‚€*¢/
ù¹!äÅEùTù«ZìúÚòäCÈK-!/Sø—B®‚E“÷:—æêƒi8á˜¡šÛ‹ñ½§LÒdN"¯Æbkz{o;Ô'ŠtkÂ‘E»w9Ä#®æx§jŞÕÂ0r7”2²%2zhŞÚYÒ}NbÓ¬şK»Âó›Êå³­g‰8…Ù±ôL£äm$L˜*óö!İ•8ª8VVŸ•ÒäŠˆEH“şäÊ¡Xä‰Yä*a«åycÔu,"4‹\ë±Åœë”„ÿ•fÿ¥êõ„7¼éé¬ô…|Í^_”nÔ¾n’¾œÛ7ÜÌ†©ó¥ »…eVòy&sUs«Â½-`ó¯›ß^„ÍŸD€­Lî0Œ~'ß`ïÒî–B–ıô'÷°®/À¢‹P€½—u|ö>@€½Ÿo°àí°
M’çÃ² í(+Ÿ	Ê>âa›W5ê˜S¬Xyğkìã¬ÉƒO°´¤é9ÊƒOjë§¤uÊ"yE*Ò“ài­şŒãóYO‚o¤ßgİSO‚ç´éóÒ4ãI “%ymRO‚­'Á‹RŸlõ’xY
[QıÒ2¹¼|mwáğ
A¥¨øV†ô*Ë,_½”Œ¦€_Ïbğ;iöFQ¾©|Y"£ië·_1ˆ"'Q¿£Õß•ê*Q¿Ç¿c‹è÷µ“W¬Dı‡õ÷2Ê¾1C_	-ü?Ò?–CşAšÂæ¾…ÿ«ZøÊª…ÿgü­şŸãOXøÁğú—|ƒ×¿ÂÛZø­cù&‹éeßZLÇşß)&^#º¿W?t¿£ENYô£VÿI{LÏ?™5ãgBÎ¯û[£ğæ¤Úª3uT%¿°>Î¿òÍóÄo
ÿwßØ¬w.&Ñ‰‘E´9ÎŸéƒBgc³ƒĞ^³†ûÉèäv›Êù!ˆ)ÆòÁ„r|S¼Ÿü…Vˆ6&ÏäD(Gİ QXuş5fãÅÌo`|÷¬xùxıÙàu6”‡x}#Æk¾-×ZÛZWc}àuv¾‰×9şœ¿±ù+àu|Ÿ¸IÄTñ&Uzá…7TM3b,Œ>q\"uP<7Ú9‘â2ÙT`b-Á–Û÷)£³äCL?•%ít%~…{Š£6TBAu"¸R´´Ãã¨[¾^î›ÍmœŞÏ•&sJµHúÎòÁ(,Ç”­öKæ•ç|‚R¡4ê:Jé@éùÙƒ§Ü®”X  ô/†Ò%E(ıfLéú|®>W÷¹¥²”^Xá/b(ı’¨[y?z)½ËüS£ÆÑ8ŸGmÌ“ÉS$áu}]şòO³B7ÂõK‚ÒÂ^i”—Ô»ØL0cc$6?Ğ;»x2jvtZôcbk¸)›¢–&‹F%
û“Å†¢(°Stq¡åò\ÒQuE…D èRE¹‰/­_Æ5{+»‰ÿ*[Ö5K7ñå´éòÒ4ª®!²’Ø$İÃß±{ø©.73Ú~¤hSGX=¹.I¿µAš¤ßZ™?KšŞåV°Š[U€5 ,sc²k¦BÀoòI«³Ì
¨ïİ˜¬¡ÀÖ´#3fR‰: LÒTc·Vôïz”ú½Œ|±¶‚.Õd%´?¤Ù:lIheú•ïó+Ëµu…ùÊ÷ãEN¾¨ÔêUR]å‹jşË5ÚÉV¾¨åïP¾øSFYgXkÆ¡|Q¯6H‡¡|ñ—4_—Í}ùâÃå‹õXÕ“/Öço•/6ÀŸ/F³òÅ†|C¾ƒ·•/ÆêXÆe1ı·b#‹éX¾ØX1ñÑ½‰‚ØÔ û£İ(rèŞL«÷Ğ½¹A÷b¼’……Pß–İ­…ÕGŠ¡XKyıÈ5’Fíïc‹ù-Šaşu“ÃüÇ¡®tKí{+ıÚT¶ù×¬Ì[³i Û|â»sšMªnÍå[ª±oÃêØ‚·å›[ğ¿€ol€Ï19°x7ë­˜ÀêYí4	±tÄ&ÖZ‚:H@¼öl¼ºâ”…`¸ÆšÈş2;? W,l§Ã·Äëâh…;yî(#—ua]ÜÉàÖ¦qŞY?xiVÜqW6Şôiö<bâjÃÇµn’‚Û]Àe]':´štEÉ±mº4Ì*ğò,³‹Õg™¥EA·*åíŠ2›4+°Y´¢´)Ë}NŸ¬­§Hë”Eg>9º]«ï°Ù0ô6eCÄØ*Âf_DlVQÙR_—+T'†Í:-›u)ønÃf{ƒÍâ\wbö'<(æ¡Âém÷(uÂÏ	×A.ñE$¾³Ä×xá#ÒPG¨3~ŞÎB 
Kª÷$NUiÒq#¿7+Cq#>9æÆDø°W}Q×q£àÜ8Ícª½§+^fhŸİ }¯"hÿ2İõ­UÕåÕ¹d¦AûŞíû(ø}Ú)vY[m¨Üpá ‰T£†1	»FÃ«ºJÂqšèUÕ~›*4k>bGÁŒQîD~ÛqŒŒdUitÛ=<r"“§†²Ö[/V³«ÅDÙ$:·q ó¬³Ó«r89±4Ù/"(1ˆÌèCÈŒ	z€ò@yäŠº B!ô` »QŒêš}•»ææš¥b×áÚ´_šfÄ.¨«Él’Š]ßX±ëH©Î¥è(m´(vaI¢ş]Ä®cÒŠ]UÉ±üYÒô-—ãØñ¬e±ë?¬™.IsÊ'À2»’¡¾'v¨ÀN²#3bó3ÀÄËÙ¤Ÿœ;—€=Åû]f<UÁ¦“Ç.sK³ÓÙ,Z ÏĞ/ü_x¦¶>Ë|á÷ñ‰"'œ­ÕÏ‘ê*rË¿c‘ë<íä»ñŸÏß¡È5ŒòÃØm~E®µÃ‹¤ÃPäšWš_Ìæ¾Èõã€"×%¬ê‰\—ò·Š\—áOˆ\—³"×|Cäºo+r]¥c¹:‹éùd×XLÇ"×µŠ‰ŸˆîëÄºŠÑ"·]¯ÕoĞS±g~³0ŞHÈØó³¿0rÊL*CØ¡ºêêÊä&V‡Øs3ß{nQğ·
øÆfºŸNHsµ¶÷¦!oäPoÃ7 Y/v^s „Lô®‚¹ˆRÚ	.<ä®°4¹]g$ ~6±|0	Ÿ/Qw £Ëó.ù‘€P7À–¨»“Y­Î=úí÷¨nP{_Ôş¡¶­5_Vãªä~ƒÚ,jTğÔ!JÁ	S6˜[Aû‡X›à®ô¿C¬XOiÈè
-š·¼šypgLA~#sAŸ:ı2®0ÌE	V/§K¢[kKÅzÆ _)—<_İŸ<2€€˜
ú“çã¨ëˆ Xˆğ¤bé©€"<]„¿FD¨­.¯¯¨Éå’gµDxNÁ?oˆ@ö	ˆc-â¶Tî¬ÓáÑ;etº![&§Oã´±
µù1•×r+EÜÈn&ñ#¦'ù	@ê-yòB„b~ò …b|^Œâ—¹/Ëó‡bÔu(œÅ¯z(æmØkŠƒ×¥YqIÿ6Şô[VÒ/‘¿éãöú–‚{[Àváõ¦ÛÑ‚ì]–ÙÍñ÷Ì.öÂ}_9ÁîbI³Ø,ÚÅ>diIÓ\V?ÒÖKë”Eb>ŠÜ.ö‰VÿTªë.öÿ8ŞçÚÙŸv7û‚¿Ãİlaí—cÀèŸşnFì}¥m°ÔæÄ ¶VYúA­ŞæÅ@^lk¿aÎ¶ö[İ_DÅwÚÅ÷eE–2TYDü£OÔ÷D–ŸØÏ–Úÿ«mí/™î•î~õ»û;ÓİoÚİïsqKõı÷œ=óø‹	ü?}øÿd“(ü¿³L¶¸4û§(“ı«˜ıW’À­gÅ‹LöoÌd(ò’hõaRİÍÓ%ÌÚ6;ÊÃ½{–a^ÊÙ»ëj‘³;×Z™ÌÁêL;Â·¤QğsøÆæW²0Ô·«u¨ä0ëëŒ¢jŸ£Il«ùgê£U''¹<Â¾¥=CÉb=Cñ^ç÷-{ˆF˜ å.ÌXpä2iMƒÔ|^Õ'­ˆí#qfµÒXG’fÀÜ7Pîİà¤Ö¥É<üäŒÌ@"ñ	Ë“€Îx-­ÜIÃy"3 n@#¬¥°o:”(Î”fg­îMßNë'-¡-‘¢5i‡5F`¿Á¹Y»0–4Í:¼µˆB^ÔğÖ¬Ã2ÅX3]—”¯_œev-E}3L.ùK(°%Xq;Ï¥ØzxÓlÃøõ)ä¥òÒÁW/£à–5_-_šŸ,¹Ó bçY•êx–Ëxi»¼?àaé€y¯¿‚ö0B§Š]ü—‘f+²Y´øTÜÍNÜ­¤­W6¸›İâ(™²‰‹"7/WÑê«jg©L½¬™—«r SÏÍË<‚øçÚZª’ÕYór¾9/×Tğk	øÆæ/€%É	ÌÛ/ã.¥ò¢5Ê5÷—ËW½İÓÉØ£bQ¦õ¸´ĞHD% 7¦YóH\áPÕˆ€éç£¦Ìˆ+†hB£î<¬x‘£Aš4 -DS5S’èÓÔuJĞTVmˆÍ"¡,óÜĞÑ"Qk’kï(MF™¹J¼ö'k³|°¹
Çsµ­öKÖ‘g™ Tæ*êtÃ\-÷¸–:¥
¥Ce@æå™«ŠyÎˆÌiJ€jCæ¾i>S«àë|x.e'ˆøÄº¾ùà‡æ3¬ã›Ï¬Ëœ?×ãçÏõñöÍg6dŒ–ç†% íP"ß”ŒñPBéc¬yœ4ËZ•à`ÑWpV%±e:——ÏÙ˜evÁ™+³àl¢€7Àÿ‹«ÍzxÓÜÙÕhév¼÷\Ü6×¾m_©KRgjÄ¾…‚›'n„€kòÀqéÙRÁm¥lb—¥îÖ¬-=Û°´¤i^.=Ûjë	Òºe‘Ü‰"·ôl§Õ'jgéÒ3Òğäö„,=óE<Y^]V_YYU—ìÀêXzèŸ/KÏ
~'ßØÜÌ3g›&›ëî`xvÎj*f|º#s†Ó•WÌ£¤v'åL–Ó•GÏ‘©V ë¬K“Ùif¢ó+ú“]X>ØDÇÅ}Wáçİä9Éq5êXWïîQ=§_º’AjK¤Î#µ®F/ÕUI«AjÁ"µMÁO6H=Jòİ]ÔÂçLbQ²V:™jÿ&[H´\†ïb‰ˆéõ&9KÆOx%Y(–åö…dJD~7"=E  H¤'!ÀTyv82 ®#ƒà•‘2t)º2¬lÈĞS„Ã#2TVÖUV×”ç“=K†^ßgÈĞ2¡5Şó|µñ‡Ùm‹œåÉôÆ—–®Êj.U¬t@àe
.¹²ÓğØ$Lkq¤Ÿ¡šßÖŸL
ÕøÌÕ3É{És¦C5ê:Tî€ê½Tï£¸Ø7@õ*ÕûAõª+
55µUH`µ¿AõÕ*øƒªV+•6Xşb!€WˆCìa,
ÉDÑ‰äËíàrÌ>¦ Ö5R‚çÁœ:Ò¦‚ƒP@*Dww«XÔ)¡‘­©Z98¢?ŞCÑ8(â­!8L‡;: ®£ƒ –ŞPDĞaUC‡£ŠĞ¡$–$su•0*K6t8ÆÒáXœ¡C¿H’@FD&â¦öi¨n›ÿDĞ`íi{ïİ5­	cnÎcfE±ë¾Ø”/Ân#Éz-ámæ'qëá|?ÇG4àGÃ±c(àû‹8vöO”çI¨ëh H¥cG@ƒSI§4XÍĞà´"4X4À¹^bÚÈ)Ûisº¡Â|SĞ;S;8K:=vƒ˜W¬ëzè!ôÎa_Ğ;—ôÎã‚Şùxû‚Ş‚åy‘C
@;¤ÈW){H¡ w‰ùRi–u
—)ËëB+^ÆÖ©è³º|Òå,³ÂŞB©°GàW(ğ+-ğÿU'tU¦»5¤»«ıîN»ãö~vwm@à5¯+BàE&pEò_Càë-oĞn,J`vÓŸÜ=„¾9$ğ-†À·ßøv!íò¼Ó å+Aà»<Sj½[Ç|"ÅJ­kÉ`ïeİHj½¥%M‹Rj½_[? ­PI­(ò2¥kõ‡
Œ2x¸‹—¹ÚŠêŠ\UUòˆÁÿ£|Sj}LÁ?.à›÷QŸ4Ïá†¡Ğ$bLqf¨¢«Ù˜™¯Â¿K§T• TB™ëZëğFİ¤´›Ö?d6 ç[o’K´¶ÉáêôÇ•lù¡HºÎòT°mŸ²íS&lÉ½İ–S&òTŠo—¶§„¼OËóGdÔuDD‚ÈÏzD&ç?§ˆy>ÀûÚï/Áûâ1ŞkÊ***Ÿ¼hğş’ÅûË
şƒ÷‘ğt	ÉV=şD¾1HBhp¿_1‡mÊŞ¦±îDhİø±™wÎÔ°t ÉÔ ‰ğL”ğÁ´iaraz¥eì-˜“‹ûS§G4¡¯©B'‚@Lcõ ƒhò8äôöÀ†Ä•ìô‚‚I,`º{ÒĞ¸Ô»ÈyÎ1îói ¾¼@t©gä$V¶l|#“W#ö =ú“×†b&f×…1Şç›=P×±‡Ğìñ–Ç\‡ßVú½#ÍŠFşÈU8««wÙ:])JeÌï±Ì.òKfVİ÷øï­cxïÃ"¼·ÔÀ«neò‘á¾ùæ¶ú‰vğ©tn«ì'X×ßVÑC¸ê~Î:ş¶úè’Á7]2ğö·Õ¯×ßÈó[‡q€v—¯Æ¿ó0Î0ßë˜fzmô#ÿ=ÄbË’¦¥‡m~ÇüsOA (ş¯‹Êä+1`YZËO9ÍŞQÿªşP¡ÜPá÷"TX&ZjªóµeùäCƒ?ùæÊû—‚ÿ[À76¯Æ•7µ!³Bú™Ä˜-bYŞ+1šF&ÿFf•ä ú“Y>Ø*‰ñÅÓ`ØâbE³áiô|¨ëˆ"¢Ãÿ­²›Œ4;~ã#æf!#UÈ ædß@dY2C-I |MZ<R^½ëP)Ë…nFnúHè@°õ$s ¹¬™Æ:l$š}i‘ÌÌÃ*wc<ór çœŞİ1®¡óáWó0Ô-/-KæÇ‰sÂKg2œÿÁš;KÙÄÙ±Š’¡F‚-KRÂÿ—4-Ë|Aıè…ä£Pfvğ‰³ËxFù‘çbO¸zIaWù–XÇ“E9Š¹xİUèH#¤‰ó¶·M2nÆÉâl<÷xÃ fIv‹	µß˜PKãMşä„XF‡±¬C'Ärü;˜k$Ëëà—³bş'D¥Pk„!0&Ärş„›zíp¤tX|Í«r·+RºæU	ô•Yv.R‚võÌ,ÍõuÌ»mnÆXh¦Î›¬‚¡UñB>!ã0ü'Y]Ç¾Â°Ã'ÎkNQ$$kç…<ÌŒÔ§%k¢d×d-<³à›¦uà¤;!$Uœ7¥½¬-½”J/sµ´'HìÜ›¬CB	Oìáu:/,:ÀMÒk™kNDİApÙ¤\~ÍİŠ°úòßŠ´ıÄù`"ŠÀ;´íM*edUüšæyyòI¦Á°„ê«¤Ú~ØªFÑ[+èmÀ¶Úòğ¤e¹‰ÃÙñ$›¥9©—şç…FÓ‡|tIƒô´.Çí“úäŸ˜ÕÉz^oëko„½ÁîßAw„Şiùö½
Ävv²¡bŒ‚ƒ‡¢ÂÄ¹˜æÂB²Ç5-Ÿ›–×+„å3÷O+˜MLÊ0ÕÂ0›²;ŠÓT4Oïç”d3ÂNÅñÚvs3„±0"'L7jõ-´«T\c–ô&BTÀ+FKzk¾ºµµ¢P‘lÉêPoÅ7—ô­ü6¾±y4Æ¼ÏŒõúıFBw S–ñj[ìß:eô6ššA¿4wÇ¶„Yê9ØşdË[ê1îx©ß­ —çö2J¡êÈÀR¿{ğÜ³šõãvpWkp·SÜX(©Jv6ØÛ…oî%»j»Iá^Ânú“I¬ë%è!Jvg_(É± kho¬¡-xûBI« £ Ï6‡€vH‘¯R&{Há}Ès»4û?Ü½ìAxÃ›VÊ^–ÔÉÇNõúâòÛ¡}uJ_ÙåWôß]”ÒKà.¶NgS½@ìf™9WÎLÂ¾§R×i¤YÂfÑ™¶—¥%M«pöiëiÒºeÑ™EnN×ê3VZ×°Ò^EXiÕh¶´UæËZk+’™†‘öæ›Óp¿¯€Ç™ÖD‘ğS¦òÕ(VS=ª•³N|ª™s6iØ5e¥€Õzm4MõÛ¾? b¯©òI‰©ĞãÉÜÃ‡Ó®¯@“šEò#[GQK#wÈÁ^B¤À˜¤›["Ú–ğÆZ¢˜K%c‚-£§5ÀôŠ!CÙš^«‚‡ærœŠ­ş±(Æ<Ó•HïlŒíıõ†ñ¤Kf	#¡aÏòÁ.«@ó"†ñ2O”çAn¶¢®›­ÂH4Œ÷fÏô‡(cğİz†ï+Âw«E|W(«)”Õæ+’Ãßõ[¾;BÁiøî1x$ADkŒœà¹DléXëÅBWËL„èS†ˆ½@KIÌi$˜p¡•Ş˜¤ZE	7š¡ğ¢³·:1LÅÉ*hÜÁhè½I¼¦Ü˜›¥ÉQ9‰¿şäè¡È	TÆä<Fy¬<säD]GN¡Èy|@Îÿ(¾OÈ¹¾!ç‰EÈ¹z¬¢©(o«ªA4ï“9O¶ä<EÁŸjÈ¹È¹Q·\Ñ&9Å.ØİÌ¦.ø&3ê0Y“MùME÷èä´u+†B†£îAÚ™ò<Ë¡uê@İÙêÎÑo;7@İuçAİoæÕÉùyğÍÍüBíà"é ÜÌÙ<X×ßÌÑC¸™_Â:şf~)°™_Æ76óËñö7ó+WÊó*‡€vH‘¯R®öÂöóµÒÌm°4€”¤¯S%¢u—Óİ_G éf9Z¾ê¿,³{ìšİıõ
ÿÿÕİß˜énCéî&¿»µ2[úÍÚİ-Jc»¥‘f·²Y´¥ßÆÒ’¦QÜÒo×ÖwHë”E[:ŠÜ–~§V¿+`¨±†¡î.ÂPkGs±YøÚÚrÉ=†îå›[ú}
ş~¯Ñ/ ¦fî3èFD³‰%
öĞ±«šF3TÎª
NŒŸ­^ÎÁÂØX 5 t?Àn3;¿ÙX>˜ĞOŠçéCÂŒËóÇ’¨ëXRğ–|ÔcIîXéw? uœAëEĞZXª«[[à{›<iĞú”EëÓ
şƒV¦İVtLâ_¢‚ãR1*ïê5œ•½•W~«XæË‘EE
\3<ÚXI‡Å}j4ê×]*µK“g#üòƒú“çRüÒÊ±«3y‘®_cùÁï‹ò|Éau–mÀòË–_Q4¼`y#ƒå×Š`yØˆ¥¼5_Y[_–¼n°ü†Åò›
ş-ƒåß!ncŸv†‘ts@¯æs$"Ã£¼ëpÊÂ´Ù-Nã-6ƒ©E ISLkCÃ¸#G‹56„+EA,	$	9h%
fà.S˜Eìi³ÆL>!šys”Ïñ2  Š…'#;Èå9‡5Ğ¤ÅEƒXiJ^(G„ÕÚ:	Í¡!‡Àx§mÆbÒDå£¹'ğJñh î,Ò| [rúÁÇT°ÏÁÊ½\ncÔÒ£‰ùrµqÑÃÁx;Y)JY)ìÌHŞxŸlÖŸ¼òş»Ey|óş{ÂõïËóÇû¨ëx_˜¼ÿaÀû)s~ğşÆ†÷?)Âûe±L\Y]İV‹ŸŞÿÌòşç
şÃû¯c^KÜDm1Ú“=¨Ï¯d?b>	V-Kº	¯¨âª©êĞÕŠ¦Nú¢ ­Ó Œ<,/è„N¸|ñm×/q¦'‹±·°öµ‘0®GAÎÈÉğõ¥óQgl\š|Ñ–hìO¾JiKõbK¼¢£1U¿z~#ÏoUQ×QUÈÄËªe¾W´ÿ ÍŠªj[*œÏëlJ›È˜b™•cÊ3rÌÏ
üü•c~Ít·©t÷›ß]Eæ6ìwíî€C73úg­XV­Iş2<ú7ß”UÿÑş•BY•İô'³,Èªè!”Uge_VU‡ñYuv¼}YuüFä)yÎ…§ÑÆ´#°|%<7ammæÁoŒy^i–’n¼v>Ö„»ùYZÒTEán¸¶^@Z7 ,îPä„»­¾ v–ªM77Xˆµiu´FÔ—×µT2êúÂ¬µé"|S¸[TÁ/&à›§p7!×.W_œ©ˆac+X¤AÀÃÙ™6’)¯Ê¹¡HR7³‡Š‘§¨ŠyúÂTUqĞ¨eSàÒN«fríBœØ–ióĞÛ‰› ‰ŞÅì×ô0„“ C;X“S^é0€o  ¥İ¾¦©aGâæ%×E¨~Z4,Î¯ÌÈ’Dò³|0YŒ×„%…Y–’çÒeP7 Xfe(K.«h^. b£¡âòE¨XSD–Ì*Zj«“GX*®¨àG**šC1×Mh¼rPnCPÙIãqštJü):
ÓsDmğ2qv Éˆ±D€bÜam×è½â'!ªuÍI<9	”&+Eøçã**ƒÿ"k2¾=Æÿ*‚ùUå¹šÃ?ê:üBÿÕü¯¡Z3ÀÿÿkÁm„ÿêš2Äo©OFü¯mñ_ªà×1øß”ø§ñ¸•$Ö„sÄ’±iû°ÛŠGK)BÔ1ñ5U4È°‰œğ“YÈK“²‡tR>1ş‡‚½JyV9¢®Ã¡ 8¬öpÈ}­F?²Vš¹}m>|,)¯!rİ½ÍÓÕ±I]Ï2»±Õevš…¾n@¡-…Ö+B¡úwšÚd}C£øæN3Z;ØP:wvÓŸŒa]_+‚Âf,ëø;Í8`§Ùˆoì4ãíï4›²7•çfå íP._	”÷PÎfss£"Åª¶’ÁnÁºÑNÓÄÒ’¦î4[jë­¤uÊ¢En§ÙZ«oP`kCm‹P`İX¥—¯¬®ªÏW&ş·ã›;ÍD¿½€olnçN³ƒjÆ¡´Ñ½§&p­ŒW/ù@½´e&îz/’gÑñßdÏ3'ñ%£ZÕ™¸]Îáô42Ù£Èìü¬ş¤™åƒíøÂxí(ÄÜI;;’¢®#© $İÅ#)gÑ®Š†İ¤ÙÆK“Ø:%ü62æİYf'ÑzµSNç³ü²­4k)Ê/­Ê/ë“_
ÚºÍğËú1¿ ÈñËd­>%à—	†_Ú‹ğËñV[QYY	ÉdÃ/S-¿t(øNÃ/t/åézG']=Ù-nÙ2ôìŠ¥}Œ ¦gPrOy&¨ëè)ŸzöôìÓaNèÉáš‹®–ºôbpz†œÛÉgøä!ç^
{f–œ¥ÙŞEÉ¹’sC’s_m½Ÿ!ç†19QäÈ¹¿V?  çö†œ!ç˜XĞ¬®*T—×•'rlÉyˆ‚?ÔóN„ ãD5 ˆĞo<µRiñ!Aº8tQìi‡‡ …%#Ã÷õN›Ú®}¼Âó®íDz…°õ‚Çàï8ŸŠë7eHãk‰Áãå§QkJè‘ÉaË5ıÉá–+b,Å,×/Ìv„<t,‡ºåõ`¹£<–£0y´¢ò˜€R;J[„RccJµVÖÕ••U$ÇJo)õ‚¡ÔHŞ½HÈªyşOÕ·FZ„Ô>:91BÇÓŸœ”AO‘‰¡Åè9YsŠ<OuèA]‡ù^ ç4=\aO×ñŸ!Í†\aÏdët…m–1ŸÅ2»ÂËLÉ³ø9Š{»#ï(ÍÎe³hG>¥%MqJ¯­/Ö(‹vd¹)y¡V¿( ôN†Ğ!ôÆ±'o}YYYUEkr‰!ô¥–Ğ—)øË¡ä”4“‡.Ñ&6µUOÚ4"Ãª[%³.¨'´N?¤ØEªLø’ñhˆ0}ª*ÂM|+ÎŒ°¯”ÙE^‡Q°2‡!M•é¸M%Rw]±¿É2lTd–áÃc6ºJèjy^ãØu	6ÁF×ltbç¿EØ¨ˆÉÇõ6ÚYÆ|ƒÏF›dØèF~S–v‘f7e£[”6%İª­o3l´iÌF(rlt»V¿#`£]İY„6‹ï‡à©U]^Y•ÜeØènËF÷(ø{M²öÔŸÚ?‹ug_]A/ì÷zÛpD3
˜ûIÌGUË‰Bê¶ŸšW$÷E\ÂéOîÏpI‘ƒ%¾+æ’„?”çCKP×q‰ \òpÀ%èÇ?p	EKœ¶ï±›ì&ƒ~Üg“ñ6yB¡?™e“IÒì©¢lò´²Éæd“g´õ³†M6ÙE.6ĞsZıy©®6­/ğoØ´Ò4w"{ô¶ƒ†gõ‘]pNÈu Èí‹Ú]£µn}‰¿CëÖİe¼/ÌÁäª14÷~E»~5àĞœáĞ×Špè1‡ÖäËÚÊàşºáĞ7,‡¾©àß2úš9cù±É¿öS]†qÀ4úl¤™E¸‰!†k4Hê­i­täòFı”ÕÊ¤·oíV^U(´aíÃeÃnIÆoU‘©	ü¢7)êHÍ‘ Ó5[PÆcMíAF×ÒèòæŞ¨ÀümjçÔ‹(ø}Æ•&oGSƒXÄÇPS§Æ»2)Ş“çûnj ®›B%L¼©ÁP˜*Ö?rÍš†MÙİº’—}ìš¥¡0?Ñ¦ŸJÓL‘^,…ä3¶Ican%ì´Ú®ÉçRŸ2À
àK)Ò^ï+‚K7óÿÇÙW€WR,á¢'¸Ë²È.°â†,K.A—“sN„ÑIV€Åáàîîîî~q¿¸»İ‹»¿ÿ¯ê™MŞ{||39½móWuwuuUu^ºõÓœ°MbT~­•£Üêd€‚û–Åà;&ÛrT~¯¥ÒMHd $ùQù£fÿI²ë¨ü™‡q'ÑF¶scñWşNÅ¢ôò7‹9Æâvñ±H=ÉïÚàÒ`ZOÒ.Åÿdñ¸[ÁöÔ“,„a5Cë|nˆS;Â®˜¿˜5wòoşÖ¸“ÿàO˜ÙÏ²¤êOfåú“Ùğvq'gÇßèËxÅîNÌÉüD:Œ;ù/şSYË„{.­bn©¢	iÜHòkå<š}^m1R·wÚ™h>ÖœR·ïÈ™7gˆW­ğç¤ªÊ6xŸµUšù™úöø¦dA­¿Lêon½Å`¬(rQß"kğC9=“¸
C½4Ñç¢Ò é:G="÷B‰[ìÅ2	tÈ_Œ:µË”Ú„×dp‰Ïâ5=0¥9f'€Ñ…¸=ØÔ×Kµºª']x)]yàñ'.®*hCİ3t*5!¶äpN]nâ—%4+Äªdfúp†€-œoA)\!ÏÅ#1’FŞ-0ß,ÎbFÒK(´K¦H×eI·Tév
I×^WÛĞØVÑ`–¶¤[Æ‘nY­9Kºó@:ìˆ`j¡1”íåïŞëïtÂutñ³¶¡®nš¥M°÷×Ù3=z·’´º©ä¾¼Q<â ¹ô~Œ	£pK1ÎI,àˆ>¡4‹sÇ§¼%C£27™åÒÄ£‰4€%$ÍŠB”Qò\É“y=ikftŠ4++t«¤H³·%Íª¤Ù9ƒ4UÅúú¼YÍ’fŒ#ÍX­uKšÄé Ë²-ëÁb;‹°ÄBI;š1ÜÂ|ìoÉ¬9|èzß8n¼<Ë=|Èëá< ßZ)ø*ôó*SğM¶ğUeÀ×Â×X‘Ï×ÕTU™j_ƒ¯Vë¯³ğ1no0Õ«td®U,=N¶æØSqÖ§÷¯$­Wõ"fÔp¦‘“®øA›ñ¾{z¹©°åÇàŠ‘°Åw…Ø6
ªMò\Ûc‹¼[Ø®“Âv]ıöõRØv[l'd`»Kˆm]e±¡¶ª¦Ò¬o±İÀa»¡Ö¿‘Å¶ØVóĞGd@l—{ú*nÄÄdaçnà%—,Bµ…¹ó¯¥”}‘†ÅQ¶¶2¢rï œ}6­mzty­–.7`óë×j$°ñ¡!Ø›
Ì›Éss6òz°=g¤ÀŞBÁhNİcÁŞ2ì]C°£Ød-ì­ø¦ì²µÖ¿ÔŸ–]ØJÉlË¼ñ34>ãÙyâg<Û32Ê|CFÙïøÏN‚ÆÎòlõ˜ j‰|$0Ù%†	ÏxvÕ>ï¦˜8i²W:»;óÒäL-kÙâÍZz’”nBZ Ş É‹7{iö\Š }– mØ=$@±¦"WQ[[gò– ¾)Şµşv©¿¹õ=pûğşSóNÆë±$›6Ší5òŸoN·³G´*OğR3E¶íŒ„M•-‡`Ï]Eåkï7°LÖ‚RX/àH8B^01Ör[Å8×KPAEyL×YD·”kÛœa9Ï–šL¿=! Í’édúp€GW—ğĞŞòœì9	y='	µÀIİ1N¢^¸GÁïM·ß·/ƒ¸{„Äm+´UÁ¤¬Âô[âîãˆk´şKÜ§@Ü]é977¢NlUÉ¶‹Ò£š7¦µŠb,V st€XÖÁ&ş¼§ƒ6
 DÀB¬$¢MdFĞFj„…Ï4ZƒZ³aöDohâ —~ İ£-å} kšÜ‘Õ§èHàJfh$:ÃS„‚Så9ÍÓy=…0 ãô÷Uœ÷KÑqKÇı3è¸g+ÛrˆQkfX:àèx Ö¥ã¶ cmcq«¶/N†½w8.á]]¨'®ATÎrsp 'û_2‡Œ'>%„óPò0yîáD^§à8HÁYÒÏ=2§±p•ç¤ÎBc¾*ß^Yo¶pãà<Vë?ÎÂy#à¬‹íÁ³U0G©ÑŒîÅxÜ-ê¯p¸mïW_6½5Pmsİıôò/B;P…“ïPj$+„#\gÌú´éh•ÛœÌñµOÉœ0µ€TH­…N'ÉódO-äõÔøA­SRÔ:UÑ<-E­K­Ó3¨µWH­ê†Ê6D®3gXjé¨u–Ö¶¥Ö2°
­ŸµpÈhò*SÉî›aa°ëZ00EÅF;ÚaÈ‚b¥5Ò@f2PÀ|$|œ:kü–h_™Å¯0L:'ªqØök`Ë1˜ÉòC²|Ú`Š±
sl;}_™óì”ªMB`/tµ·C’ÇnA®%&ÔœEÆm–Ğ˜¼²›†Á½ÄP3ç|AB ğ×H|š„|qpÄùò¼Àóòz¾Bƒ/.LñÅEJ·‹S|1hùâ’¾È…|QSÑP¬}Š¹ÔòÅe/.×ú¯°|Ñ†Q¼5D	Ü¢ƒ2Å„Î¹Ä-–zÂe=ÔdÎQ/¾}r¿EŒ×EmKoÏ@Ì•¾ü ’¹j$|ñm!¾W²×ÈóZ/òz|0à{]
ßëõûoHá;dñ½1ß6âË£¯øŠÅ“»É"|3ßÎoÑn•ÒÂ9ÛÁÑóÆ…s4‘Îog¸p~ œßÉ7„ó»ğçw÷Èó^
ªö¨Èg•ûb¨P8¿_ûü€¢â„ó)ÒÙ™7ÎbjYKÂùÃZú)İ„´@8G’Wõ>ªÙÿ-ÙUÕûÿ†ªw` Oİ–W#²ÅØÑZ‚mµç%Æ<®Mœø	şN+€§JßŸ´ß	İZ!­ ~J»ñt&¦Iñg„NGIœñ;B%Å™*€Ÿuäê¼W¢Ä<Çßª ~Bü‚¥ß‹–~/)ı:‰ÿ´//'ñŸ.x%ÿW„vâÿš–~İâßâ$ÿšıÍşoYü:dªéÆV”×®nŞÖF:Òïd!½¯ôò]tGúØë=mğ}ıºHÙ¼Ÿs°hJÙÜ™¡k«ª+æÌ‡ÌeóG|s7ö±Öÿ‰ÔßÜú2Ï½djç¥9é™Ÿæ7½ˆ‰(š¸79××Cacw«ÒçW˜Îü}HœïÜ‘şz6O*N§®5uOgÅ	+=+3v÷µµM—}—ø¦X-jär"nÕ±¥[GI¡0uÚTó)?8±#„%óÓ‡Û‚Ípı¥pÑ¹<¿èD¼)a¾ø¯¥.ùU®9QÄ¿’bIÙ¬ãà¯Y<šVö—NÃ4wğÔ•pşøVkÿÎÕşÿêüñ}¢¹ÒÜñæöN˜äş¨Íı”bÏ,{şœÁ“‡YªÌ/–Aå›KÂoÚÂïÒBzI`;¸Ô„yãKšH/	2O|Iø‹	XşæKÂ?xÇ—„Y–"qg•çlxZ£jObùLxvü{ÜûcüFŸç”bí”Îş‹yƒ%a.¦–µtsJš[KÏ#¥›,	Hòúšy5û|ÚX4CdI0?kNÍ=
³úºªê†ÆF³ óc†XoÎeZÿBRsëµ4²çQ20#?‚ŒÓ=†İ°á¤ebÿW ¢
76r.ı:p.Î˜‰ŠÓ1OLµ¢!:ÔØ|GaÖ°«wJ—Xß!—=zs!ÌU±pËT
Qz–fa”·0?$1ò	MÉ,ÂôáF>P
Gş¢Â‹ÉsqÏÈ›‚l±DŒ-äêEr))öÿfiÖ·@Ko2ÍÁò5Ë¤XpYmk¹$"y—ÏdÁ”ûÈ‚+jéQ–ûBD’gÁ•4ûèjYpåìY°¢!—¯©+Ö˜U,®êXp5­ŒeÁñ¢2tqW¶Ç§¿Z òn&ÕÕ$áTnÆ<À¾•Ìê#ñ ºòÀBı5å9Îó òzoŒÑ…
¸rı”µRPf¡ªÈ€jŸŒ½ke¡²¾¦¢İTZ¨ªTÕZ…Šq±VÄÂ?,ÙâãäFÏ¹Ñscu›Rc[ÈQ¤qˆz—.ô±ƒÅ~§ß­¯<%ClÑ"bÜ`vwµãHh*F%cÇº&Mm@~uÉÔD ¡^àog£'òz"ª BSŠk+Hë¤ˆp¸%ÂºD0SfUe¾½¡­Á¬g‰0Áa}­K„Í¡@à0§?ğ)¤r^SŒ[lL_[7cíÂªkp‚8õ‹òÌëÒdÆõ :ÇFwo["h »à¢¥ŠL˜V˜A43è„á2çT1MÜæœß¦z@Ô®8Ä¹Ú™Ü¡®v\c£Ê%^ĞŒ¦ºFòQë» 1E :*>úp w±x¯4,-„}ü\†â#ë¥å¸øY¬c´r³aÀE$[Él4‚!m,ü³‰<7õ\„¼‹„-ÀE›¥¸hs¥òÄa¹h‹.È8¬©Â`n¯7Í–‹¶t\Ô¢õoe¹hmeœ;Ğ WZ³N`ƒßĞY‹õ—w¸æĞ–ÃXºc‚^P š­àØS\ä2pètÜ¶ÙvòÜŞ‡¼8AÀínGı°RÀ•,p;g 78ŒĞXmZ-t»ğM¡qWma7i!-4²œ›1o\hDi¡qæ‰{2Bã$¾!4î…w\hÌ	mòÌ{TPµGE>¨b¨p_PÔ>·K1ìş_%÷Ö	›GÊGv2Ím†….mno×œ½¸Œ»X<¸\å‹•ŞSor¢ò£¤òîxåSæo=Zy¯RØéD–b},ÀıL-k™Jéc-m¤tÒI^úĞìƒ)v:Æ²ÓP;MË€+‹µíy3Å2ÓT¾) OÓú§KıÍ­Ó) oŠÉu¨WnóÛMµ¥’SvLé:C2$Å@n¯ˆ‰!·œáÈ©{ˆ[SQ8Çê™=/¢ÇèıN‰Üİ7Ä9’ ö";sCšİ—½JH³üÎ’ÙéÃI³øäpï/œ:Cx~E^Ï¯‚#øõÀ¿R’9Ha98û±öC2`Ÿaq’«©¨Ëc>;ÔÂ~˜ƒıp­ÿûÖ„=
ÀADÍ
Å|ã¸ŠŸ2–(YI„ ’BI—AÈ	zëĞï¼ İ˜ÂŠ£‡Ñ¦€ÉŞ—Ì‘#‰	Á<J`<ZÇx0‘×ƒ)è Ìcc`rğ§{¼›™RÀ_Av‹Gãê8éô‰Lsc}ßÄp<Ik?YIå†ãñRì†ã©L-kÙÃñ4-}º”nBZ0‘ä‡ãšıÌ_œ`ùâ¬¾Ø?ä‹†šb]·ğ˜³-_œãøâ\­ÿ<Ëé~r)d•äpÁ…]Aå £·úéöS$†,ÑQ§»=gVI‹QI4¨cw}T(îÀ^›U„¥Ñ"AëNÖ9€ aÑ°É³`´ë•óçŞbQ´S}£pë¨ú´€Ï8‘x•Ì#q" 9ñBáÁ‹äy±çDäõœ(ô '^’âÄKŞË†åDï­py‚O”N_çÄ	N¼Rk¿*É‰'I±«'Î’ÀwNd}İ òåÆÈ×j×Yn< äF$y…íõšıÉ®
óùwÊ6
Û›´‘ÂöfşN«ÆO–Şb1ÃfüÀ´ÂöVmğ¶ûŸbÙÿöö?(dÿ\}MC[öwXö¿Ó±ÿ]Zÿİ–ı ûûÍ°gJ¹SÂíb‰²FŒ"Ë½²¦Á¹64UÔ$½2Eo*`a6¹)$—½nw¥›qYÕxjœPçªı@¤ØÑ»4ìfšå.ÔgDUÔÉpr¨:d¦tM¡^£“Z{‚C„KæŞ‘ÀÌ}2Tî—ç~À ¯0BA˜c†qŞR‚<ã°G²9ìQå°ƒ‡ı;‹ÃN•ÏxÌsØÁi{\|"Åa§Y{2ƒÃF|®1OY{šoŠÏÏhÏJiñ™í”ÌsÌŸÑDZ|~yââóL€øü"ßŸ_Â;.>ÿGğ²<_ñd@Õò™ Ã«12P¹öšöùu)öÿ¡\{ƒõ-ĞrhR¹vº|ì›±¶¸Z¿¥m½-mè:òKG«îRã»Ls‹õa‰)ò=­ü}%¯[¬Ï”b°X°X¨|u8§Ç´ôÇRº	iÁb$?=~¢Ù?•ì:=~Æ¿ÃéñsmäÇ¼_ğwzz<Kzù¥…p‘fŞÿjƒÿÓ¯‹´Õg[æıŠESÚêR8=ÖÖçĞÖ…_3?´ÕßğMaı[­ÿ;©¿¹µ’ú/a‡æ…¡ˆ¢Û¾¡éÆq]åu{„¯ôåæ{Ö–²Ù?„0}8!]'—…Ÿ’çÏÒ/9,BŞÔ÷ƒ«IqÚ¯ú9¿epšÛ¥UÅn|OpÚ9Òç?âœvd‚ÓşÔÊÿJrÚ¹RìïLNûG™à(rÚ,KKéYñ"§r’b7¾köÙ%»ÿğó,áç@zšğGgìÒòµUUíXçd~^ùÎ·\ù®õÏ-õ7·Ş ^3Qˆï„V*©!Şë¬–M²,ÉKïjOI‘"(Šó)¤Ä˜? .š]%¢%ux=9^eŒ5Ñ’¸tŒ-ÍØƒèˆ?u–ÈĞ0ÑbÈpiN.œ‡ß’`;¢ƒ»Ü™>Û¨íæC)Üå.Ïa;äM¡¶[-ÄïrW0’bÉP».bEe#Vò(jÅÂ¬ š¬Î—n/Â47Ç“à¼EµşÅ”Üw[œÅ‚9n	¦–µKÎ[RK/e9ïØóä9oiÍ¾LŠó.´œ·lç—ÁyÅJÜTSe–³œ·¼ã¼´ş-çñ€œG;È¾ìHy	Š:*kš¢3ù‚UUœ²xê›BUJGR°&lÀ˜ŞY‰G¨İĞ¢¼ŠN+gå 	T-±Ş4JO¡˜q_1×ÏCuèç‹EŞR)Ş£0Óu©ä)7£¶#4¸\~$¶J!Û†[Y«x¶C^Ïv=ØnÕÛ­¦HI±\Ê^¡06ÁsIŸWóÜñ	[C+_3ÉsK±q™<7^yîò\¹–^ËòÜ	!Ï!Éó\…f¯LñÜ%–çª2xîÄŒ±šêªºFD¾©¶<Wãx®Vë¯³<wNt†3}°@Ä©‹X¡³©“ Ü.×5Èëÿ¬mD;vk0ƒÓşŞ'Ò¶s ”T†"ëı‰´I†{ŞÊ±£
•S(aiáÍğ¹8ŠXwŒîŒµ‰AgFk%É!ßyÈr,7èjÏfvJ¡#GÂØ¹³\iÇŸİØ Áw«Ÿ°5ŞÓ
ÍDÚ·÷-0°ãbçL.îx4oÌçòÅÅªfÏÒ!–íåÉ±³3Ñ/WêYŒ;ŠˆyÍ ¼™‚AF^€7ÓHƒl‘áÍ$Ã«IkûA†¼~	¯Ñ›)5ÈÖUÖY/5Èf`Bb”]*^?>ÊNJŒ²´ö“£ì2)¶Qæ(ÛXGÙÉe›héMí(;9eHò£l3Í¾yj”]nGÙÄŒQvJ†ÙvE]¡½º±`¶°£¬Ù²-µş;Ê®Ä(Îa0qéƒ¹1vŒ5Ô‹˜dVçÖ”¨Ü´ˆ¼qõ’Gì±C+pšŠª¬b-†­WƒÀ%o{ô£5\tÊ<jh¶N‹UlÚÿïŒÏgî‚&1xû ÃŠóÿã‰†ó{‰„ÒG®kê3ÃÇtõîSK1fW9ojĞ5DœÙ*pd‹’Ùz¤	Ü62Ô¶•çv~À!¯pÂvpÛÇå;(í˜âÒ+,—î”Á¥§³_¯5;[>må›ûõ]´…]¥…ô~í”ÌnÌß¯£‰ô~}wæ‰ï×÷`öë{òıú$¼ãûõ½œ<Û<*¨Ú£"Ÿ	Tò1Th¶YĞ>'^)mgŞ@ì`jYËiœ(:µt—”nBZ°ÍE’Ÿ(öÖì“S$¸Ê’ ;ƒ§gˆ€••…|Ee­é±èå››>­¿_êon=PT°#€ÈÕ1à WaQ&Ç®‚åîA—@ŒBãÄ3[<5ÄŠbÜ
c
8¸·Ná‘å£ÕYË`ÁŞ3ÊTéfP	fö-±™à×â¶(¦·™À‡‡ü? 4”ç§4òzJš ô”¥ÉÿSœi)ğ¯¶àOÏ ÿŒ¬sò\UE]]£Ù×‚¿Ÿ­†ß^ùgˆ·€0PÄ+ëÕŒ÷Ä#©„7ùâ´Üzr8óŠNz¸G—BN×£èFkU“;’g*pÛ}Ÿ´ÓEÂøÕ%sàHD  !ø–ç!Èë‰ ¨‚‡Æˆ@•Õa
ÒáRÌïèÊ¨jw[”´ª*¢=İ¬"™×HÇKLs{º3¦ GjG¥È|­%óÑd>k˜i®Îc	},ßœæÓ—ÒÓÛ3óÆ§94‘æNdø4w0ÍÌ7¦¹SğOs§
â§Éót;ªö¸Ëg÷3b¸sš;Sû|–¢â¦¹ë¤³g3o0ÍÃÔ²–³9Í«¥Ï“ÒMH¦9$ùiî|Í~AŠ×[\˜A‚sÂ‘–¯®¨¯Gis‘%ÀÅ|sš»Dë¿TêonİòĞ.ÖˆÌN[²áÓ3‰;"ˆßFìó8bã¹-Ü2#¯Yq•j‡;”‹ƒlÏõ
¹éãiÎ	³w±_#7ygD¤Á¬!@µ#±d(Z«SNoN(Œd=	#z|'\§0°;ºŒÜşˆ™a >÷ÖÊ”Ç€8?DŸr’ºuŒñÅåL9ò•¢E—šj1‹ê| àa?fcgßÇc, Â p:¶—ŞÄLM‚•ÌåLn¦íÂIâ
aÓ+åy•gVäõÌ*f½:Æ¬œ©¯Qú^›âŸ,ÿ\—Á?çfœ]!şu[CM½¹ŞòÏnÔúo²ü³ø'îâÄƒx”F	³›! Â^Q8ËÜâEêNMBo_½eBoëUƒ2xò"€Íı¬
ô°ãrÊÖ²ç¼È‹ntÑõ+à…¾6µP+<p	cŞ *½òPAïqô¬>ê±xêŒY¨ÊA’°@À†–FşR(€Iİ‘^\Y¥nNã»×\x	+İÎk}9Õ–°åææ€H1SÄ@ ^È@·
ëÜ&ÏÛ=!¯g á0Ğ)ºS	|WŠn´tw—qö_×VİØ€ëî±t¯c û´şû-mBÒ;YeT¦€³›®ê²FÛM‚Ïh3ˆšV¹wùÓHVÀN^¶E4Xôb„kGd¹-Â·q;Ë‘%Ç·NÂ3ñÉNä?ÎùZ^·‘S
˜„Tu€]Ù”Î¾Ğ“ŒoÃØº÷“;Æóæ¡ë19ë	<(Æ¼¢©é„¼#½j}	†‹ö•ê‰ˆ6†pÃµ¡=r•›"ÍàÀ6|!=$Ìó°<ñ,„¼…„'ÀB¦XèßJâÇR,t“e¡Ç3XèüÍYU®²æ	ËBO:zJëÚ²ĞÂ¼}”Q1˜ÛŠz£…“Ğ5Ù/b¢vÍL]+bïO)Â¥S|’p%­½¬!.èGÖÒâ=rùÖDÄ)àÌåÖ4o˜ÁÑ.Fmä££vu †"uµ¨N–1òœ¬3BÂj[øi”ÁeL hlv‹óLlrm¾ÁÑéEáİ9{¹y&`â_2ÏÄ EÈÏ	#</Ï<; ¯g¡/ØáÅ;0BàKJ®ÿøb$#Ş,{Ù‹"¾¢E_•¢‰b*f^c™(BàE.Bàë’Ÿ'ûohoJ‚¾Å¿q8ÊXnñh—ØL†{åÛ¬²¬åâÈé¿Ó‡¤·Hßµ=Æ‘ÌÅñCR
ëïiÃïKÃ^Xç¥ß .§o€óë‰Ë[¥î™æ¤ôKú¹´êux9yô6)ö	‹òè§úM—RıLK.¥›È£Hò§Ë_hö/c ş×÷–¬^İüO¹Ì÷Up·K/¿öÀ]–öKıFüVLïîâß±xÜ/õò™ú¥~Ï¬±À„?ğ·ú¥şˆ?á—úS°sø™oì~ÁÛù¥şª}ù-‰ôÒ‰ßÒa`Â?‰+÷ŸZÅ_î+B¸‘äÅÿ¿5û?Úbt¶~—:gY5§ÎÖ¯ŒO2,&p¾Z•Ç&³2?Xgã›âÿìøõÏÅÿ#ô K>£/ãŠ—×}h Ì9q‰ŞÎ~±àªz'¤xHp‰®c@ó3+Ù¸‹ix…‚ŠËX¹™“]LˆĞüh8Û1}8ßÎWs¡N’å9|¬œœ"o
TÌWó²…ØÉé|ŠÑüR,9tåB5|D´Á^€e£1x·ôxA¦¹¡{UÂb»L«^ÈU=÷îğÈh¥éve[+§×Fi«­öÀÿƒfáD÷H‹ÄÛ¸:y0«m,&mD]»WŠ-ÎbáÁ,SËZ®‘ƒY-½””nBZ0= )v0«Ù—ÑÆ"~½Ïòë²üzmÈ¯ùÊêêºŠºj³œå×å¿® õ¯hù•47Ñl†%lÖh&‡;ŒEÕ!GB*ÛÇ.7lƒfÎÊaÎ¢÷CB.à}§à2ïãÄ‘?ë•#0kòfC>Dg
kPr8W{^Hm(â¤6`sb…“Ú‘Ø°eœÔ
ƒ¯,ÏU<›#oŠ<©±9wŠ«)´cR¤»ß’nlé®IW›‡Om¡Ê¬nI·†#İšZÿ8Kºï9Õ¨(.Úÿ\w$Fy
éÁŞQd-Å,ÃÍã.%	Å‹4ÅQÓG¢ÊüÎïÈšm$‚èl`ÏD‹¤28]#¥rUerõ—‹®2ŒxA5=”Øip,ç:SõbõÏİ)w,4ÇÔƒU;s2D~3> 7.™ò‘è¬Cz¯%”®g¥§7òzzAïª½)†U+=j|±ë“bØÒ±Z_,Ãê´h½1LÎó®wLErØNk”‡š´†µ%!Sò*ë°²hâzPzµ.ÓÜœzSb¾[O« |ìÄ¡‡¤Øú,Ìw0µ¬åfÎwjé¤tÒ‚ùI^ÚX³o"ÙUÜ”‡qš7ÓFnqâĞæü–#–^N´cº%-m¡6Kƒiqè)¾%‹ÇÅ¡[g*µ0kLÚŠ¿UÚBÚ†)‡¶åâĞvx;qh{íËI¤•NìèÅ¡‰Û÷ÎZE«…û¶n$ùåeÍ¾«¶-/ÿ¶sÔn¬9%İÎ9jÑ{Nª¬È×5ÖêÍî, yh¾)í©L’š[Oã@íŸ¡ÍÌáîT‘V¶.g”vÑš‚ÚÉ®¾é½y]C^´ˆSº
0I‹\‚¸“£F’Á ÜbÅH b ÆY‡ëÍº±kWÒN‰*j1ºİ^wS!\ÿöbâA(™Ó‡€G8´¡ÜÛäYoñyS c)Zî$pİhWÈ:R4yÌÒ¤3ƒ&wdĞ¤¢²ko«m4]–&{;šLÖº-MM¶nCI,BÀP”8Üïƒ¨ªØĞ“f	%š®¸ËÖ@4gpœg†zÄĞO4<¬'ß—³wš‹~§ÍîÃ1÷Ó®S}¾o ¶¦âÆ&¥]èmT(¼;°¸^§A®-ò$Ê¹NÓŠ‚U}=%	]ÉôDI R²OhØ/Ï}<%‘×SRHJš%èÁ%·”Ê ä”l¯¯­o«¨«1S,%§:JNÓ¦[J¶‚’›ºË7îËó&J¸ÓÁ«w<q½ÑÔâŞM² o…lq`´x¹#âÚ¨f˜*{ŠĞì¦QAwqÆNPÁïÀÊï€WİH°â“2¼êĞò<ÀÃŠ¼VÁ‰^u1X¹Ğ¤_}°/vWr¡}B:vˆ/-´‡jÑÃ¤hBßÁØrEs8ËDëì=n=Bòs-iGJÂÈ‘ib}Ñšù¤ôëh¦¹¥öŞÄR{ŒÖ~¬2Œ[jŸ’bÇ±X°ÔÏÔ²–û8÷Ÿ ¥O”ÒMH–Z$ù¥ö$Í~²d×¥öş.µ§j#÷»¥ö4şN/µOK/O· c²»?½Ô¡)¦—Úg¤øY,_j˜éR{6³Æ–Úsø[—Úsñ'–Úó˜‚¥ö|¾±Ô^€·[j/Ô¾\”DúYéÄÅép©½D‘xp_ªU\fá~0„I~©½\³_¡-FKísv2¸’5§–Ú‡âÛaĞI¸€¸²¢±±Ê\ÅüXi¯æ›+í5ZÿµRs+o†ã8‡ıì`VMhíá‹½K1õ¹ÀãŒ„E§}¿-BïPO7ƒˆ2Œ¦èŠ*{ €½šîì­“lån;ŠÄ²’ijŒ¹Ô_n®ã—$V`bS2×3}¸0…Ì(…k§äy“`"+0ò¦°Çs³eZ·ß¢PŞš"Õó–T·eêáTm…ŠŠ|CeÁÜnIu‡#ÕZÿ]–T×XRYsŠä¦$½<º(§6P|tVa-ÈlŒfò…3±l%ÁÔÅ c²:Ù;‰m@K¿)G;Ö‚:Æ²
Ã‡;/‡Éµp0\nîEdJæ‘BBİ+$ºO÷{B!¯'” B="Ôƒ
äC)B½`	õp¡		UÑVÑVlh,šG,¡u„ú·Öÿ˜%T/	…àŸî¨=­†}Ós)k˜Ç¨ÙnqŸÊqè%q“›‰±;$ü“„yÃ©«2ªyz‚£õBßPğ.7XóãJæ‰‘°Æw†X?)(?%Ï§=ÖÈë±ğ€õ31¬¹ê>«X<ç‹=š\u_”=ï‹E«îZôE)*«®èá°½…® İ¼Ä"Ñ¢û˜[tÿ#Ù¹è¾¬å_‘¿èş‹Ê=œçUz§ïWYU´p¾$=zin½}<ZoyzñºVü†T¬Kà›üÛ^ ò±•ãÓe`pİpiËêæ-VVÖò„[
ßæïôRøi÷‹f'âK!M^ŞÕ†ßSÆuıËRî}–ú´á'¹ò|¨¥?’ÒMHz$ù…şcÍşIì+?µ_™:bøLyÊ}İçY_÷ŠôòÿuO¥ú/µÁÿJƒé…şU)ş?/ôOÏt¡ÿŠYcı×ü­ı7øı·LÁBÿßXè¿ÇÛ-ô?h_~L"ıštâ'‡t¸Ğÿ¬H<C¸Ñ*~µp?Â$¿Ğÿ¦Ù×£…şu;)ıÁšSı³œ”ÌÄ‰Iˆ¯›¯ÇM2;Öù¿øæ:ÿ·VÿTßÜÚ‰RÖ¨‘6`Tã.§E¥OS‹ÊÛl¨Ùã­rºÆc©. ö$­A$ÒP±W®V%¯/¢ûWq¶e´îÄ=Ë²é%š_U2³2}¸%ÎF³¡¼İä9v‰FŞj˜æd±[Šş…ß@a.)æ³¿aA›ÙS ?€\_•¯*ÔWÔ›y˜ ÏË7AO«Ÿ_ªoneŒ~ŒvĞŠå‰5LÇOoµc VnÔ\Ë}8.B÷|JÀÍÈA„w%Hì	.;×¡ºÿ¦ZSÒÊ× v]íSŒ’#ÀUl­lÈ2ª:"Sz³@@Fâ†ƒ•‘ÈC2–	’çÂŒÈ›¢È¸HŒŒœÙUœ“bI/áö¾¾A-ÎÒÑlù¦ôy	¦¹ÙıùÄnjI­|)å7É¾%Å–f±`’]†©e-/pÔ/«¥—“ÒMH&Y$ùQ¿¼f_!Åo[†\1ƒ!_²±¡XU¨i¯0£,C®är´V¿²eÈ˜d0^„çÂŒVQ“ltXxÖA„M\QÁ#â¨Lp ÓÙeú¦ÓÛÒúè@Y¯)#¦vè¦ØIãÃ¡^zÆ¡%FC·ZZßx:‰ÎÒŒ`6á;tj…MtåN?TYcİ("ïLÌ¾„ß¡¢É¢xÉ¨GÚ{Ø(	hGnË%8zÄ1÷<b‰†B–íhÃ­F8ú`zØW@^¥´J0&Hº’Yu¤1*†cb5cä9Ö	äõcBXcbõØ˜  µ†’zM_ì¥¤ õtlœ/	Zãµh¹A‹2•|µY‹"1ëe'fUHfÆJ-]•Œ³£Š|‡?>¨NŒÂw¥35ñQøJbÖj­uÉQø«Ï…:
_å(lÔÒMv¾B$yQgmÍ¾dWn]şê4ÖÓF^s¢ÎşNrïK/×·HC{--êl n(¦E¤øF,u^Ÿ©¨³1³ÆDMø[EMñ'DÍ˜Qgs¾!êLÄÛ‰:[h_š“H(ØÒ!Š:-ŠÄ„{+­bk÷!ÜHò“Ş6š}[m1u>²“Şv¬9µ
¿ÉI&õÊ•“ÚÚkëëpt°=3cŞo®Á;jå;IåÍ­¯Ø]2ïqóÕ~ª*¡G FSËèm ÑìÇ ÇººzöPn¡›—DşWLİC0-¨©ÿ=~÷#\¬º8·Š=«­ÖV‚Y–5Ò¨:Ú1;Õ6}"¥Ñ>Ñ¸{0ÕX3X4ÁKhíI««5×]nvæ'°dZ™>œT,Ã©g”Â‰<wìDñ¼)aêÙİr¶S|ì¡ï™¢çÇ–“2èùVŠÕu…†Z³—¥gÎÑ³M+Ï[z>HÁû4m ü”ñF›&ºâÂÿ¬&éâü
PÀL“qYùxP-ë\L<‹®2Òµ¹`-#š/†íC”	Æ¹‘å¢Jæp?jõ<Û6¤–ÍŒü™XœrpÆö¼X•Lq$Ò¶tíB´yvzÒ!¯'Ğ¤ëJ‘noEwrŠtŸXÒugîíéòí5ùšš\é±¤ëu¤ëÓÊû-é¦€t[b	g`?¹NY®BÉƒÓG{¾ÆÅ`:7ë4G ß”.ŞŞ‚EQy¤ÄèU¸µG-n´ÆYBGÙ' œ_—­‘ ÇÇf¸l	Ôƒòò€#¯\¤ËV
ğ©ŠÉ´àŸZÀ§g şN
ğ:èr‹uùJ³¯|?øşZùø´À$¶Ş.P›
“
\‡B¬W† ¥c¸++wc+Û5¸uõ²>ïÈbÃr@–²áÜÇĞ€U÷sĞÆ
jñÿ øˆHí2sÆC	Zó[«K†¡~WOmÈ)rãÌ­­Ç‡Ò‰YÙzöF#OÇ"àª|±ßAıX7xçğ#şbË
—²€IH¸”Ä$ P†K™°ÇÁò<Ä3	òz&ªÓ¥,Æ$”åS:î‹½›”å>“á‹E²\I‹)EE–ãÒÍU³;#LK¹~sËE"İûN¤;ZÊP¤;F+9VüşŠÑãà/Ü•o+Â*»¯'ÚaÇ
£­ÒçÒ¹ã™ævX$ÌíNĞêOtÕ[s»5·Ë‰šÆÿ”±4·3'±®ºVŠ”ıÕÕædş,kù¢Ç)Z×©RWÒì~+'6z§%:ö…tìôxÇ?fbx†Vv¦ë;‚0"Üòô´²—•¹şÊÖ9ñÇ&òAéÛY±¾UV›³µo±oçhuçÚ¾}”ìÛy‰¾})};?Ş7ä·}£îï­ìB©,Âú¿Rì"¶¥kW>fW.ÑÒ—Ú®|JhHòñešırÉ®ñü;ˆ¯ÔF>qñUüˆÿ'½¼šÿÄKk@vŠ+tA‚ˆ×hƒ×Jƒiø+)~‹ÇâOg*_Ï¬1øşVøFü	ø&¦@ ¾™oÄ·àíâ[µ/·%‘şZ:q»C:ˆïP$>#ÜwjwY¸?áF’ˆïÖì÷h‹‘@ü]îeÍ)øs.
¸Ã=9´'+mÅÚ\…¹e ßÏ7åâ´¥æÖçhR‹ÉØáSüY­”‘“#;Ôİá…ÿÄYÏì"Ç¿È+[<€U™#§ôŠ‚€À~À;YÓdqÄ@41‘Ÿ{è(‚—%1¶ƒ·ãİDZQnâ§&bX23}8X†ó÷#(5Ã<*Ïh"#oŠ@˜¿³œíâÇë'RôüÖÒóÉz~‘MÏšºÚºÆb¾Ö<eéù´£ç3ÚÆ³–‡è>Ç^O®¾í‘ˆ–zö1v¹ØLŠ§—H(1°”ëbë½ç¹Š\ì­µ„ª\¡ošR5"hä£g¹y. ?ç;#Ñ ßÒàAÿEy¾äi€¼*hğŸ^V|^IÑà;KƒW3hğe6àqy«`^³4xİÑàmãMKƒıAƒ(2F .wÀÍ6:®qƒä±yÊuw8YÆgÜeÙbèìš@¨l‹¸<ns8”@pÊ„ôÒ‹$¹Ä¾Ü¼ ÏÏ-™·GB_¢ÿàş®<ßóè#¯G_àúïÇĞ§ó"ó¡/öß¤ó½tì#_,’`>Ö¢ŸHÑ„6
À}Ê‘èò•]>“Ì]>×Ò_H‚]æi`L\ä®Ïk†¿dmÑZúƒté¿LsrË×‰%øZ÷WÊRN3ü£ûšÅ‚%ø¦–µ|Ã5á[-ı”nBZ F’_‚¿×ì?Hv]‚äßáü“6ò­[‚æïôü“ôò‹7&²oÓKğ¯ÚàoÒ`z	şYŠÿÎâñ%ø»™.Á0kl	ş“¿u	şb	ş›)X‚ÿáKğ,Ëù%xVü¾Ì†Wé_¤³#Q—à9øOe-ßî9µŠIMHàF’_‚çÒìsk‹Ñü«.æaÍ©%ø‡ø¾¬37©º¡ˆà™5f^fÆÚ;ß\{ç×ÊÊ›Eµ9æĞé£¶Âl¶­ddŞÄâÅ¦K¦ŒéÃ-^èE8tB)«ÈsiU/äM}†î¢lÁ
šº‹ig÷Å~Lİß¤cKøbÑĞ]R‹.%Eeè.h%”®Ò€=vöfiŒ†ğÏn/#…8„—ÕZ–“„¤Q:"ãn–ÉÓ£Çò¬,Š¿KÏV`šÁ¿$FğŠZõ¨$_ı!ÅVr|E©?
=ZYêW²ÔÊZzËR¿†,…$?‚WÕì«IvÁcøw8‚Çj#¿¹¼:§GğŸÒË5,ì æoé¼¦68NLà¿¤øxàßg:‚Ë™56‚×âoÁø#¸’)ÁU|cWãí„èíKmé¿¥uép×+î­¢ÑÂıG7’ünÒìkk‹ÑşÇàuXsjÿÉŒÛéDˆö,:©ª¢¡¦®nòë²Fòz|s$OĞFÖ—Fš[Oá	ovŒÒòòrSÅNÕÉØÓBEB½ƒèŠÂÅ%š±	dŸi]˜LÊC	L gtj¢ö¹Ş!ÆA­„‘:L¼4²GŸúBktDÇÙ€ıMÌ&„¡d6dúp³		g“Pj†ÙX›È—Ël‚¼)˜1›ljùÓ‰Â›)`›§¨2ËBÖ43¨ò×L¨RY,ÔµÕ5Ô˜-,UšU¶ÔFZ,U½Wt5W¤Ìà™"Ñdà8Ñzt®Í_©­;b—HÈZP<Ï`§g…ˆªÂÜ¸˜‡¾Ä©IÊGmXYLT_6fâQKEÑ¼é5Q"ÛbrøI’'ZX;b”ø=l©>±{pÀ“ğ‹ªàs4DÃ7ÔÛß=Ô¡·Ò™Aã1ŠM7\İ‹Cİ8íÔ/d8ƒ~ësg9Íï½|UŞmİ6q¿VtÅ¶„€TSÛV<ÚïËòQkm2ô!C¤¹€É7ˆ47ƒ…2"Í	o+Ïí<#¯gcáKFš‹±1×¤”Ãv”b¡-Y£÷ß‰%£iVéïÎLs+Òß‰©U+ŞEÇ‡“)g“b»²X SîÆÔ²–8Eî®¥÷ÒMH„$ù)rOÍ>)5g·ƒq¯ŒÁ8ËÙSd]¾½½­±²Îäì`lsƒ1¯ì`<SäÖ~Şªä¾8èYó#5:ìK9câàŞZ‹/‰İî8Üq²ÛqÌ‹H¿˜_ajJ=´º9Û“}†?¥FÚ†¬aU¼>¯Ü®" ˆ7W‹«:„Ÿ:åÙå¹
y=W	Ààª½c\EŸÉ
UwŠsXzôdĞcÖ™Ñ£±ª"_•«6½–}ıÚÈ>–÷Šå—~ĞEƒîS©	ªİ
Ğ$ú*yb/Ü;d®è,"æ¬5¶º~œÙĞXÌZºZ«c†wÃyör±±³A´ª%¦81ñp9ôÔ@,H0#ç b0ùˆWÉŒD>@’oP7$Ï)|ÈëÉ'ô ù¦¦È7M‘"ßœ–|ûfo¶™Ï]İnö³äÛŸojFgh#H#i¡Má€‚yã¡ÙĞJ:4ÛAÌÍv0 ¼Â7„·Cñ‡f;L 9\Gx`PµF¾À”bÀp¶<Rû|”Ùİåhæ¾É7Ã47eÎ>G\~¬Ö~œÂî¦Ì¹¤Øñ,L™'0µ¬e90e¨¥O’ÒMH¦L$ù)ódÍ~JŠÆs[ŸšAã9gBcx;B¦¬È›Ó,Oç›RåÚÈ™ÒHs«±6XŠ£³m{4f-ù±<C Äì†¹T]ŞÕ©»^R}ÄÏÕ—¦PZİgíh V„+%¼$­3#„Æ³Ø„ĞÈ¯D0=¦'4âƒÃupÎ¹ò<ÏóòzşÁ?ç§øçÅãÂÿpcì /J0Ï<Òã‹ãÌó¯ˆy8å^¢U_š¢ç¼–—eĞs.Ò‘?Ò»7f'UšË-E¯à›£öJmæ*i&=jÙC˜7>jÑNzÔ^Ã<ñQ{-0j¯ã£öz¼ã£öÁûFyŞäQGÕuùVú¯ÄPç	Ó-Úç[7®æ“ÎŞÆ¼Á¸º©e-ss\İ¡¥ï”ÒMHÆ’ü¸ºK³ß¢Ãü–÷dĞa™Œ«BU}[e-”­÷Z*ÜÇ7ÇÕıÚÈÒHsë6Ø´ Šx'|sŒÖnã‹¦¢¬`¯Väñ&É@ql 2&dÁÎÇFwA¢í’oFğ¢q¡ë¦\_È«º=
p –˜0‘NmşxÓYì”dÀÂ¯çójÅâÖK »õ×•êUßğÖÄX¦‚YV_ZTÚí`l²|&Û¨’X‹—Ãv›İRÏ Ìv·/¶wup§B´w?H°³iX21}¸Yäg‡…s‘ç£‘×ó¯ğø÷ß1ş¥[ÆcJíÇ¥˜ê[àßá;O*ßÎ;ÇwÏ?wgÉ<Åßi}ËòOÛF°ß—üë-¹Ì=£>+úeÇÔƒSüà9V§¥Úç™æ–·ù3ÔZë‹©‘QfGÆK#cş‘f¨*ó;6^æ›3Ô+ÚÌ«ÒLz†bcpaŞø…vÒ3ÔëÌŸ¡Ş`f¨7ùÆõŞñêm¡í;ò|×SU{
Ë·‚ÂïÅ(Ìê}íó
›¡’Î~È¼Áõ‘RzÎPkéO¤tÒ‚
I~†úT³–¢ÃÂ–ŸgĞaÁ™ÌPùB>—ko¯3_X*|É7g¨ÿj#ÿ“Fš[gØEêzGm?lªj¨èñƒ_ï£2•éÆéµ›}Óİv(}‘ƒ½ÿA¥ÔQ3òİ´‡²R9âäYg¿lŸˆà…bÂB‹"‡Ê!­½ó„÷°nÌÉ­òeîïD	!…dú“H‹œ€«QØo5©ƒêı :ÀÔe7â°šî,+äÆb”8Ÿâï ¥»¯k PŒíÀ(·b@Å­ŒÜ.Ô°p9=ÒöGCÏĞĞ]£TcÂ-7_‘B‰i„Ç9Ó‡›ÖÀá´ö°û·òüÎ3=òz¦ÆÓczêãPùÑ+›£s¯­<ÿ/"ûÉ‹ôñ?kÑ_¤hÂo½Ÿg¿æW–‰TñËü6fó›äç”ú»Vğ‡$è”ú'ÿyœ¾¿tÀ-â¦Ö¿ù;=µ.*=şÇöSë"é©u–å¥áYñ’©•67]¸çÉÚµµò@Qáêa„ÄŞg6ä÷À,&ÍÌÎ47Õ.MµœÀçĞVæt­Ø›šãá¾¢“†%ª^\ª+^õb‰MÊÜZõ<Ru4U-!Åæe±`ªš©e-‹sªš_K/ ¥›LUHò'jö2É®dZˆ‡'k#K8ò,Âßiò,)½\”ÿ¤æ:KÄÉÃÅc1mpqi0½x,%Å—`ñøIÃ’\<¢¨,ô,¢'ö1fIf4,ÅßzÒ°4şÄIÃ2LÁ¢²,ßXT–ÃÛ4,¯}Y!‰ôÒÒ‰ÒáIÃ(Eb)Â½’V1ÚÂ½T7’<Ü+köUbp¯já^ß‹`3¸U_¡8v4YÁõ+Àr5moi‡ü˜,ä—‘^õÈ/Gû—Õµí5ôk£Seíª´&‹¦N9–áªÄ°š<å?©¶NlmUfóã€c<ß\Êµşµ¤şæÖOT{—ÒÏğÆ5\	¢Q  Ë3:ªU#eCk¶`•BÔËÉñTÒºf•áôæ‰]O4Ø7¤µ`n®>òj¥Î¾î(ˆ¹|çvèŸ8mû[J¤aøÒaıÜ
kèå«dÅ¾Qß´¤Ü‡f¬£#ŒLHLøÄ´d*™>Ü„xÃ	¿
¥f˜jyÖ–rd‚¼)šaÂ¯µävG&uJ‚ú‰—³$nÈ ñ²!‰+jÚsUõ¦Ñ’¸É‘xm­Kâ_ä‹w+Ó˜1”ô˜§¢½JÁ“Gg^\‹èq—e¦ôÑ¶×Bû#he£­P,>ŒÈ&ÓÒ+2Ï§º¢\kã¶fª8È?w‰ÆÔ%î¦]ƒ¼¦|dé'Nê¬yHDœ9¥½ò‹¨-3M0ëD'Ê%³ŞHDà!Ñ'¹×—çèÈë‰.TÑ7L}#%ÊÆ)¢/o‰¾IÑ—‰Ş^l¯­kk¨6›Z¢oæˆ¾¹Ö?Ñ§¸pÉ]ÌãiX !¼ŒäÉÅb¿¨{E¯Î }]ü©’› lckL%°İPïùî`åÄ‰×8+¥ÉÉ¼DMù”hEºh˜Gj³„Ô*?J;¼^”[fõı;*ñğÔŠp3¯àÈ—í4_ÔóEÄ”"‹Â—C‚JÆWËÍ3ı’i‰@ˆ¶6h‘çV×3ƒPÌ°uŠ¶Qbm›b†,3l—ÁË‡ÌPWY[ÑÕˆÙŞ2ÃvÔúw²ÌÀ /-Ëå^èqÂ	œİ‹±ØÑM=`¸Õ…WqÂó&œ
^ü¢D'™$2eTTßP%m[õ“JK5*µÁk§ÜŞ5ª	R¾O©ˆ|ŸF"`Êğ}"í*Ïİ<©×“J°§ïSŠT{(”{¦Hµ¢%Õ¤R­1YWåÚk+Ì^–T9Gª6­?oIõ ¨†ŞÈî´,Á¬¦È/Zd¯ŸT.Q/Lç:ûB­c+–uÀœ–§|p£±éı@wSWÿ1Ég¯HL;]àşPpÁıi$ê¹÷'¡[‡<;=õ×SOÈA÷§õöVt'§¨7ÊR¯;ƒz+†Ô«É56æk‹ğ€²ÔëuÔëÓúû-õúÕ\D­sVHuë"7Š“°W­ß³¶&lnáQã7ë?nç Ú3¯›İeÌğ}
ĞæçÁ÷i$´ñ¥¾O‚ó <‡<ÚÈëÑøèûC›;Ù©ŠÆ4_lTr'»’tlº/íd÷Õ¢ûIÑäN–ñÍş,ídG»ìÉÏ­ŞZÁ’àuuÜWJ„ÇhŸwkŠ6l£¥G3Ím!WNìóÑzUr*©•¥Øa,ìógjYË*Üx¡¥KRº	iÁ>I~ãq¤f?J²ë>ïhşîóÑFVu»cù;½Ï[Ezyœ…âéªé}ŞñÚà	Ò`zŸ·ª?‘Åãû¼ÕfºÏ;‰Ycû¼“ù[÷y§àOìóNe
öy§ñ}Şéx»}ŞÚ—3“H¯&8Ë!îóÎV$Æîs´Šs-ÜcB¸‘ä5€çiöóµÅh¯5ÆÎ°æÔ^klbv cMÊãÆJŞ¹r!óc¯ußÜk]¬õ_"õ7·^F—ŒÈ]Oã"îÜ#·âÃf
„kúEjüLÔ±Å+Ö!ÅÀ²¬—¦áöz3•†j8™Ãõ@AîË£³›ÜL¢¡B4èttbÒÈ·ãÂP7dĞÍig4N
/å$öJÄ¤d.cúp{%ÀN)—£"ÜÉóJÁBöJÈ›ÂSÊU–YÉTP]­^#ÅtD\Ë¿g® ºNùau72®çïôÈ+ŸsƒmY=­ ºQ¾Iá"‰›YO47¬.ußÂ47¥¬‘ĞJİªUßf««º.eŒ*“>ß:­Taÿ×Ÿëí˜hV%pT®néœv;[±s¸²åıö59îÔVî²caM7ÔqîîD—×.ßï2òÇœÓîÕÊîÓ‘âfÁ5¥Øı,Ì‚hWÆ±+jé‡lWÆ…ÃI~X>¬ÙÑÆ¢a9ÎËGYsjX‡e]¾¦­¢>WeşÍü–ñÍaù¸Öÿ„ÔßÜziÌÆÓ^Æ +¡Á°ÒğGzÒEJ)šCK¢äáÀ]İ¥hò„-N<xÀÚŞä…;iädX¹Hü¥i“„Z‡bA/:òªÊÍ“ü€Ä¨$$8İbúp£è„£òi”ša‘ç³…ŒJäMAQùœ(•\lŸW_ÈÁùı‹	N/=~)Îiå§ıŠªÿ£U¿,Uÿ‘‡»»^a´¬%£6âÇr©üÕXgy¨ôšÖøz’w×’¼odòî›Ê»äİ·´ôÛ–w+BŞE’_ÁßÑìïJv¯Şãß˜¯ãôÍĞ`qlˆÆÆE=J±ºy_›«t3Öü±*¤¿ÚoÃ·W¦5‡iÓëwFÃ¦Ò›OX45lª2V³ºb¡¦²²İ|Êü6ŸñÍaó¹Öÿ…ÔßÜÚ ×?…sâé§Ç?Îš+y¨ß¥ØËšxÑ Œ¤Å [t¬]¸®ÉtaÙ+Ÿ­ñ l÷imË\4?…˜.SXĞú¡]°÷‘ûÚèˆewFveÅ(ãh’-®è?d×S"=Îw‡S´ñõA3ıbm\SD¬ä$6#6µ¼ÌB®sûf~Z¾¯Ÿzí	öHEÙb©,NµÌ—51”I&8'1}¸¡Š…Cù2ˆ¿’ç×BÊÈ›båob£ƒCù[¥êwRl8¹ù{Œ†Z•t÷¦¹E®:±bü¨õş”uÕRìçÌQ÷‹ƒº_µôovÔÕ„£I~Åø]³ÿ‘bıËúf°~mÈúÅÆ\eu\ßÿ²¬ÿ·cı´şYVPÖoëoŒëîôbŠW=ıİÅ°³ß)‡–U®£yÃí‘ÈĞö0”›=›ÑFÔEm=°ÏîB…8]Õ¢²1°b;PÃI5Î6¡’ójåGÆ®B@|2¨bpw¤`ïÕFåò¤œØÊ›¢õ›Qöh EÅ‹‘÷åê3r¹|†¥HíŒÎ½İä†
Cİ×±DD;¹¡Y¯ÖÃù¯l‡eÌ0PXŸ‹ÑyTcø0¼Çô1BgÜÉAB‚–ÌlLn€¶á ™¥PPs
!e ¯$Â0$ÿb±°‚sá7è?·óÙk-ÍÃì©©µ.ä¯\m[}c}{­™—ùé?Æ·øiıXş¢}àÖşnkÑˆJhjN#‚‚ìÎˆZ¸D¬$ÜàtÂÅT½ñ/™EéÀ¥ä¸†"h€ÊÍ‚Şü@¸¨„7¾5ÃEM^X‹x¼‘7 ]Ôbx‹‹šâ±¸/VŸT$ÔIÇ–ğÅ¼‹š]JŠŠ"a>{2¶·zÖ˜¥Y*R%4:UÂ2R‚Ã²ZÅrJm'ìÖK“Ë³p ì®ÀÔ²–&N]+jéQRº	iÁ–I^`XI³–ì*0¬Ì¿!0ÔSwaŠ“x¬±²cÔº¶½ıÓË{`Ÿ/ï(Nâİ öXš:ô»×#ÿ4fu³Šöhm'S¬Êßi™¢A>i5‹"ÃÚq™‚Û¯1Ú»±±Ş­n{·R¬wm=“h6ÒªXîÌÚu\?ÖÌêG£ôcœïÇ:é~Œ×~”Çú±–í‡ˆU¸œ¨…_>¶¾ÜXì×ÅÅxÚôº®éÊ¬¦›¤é*ßôºé¦«µéšXÓµ¶iÚlCo ±5«›:mn=×\}VskKs¾¹õÒ™Fm®IšKkdÖ‘âk³x\#3a¦™u˜5¦‘Y—¿U#³ş„FfS ‘YŸohd6ÀÛid6Ô¾l$}‰ÂºÒ‰™?ÛKwEb}†MµŠÍ¤Š&¤£I:(l®Ù'Jöä®;'×ˆø Î[°™¨WëI¯š™æ’É–ZuKòc&H±­ÜÇ$\C·ÖïØß±–ŞÖ~Ç†áw Éêí4ûö1¦Ù!`šÊÕÍÚÄFivÊbšõ¥;{¦Ù(Í£­ÚÜ.±ævµÍ­BÅ,¡Ãc4”Ğœö^ò2”M/]½ë¢+»iW6v]Ù=«+HWöğ]Ù8İ•=µ+“b]Ù+ëËsÚÜ&®¹¶¬æ6”æò¾¹MÒÍ´¹b¬¹vÛÜRIS«`i«km~S×|gVóIó]¾ùMÓ{®½µùÉÊTÑkc+t³hJ0ØŒ‚'-NëvMš„‹#óõ9\ßÃzù¦hĞ§-ôKÍ­cQ§8Iß¸Ò §9PBë‡0‚0oËáRlÌp2ÀJ»v'LJ‚xV˜¦lwdçö[q¶Øa«Î)¡«5ÈŠ£yN‘^‰…¼©ï§C…Îió¦éÇLQkß,æØO©³¹£ÎşYÔÙD¾e†§Îæiæ8@›;0ÖÜA¶¹™nÆÖ¦'º¦ÉjzSiúPßôÄ4c¦MbŒÍ,c‘Á[d1F}eu¾¶q§J–1tŒq”¶p´eŒ•16¼R¡ùÅÅ‡£ZrÓº|_^åCá—+KxêœÓ(Rœ¿0Fnt‡a#ôj´_5×ĞL]Ø'P]MKÑqÉ¼íÔ™§ø¼ö Ü0 (™c#ÄNj–®ó€EÈyÇ	Ï/Ï<ç!¯ç<œwbŒóhVu’¢urŠ›[zœ’Aæ,zÔæjªÛkÍ©–§9zœ®-œaé±'ÏÜañ¤wŠ5všˆAÊË
°¥¢ı*èAõ½ªè8Py€Ã“Ró`ßÍ·µ»Pd¹93@—ŸƒÃ’‘ĞÅ—…è-¸#Ïs=ºÈëÑ¸€îy)tÏ×o¿ …îD‹î…èn™…n[±-_ÕŞXi.²è^ìĞ½D[¸Ô¢[t5Â”\õM`xj*Ìón$ªØÙb;J/rsY€»X2—„z"v…`u¥<¯òˆ!¯GL  bW§»F¿çÚb[XÄ®Ë@¬%±BCuU±ÿ\o»Á!v£¶p“El_ .Ø8¸!ÌÑ,æ5É{sÔëí0`zmƒÉ3¬”ÓÕuÓ}ÄÎ…ÑoLa¿+ì®ñ¨4ÂÌ¹ËÍÍòüT“DÈ»¥èV¦K>>$Àmıíò¼Ã y=QàÎîRxîN Ùàl•E€ºöêBMC}­¹×à>G€ûµ…,ø}˜ Íƒlş4#ñ šÏğ§‘Dz×C ßDšâO£|\ŠYş:m®_İ<É’e-[Gş4üŞMn)Ÿñ´m"ÁÖéEñmğÙæ-óç20ß&sQ¬k«j/64˜ç-æ/ğM»åµ…—¤…ôî‰í”Ì˜7îô‚&ÒN//3OÜéå&`—ô*ßØ%½†wÜéåu!Àò|Ó“U{2Èg‚oÅÈ@uÃÛÚçw§nØJ:û.óê†÷”Ûrcò¾–ş@J7!-Ø`!ÉkJ?Ôì¥H°µ%ÁÇ$Ø.“í+jªŠmµuæK‚Où¦Àú™¶ğ¹´ĞÜzØŞÅÌÀl,Çeg#ˆ6Á€*ö¦bÁ‹DÍ÷pó7|Óè† ¯,ò¹ñ{U¥ÖD©1ˆÍÆ`:¦™ˆ¬µ¡Ú/ÉjKÒ2ŒRÍìyBJ&%ó%Ó#5c†`Âù_áÿÉó+Ï	Èë9AĞ'|ã
)ß(tß¦ˆ³%ÎwÄÙ>‹8ù|UMMu¾Í|o‰óƒ#ÎÚÂO–8OPw¢‚éD} LÔy²!%Ã ş‰AX:ƒ[ ¼I®*ë–>\7#D{Ög[«oÆîš¥şÉªAo‡úÑ;ñ6Á=¸µšgŞg/ÔëÑ]]78µÈÑ*µbbı9 #CL´‘èC:ş*üM¿{:"¯§£tü#EÇ?å¿RtÜÖÒñï:îEÇ\®¦¡¡P¨6ÿX:Î²¢d³â´0^d×ó[GÂêj¤ıíœª\L›irµªjúûMnªÃî\Ûtiâè‹*ÿnâµ¡chÃéŠ•ŞrËä{­Ç^
„‹]å€‡!â
9{¡&é5À>C¤ÏÎOIŒ:ÂS2s0}¸Q¤BjÍ‰Rˆ'Ï¹Ù”"¯§–ÀjÍÍbÊıyËy¥˜Ï¾¥Ö|ÌÚÃï˜¹*UT´×´*Íü,=üZje–ZgYOEo"CÊ‹W›?œô§1ÎW”Ia{Nl*ß:¼%Œ‰ëT<Ô+~Âr­ĞäéœeÅÀ”VBB©$’úÌBaˆDÉ,œ Lo(¢”0‹I•çb0È›B„Y<E˜%¶%S„ÙŞf©Âì”I˜Ú¶ÆÆÚŠ6³´%Ì20ËjËYÂ¼Ê=¯Šš=N+Vä:'ÊF¸€“yë·MjÁ§ØN—¢é¢]´¬6ñYÑ:ó$f:£?!²Šl˜Õ§N/ÜFËzÄb</¶Vë6d]0y£ ‹¹"®îf(ëx®Ás»z1ïöèu=¥~á#ˆäåfù€ª„±ôFn@4¤êŠBÏQò\ÉSy=U…L êèUWVÌWIQuKÕU3¨º3©êb!;•Y,:Ãj–®cø¦8VÛX]ÚH‹l	qö˜7.¢‘´¸&óÄÅÀqL€8oˆåxÇÅÀµ‘
yVz\PµÇE>¸TÅp¡X­}®Q\œ¸£t¶–y1°©e-­ëµtƒ”nBZ "ÉëÙ5{“d‡—ÌÑ·ŠâIíğé¤‘Ö6à±<W4“lš­Í¦£Nî$\‡iN÷¾KÂâm]mn=×œõÃ”[ˆ†xpYçNHT¼³T¼~¼â]Jı´â“ µJ±2AÛXAÛ m¢¥7µ í‚†$/;o¦Ù7×Æ"eï.–s'²æÔB±{¦©¾²€ØZy³K`¡hæ›²ó–ÚB‹´ĞÜÊùh"¦ƒÇ9'Ò¶åxQÎ9?réò“#mwöõC´†,`ä,ë“s"‡º6ân"ÃnñV]š
\ßŸNdÅ)RmØ6Ôï“W]ÁXy4@•5’È~ükİªÊ¦ÊŠrxÌğ“Ë?aDä7¦GËÆ*D3"¿ÉˆÛVÛ	x²ü#oŠLwÛ³…Øò¿ƒb¾cŠª»Zªî”AÕ=²¨Z¬ÈÕäÚŠfgKÕVGÕ]´…]-UgÎs¢„_)(V$¸—,‡Õïâ»•ëèƒ×Á,ògôˆR
sÆ•C*üM…ç\['ş­hõâ¾Ê{ #Bx¡9½†¿cÙOõã	ˆâ‰ ª"Ş°$ˆ5>‹dƒ}œW~<È¡ôÙìĞŸ€—Ìî#ÑØ‡ôßC(¿§<'yú#¯§¿ôß+EÿœR§-Eÿİ,ıóôß3“şÕ5¹†ºš‚)XúıÛµ…Kÿ<f?Æ€ wc(|y&ÀJõpÖ‰ë:ˆŠ•İÅº‘»jÃ­vÓÅa’6C`nèàáJP1 ‘-uŒ:Î²¾VÍCTÂD]İ]´&Wu+‡9Y*6šg%x2>;°áv\A
‰›“|ú”ï\û  ê·ù»wÂDB†ôèzoŞ
gE8#2ê. 6.@ªº£ñC-ŠÄ†{¶dûŸĞBoòÏOTÌN†¦L¼À=œ ­-¯mËäùoœÉdt°[±ë‚Áà¬›dƒ…ñÀ›¡3…¡ ¿X›ˆ»ú W^é˜L“]+ xl‡­&D¶X´“’ §¿|(¹£ì‡;ƒ!FÆyæHCì±½epM–g·bÈë‡˜Œ±ÔëÕĞ—b»Û!ÖŸ1Ä&+òU™}ì 3|SäĞ6¥´ÈÇ–Jfˆyã"I‹|S˜'.òMeD¾i|Cä›w\äÛWÙOû{\PµÇE>¸ÌˆáB‘ï íóŠ‹ùöÎÄ¼Èw0SËZö¢ôrˆ–>TJ7!-ùä¥—Ã4ûá)"ìi‰pDr™š¿ÆŠÚ¶öú
S²$8’oJ/GiGKÍ­`KÎ
‘:‰ë LÏäNÎÎ„¶Œ—¾Éº’Ò>ÅC°õVÖ‘™—Ş,ßz´'zâ\Æºşæ‘ ƒ3´¨rV“”x~Çvë6ƒƒ:âÈmsPkˆ‡»º6;ÉŒóZ¶Ç‹6D±i'ÓŠ¦jˆF¸‹j·a¾+”âáv›**fğû"5'gôø¨UIÔj‘ÍÒëM\X«@eèQ$ÇÅ…¾XÈ3ı
J‚œ\Gå°DAÃsù"!â‘×pøËôáD<°]Æá¯Œ°ãåy‚gÈëÇ™ğ2cãL•1ON±ş$Ëú§d°~[ë×TÕ5´Õ+Ì©–õOs¬º¶p†eıûDp70	–vBWù{ª.wª q×ñ"Új_?´›â›/Q«­©]Ò¼ 
Édùİ
xFVx[¹øbõ²e¤ÂYªS¬Tqˆ*ŞI¹©Æ*‘™ÏˆG´p¶<ñ \ÆÙ²íyë‰‡¼xB-§ˆw¾B{AŠx{Yâ]˜A¼|æ¼UY[ÙXQ(˜‹,ñ.vÄ»D[¸Ô¯^äó¤¬¤—ÉxåN2Å*µçö³@;–vª_œ·ûD^!­d¦‘#%¨NrWé€Ã°S™9	MÑ:èAXrÂ¿ê)‡Xù;.r¸í;¬âÃß~Ş’'Á
)ÉMç6R®ÍÙH-à	«wŠ„µ^ŠP,#Q5¶=Œ¡†Bn{£¹ğ4Ø¶!pÀ>Û€dìÂ0WÊó*Ï6ÈëÙFø€ì1¶¡%á5JÔk¥X2v_üÖâëX,ZzsÒÙë™æ…Dì¾´ÖSÌØf™ñ¦f,+ÉT››-;ŞÂ7%™[µÛ¤´$Ã–pKóÆ%4’–dî`¸$s' ÉÜÅ7$™»ñK2÷Î÷Êó>6ªöhË‡íûchS’y@ûü ââ$™¼tö!æ$™‡™ZÖÒNIæ-ı¨”nBZ É ÉK2ÿÖì¥ˆP°Dx<ƒ™¶Õµ…ö|…yÂ’àI¾)É<¥-<--4·¾Èé|Ïš¨³µGö¢Kİ+qD@)‚i£KŒôíîŞYö°Œ`Ütso]­ÅY”`ã¸‘ËÚe°cwJåÎaIà~1µóçÂÜC¬şNÌ VØök? †	’í¡{şQEŒ_lèÌ3üÚÄúLKæY¦·>Ìp¬>'|ó¼<_ğÜƒ¼{„BàcÜÃ±ú’Âı)ß¯ô6¿/³dÄ_Eéï+LsÃµ3¡|U+~-É–íRìõL¶|CÙ²‹lù¦–~Ë²eWÈ–Hòlù¶f'Å––-ßÍ`Ë½3¥Œúêb¡²²Ö¼gÙò}Ç–hZ¶<N*]'$r"¯@†k*ö€nı’…‚€¬(˜Ñ!G1)C×1#Hº¥‹È+@É³=*8©Ú-3îÀ#R*rY‚YD7È‹â;AøåŒ—¸³S°	kªZˆÏ:TNP=X??ñ( ƒP$Í¸£ñ¹e’^Q¥ÑøÈÊZl—+k;İŠ½l¤Â²Vk4R¤xS“ÑJØn=3»!g|)Ënë»ûpï0‘íãÀcé£`H‘ú%óñHC
Œ©Od0}*ÏÏüB^?¤„»0¤>)Š¼_(«|™bÆNËŒÿÍ`ÆÉÃ.T5æ–¿â›Õ×ÚÆ7ÒFz¡bK%ó-óÆ*4’^¨¾cøBõ=°PıÀ7ªñ/T?	"?Ëóªö¸È‡—_c¸pªùMûü»óSÍ¼b]]ó>VÈ,M7]òI2ÍM7İ‰éæ/­üoİ­‚{K±X,Xg%ÓM§›Yñ7JÏ†WÁpºA’Ÿnf×ìsHvÿá“-…çdÍ©ÓˆŞL›Ë\e{E¡­Ñü‹%p1ß\çÖæ‘š[ï ±§à1Å¢zÆ®{¦‘ £´ÒòÕ*ãâûÜá€D9rŠek±á,à.b«X§²µÁ<'Ş+¹ãäŠfƒJEÉÄ‰X=İ°—›yùM‰µ8•Ì|Ln­dáÀœ¥à­'Ï9n@ŞÀ€el!vñB
êÂRÌ3 ãšØ«X{93VF'b‹°‚ˆ™º¥Û‹2Íñ`_‚ÓúW¶p<Ø#Å–`±€—Tì'.¥¥—¶<Øò ’<.£Ù—Mñ`¯åÁå2xpŸLC—†|ECUMµYŞòà
WÔFY LP§Ø#,=äf\%ìg'kô¹!K–Ú®¨ÚU}ÓI]ÍÄŠ(PKƒH²çû=p„qZfZõ2¾:LF±4+üÃo,™Ñ#ñ>7äŸ•…sV‘çª×ó`şY-Å?c±)şÉ¾ÿrõïôI—×ˆóIğÎšZ÷¸$ïôK±ñ™¼S®¼3@ŞYKKWXŞyIw*5{UŠwö±¼SÁ;ƒ™óW¾²áN+LåZÇ;uÚB½å„wä("7ĞÍğ‡`HªañÆ„Ô¡ôr
‚Í†¨ñ%š¯	sg.8qA½2T‡ªÍ«„®B¸˜@GGf¸ŞĞÇN‹Ÿá`íÉ™ü¤MøDF=îL§|$™H¤r†ÛŒ…=JšaXThÒ RUdobŞ%Æ%Ó8ïîw›„k×–ç:w‘×ó®Ğ¼»nŒw)”¬§™"¹±$_?ƒäC™=5…š|nX’oèH¾‘¶°±%9ï¦²&¥U•Uz–J¼ä6¬(6¥ª@”2Ş|”ÿˆ"hÙ#Ñ\DwÃp±CNLÚ`ÎZlg8Eñ«i/B§jAQL!‰šMbğëKfÓ‘ˆ Bbl&dØ\=1×CĞ1¶ˆƒ’P³Bµ¥áÎ–“éñVLskĞ”Ä<²µV½ÒÙ­AƒRl[Ö í˜ZÖ2•óÈöZz)İ„´@€$?ì¨ÙwJ1Õeª3˜jZæT×XY_]ÛhZ-Síâ˜jWma7ËT¿©¸ñvvº+¢[¥ÔéÆ›Fµö¤5Ò¹ÃJ™ZwD
ƒ¦€–³>JiÊ‰Êß¦¥—vÄïÔš,Ñ˜es¥‡µ´Ê ã_O×4ğiï´(ºŠ{"gŠ´LóWşÑàÑ:7Êµ?r•µ-œŠbEk0 18I@·T–›İ&Òğ	‰zÈÀ{
ëN’ç^‘×3°Pœ‹10g“6%K>Eø)–ğ…ÂOv‹S„Tnç›[œm£SÚHoqØS™7¾ÅA#é-ÎŞÌßâLf¶8İ|c‹Óƒw|‹Ó+ˆôÉ³ßã‚ª=.ò¡ÀeŸ.ÔÅíó€ââFßTéì ó£oˆ©e-ûrôMÑÒS¥tÒ‚Ñ‡$ïè<M³O—ìêC²/ÿïdÙOÙ/òéäï´É4éåûE©÷KÇe;@<PLêu¡¥ğQYEôñÓ¥Úƒ™æf¬ı“QµÖC“˜í+ÅËÄìpıœåQK—,f3BÌäg¬#5ûQÚXdG¶ŸeÜ£Ysjçv@æ‰F!WY¨*6šcXl{,ßÜ¹§-/-4KĞ¸Í!÷ô•›˜%±b³ˆòÈôh#T­{Ñƒpø„R8W“ç)Ò˜l„7õY`ÓS-Q]ôÓ´§§PØß¢pF
f¡€ èµù\£9Ó¢p–Cálmá‹Â2‚Â¨!†¹æ>R/àÍaª£7å¹2ìJÉœ—@&Ã½
‘9_0¹@zd×##Ÿ
d.Š!Ã•ùbí÷%R,.‘ sREt;ôÀD¬Ä(€—²°²Ò\ÆŸe-‘5/×º®ºšf‡³F¼’9£Q2C¾÷*¦¹Q‚ü±(€Wke×(ÉÜÌr€»–Å8³Ì®µCÆŠnØ¾N»s0»s½ÖpƒíÎÁáHA’)7jö›R<r å‘›3xäL‹ËöBcU-Ş[,Üêxä6mávË#Äuótîæ€ØjÉÜ™`‡Œ‚„ìp—0Âİò¼Ç³òzv¯;Ü›b‡û´‹÷ÃÁe)æ$K<¨48”4xHë{ØÒàĞ$K<’`‰ƒä›³òÇXâßZÙcI–8XŠ=>S–xB»s»ó¤Öğ”íÎa!K É³ÄÓšı™KbYâÙ–8<Ó\¯Ğ^İ˜«i3ÏY–xŞ±ÄÚÂ‹–%>È†ÙÂök%óRÀl~…#1º2ÆËÂ¯ÈóUÏÈëC¾ŒñZŒ1( ½®}#Å¡Š73 8"Šª¶êÊºöÆ6ó–…âmÅ;ÚÂ»
FÔØ¥˜ƒÉ©Ä©Ôšª–›÷\Ø‘’y?ÂÅyø~À”ÀÃ]áùP€ùH{x×Ã#ßx>‰ÁÃiôSíügR,kÍ…—™ÏY‰ŸJ¿àÏ²–õK­ï¿R_ÒSéÿ˜3š“OÿŠin*EşØ¸ùZ+ûFiç¦ÒÃ¥Ø·,–9•~§İ9’İù^køÁvçÈpÜ É›5ûO)f9Â2ËÏÌrT³Tä`¹^U,š_,³üê˜å7máwË,pY›eëNšlÖWXiÔ.ãé}Î`ØÏˆcøJæ€eØ¨Ø#–axˆŒ9=yå/á’¿åùçäõ¼"Ÿ^™Ñ«âFà³â7ú>^q‘¬dÑ™ÙS"ÙÑ™ÂH]%n@¯Ì™9X"Ùœ|S$û—¶0—´Åq>>ôÖ>D\$­ƒíÙ3b:•æf%	¡+™y˜ˆã2/S‚¡…®†pÍ‡¬3Ìüò\@z%²òz¸äû×‚1¸8´Êôc’bÙC‹Bô§ØóöŠŒ²0«ğkş,k9†œ¼¨Ö¶˜ÔÖ„´ÄÀZœ9£r¤|øLsùckI­l)¥¤XGI±¥Y,s`-£İ9–İYVkXÎvçØp`!É¬å5û
)Ö9Ú²ÎŠ¬s\&ëär•ˆ#nFYÖYÉ±ÎhmaeË:`mK¢3x'ghV2«,Ã•ÌªËÌš=´Ğ·WV.#Ï±W×óŠ|0xeõ¯p•ZC{¿f
Ÿc,>ã2ğ9>sÁ®o(ÖT4Ô˜ñŸr‡ÏZÚB…ÅgC|ØhX^åzs”ïGµu!<:)/S‡‹úa‰.vÔé!(mô5„GG¸=\¢ˆØI£Me€ »ŒXq	3öè}ˆ`µ`W#ÏZ òz X—B°^¿¯!…à±ÁÆOÈB°¡*ßXU ‡5Y×v®£-¬kdDlì”¬~tö*3H¬<ÕÑ0¯>ÆÁ©œKµ M¦K!H=CS‰:LÎmäæw1*ce³r²wıg<#Ş&çŒ¢Î*7ë4"(%3!A£/"àÒh}¡ÎòÜĞÓy=tĞh£8#n¬n"Å²gÄämSVàçÃÍø³¬åDN@›k]¥®&¤%æÃ-˜3šØ“ïmfš›‘?6n©•µ(ó¸ùğx)¶‹eÎ‡[kwN’ĞwZÃ¶¶;'…ó!’ü|¸fß>Å­'Xnİ!ƒ[OÎâÖÆª†š¶šÆF³£åÖ·î¬-´Zn­·N7·¾Qİà+W#1n2_ôÚg×QuO_‰îIbu\Ì.ÿ°›%³k‚2ô8äŸİ„sv—ç×óÀ şÙ3Æ?œ%'é7í•BíD‹Z.µS2W‘ÆêÆú¶B…i³¨åjm¡hQÛÊ¢Ö7Ùû¾D€AêÀŒ)íMá’†{(…öij/Ô“Û›¡À¬¬Âyöm¦=@“İ/™M·èdJ ¦àƒBP»Î½å9ÙƒŠ¼TA	 vÇ@e€›ıä^)¦ÊÉ>ş^§ÒÏ’e-§:åä>üVN$_cl#•NM¸ĞST<ÙRq(ƒŠ§«’®3S,§òM•ô4mcº´‘VI³¥’Ù—yã*i4’VIïÇ<q•ôşL€JzßPI€w\%} à yì	ª=!äCAˆCb„àìx¨öù0)æ•¶™—äøÒ_¨}8‹GsÕ)òMG0ÍMq§'®(iíGJí¸2 ¦/‹.8ŠÅh9C(U}ªT}t¬·T £õ«TtSæi’÷8æèÇ+ûœÉéò-}¢”nBZ @G’Ÿ.OÒì'§XætË2§d°ÌY™ÇàÅš‚Ü0vªe˜ÓøæÎãtmái¡¹õd€¾AäsÂcjŞ†sO¸ûqítÌG!<(O=Å$}¨K®æŒ®áš@ı©ŞrAÃVç9×'§Fø'‰ˆ`ú:6Ü+@ëh~aĞsOâén^†Ã»›Øã80}8 ‘áp lz<ÏõÌŠ¼Yb:¤˜õ|Åë‚³rîŠŸ0\˜`Ò3¤³Å™ôì„üÅZë%®Ö@©›“[^bJ]ÖSê*‹#J]­ë
Ëbç¤”º‰)»*Ş1ä+uµ²k’Ü~–»6“Û¯Ó®œ+
]-}ƒíÊ¹!·#)¦ĞÕì7¥¸ılËí7gpûyYÜ^¯Ì×¶·W™[,·ßê¸ı6mávËíİÀÔŞ§gd;úúÄÉ†~´`İv‘Üí.àĞÜ4{3-ä‚O%Ãå¹ T8H…É™¸ÑvÂsFï¥èöªÊÍóã 7Nğq†HïÌĞß-Ï{<#¯çczãS¤¸O‘¸?…õ9ë2°>?S«È5âÉ
ó Åú!‡õÃÚÂ#ëÕ€5-T¨DÜ!LÜ›&Ñ’xµåæÑ %v«dş¡äD…Ç˜ˆ
èhÖãÓò|Òƒ…¼,ùz€õT,®POë§<#Åşï4Ï²
?@ŸãÏ²–8*×Ú^Úš–à_dÎh]9W>ü%¦¹åùcô?ZÙËJG·'Å^a±L	şUíÎ…ìÎkZÃë¶;†ƒI~¾¡ÙßL1Îù–qŞÊ`œ‹2ı+Úà.—3o[ÆyÇ1Î»ÚÂ{–qöæ’¤29çLqV”|Nlszr\D#laJ*iÛŠjZŠÁ×MëZ?ĞñSuSÏz/8#vpÒíÁ€2ßûóñÓJæƒˆùfÍÖà+3TÔÂoÉócÏuÈë¹N £Š:Æu¢Ÿ*Ÿ¥¾À"ıyÒgW7Ô4ªsæ‹ô—éÿjÿ³HÿˆÛX¡s¿àärÑêëÚ.¶ôâW/a¥†z –7‹3ŒDüˆû‚ÉZn)³f°âÇÖÁÊÜÊ»àbz´ÀT¤ˆ &j°"š„À€¦­«›7G–3tLà¾£¿ØÇ{QŠùn$V9Ì(6P.¢ÖÑG¶o¹îÆq]X£Ü|Ğœ —Ì×	šgh
€wHóo„ÚßÊó;Osäõ4"‚æß§hşƒRäÇÍ/´4ÿ)ƒæ—d.ˆB\Ì×´›Ÿ-Íq4ÿU[øÍÒ|!–á…‘0,ÊÍïì@Éüáá&à?™LÀèR†^ ù[ÿxX×Ã"ßIühTÃ2+~£Ó³á×À_da™ÙSøK3'Š†ŠººB­™ƒ%¨ç[4ğÚÂ\ÒBsëf
:WÈRÎ
yyÓÃOÀEÉ6Ö]¡ˆ;¦pU»Âº¨­»·/Âv`n¶‘^Ùo(è™>œU>!„q^”šaæ“çüÒ[ÑÌ#¯‡QpŒ¤`\P?²,ãÅÆ…2`¼,SÛ
›Ú|{[•YØÂ¸ˆƒqQma1#õ;2ğX\K <åJ§"pV6ò‡½BZØò9¹«·âUZnĞd÷¡õĞt¼¹$SŞÄ… .%p.-Ïe<¨ÈëA” ê²)P—ÓO^>ê%Ô2@½<Ó³«¡X•«ÇS+ZPG9PWÒF[P× 
ŠTëHQ€÷Ô8^ˆ(àPiŞ4ˆùQ£^CU½r »V2«$Ø/CU^†H­*­&Ï1)äõHÉ§©±)¤V×ïX#…Ô¥©53ºbXH½g±Ï7 åÚÆZÒFZÂ–J¦‚yã
4’V€T2O\RÅ(@ªù†¤ï¸¤V©“g½ÇU{\äCKCªµÏMŠ‹“á.“Î®Í¼Ja¦–µ\Iùm]-½”nBZ R@’·É› Ù×—ìªöÚ€‡6yj#W9µ×FüV{].½ÜØ~&¢«âj/ŞÙ¸‰6¸©48Ìf,¿@ËÕIÌR÷æ)´&j}[$ÑºRò6;´;£-õc®!b-ZÃV±kBÄä%Ş­5û6Ú`d‘w•eÛmYsjñ¹6óp¼-ß^»<Ìv,Åg{¾¹øì -ì(-4·®M‰—şÂ<*)ÀæVNXpVïk‡pF'z0æä¤ÂñÒ-U­;±ŞÄ‚Ã¾â’¦§-A·ÃßŠR¸=F»JeÁAŞàìİb´âÆiwı°=¤XÒ3×–ì1÷d±ˆñ¯–ÎNbšÛó\—Øóì¥µæ’pks¸¬'¯Ô¿Ô/hé¢¥şõ!õ‘ä©ß®Ù;RÔ¿ÖR¿3ƒú7dŠ¸q¶¶P  –ú{;êOÖº-õû¨{W§nJ°İP“aÜeÎ§ræ…°Çt·Ed·Œ5Ø53º ~ä±4—*$$¿ë"k$\¥¦²j|E%£#÷Ãï+™Ş‘8ŸrLŸğJ¿<÷ñƒ¼c?pŒ‰q7=
Æ`
îë,ÜCpß˜) ×Šmõ3ÅÂ=ÕÁ=M[˜ná¾1& _7*±Q”x†1•¡q5m|<¾:Ç‹Ó¯:¥.“ğÃ‘*N^İŒl…d;“ÃÍ…R³ˆ@Ö@îåá!	oHM§5ZÎÁeÍbUª/7ûô"@%³ßHôV!½öJÍç^Èëé% ½LÑë Eóà½®·ô:$ƒ^7gÒ«2WÙXS—3‡Zzæèu¸¶p„¥W‘ÃCæ?áŞ¦Qôİo#éjh7x$Œ;°èÑ ™¨±r8‡Šššf:ğHd9OŠn}¥ d~UÉ9ÈøÀä£Ş£åyŒy=È‚@>6òq
Áñ)o° Ÿò-™Ç ••uõøÏœhA>É|²¶pŠ™ŞpŒBèbuwÁğ{g=¢§÷dG[ö¤Çÿ—ÕO‘°F£é¥óâØäÿioXGñ½ã^‚»·6Ä‡R‚)ÎÍ½7mh›”IÓRÜ/îîîîîîîîî®ïóœsvgwgI~|_şØÛ£ÏyfæŒ3¤=½x‡òãñZ/I†š!#“v°—ƒõæJşMñ*¡¬Ù½Lö†ØüVô€Eºš¿Š02ÅµìüĞ>A´ jA¬€rºé•»ˆğ5îÄ@äÄ¸âNLä€;ùÉ"ìSä{ª9âz‘‹!òÓ"çéäé*3$™ªigòß5®ÏbÊª#5ílşUÓ®•fœc…`ú¾1ûtâ\-ğ<)ğßŸNœÏ,â©ú:Éö†ESõM©ƒ5×‹¢\½­~1óòû¦—hãnæÄ}©æu™äÕ°Ô¾éå©Š]/»"Y1ÄOì›^©™]¥]*Ò¹odW3Y s_£U¹…U¹VS_gU¹%Ô!äuˆë5úZX¬AŞhı÷FæœÑ oÍ½£ÓĞÖßewS@ƒ¼™¿Ô oÑn•F>{”k‹'`¼:,Ğ“ïĞjÛÙKY·¡röóä ß«“\dñ?2
EOÆÉ§Ï¥néàÚee_d„¾uÄm)³ª!äµ›¼ cæ´/J¥†?ğÕ“=¯ü”è¿˜ı´z5›„qè®üãÎFdnÔÛ0#¥xn‰¥o¶r0CÀx½^HÏñSÍØ ­øûğïm™q|©©‘»¡kÃ£*÷<Èë:’³™^ç#s±¤GŸFf8…7RV~ÜmXJ5'	*îv†¤šƒá sRÁ(“|ïÑ‹j¸’a€¹Ûú~ôÂæeÌ½NŞdœ¼/‡“·¸ou÷+à/ãjIÙÅ8Kª¸‡7¹G!ÙÅø#Œ“\Œ?Ê ,Æã/ãã7¹ByR¾Oy\µÇE
\NàÂ%Ë3Zçg%Yhn¨¾5^µ<Ç”ñĞq³4çy†ECáí©‹/hÆ/JÆÿ²~‰É‡tÜ‘^ß"Y¿œ¨(w^Ñü^UF#Ø­÷5ÆF°×ZÕq'G°74õ›’ºaÁ®‚üö–F;Ã–ÛŒ-ïä°å®ÜÃbcSkcK§{×¸ò9‚½¯%| %Œ½ï±êùìïŠæ‘Ò7ä}­º Šß]¢»ÂI\Åv´Ì[ïÈüo{f4(éT%ÇËCüÎ2'Ş	‚ú%û•KõV6¸â>bø@½m{ëÇÂÇOäû©g%âzV
 `ågV~®è|‘a%¹ëÛ/S¼¼]jüU’—w§xùµfıMÄËÿjíÿ[åì=iÎŞ!Å~—áì÷ZÖiÎŞ)qÌåìOÊÙ{ÉÙŸ5õ/ÆÙ{CÎ"ÈsöWş[†³wgÏáì}ùZºZZÊÍîãìŸgÿÒş6Î`GÜe±óÆ2Î¬èK‡<ã	™¹-s¸™}ã-f^ãxñİ³:¡Wqxj©ÎAÌo$/Íb†¤A¬.¹¼<LjÜ?‰AÅM³L’Æ9;À€#¤ñ´H…£ùN¯M:ˆëi,ƒÆ3°„Ä9ÎŒø€Í$É|ô»M$33zFº?w3¥¹®¹‰Ştfa
(B³ò—ÃÈlZÂìRÂÈÑ+@$¼gÀNNs¶xÿc5`
ƒæL‡êƒ“ánæ‘êí¬WÅ‰aŠNædHp²€š†hU	NsÉwnâfš´æI Å5À¼Ú–ù$™®æç¿Ã5ÀLYÕñ@´Xg× ÷Hk²BĞeÈŞP\X\$#{M<‹æˆçÁÜçºrcs}±ä3ñ,‰g	-aIı¿‰[NÛ·´²ÂË_´-×‹³İl‘#iLPã“hÓû¬‰«Ú9—¥¢éefy†àè@7bÔ¹›t/¸ª¥í	‘=ÎCÅö›øWpÕ)ˆFÅ-“‚×rú€	Ù°´ğ`ù.ëÙ€¸‚6Ø°\‚TL–WèVdÿ¯,+2¿XO¸OZ±Ã"uå¡ÔÊme-n•¨¸éĞÌÎ1òZœV(zĞĞTÆ÷KÆÃ’?œZyÕhÆ«*É"½åIVËdŞR§ì~„s@½¦nÔíôù9 Q£7eı 1º9‡ÑæÎ•ÊµmÅÆz×bŒnİ¦%´£é¾ïKÆÀ§˜é!åè¦—v8ñ;Cr™æÏ’vyÅæ‡Øê°‹,äÍIãºTúI^«pÆÈºöš‚{ktA%ÎT³QKhjT‡â,pµ€ÍDŞyc3@	Ù¼ºğxù÷lF\ÏfAl^3Áfîó®¥°­ÌC&˜uróXî¾a}kW+ŞºuM0ëE‚Y_KØÀ3ÁNM¥¸J {XIVÏf6[÷»haI¦‹ørª„ÁøŸŞe‡MŒMå=(Ñ>u×E¡<ö†Øl]Ål44{#y¤|7ö`#®[ĞØ	°9tl¢Pl*ÉÒÖ|íq3¦»åÃRãÍ§´Ç-4ëQ’5V5ÿU{Ü’Yéx"­=>"Ån•hW<[kYÛ(g¢‘ãQ‰;šqƒ‘c[†Vu<É‘c;M½½¤nGX0r È;hô3}ÌºSAŸÊ=õk+Ô·”jng#è.AZB§t[^9%AP=»¯Æ>¥½E‘»’2ê¡ ZJ…úg·Şxã*iWVğğ¼Å®XAé©qÅ€ŒlIÅ•b2Nò‹}®Ì@¹AÛBNv	ÇÈw¬ç$âzN
`àdwB˜ vÕÖËàû¸á;>ß§óğ­/¶ÖáJOÉM0|{"|{µ„‰†ï›hß:p^É=eï£>¶„9Î‘E#uqÊ.ö¾&õN^Ü:¶5ñ%âÄÀl‡sééÑxL±<Ëá¥z•ÁµWˆWu|'Ä"¦,äñ‚u§L¢«MMËšC–]Ê£ICqu\ãvDL0ñ&%1U•œ[lÀ5”mŸHu’|û½l×ËV„ÙNNÈ–ŠëE~wI¦ŠëTş;¼c°SVu<)®{òï¬âú„4c/+£Å3YÅuo-pŸ™42í›C¦gÜÌjsûöç/7³Ğ2”2²›Y,	Æ€7¹™…B²›Y3Nr3ë`3«Â_lfŠßäfÖa"‚Ãå{„²ö‚†òà(!˜GiV\¢ó)©ì1ŒŒ˜Çª@ãˆyœ¦>^R·#,1äİ ÑO”èáÎYkS¼sv‰«ó´Tçd†EsÌó)UôÍøÔ(ãÿ:Çœ–*î)îôdq/¤Ô3´¸3Ó =+ÉÎÊílíE‚v¦>×@{1A~š9O£Ÿ¯…ÅGÏs/`Î™ñK¹G{­Å&x˜-¸™+â‹øËñÅZÂ%RÂÈÑŸñhÏ&‹—æÈä¼®ºÄ»¸¾ÆÿQ+öv*m×kåñ$çÛ¸ >¤Ş«’N1b'2t!_½«-†Âkª7ÅègË3¬øpüF“w˜Â0Ò½zåöÖe9gÅÇ½ek]¯HÈƒ#\ŸÜ=c£e\×DOr—…ÔšÈâÉÃÚÁÈá˜x¹tÂ+ä{¥à)ûíˆ›‘ºâU,!aÚ÷jÃ5™Ş1/“¦ÊÆ&…	'MTèï­L_›"ïóRûë’ä}9EŞëµ˜Òä}A’İ˜KŞ›”¼¯¼7kê[Œ¼¯„äE'ï­ı¶y_4òŞCŞWsÉ[‹7$¥B«»ÃÈ{gDŞ»´„»¼ëèÛ6ê¾‹¬Ø{]™¯ÎåíNÆÊ/çb®ıíÖş5î€¬sÅİ;-Pı÷	!î—ïˆëi!˜€&hA5è!màÃ_2Éğµ\5³ÜR×X_lt„E>®%<an‹’O—.—ƒ2¯¥ußd©êmìZ.´N¾ÓÁaİRîÉ GV^"b¹mĞÓçf@ T¢%!šÏÏÊ÷9&âz4 ù|Í´­/fĞ|ÙĞ|)Í×sÑlhh(×·6»—ÍW"4_Õ^34yUOçÁúSuôLE–ŞÃ«·Iß77|Sï9¾ ÈºVÜY ßÌ•|K {[¾ïx ×(ˆ Àw3 ¾§Í{?à+à9 ¾‘Û£»êZëZ:Ü‡àG€k	Ÿ€?ËuÛşƒQÙıÃÙmÇ=âª¢hf%Ğ1Ó`&A†J<¹—à¦ƒËb‰¶P1iáˆºÔm/ÒcûË˜5Ê0ûÎ³ÒÙ\_ó
˜B7ç$C¦âwEnÈ%gH¬±&É-:ó»Úßƒ¢ÄgÊ_œgcüÎ8ßÖ|ô«K¿0x Å£^Óü4=a®¸ÏbÙÿ‹¾ÄC©.òşB¾_z©#®—ºˆRÿ*!u^ÑıZeò$û?,â¿e~C:ŞL/â_•Ö|—(‹{ßkY?HYƒìEüÈ´±øšä÷Ã"=ñ­ÔÜ÷³fı‹’7Òv_—d¿2Y íşÆĞª·9÷ı®©ÿÔí´]ù¹ïOşW¦§¼a=åïœòN^Oi)b_±«³èş±2Í²¦¸M‹ „éğCÅm°ÁvÁí
4¥Ø Ôzê‰UÏƒäê„9y‡Ò%Ş_Ô¯*yèBCÉD\9”õ&T·)=Â{™Yåú•0ñ^Fâa¶Ş4U¿ÎÜ=_îÂF{|¨½Ã^'ãQ“äÕ.Ú©MM5yBT‡bæ×Tê&}‰Éâ¾‚^E?*åİ»ém/½XºJcå¬g‹74Õ´QTn"ŒzèÕ¾ÈcDú­ÆMO¨SÚ!ÅWq30<Ös6÷!É°ÎˆT8Û’ïÌ"4Ñ×÷@¡zà,,!q06«Êz6Iæ£¿ilšÑ3Ë€wÉ¦1|Nê¸sè÷¾ÖÍÁDX	á/W°sj!URHvË¢*n.ÆM®`QJv;7ã$W°ó0 +Øyù‹ì|øM®`çHï‚di)€Y(W°kQ`¢>ı–TvQÆúôb­êx}zqM½„¤nGXĞ§äßF,©Ñ«%ºî[,Å‡ûKk!ïGûËğïì¾ÅÛRËe­E ÂûÙKwËiËK~0œ'µ(àı*\,š/ŸW`1ïH)+2,?H-ŸWÒBV
ù¯ËçURÅ½+ÅM÷aj¦ÅÕ¤%ö$[5Wbµ
æG”X¦®7‰}JA~nĞèZX¼|~ßúMsÎô›sO,Ûš ò5•]3S Ó´ğ—ËçV-¡MJ9úöxù¬eÔ´¼WåA<†\8…ô2ööä–qQİİªûd@¥GfÈ2¾kC¸c°D¦[Íø]³]¢Ó[üI‡qÔD M0»)p:Y]ê—›ãêÁÄÎB»\w	>NôTpna—Èk\;›•ñ1| õ0PG¼ÿ!ƒÉwHF<ÄÍˆ{¸uŞ?£°¦âºV†ú$§n„ò4c;×m1ó×NQñ©ú:I*~’¢âºZÆzi*~(ÉÖÏ¥âJÅOÅÒ–¦aTü4¤"‚<7Òè#3TüÈ¨¸q?Ë£b\‘Z[\‡Qq“ˆŠ›j	›yE*¾¤-~Aúé¾uŒSõ•Õ§NÖğ0´1ï#­t$LoVcÄp“)”w[ ½8åc=Ï:R‚G¢·y@(6¸â¶ŒPh{H¨QB¥-å»•'âzB	  ÔÖ	Bq%½¢3:ƒÿÇ†ÿ¶9ø>ğZç¶3lÏ_N¡;h!;J!Ù)”EUÜNŒ›œBQJv
İ™q’Sè.ÀZà/¦ĞNü&§Ğ¢@R’oÙƒ¬=0ÒR Ó• †Sè­óX&šB?‘Êv3n0…îÊĞª/ØÆiêñ’ºaÁŠ ?…NĞè=İ¬jñß™)´e%7Qù2¶ªÅ¿³Sè§RKg-ÂØòev
íÓ'IiëQæ2Ú°÷ÙÏ¬b>“ì'3,š;¿J S4÷İÓØ}.É¦æb·‡6ëkb·§¦ŞË°û:ÄA~Ù[£ï£…Å“ÙÆà}™sf2û&oiknl)Ö6¶ºı˜“Ùşüådv€–p ”0’g¦XRD>§'õbÂp½Sè)¡zúxR\Oë÷1}jÖ`*î`†4k za'?©àA¾‡JMdÖ@ÜL›ÁåÃLòÑ¬q¸6àˆŒ´iIºx¦82%ç/¥ºG%åümJÎGk¾Ç¤åü•$;6WÎÇ©œ¿£œ×Ô'˜œ¿åŒ /ç5úI9mr>9GÎßç_¦mkihîjp§˜œOä|š–pºÉ¹KG³s½è‘K3¡!¯fÒ~ãëyû_†}=¦4ã²A(Ó6gb“*PbŠT„"Uòx@/ ¨ı/¼´’uÿè,}¬HP‡°ŸÆE÷èñ:¨zéØköÒbÈ¯ïğÎ@ÏÔ>¨,)mFZO#§°)TèéA»ÄF&?Ù>‚U—ÈÌ¬·ö‡ÿì÷§ãR­EäÛ(ĞšHl€$6Z¢öJDácEÌHilÀ ±à­qg½…’­¸3ë-rØ[Î’~r¶|Ïñ½q}oæ ·œ›è-œÏSœŸ!Ú7F´rˆöCî»“®Öº2]j]hD»("ÚÅZÂ%F´-u~mÙ³ƒ99i§şIë®´ÏŠ5¹.÷DâÀˆçöP{q[ºa‚ÇŞş,Ê]`ÊFàg0LÑœsAó
ù^é1E\©€Äsœ¦Ô[¯Ö_#ÉñŒu-ÓÆ“Í·RãëM6?¦Ïn4ëT\ÑDı$»‘É‚‰ú&†Vuü$g7šúIİ°`¢FPâìF£ß–áÆ÷ÆÛs¸ñsîÊ©¡¹©µ¶¶èî0nÜqã.-ánãÆ·©ıÑ#öÈŠ¿ª–º‹/÷ÿå6>ŞuöTkO¯Ş’‡d	%ÏŠúÄ£l+ÅCGb¸[F
yé,ÅôôŠ?úÄTQŞğ<C3­ã•=—j]8åtxåÈ+ ñy&VRØ„Â=kŒ/20¢†È@Eu§)5Üğ– ã i0Şëœƒ&aìıò}Àóq=oE€<hÊğö!•ÆÃÆÛGóíÀdíkãÅº ­‡ôŒæM]ÂÜà$Øgw0¤Èüƒ4ãÑ$™Ií:<¦å=ÓO¬ToÒó‰TÖ?JÖO&³ş5ÕOÒ¬ŸN÷“Ÿ$Ù3¹ıäYí'¿±Ÿ<§©Ÿ·~ò[ØOäûÉıÅL?ùÙúÉK9ıä÷¼~‚×dm¥æB§{ÙúÉ+Q?yUKxÍú	o‚Ù1KƒU¼ÏÆIµ–í`¤Hn7óE€z7UcÛ¼º„ƒR^.2¯·ò. Ëz&Û:§ê­jŞÂD«ğ˜• NËÑË7Z
x= 4‘ÀÕ`„(!¡ß*¿%ß·=¡×Z¡ßIš“Û»
Û{Áüb‚y?G0ä®·[õ-…z÷	æÃH0i	›`.±õöİ—[ØêáëaZŒ¤™¨„y4Ûãh0ÏÓ›»¼ÚĞ=Aä9©µ·•¶‘#>É{]ÿ^'•Wê¼Y!O  põã±z7-V›'›ïÜ¤åõ¾‚XüÁô§÷I &âRqŸ&&@Šé3ĞçòıÂ‹	q½˜wˆéËŒ˜¾R¿ÎˆéWÓ79búsàey½ûÖ$õ¹,ÿ^ùA
É.ËY1nrYR²ËòŸ'¹,ÿ™X–ÿÂ_,ËÅorYş›@ò»|ÿğÀ kŒ´Àü™ †Ëò¿´Î+0Ñlÿ›TöÆı/'£Ø_Å¦Å¿‘z:üp¶ÿ+Åä—åÓkô$º.Ëgä¿Ãí™´¿£eùÌü;»,ÿ]j9ÿ1°xû;»,ŸUœM
Ì¹Ö¯Ôfg.qûÿœç`X¤$ı“ºp<D3S2ÆYer‹:W1ıif¤4ã¼ÿ”¼ç²ZsII9Ì­Î#Æqÿ’¸ó2n ‡ù¢ig„æ×Ô˜¦1Ğºäg“5úBZX¼ÄÿÛzÃÂÌ9³ÄŸnFœóğšPòœ§«±T__.Ü"L%ş¢üå1-aq)aäèqÔºô€Nw£aÿË1Zh.Ç
ÆÜ9Üó@N®+`ÇYítÂC†ºQ{
p¡aÔøŞ)Ùç•İXQñp\·ã[³%XÔVÛVqK2| ­43xª‘jo·”|—–ÉVâf°CÿZ&!W*êË*Ëıšc.Ÿbà?Rß’œ~Æ¤é€5ã•Ò„™fn&[9—0«(af a†jêaF˜BÂ È¦F£¯š!Ì´(mìš“\mafÌ#LKg}gW©³ÉÕaê#Â4h	F˜É Ì&ö¸ÛÇ}Å±½½8Tc™ú¬]&#yjDÜ€iM°Ht`]›.]¨îè¥a¤U–n`›kèõ´0'Í|H_ãšî°™×<wĞâ;-ÂšVù¶yî ®çÀî´g¸³šbò¿áN£ßO\=Åé¤¾k$¹3SŠ;Ã5ã5ÓÜ™^’­•Ëµ•;3“;ëhêu;3‡ÜAçÎz}ıwf0îlÃYò¸ÓTªok¨kmswFDÜÙHKiÜÙZ—ÿ<”à‚	Køè‘µ64¶ÛJ\5ÙSë	exSL>Äîêí-ºiµëï"ğş»ÆmpƒÍ¨¸Á¸…ÜØDX±©|7óÜ@\Ï	ÜØ<Áê[h›GePÑPİ2ÕYóPmhik®olhq[ª[G¨n£%Œ6TÏªÛŒÅ­;±m4¼ÚvòhØX;$oìá
’XG¦¾>µŒ))¨ıóbmW/®¨ñ +d(¦¶¹KÊö¸qÔa_-âBl½Éç&ÿzÉV½öÔ¸mé¸JL:@&”Îö"—ä»£—âzéÜÎN	épÔßY±ÛE’y½c~ÎŸÜg’¶ñ…Û®®x(0£xúŸIªßÉ°H™-Õ‘‹ZNIYio3K²2“ZCC«:fgG£©ÇJêv„Z‚|GîÖè»f(7‹Qn\åæÈ£\±®­¹öÜx£Ü„ˆr=ZB¯QîKÀoâá¤9éŞ%ãØ…;y|LË‹¸fŸv\Äü6,n÷pK„7píÆ¸lşÒÈ¾¼m§G½p·±·c·—rïìa/±¿‡ZI|™ÓÎTMõØîå¿âi ¾hÑ®¦—w×KÁ¸„Å¯:—Ù‡OŒqôî&&¸·Û`Î!P·O¾“<×X„÷'Ìáe²JbJFÖ³š¬wÏ‘õÊúßo5¸©&î=øËõÒZÈ^RHv½Ä¢àf›q“ë%”’]/íÃ8ÉõÒ¾Àzi?şb½´?~“ë¥’å{Y{`¤¥ æà0ÔÓÑ:W˜¨ÇÍ&•=”qƒwC«:æd;\S!©Ûô8ù·,Gjô£$zzI9×õf™qíf—ÚÃ°h©J#Çj9Ç¥5‡$;>·Q'h£æb£NÔÔ'Y£æ
… ?Œœ¬ÑOÉPkˆQëÔjÍ7Œ´µ–j[ë[Kî4ãÕéüåâã-áL)a¤xP…> ¤‡»³+µ4`Éw6ÃS*ÏaHp[u	»Ú¹Â¥óä{¾gâzFIÁ¨ŒbW»Pk{Q9‹sğ˜'Ö¦RSSmKÁ]bx\áq™–p¹á1œ‹±a›âd†Åí~bÿÄ8Aí-É0¸!6“õÜLn!›Û_¸»"@‘õ…7–EŞÂ‡ª‡ğ]%À]-ßk<|ˆëá< ßµø®ÓÆ]Ÿ¯Êà»!¾yóà+´ÖÖwà£ıFƒï¦¾›µ„[¾…yÙ¾ìğêmá÷´ZŞàt)r×vk kRq·ôº=—^¨[…-AæNùŞåñA\4øÜÁç­ı½|æ2|îËÁg¾<|Êu­­u…¶‚»ßğy ÂçA-á!Ãçrà;ü¤ñKìOŠEZÇå`¼:°¹rxuì‰&ğ”Íö‘Õ0¬>5í)ë^è£¹GnJêAiÒ›hò(ÑüÙ/};aŸê¾ºtÄî‚·«‰ÁñÛ‡‡xŒÉ@)”Ô£"£Çäû¸—âzI	ôÔI=©8>•‘ÔÜ&©§s$5¤êëKm-m-uî“Ô³‘¤Ó7IÕêÀÈSĞØ“£tÚKæp÷B€+Xq/)—à¨rÛËØ+ò}ÕÃ†¸6Á°½–íumÔØæ1ØŞÌm\µ´\_ÛÚ†•Ğ[ÛÛlïh	ïlôÊ°ÍØaÜ¨Â ¹FæíKï‚IùD‹¤)c§¦\8E]¢Æ½ ÉzWÜûƒ±Maü@ üP¾y×Ã(¸ Æ30~¢ü4ã¼ãg90.˜»ÅS×
Gíp/ı¹ÁøEã—ZÂW#o+ûøh“n¤Åk{drš¾S¿Ğau*î›€kßærAúNàù^¾?x×ƒ$­H?f@úI›ğs¤ù¤_r@Z(w0mikl*Ã²ã¯ÒoH¿k	H‹Ëİ(c 2Şô‚\‰„¬ş0bm*î¯Á„Š…àü-°ü#ßià,Ë¶:×ƒ#­8Óâÿ'_L‡¿Qõé%™>¿3£gv•Î§¶Xlël-İŒL]å™øKÅnf-a)aäèK¹>ä“ì6Àœ‚# <8´ãGyø!^˜ì¶Na<³xô®Ì£'Ã™c°Niê§N=Ì;ÕÔ{Jş•÷=¢dÊàè´¼+á‘å¬lDJï$07ÃÚ’F¡œfG*x^‘ï/'ÄÍ 9Í™‘S•¢8WFN˜œæÎ‘Ó"¯íİ<&ªyùËµİ|ZÈüRHvmÇ¢à+…q“k;”’]Û-È8ÉµİBÀÚnaşbm·~“k»E’Åä»¸Y{`¤¥ f‰0\Û-©u®V`¢µİ‚RÙ¥7XÛ-ÍĞªE¹ZFS/+©Û¬íä—AËiôå3RXÈ¤°BË]•êZ›ZİŠ&‚•øËŞ²²–°Š”0rôè-[R©ç&šƒç‘1g&nÜEO“éx‰:mô^^pk[°)¼'ÕÇK{<|æ¶IÊâR¼f`{‹á1¯sVhMÈëÜªò­õâC\/>â«Kˆ©zmoCÑ…ÑÆDÏ=Õª-·µº]“!Ú!Ú¢%´¢sê&'V@»¢®-@ƒÅW\{ŒÆô¼ã7«1$X]¢B9Õå»†q=(ÒJ>pÈ€²¦Vy­(‹(kç€²D®RY(74wÂ^Õ:Êº(ëi	ë(<¹(æ¶ŠüÁ_‘aæÄ«UÔAW›áõÏ¡ÑÃúÁT)r‘ËVóìš4á6Àg3á»e0*¢Å!ê#ïä;Ò£¸u¨oœA½C1Ù$ƒú¢†ú¦9¨/™¿(-5â¼¬ì63Ô7PßBKe¨/$:©œôp·e€+ËV)·Î%%ªÂ³ 3Z¾Ûzx×Ã#í<ÛeàÙ^+¿CÅsà©Îƒ§®	ëJÜ
u;<;Gğì¢%.À³Şî°êÈkvj«ê­ñòTY^Í¯¯3º½…F­‰ä`	†íx°ËIK¹Î l6«âŠƒ‘-Q.	¾eùvy”×£,°å1”Ç*İ”7”wÍAy©\Ö·ÚZKnœ¡<>By‚–Ğc(7i×7}ÕÈJˆÚka<ÅFWÄÄ‰•$<I¯q½h¬eÅMº[.CQïœıoA­O¾“<vˆë±0¸ÿÁn²¶lJ»%»İs°[:÷x;”ÅB¡ä¦v{DØí©%ìeØİ$çÕ[Û¢ÌÇÒd%.;˜q]Î¾ICKÑdF4«Éõ(õÌL¨¯v)LLt‰‘|ÚÊÑõ)SA%°»ä2»«n,’™‚£;˜‰ì^mƒ¹Úãe1ÆÄet<!îödG”*nŸÁÀB¡í+âÚO¾û{¡!®šHB; #´Òƒ2B[Ò„vpĞ–É=i®İ;›İ!&´J$´Cµ„ÃLhkË%IÚ ß;u:Ş¬/¤C“÷ˆÜÃâ*^@ïªq‡²ÊwDÀş#sÙF„@%-ßc<ˆëd ä± ÓfŸ²Ú€<!Èeó·è±……®;Ñ€<)òd-á’6«·ÅúŸ„Æè,'Æ\ãN )i¹X­vHq@3¢â“Š@÷¤ fäº¨·XìÇî"/Jëÿ0.Æºaîi3uÌ*ÜÕa(}O5òç½{¥›ÇSÉx|ŒÛ€#Éé"Œ3ä{¦	âz‘ÆÉY‘œ­€“ÉR&’ssD²\îâº³X,–á’õ<Éù‘H.Ğ.4‘ØöiŒå,nluaM,VdÅu1·g.
Ğau*îâ€·—äòAºTà¹L¾—{×ƒ$­HWd@ºR›pU¤¥¤«s@Z~à•m“»Æpº–¿\Ù^§…\/…dW¶,ªân`ÜäÊ¥dW¶72Nre{°²½™¿XÙŞ‚ßäÊöVä6ùŞîAÖi)€¹#W¶wjïR`¢•í2RÙ»7XÙŞÃĞª¸²½WSß'©Û¬läW¶÷kô2RXÖ¤ğ`VÌ£j	<mmm,º‡Ló—+ÛG´„G¥½]¸ôÿßyliYÛ©¼Üaá†.‘Å¯=à¨q±©%/ÛVq3| ­43$ü"Ñ'åû”—+âz¹
vëÓ	¹rÉûŒñlêåêçr ^)WÅkÆÎw¯½Ÿ7¨_ˆ ~QKxÉ Â³CoWEï c8æ-
xÎ±ûwº8Ky	Ğ½6¨#úÆó‘ÜÄ~×‡™’ÉÕˆMêÑ#·İp^D|ÜGÓ¬`ù¨Æ½ÀÎvVÜ+ƒÁ&‡°¿*€¿&ß×=ìˆëaûØßTPŞÊÀ¾¼Áşvì+çï•765•Zİ;û»ìïi	ïìˆ¢!Ã0\úárÍ®Ä'\÷|ÑFGÏE^+ˆ±ïsØ°*öÃÏŸ6:<Êwâ0rUÏ3:Â9fGÂºa÷˜(‘úDRÅ"Ædm[ú.ïêsFséØ7¶/QÆó¶ºa×'ˆyÆµŞ÷A FâVq&F@Šñ#àÇòıÄ‹q½E.ã§1~¦ ã
&Æ/rÄ¸JîÉQcWc]m}½ûÒÄøU$Æ¯µ„oLŒóÓ!Ô“èÑÌsŠVc—‰ ¿C_ÇCVyÿÙ=	ëÁ®<^}CáùW£ÑíE‘B¡¿Ôİ[ƒÕBöÙ4 F7ôäÊ¬¼u„Y]ˆ²ÏUARá§®äğÿÔ®%Ş—‰®j¯xTíš1g¹§=ïI¼ûßh]ölô\eéÃØ÷m@
Jv»#’â{¡ÃòıÑ“q=)DÊ ÅORü¬"û%CŠ¿æbhî†Y[Wg¡ÜÚå~3Rü‘â-áO#ÅÁºjÆüÅî•DŸv×Îò$,¿t¬åZL9Æ•'Â0¿}¡ä_ªóö”!F‚k‡!…ñ22POö^Ää%£qFQ&É›¬n>ÿ­®¸¿ …ğÀ?|Ÿìí¦Å×’×AP…¦ÃÿO%M¿Ñ’ÌG_É„0#£g’†¬È5»™˜§I3ó—ŠÜ,ZÈ¬RHV‘cQ8œaÜ¤"‡R²ŠÜìŒ“Täæ` ¹!ü…"7'~“Š\•@2—|çöÀ ëLKÌ<	`¨ÈÍ«uO‰¹•¥²ó3n È-ÀĞª*rjê…$u;ÂEAş¹ÎÂ}‰®Ïuå¿ñ\‡ï]6ã)ÙŠu+¹Å´ˆUgÜèö9f[q‹óïìcU¤KX{ğ|bUy³ÄØS"«
KjqÕRœ¿í6E™îZ4Æ—e—bf1C¥€¥İr«Mİr[Fó_6İ0I¶\.vËkÃêˆİ
šzEÃ®.ÄA^	^I£¯¬…ÅOljŒÁ«0çƒëó†‘æ–ÚRCm}­Ê ï0şR	®ÑV•FŞGNŠ#+¦ÇòÊìxCx–Ç[79öxZÚ›ö¶¡„/5é‹Œ3ÖàbØ‰Ï½w‰1œìªGO	ãG-«–Ò‹ÙÜŠ«cø@z1ZõH…Óù6J#åÕâfàD7i2ZETjVlZ2Tš	ÑI«çPkŠC«J}Û’jˆ9D›òíšñj’±v‰ÿñßè4—6
™¯X7´º/_WßÒõ—Wr«+‡£Î±ÿÎvZ)w¸µ­lLvvü5µàµÒä­“tkç’w-¸‰ä]WS¯gäm
É‹ OŞõ5úòÖy7Ì!osî5‡R±©«­­Ö0òn‘w¤–°±‘÷>!¯<ÏàİüÂ‹a>úUB5[{tÚ+ç÷jÃC\Õ¨‹õÈ¡Âõ/Wêí¥ÿ×¬(&!C½¼gÎFq£ç™.º£&v#İĞ²µK?úøˆäº7,Š@“®qÿ‰XÅm2ÿ^ÈÿM…ù›ÉwsÏÄõü‰€ÿ[dø?Jáİ2ÃÚ¬có0o«Thoì-©°fMŸfQØÖz@²ßHõN€æ!]a%·²°5¢ÿöyôo”BwğôoÍÒG-u§4ı›$İÎ¹ôßEn#ıšºÓèßÒAşE^ÊĞ¿Ùè_Î¡{î^[ckgS}s­ë2ú‰è?VKè6úóm8©%¯TS–Óù˜µø_]½cÆàüIÔn<…(c}¿#XçÁ’ª,Ì¬—°3ŒÀûÉu
]\¦vrppO]1Z˜±<”EÓ¬j”­¥½¡“€t![Ô9$«q»Ü&7n0n™Ûã…ÕäÛã¹¸Û7¸İ›à6÷<&*v»e¤ÓbÒq9ÒYm`İ°Åõ™€&ñ—ºa¿2Y
Éê†,ªâ¦0nR7D)YİpwÆIê†S İpşB7Ü¿Iİp/doùîãAÖi)€Ù7í§uŞ_’yıi¼ğ`ºXmj•ÆÈ°Hmú_ªÃ¤Ù,Ùê”wÿœòjSS^…™Uu¬õùCùwvÊk“r³6`Ê[=«®µgf4¤Tp]x=ÙaPO¹Ûùã+0âdvæ·»¡Á¥YƒcÀÑšÛ1’[;ÂR~»MaÒ.u;.‰	â'üv¯™ ™ÅP®&ÉNd²@?I«2œU9YSŸbUGòÃÑ©ı4-,V%ÿg„?9gTÉ5s‡£ÚbgWK}ÑÁP%Ïä/UÉ³´„³¥„‘£›©ÉàğOÏ±:ä¿<Ì+ÉÂ£v"Ä¢8œñPkN>îÎa–)Õ¬¸s«€¥ğâjç!TÈ÷©œ¨€ˆ›½áBcRäYú"mÓÅÔV7Ô.ÉAm­ügõ-õ­mîRCí²µËµ„+µÍâû¬›ğ¶¿¨·YÅÿw¯ùJÂªjÀÃƒwl˜é«dq[b#?võÄœy¯qWx²wUŒgtŸèj†÷‰Ğ¤ÖkĞkå{‡q=¬‚`½>+™´Ñ7J223çwJìdË®G:åMÌÂwÊ›ùgUÇÚì	·hn·JníKuÊÛ3î]kHÃogX4P!~¢SŞ¡™İ©ÖÆÃ%Ù]LÆN9êKí{l}½ã±Ûr·VgVçÍá^«Î:aÇDï˜÷iôû3[Ó(ö@ÅÖÍ£Xc¹«T¬íjqÅŠ(ö°–ğˆQŒöÓÖÃõ•Ì«^y·ƒ‹ñXŸñâ”{4 +XqÅâSœ.‰º†Üy\Xó„|ŸôÜA\Ï Üy*ÁÎÜOkkÉàµ–áõl^ëåî·67tuÁÑˆ{Îğz>Âë-áEÃ‹ö*äBŠÔİ2w/˜°ğncu«Wt+T+çDA@yM¾¯{h×C#må‰Bš7µâoe YÛ y;šõó¡é¬ƒÏ÷AónÍ{ZÂû—ÂzQÇ}€Áb±!?APƒœyiÿÇòıÄ£€¸i7ä(ppùLëø¹$4¿hÿ‚éâ¾ÔöK†EÃñÀ@Ç_i¶_K¶ÿâóş&Ò±aÚVËº’õ·‰jr-şæ÷½
+hÖ“¸?0n0ûÿÈĞªd~ÒÔ?Kêv„›pòƒÌ/ı×3Ö7fü–ÃŒr™Ñë‰Íğyÿ»1ãˆj	3Äò—¹ò†¥LYğ…2İ“Šıó³E'‘Xùb¶¢Nuú€5³Ù/b½æU%WÀsi.ç¹Ğîƒú 'FêC‰+•è4A\šôé‘İkÛaÂh{1Eõï€¬D¶ŠRdÍq/PB²N³¢ìNËw:|MÁ@\OVAdÿ?éJküØf”dÚš‰)cl õ™a]G¦îY4ãY%cU¸gã¿ÿ}ivfVÕ±q¤pÏÁ¿³
÷†Rîk¸¾qv‘=§\%Çõ!éæbº€×skÁäõ<šz^Iİ°€×ò¼O£Ï¯…ÅZíFÆë˜sF«İ$÷²®%746”Ü‚L­v!şR«]XKXDJ9ú)9CEËÎ a¤¾¬WÙqØcéèUO´Ö0’"¨¼F4ÊÌÔÅ7e)õ€ú^d­NÌ×iŸaWÁä<4e<¶ wÇÄÆ­ºç{	#‘±oM_=1çVãeKSÊ6Ñ«¸Å>Ğ~+€ûÂâÒ–ï’¾/ nF:èÕ™¾°”B½ô¿ô…¿ø\&ÕFJ}—Mö…MS}a9ÍxùD_XÁúBŞnÓŠÊÇÍ¢°R^GØX
]Ùw„Í²a-uhº#tHºa¹¡FŞœaUM]kaó°# Èw„:^Ÿé›XGhÈé[ä^&h†«°¶R—k´Ğu„f-¡Å:¯šÒ[¬cá™aÂàhÎ“a1‰„•Jä÷İ†ò`Ô¥Š=÷OS&•3ŞîhøEö¬Å)…IE±›Ş‰vwéfBy>è+ïJ<²’Ä5®5 <QÂ†ı`„`!áÛ…ê«É÷ğˆë	/R áWÏ~…tx†ğ3Úâ˜ºa^UY3Å÷M¥ºk%ù>*Å÷µ5ßu|_×øŸ/Ô§6[ÖSæmQ~ı<Êo&ånà)¿e–òjÁ#Ò”ß\Òm”Kù‘ZğV¤üÆšºÃ(¿UHyyÊo¢Ñ7ÍP~£üf9”ß:÷şsCSmìÏmn”ß"¢ü(-aK£ü¾\8É:;ËÇb7_MŒòº	D¦HA\Ó|Ä´¯^r*â<A­lf};rt/á¡:nVDš}_pëDnşâ’DÛ* /Û‹½öÁÈ‹¦ç<¿Ú–ï¶¼ˆëÉ+xòùE‚¼\‡m¯àì”Á¿cüÛ¼ƒÚêv2	ìÌ_î î¢…¤ì*‹‚a#ÆMî ¢”ìj‘q’;¨%`µÌ_ì vá7¹ƒ:F +ßn²öÀHKÌ®	`¨ØÓ:W`"Å~K©ìÆ †VuŒf'èÕÔ%u;ÂAşt}7î$ºªy}üwhs’²mÔÅûùwV½ÛJj9ÙZõnÛì~ê-pw)0Ga­Ö§2—¸ı[KÎ{0,RX·KZ{jÆ{%Z²·µ$o’ŞG›³}Ôœ}óš³ºŸoÎöÙk-õ€´°FKºs…u¼…u°¦>Ä„µC(,ù«¢ÑÕÂbmu[ë2‡1çŒ¶ºcî*¬FZšêÊîp¦€¶z©­©%%%ŒÍgtvÑ–çÄ·:Ï7e>•7ÍrDÛ‘ñ_½,É9]\ÌÚ:M¯èA¯4ŸyêOOnê[hŒSb‚ªÈ{EÈnif•Rj%›	BH­D‹ÃêX¤‚i!ù/“=\ÄÍÀˆşx‚‰;ÚÃ=Q19)ƒúv†úÉ9¨ï”»‡[[×ÙÚÕ†ú©ê§i	§êñî†ğM(»FrÓJlv‹Ÿê	r
Œ§dı²2ÆKÈq€¸•`DÚ­S“ÊpÃ€ÉÚÃÃ``¢!!˜g	ŒgË÷&âz0€ynLn®œ§M=_’…İ¿Íwÿ˜2îşÛK}/dXÔıwNuÿ‹4ã‹%cÈ.á¿1åuÿK™SUÇ.Q÷¿ŒgG³¤ĞË­	àË.Ùî…–z¥r#«w”tW1]0V_­Øı¯ÑÔ×Jêv„c5‚|÷¿N£_Ÿ!âNFÄrˆØ™GÄÎÚÖ––:ÜÊ¹ÑˆxSDÄ›µ„[Œˆ0À0Í¨a£à	'´†Ë#±ŠS€‰üØnÉpwk@0Ö
‡b‚E[™·3$ØÊD=Cİ!»S¾wy!®ç™4<»;Á3j÷hKîÍ`µ³au_VÅÜÇC¥ÆºB¡©ÁİoX=aõ –ğaµ(°Úp‚Ùcâ#Xœ²ÈE˜ş)»áîá !Ö~b„Ì=ô£¹ ¡r!@	4Ë÷	âz€¤Å èÉ@OiõŸÎ ´‹ôL@¥ü¹¤¹ÔÔ…¹äYè¹ çµ„ Ñ\ğÉ+lÎå²8!—I$¾Á›™<Ì ŞnW¯#—{Å‚FdSl¨ÍùáîÅ ]6¤â^
ø÷r.¼hZï+ì«ò}ÍÃ‹¸^Áğ¾÷mü›xï[9ğ–s/ğ–ëj»
¥&÷¶ÁûNï»ZÂ{ïª€—ÏO@¸®Y§ğj—â¯Y.0a
î¡cW˜Ø‰À÷~€ëWqÄ¨ñP&Çç+ªÂõ¡ õ‘|?öp!®‡KÚ¸>ÉÀõ©6æ³\×ç9pu¼hs_b_ò—‹¯´¯¥ìb€EÁ¦ã&(%»ø–q’‹ï€ÅÀ÷üÅbàü&?
$?É÷g²öÀHKÌ/	`¸øUëü›M0E©ìïŒL00´ªc'˜?5õ_’ºaÁƒ ?Áü­ÑÿÉH¡dR˜f¥P¿û/ç?åÚ2lOËĞ/§ã/õËéñ”0~¨_ÒÃ¥•˜Zœ˜aîfdì”êÇTÜLÕÏ†Ê™Ì%¨RHÎY»ÙòMJq½¤ÁìÌ6áx­ôIæ£—–9s`éÎ}JÖÀ÷­M®Ê`™+‚en-aƒ…¾è:àã£¥¼–‚˜OÌöauG7üUjÜ¼P¬SÅÍÍºóç"…Z†H- -(ß…<Rˆ›i:Z8ƒÔ"ÚE3HuR‹å µkî¨WWhÅmë.·¸!µD„Ô’ZBµ!ÕÇQ>D`_W<ËÒ6¿^O£ì4´ Ì‹ËÄ&±îÇ‡zCåE]dT¯]à5¾À{'à2É$xÅå³î.¹\É©¶, ópó¥fi·T€<Ûˆ‹ß1òÿ2r¢¹!äËØËÊw99âzÈC@¾|ò31ÈWÊ|\.9µ­Í¸àV6ÈW‰ ª%3ÈwÏlåÔ¿ˆé¦oRïDV8ú]‘5(FÀøv|+€ÿ’õ^ˆ¶}%®Ø‚í*Ù‘¾Õ°ğÂ‡½]5®&@šMƒûäijs)¶†x×	Òõòmğx#®Ç[ Ş¼›æŞcï–¼Ççn”»ÊÅbm½k5¼Û"¼Ûµ„Õo­¥7’u	_Z
mE§*TwÊ«8ñe«;æH#/g™ìª™Ê(Ş˜NîÜÛÑèE´Ô ê=Lq}ÉXæÕÇŞ£‹%(q“YM[Š‹AVîÙÕ´à¦øQãşˆ”èUÜê©Î“sz
 Ca®!b.ß5½0×S¤a®•æÚ
õ:av›0×Íæ„Õ<‘XÏä¹>©vl …l(…dÕUq#7©v ”¬Ú±ã$Õ‘€Ú±1¡vtà7©vl"l*ßÍ<0ÈÚ#-0›'€¡Ú±…Öy”©»Je·dÜ@íØŠ¡U=T;¶ÖÔÛHêv„j‚üäh¾­D×¥ûvüw¸¹½Ò­ÚwàßÙUû8©åÖ"Lò½Ù=È´À¥À´ßÂÂ¤¾şqİ}ş¨pæ#0^ò.0,Ú†˜˜Ú†èÔ¬‹‰¶”¬-ñÑIújYÛ´[Ô¦®¼6MrÇø6í–l¯—ŒÕ‚»¥`\/ù¯íweŞC:\úêI”;.ÃñZÖ„4;z%nO.;zµ‘}dÇDM½›±£/d‚¼Rê4zŸozN´>:‰9g6='å^<mª/–Zê\?S@)Ì_*¥S´„İ¥„‘£ß±9&êd8Ô½KsZ¢0s6\_uõ;yú(
lªğı$wl![ux‡à';>WÍWemÛëà”ƒxäªUÇW¼Á]k\ÁáîÎrx^D»w:@k˜˜g£qÍ89PŸ6uG6$¢×Ó´¼½¨öïÛMIbıûy-&í¶M}atÃ+©9P—úˆ§ÙRµ¸˜Ä¿'Àõ-=Îö¥Ì óFìO€–&sUTËšêµË¸‘P¶‹ÿõu¸ö¯wåàÊ^wûÊfª(³V§¼ãÎhöê„zSéè¦ŸLy,Ã,kÜT
>µ¾ ™p¸Àğ¶–Á«pşÙ©pì ß½…B²²@ÜY1Ìî“èHÜ¥ÚW™·_†Û»·÷ÏáöäÜ÷y¥B[c¹®è0nqû -á`ãöAr©—?º’Üñ“;xR0 P=z*bÑ§O%…DøHŸ7PÀ1™éÍwŸPÂ¬géçëó}CÓ¤Ø©ö	dÀFW\e0 ı¡ô“ïá^ˆëe  BGddp¤"tTFÎdpt¦äÉ «¶¹©Ğ„gfÇ˜dpœ–p¼É`]Œ/ÆqµF–T™
]ìy£
İÒ­Ïêr_ësKÍ~dQ£Š¢»ˆ~#‘³†b»Äö«ä–4ù4‡uZéD¸B¯Æ’¾ı9Nöõ&—P[8Ü)-H ±áeDüÔ[«GÓÔ<Í­¬ Äx
\ˆùŞz’+ŞŞÀN3†Ë<¹±'ÆÃxOªÆpˆBÃÛ‡Á8ù…:IØs²|OñB\Ï!!8tj‚C|yšJøtI¦ÌüwFƒi\ÉÉ”U»G³ıYü;«ÁôI3Î¶B0˜ìœí9pœ£›!í$#íy9¤:°âZçÎ7Ş^À_*®j!I!YÅ•EÁÈã&W”’U\/aœ¤âz) ¸^Æ_(®—ã7©¸^!2¸R¾WyI k/	i)$quBT\¯Ñ:_«ÀDŠk¿Tö:Æ×ëU"{P5¹ASß(©Û(®òªÉMıæŒ&›nÉ‘Â¹ûe…Zlx[Ü­&‚ÛøKÕäv-á)aäèXşEæ»°=!bğê%2#–×ßm"‡55ê`^ÆèuˆÉSÙX\õšËÎêú±¾Ä”Ïx¬ü¤CO„•9øpÕ‹³²ÊÏ1eÙ‰‡dp¸»‚=BA}r®)ŠÙZøK1|Ú#÷S­eÿ†‡xbešrî«çÈwÊÔdOñà-Ãšì!©p¸[Hy|ïõÔD\OM?¨y_‚šì³÷«,È°eŠ±åÁ¶ì•Ç–¬4ğ‚ê!cËÃ[Ñ5¶4‹"+sö˜^h‘íH	°:[$eSÀ:ÜÊÊ#á;éM1HYUÊL2vCƒ¤°èæ®›H™5ö„¼¬õ*€”HÕlrIjĞEÍöp+N·do)à)…ñãÔl¤ˆ´€¼¤ƒfÚ=¡0&ŞŒo(xsè|1c@Ékßq]PÕ-·†q­€5ŒkÆH,dÍÂ—'åû”gâzÖÀš§3¬yFeúl†5»kËaÍŞôõîy#ÎüåHÿ¢ò’’éY¥0nr¤G)Ù‘şÆIô¯2 #ıküÅHÿ:~“#ıÉ›ò}Ëƒ¬=0ÒR óvôïhßU`¢‘~ªTö=ÆFú÷ZÕ±Gú4õ‡’ºaÁH ¿Eñ‘FÿX¢ëÿ	ÿ™à[VrŸj!ûFügü;;Áï!µüÜZ„	~ßìÅZà—R`z‹‚oç[Ú†y—ñ_1Ÿ=%ï¯mQìoQğ
Æ7šõ·QÖÿu§à»Tq{Iqß'‹Û?õ î-îÇ´œö–d?åÊég…ğ ÊéMı«Éé€PNò3òoıw-,Ş,ØÇzËÌ9³Yp`î}şÆÚÆºÎR‹û“)°Yğ9#ÿ­%ü#%Œ}­œ`™$.ÍÅß«®®`æã¥nÙâ¡%¬\éD…ÿcã8ŸÄµ²Ş=ÖÉV}ù›\‹ÉpVŒaÉñÊ®#hŸKFH,¶hÊµ öD%¶ë/ê®©|Ş‰KVX O³rvN$@7-ÃšU8ºM‡Tp¸!ßğµ0âf€N<#K°£5rq&ü4g–dæ3U˜ÆRhj|p&Y¾¯TxV†E,?(E»Ù4çÙ%ç8Ù~’l&†‡!­ê8˜´›SSWIêv„Ã‚<íæÒèska1íö7ÚÍÃœ3´;$vå®æ®úR¡ŞÍË İ|ü%íæ×F¾UŸGñæ½Ò‹°®ç¦??aO…S>yÉ‹Âeš¹î’ÿ33<›êiT«îñÜ›ŠÎÄÌ“$HæéÖK¼+é“Ûg¶_ /«àÕ˜‹@SpKZl“ÈS5É‚Bq˜K`R¯ánÁ€~ªâŠé[.Ìà€Ğ…,\Dø·¨|ó,DÜŒ<ÀÂÅ,¤f¶„‚»dF|˜øªsÄWÉ_C±¡©«¥­Ş-eâ[:ß2ZÂ²&¾y¯r`!82†'øà–U¯xÕáYšŒx”Ãîr/T¸'ÒóËµz¦
ÖşÉO<=mŒ‡|½Ã•Ë(³=·|Œ²œ­2‚¼¢À»’|Wö #®YPÈ«$@æõP…`˜$û?lP×0¿!‡¦7¨”6­š(‹ÃJ­–U'e²Á_Ï´ñ qä×À°h\9,5®4jÖMÊ•Hí8X’53Y0®´0´ªãp+­šºMR·#,WäÇ•v¾Z†˜‡1ÿ—CÌ#r÷‹õõÅb«[İˆ¹FDÌáZÂšFÌ:³¡vXmÓ°ºúauÃêš†Õ7c“¶·VÿêÙãÕvcä=ú·[+ k“P1Õxs ‡Ê†$[Gèµ®|×ó$C\O2A $[?!xöä´9f «`#r ;2÷° ¥®­ÜÜÙâ62ÀFF€m¬%t`· arX`G°}øşbbwÓ8æy¹pİ>§Ëb=ó½¾’‡UrqR ƒ®:æ¨i‹İä¶X§î–«éEíëÆ Ë\qÀê
¶øùĞCWV¸€-e¨k`ÍYö
º»à Šëİ&ØˆSÅmš[Îõ/@Šm3ØæòİÂ‹q½ØDÛ¨ŒØ¶TP·ÊˆíPÛÖ9b;*Ol-õåúæÆ‚ÛÆÄ6:Û¶ZÂv&6Z6§Î0ÛÕmfŞ©pÔT¯—8`1Ÿ]‚\$ÎŸ	™ÈKJq¶5ÚŒMå\×/²$ˆıÎÈ!WÛ>€í„å©Á`G“CØwÀw’ïÎvÄõ°€}—ì¥3ûa{1ö£^[Bå5äËüåÚ²K#…d×–,ªâÆ2nrm‰R²kËnÆI®-we Ö–ãø‹µåxü&×–’ùöz`µFZ
`&&€áÚr7­³S`¢Aşp©lãƒü$†VuÃA¾_SO–Ôíyùµå¾»D×µåTş;µ¶¬«©]Éí¡…­-÷äßÙµåRË½¬E˜1Í®-÷Ö÷‘ÿ‹Cç}™iÇ‘RĞ~‹¦ÊãRÍıµœ¢rşëBóÀTqGIq%‹;>53¬Å’ÚÑ’¬’+´CÏ(´Ã4õá&´B¡!ÈÏÌGhô#µ°Xã?ÆºÎQÌ9£ñŸ˜;37Ö×u6v–ÜÑLÿşRã?VK8NJ9š7İ¢C<æ´ÉAî ‹vO“ÊÔØõíªXdKnTıé›%zPËKıœ-Æ`à/À1¥`çWï©SœãYŸÔş)ÛXq'0| µ"šV'"ÒÈ÷di™–"nCtÊSŒÂ‘9ÍSÓ2´ÀØP¨‹×‹§§Øs¬TúŒ${NJ±çLÍı¬4{“dgç²çeÏÉdÏ¹šú<cÏÉ!{äÙs¾F¿ Ãã=æ°ç”Üƒƒ¶¶rK¹­Ó]dì¹8bÏ%ZÂ¥Æ©rp€iWìP{]Üüâ>~çø~Ü €ãínÕchøÊƒğG¶_'ˆe nØbY.KG²-:y-K%mk·áˆ‘K–Qİ¸ªFS°Ø¶àÕJÇİ	ìDG¹tÒ	[ì¤5³ÉÛşº‹_îŠ·~EÍ)ôÉ¡¡ßİíìÇæ±]P+ã‡†«iÒš2tÏ8¹s";ÄR];œ4&Î$j#Ó	°ÄÀÒÅ­Üe¯Ÿ	+â­ø›O˜º­Ã1Š»,èC”4^Ö‡ ô°]!½çJù^åûâú>$LâñX¦]£´¸6Ó‡fEÚ“Ê}ã¦ú}ÅëR=è©òõÉtjªİ yß˜îA'J²›r{ĞÍÚƒN#\šúVëA§…=A¾İ¦ÑoÏô “¬İ‘ÓƒNÏİq)”ào¹®Íİi=è®¨İ­%Üc=hÃÈŠ“§ÜKãp	ãåzTm+tÄ´X«ôr€á÷òhS·úÜ½!XñŠ»o0B !!î*< ß=!×B€!J‚¦‡µ•dp<Ùp|4Ç3Vİcåãü¥
ø„ò¤’UYTÅ=Å¸I¥dUÀ§'©>Ã ¨€Ïò*àsøMª€Ï$/È÷E²öÀHKÌK	`¸…ğ²ÖùIXòäU¦‹u¢S¤1¯1,Ò‰ÎLu’×5Û7ïH³<U’½ÉdfùC«:Îb'y[S¿#©Ûh–òä]ş^F¸§™pßÏîÙ¹«ázx,»Ü&ÙùK%å#-ác)aäèëe5,'vÆŒ!³àÔJ2Os÷‰ü’Tò‚4Ù°îvØóıCvÅi¥	åR·_c£³=å)('v'!ƒ²yx‰üDÀ–Ï;9ZG™ËÃEÛ¡Ç´†ÉÉ}Âæ¤tBTqŸ2| h…İñ3áÛçòıÂ³q=ëD`İ—	Ö±;~¥x~‘Øé&±or$vNî°­óiÁ}kû.’Ø÷ZÂ&±‰ºc×À2ö.$RPßp“`¹İ.‹É[;ş¯©Ñ10Áïï·!~3˜;ÍzºlæZxèOû¾z^¨ğfq4Şhkˆ÷Ï‚ô/òıÕã¸oxÿ–À›½üwEãIöÿfHòOfa†$İ_Ú=Ïe÷ü[sûÇºç¹iC’Ó¬’)ÎOË°h¤@ü„!Ééğ¿ÙôøIŒgJ²˜,×äŒü?Uç±:3i3KíFùÑb>«/iÎ2îÍÆœ3KšósG‹ÖB©«¡¹ËÍÎXÒÌÁ_C´„9¥„‘£«ù²=3~&â_¹“¤äpWÅÄ©¾É
ÁÃ²åŠº…\™©ğÎJ¾óJ5dı¸™ƒ+ó±„Ä3°ùµödğ9ÛğY0Ÿr7]å–·á³p„Ï"ZÂ¢†;.½®Ø®.”J|}¤·åô’ hàÜ˜’]&İ5T³­]å)<Ä%Ş>¼UZ,@U†ƒŒ‚9Û|¨}ˆà‚İ’ò­ö"®GP ‚Ke\ZÛ·LÁsÁes¼0ÁÖR[W3ÜcºåÁå#WĞV4#Ãø,FV2ò´…>wgñºh¥ Vv¹bl¢£¨UE¡z!DCœaò­ñ!®‡HÚˆVM@$'Ú€:IöïRÒÜt=³ğRÿ¬ê¸ˆ#@£æÖ$¹µ#,eÙ¶™1cä\ixÃ¢	ñR«fÖ¦Ò‹T—ó$Y;“åH«iu.fuş§9¬nÕ¹8ä¤54úğ]Î7º¬™C—KòO?Z:h“l-£ËÚ]ÖÑÖ5ºlàŸ¶mƒ‹Iv>7ëbU_¢‡êblOBÆàîùÄØL\mf¬qëÌb½+nı˜YÿbğM)µiCùğ”B\O)Á”Ú(A)ê#µ‘g`¼À`ìÈñÒ<Û`
¡“0nb0nÁ¸™–°¹ÁHôêGş–Ç8Fn Áâ+nTŒFÔÏ¶dHĞÏP¡”­­å»q=(ÒJ€2:Ê¶Zåí2 \h lŸÊe¯{šÜ†Ëüåºg'-dg)$»îaQ·ã&×=(%»î)0NrİÓÉ ¬{ŠüÅº§„ßäº§,tÉwŒY{`¤¥ fln}wkwU`¢^~‘Tvã”ñ­ê¸œ=|‚¦î‘ÔíTù­ï^>Q¢ëÖ÷nüwøòËi!WD[ß}ü;»õ}±Ôr’µóúÙ{ÓıZàäŒØ/1±OÉû•¹:Ng©ÿÕºİMæSùKg-aO)aäh>å†Êk¾«Å•§Úñ¡†3ª<k¼Nîöbú”šÃ:UÜŞ5'ê û0$è ¨eØAöì'ßı=×ó@šà'¢µI²ü‰h´-rÉ+6Öf~&:Dev‰QÑì5b\•‰cÌ˜l—JËgX4!~b&:B3;R¥qô2Iv“åÎDGku®fuÑµê\òA~&:N£Ÿ¡ÍåF›rhsMm:uÅ–¦®‚;ÑhsRD›“µ„SŒ6ÓšLÿØá|úO	4ìG5™o,†»S²°&p“å_æT*dÉéÂ3ä{¦g	âz–HKÁ’³,áÜr¶Vûœ0W0çæ smîzµ¡±T_.5ºó˜ó#`.Ğ.4`hËi-¬ı§Ò}+ïÛa{õ¢ –Ç	1Qß¹„!AßABT.<.“ïåÄõ¨H3ÊT®Ô:_•AåJCåêT®Ë=Î.Ö75v5·ºk•k#T®Ó®7Thb^qÖÅzÏyàÙ¶Æİ@ÃJTÜƒ1õ	1¹IĞ¸Y¾·xL×c"&·f0¹Mk|{“«“;r0¹>“RgsKkK[Ñİi˜Üar·–pa‚ŸiT‹33Æx…ÎKäÉqw¨Ş%§wo ë†=Ù€E÷ç²µ{@°zP¾yÄ×#& ±‡ˆq~DÛó¨$ûc~~œVuÜÀ!ï	ÍîIÉ®a©µÀSŒ¥WKËŸfX4#~b~F3{V¥À×H²ç˜,w~^«s#«ó‚æğ¢UçÆpF_Òè/gès­Ñç•úÜ”{E¯­XÛ\jhr¯}^‹èóº–ğ†Ñ‡îg¸1ÏÑ$Iõ&Ã6Á6üs-ÜŒ,`­3Şâ6ûx‰7ÁŞ˜ÄjVÜ[1“şexFC
½-äyG¾ïz
!®§À 
½— ‡ç÷µMdP»ÎPû0µ›sÏ±~j+Á ÏG†ÚÇjŸh	Ÿj4òµ¯‡±[Qÿ—5·Ş;æi	Ü8Òä
İF‹…q^yÒwË²“1±@"€’ş¥ÍÌm´Tã>peCp>Æ5ç¿`H0Î£i!¼_
°_É÷k/âzx/ÀûMŞoµñßeà½Şàı>Ş[^D4»áùËEÄOZÈÏRHvÁ¢*îÆM."PJvñ+ã$¿1 ‹ˆßù‹EÄøM."şHş’ïßdí‘–˜Àp1ÍP©ó´øI7He§C`¸ˆ˜¡U·rh˜ASÏ(©Û,"ä3iô™%º."fá¿ÃÇ—³j!·E‹ˆÙøwvq£Ôrvş/xXDÜ–5µ0‡8D
üOs2ıÛÓ·Uo’¼«,ïèbÃ\šßÜ’_pÔÔßh˜‡éâÁöfÉk^†Ecô©1z>Ívş´n‘dä
aAÅçN
a!M½°	áÎPòãó"}Q-,Ş<¾ÕºÂbÌ9³y|Wîæhg]±Pn„å'¦ÀæñüåÂjI-¡ZJ9úŒ4ës÷>¤ısäÈ­|äÏĞ¼Äóa£>q‡£1öÊ,2Tƒ÷ƒá]yÎæD×ÄûÅ	jd ¾)7eè	Û°EØ„H¸:WÏæ6òA[ŠmI-òˆ¬F1| s&@•c5
©p¥\¾Ë	*²—¸üÑA—ÏPnsÅåb×´­1éVJ‘î6©ïÊIÒİ"İ*šñĞ4én—dÃrIW£¤»GœhêZ#İ=!é”pZ Ñë3¤»ÃH×Cº{óO,ÊÍ…2Şß6éš"Ò5k	-FºŠl’=ò‘'èN¤Àß˜ı'ãüQo­èÓ‡ŞÇ5÷5ÕĞx×,pÑŸfÌ9zÊV(H3ËÌĞ„¨¯6»JÊ ^ÌjÈÄvÃÁ`d!™Ú…F«É÷LˆëÉ$¸‚L«gÈ´†‚4ü_ÈÔÒ“iÍ™î”ú®•$Ó})2­­¯“&Ó]’lİ\2­§dºŸdZ_So`dº?$‚<™6Ôè#2dºÛÈ´Q™È#SKC]ç6»‘F¦#2uh	›™v‹
Šde‚—5~Á’ğ/¬…Åˆƒœı@å,ŠQhòÛÒ±m0ÇŞ*:„Õ7µ5nÓ€6laÅm6mĞØ6›a¶ï(OÄõ´A›-´¡rº•Â±uğ{ğmr 0wEØÜTìjk©s£ğm#À·Ó¶7Àçâ%¸&¨NŠ{;ğU‹÷ğ´X{£<ÿÍ©¼á1s(¸‹İ·Ô—Õj®‚’WÖ7ú±O8ñx=‡œ6RÈƒ.éşvÄ`s†VL•`$ÈF qå2ü¤°L
:z7­ïšY¹®F#rxÁÛ{2*Á%Q)„W‘vø@À~Ö`|€,B>ì$LØY¾»x> ®çƒ|(døĞ©Ò*føp¯ñ¡”Ã‡‡Ö¦[pDµˆ.şR›£…Œ•B²Ú4‹ª¸nÆMjÓ(%«MïÊ8Imz Mç/´é	øMjÓ=I¯|'z`µFZ
`vK Ã §uî“d^?ä1K7hÁwŸ@Še)isˆ5Åû¤Yı‹4Å‡Sãìd-`Š"­æï—d»3Y°ç?•¡UpœİCSï)©Û¨ëòãì^}ïŒ˜01ï“#æGs7ÇJõm-0<½¯Éx?şRSÜ_K8@J9úwNÚâ5NúŠ9!ï5Jİ¸Z„]°2Q’¾9Q6Îxë”v“yswfq¡T_B2ÕÍUèDs>íQ»ò$Ü˜1#ŒØ'àÅ×Èê–]Jø×–¢¢Û5ÚÁÇöâP?=ş°H-…c)ÉúY9pÜ×ÚÅcƒ]	öòqÖ„%¥tjÜ¤gø@J'P;øÁÂàCä[ñ<F\Ïc%x|h‚Ç|x˜ÊåpIöxxóÒñXzMõ ´æÈLŸ9JË::Ógxd˜ø;&Õ[’üMö–ÇS½å8ÍúøtoyX’Û[NÔŞò{ËIšúdë-O„½A¾·œ¢ÑOÍô–G¬·œ–Ó[Ìİ÷êl¬-´ÁøéÖ[ÎˆzË™ZÂYÖ[Ú0I‚·ÜúJÛˆ£ºZSo 	ÓQbN<	uûàşwùÄî®’Ø©É¥>5D5…¯eHŞVq$„¯±Ä’”±;§›»]ÍÎğ"w/Ş8‹y_ü1›_âX1	g7­5Ißzè©jf
Şc÷ÅB'®òj¸]èÕG^’ÎìßøæÑH-Ş8‹^î§twvĞÙ(©Š;g°Î¡…í\éfçÉ÷|ßÙ×w6a:Û‰@íêBëEâ<jÄ¹8‡8Oå?P)šŠ…Vw‰çÒˆ8—i	—qä7EÀº¤!r¼-NãXWË‰;òÜ`ŞP†ÖİáÒD³H\Ì³0¬éN«²°9,ÖkÕ£.Î;(	y—Pã®DÀ6WÜ•ƒ‰ ÍEp•€µ|¯ñ"@\/Á"¸6#‚ë ë3"xÌDpCÎ]QÔµŠÅw£‰à¦H7k	·˜Şäî«¬&du /âù‹ûñÇ(­é€ÿ¢òÂzúí#}áÉÃH<'ç»!`lz¨zŸñ–âŠWîê‡„¤ë²X‡ê[S5Õ…©è,Ô>“K›!“>ÿtnäÜJÃAæÅ²Mt¯[ÙL¸L¶À5”íí"Õ;ä{§—-âzÙŠ° Û»2²½[‘¿'#ÛÇM¶÷æÈö™ü<-µewŸÉöşH¶h	šlß£Ó%8B,:HAÙp°"Ïd"iV¯¨íp¯‚š?v»°Ø@µ½Í¨	‹Ü,Óç4ò,ŞÔ¢"‰`ìe66ªò½Ì$<"s½ ë!ëŒxÂe«<}0Û2; ßxÂŒh):¨›&EK„î¡@ÀD´âLÀ 7ğ#"ÚGåû˜0âz‹Ä àÇ3~Bá2#à'LÀOåøÙW#­îi“ñ3üåjäY-ä9)$»aQ÷<ã&W#(%»yq’«‘€ÕÈKüÅjäeü&W#¯$¯Ê÷5²öÀHKÌë	`¸·ÿ†ÖùM&Z,<)•}‹qƒÅÂÛ­êxêÏ;šú]Iİ°`±€ ¯ş¼§ÑßÏHá)“Â9Rx>w«‡yÎ®r£ûĞDğ¹XøXKøDJ9ú½¯ÃG:ı—Í õË+CX}]Ê*Ÿ˜Ó£š…ë6NÚa/´’”YÎQº[›íëŸHÛ-²¯ V†2†ó UÑxkÔ¹d!™Ÿû”mN­ˆcÅ}ÆğV€4ì\Ÿ{¾ï—Cˆë9$r‡¾JpˆÊÉ×
ú7±>mbı6G¬/äjµÅÖBg¡Üê¾3±~‰õ-áGëLÜúÑåµT˜W)¡éÑj©Ìe˜¡hµ†cØä^5ğLûÈ|YHiÚH)bäoÖ—1AŠµjÆPFôr<ì”Ê0ğ0ÌµI4×ÅÆra‰‡ÔŠïÅ›Dq©¡QDV-W…UÕ46İÊ_mGÄS}r­Zã~
X@Ø+îçÁX 	„,øEäÿ«|ó,@\Ï+Xğ{†¨ŒşÌ°àcÁ_9,x1xnĞV(×Õ»¿ÿD,˜f˜”0-~Ø¹¯¤å]ê}Ô@UÅÜ&· œÊJ7˜,«İ<Ìïå|‰ŒèËrÎY}Ì*‰ÇÙ~‹¤‘˜çˆ–ìj™Ğvİbã‹	r%|zû9×Ş¾f–÷Rª˜^1UÚNlÁ/Ëğ8\-0Çt—eUt…ÍÎŒ‚•|Ëj[ä)ö=t“r7Ne„IŸ]¤ö!XÑœ†àÅ°·!ƒ{+Üƒ_iÍ©?Øv&LE²¯Q—±w’ÓApé‹ä¨¸é>Ğˆ„\©p¬,ß™„r`†¸«B>puf–xü1‹2iVIæ£?k\Ñ3ç›/¬´¹Ù™ˆïcøKu`ˆ2§’UXÎ7© ”¬:0ã$Õ¹ u`şB˜¿Iu`>d~ù.àAÖ™–˜ÀPXHë¼°©ÏIeaÜ@X”¡U/SXLS/.©Û¨òGıKhô%%ºõWóß¡©Œ¥´W¢£ş¥ùwö¨ÿy©å2Ö"Pá•¬©ŒeµÀå¤@¿õ:ZB'ñüà%I|Âµ<3‹axA
XaÑÎë«)+jş+EùÿW+§Š{QŠ[%YÜk©­«¡ZÜ°´°^’d5¹ÂZUq|ÂªÕÔu&¬×Ca!Èënõ½A‹¯¼l]¦‘9gºÌyÃ{S]}m±¡Üæš˜ı¥™¿ÔİZ´„V)aähú×^;ZËÆ~jupÂ·wİ%ÌÓ4p¡ÆdàÁX…­Rî½rù)$:VÊˆÜSŞ]6$Ä'·x›—‘cîÉğÆm¾y8ÂÕ¸6Ö-¥c±½x ÃğF,4=±VC*œÇÊwui¥ŒXˆ›Ás£qä¶v¸‚³fşWşµrà3÷±UC©¶¹ÜÚìÖ6ø×‰à_WKXÏà¿³kg-yŠf%Ö§rÂf7,¨¦ğø‰çÇãôÊvó"\fI©Äs-;ğ–n¦êì6¶·¾8`S»Jr¤ßÉW¿²]dOğ£UpôL»
<­—»fbH/Ş£÷“¡<,î§¥k½ÀÁem5JÃ|0¥!'ûØÑäõ z´PÆi‚‹&X+A›¥ˆ=¹ãâ|tP¹äfôQËø&\”³ëÆ?½Å¯`iµàŞ¨LÇjúši“Õñ‹j5B`v¡ÀRWª®P•Ü¨¸£*hRuC!éùnä©Š¸ªÂ=Pud‚ª<àÚX‰Ô!ÉÒæú°¡ÄÃ¦x€İ„iãöU©ñ¦‹Ø·R#ŞfšõæÚ¢éé5I¶“ÓÓ(†Vu¼ÍoKM½•¤nGX0=!Èx[kôm2]îuër£sºÜ;¹~¥Úb±³¶Ómk]n»¨Ëm¯%ì`]ncnø™%HŸÌ_‚Ó­V2'2©M.F÷¡ËpÕ9ô’­˜·cÀ	V¾âvŒhGÈ‰…»È·à9¸8Ñ™áDQ[ZÊpb´ë©rY§^äYNñâ©uW’ï¦x1F³›æÅ›’¬;—»*/Ş#/ÆiêñÆ‹÷B^ Èób‚FïÉğâ-ãEo/ŞÏ}WÛV¨Ã1›h¼Ø-â…ÓúŒ´/ªŒd“\ß«vnPÈÑÇD:f£UbÑ—q}y><š¤¡W_:ïÑ@QeR@¶çÌƒQM©2YH2E¾»{ª ®§ŠàªLMP…»	{hã÷ÌÀû¶Á»W¼ä>B)4Õ7·4·¹½Ş}"x÷Õö3x/°»áÖ½¢õ7gyhl¹İß‘…¤^wNí÷¨mQMJİğÊ[ˆ-Z8¬ä^j‹SnV°ëJE&ñ§Ä£X¦<31s˜ı`àG!û""&wÀ`"<¡ˆá$ßƒ½ˆ×‹H0‡ˆÉˆ¨¢ šÑ;&¢ÃrDôaî>^©¥­Tn­s‡›ˆˆDt¤–p”‰hy(#£Àcó*)‹¥’wìXH÷Ó”š»2´a CîŸ/½	Ô“2#ËKsš`+ïÄá»u%¸Cˆğõ`_ïÉ;İú”ÊĞqáİĞSàZÔ‹o¢GD£ ø˜Ã3ìİ™Ó‹Ô ŞÙÛX6à1Ä÷â1‚¾†Š8'ûê°£ámŒŠUñ=
êk5Ãˆ û€¢Ô[ãXB±TÜ1ƒ±
Yr¬ğã8ùïY‚¸%"v°ä„KNT”aÉ»Æ’“sXòÑ€‹ì†ZwŠåTşr‘}šrº’]d³(˜‰cÜä"¥dÙg2Nr‘}°È>›¿XdŸƒßä"û\ä<ùïAÖi)sÀPAºPë|‘$ËUüË‹™6ÖtŞ“]Â°HAú85^ªY_¦˜G
Òû’ìr&¤+ZÕñ	'Â+5õU’ºa‚„ ?^­Ñ¯Éøğµ9ş4wÇ¯­±©Ô/±×™t¯ç/—„7h	7J	#G+á8˜‘>ÙWÆ0o@uöw/™ÇZN‘Ôë-ªØ*’[uè¢°å:;…İb¤½¯«9óÂ*®kúk™‘[{¿aO¶sQ®YFØ#ŞÈ¹‰•M­	@ÅİÌğÖˆÀ"ìp·£n•ïmWˆëy% ƒW·'xÅ™óEëÎŒ<>4yÜ•#ÏòäÑUn¨o©«msw›<î‰äq¯–pŸÉƒ—FÈRŠHšIØŸ(öœÆ0Hô:B¦©åÂs¼D²)Î.³òp’Æzû
¯É8è,‰é]¹p ÖÇC*aØãıµûq ¶¹âLh~(‚ü‡äû°âz¦Á#<ª =–ÁG&‚ÇsDğyîÓâÆúR[}]«{ÂDğd$‚§´„§MK‰)ÈN.Â£›£RQ—×¶RHÀ—£,1yB‚nİôû‡NdBŒwyŞa»&æ“³PÙ¹Ş1âË’öğdöéîÙ­¿›ÊÑCxî¡kÇÄ=ÜµUI¢RGÕ«yV ¿«ò5ù)z’r"¯Å™mSêOì£|«ŞídÍ“l¹©É‘QgôsôÑg‚P"÷ì`pB‚<'Ôx^¾/x‚ ®'ˆHy1C—T|/gò±ä•‚|‘»ÓÒÕÕZÛĞé^5‚¼äu-á#È3è£›FOˆ±âÅa*Œn9ğ‚v]pîUFgĞ#‡€ÇÇŞMÌ,œÇ[m‹o-§/‰À¨oIô$*ÃØá@M[+Üz³Ù ’Î1@¥ã@@Sœoâ$~8°Lœ€2çI¦òù¾ëÅ‰¸^œ">ÉÌˆó}ûƒŒ8?1q~˜#Î/ÖqêÜG&ÑùKç-äS)$«ã°(ú2nRÇA)YçsÆIê8_0 :Î—ü…ó~“:Î×É7òıÖƒ¬=0ÒR ó]ê8ßkd^Ç™lì„WœqñĞLk*ŸJk~bX¤à|•Rp~Ö|QÀ#ç3Iö+“
Îo­êøš
ÎïšúIİ°@ÁAWpşÔèe¤û¹I÷ïé~“û®«¥¾¹³±Ùıc¢¦Æœiñ”0~¨àÜ)£¹¿¢?°gHÙáŒ·à¢!¾5Íÿ»n­év wU\€õHA.jú3<WÃ—f Q¶¼{oË¸ÚœfwÄ™3¦n§®%>dZæº†‹™×a~W÷ÕùÒÁ	>X¹úÓÍøÒi|+TXô+LÅ%Áh#SW¿<¾ç[aL&b~Ğ¶z`9†™«&S¼­4³[g'†«	e^ˆ‚“f<U–pz±›£$qã@oLæáVÙyuIOaÍ+v‹¬ÙÕ»±\§Á½;'c¥56ö^(æ-%ó7=›RI˜øcø@Ê xL3"7å;³PD×w@!#:à,,!á‹iVeÖl’,ıÌ ‘ØÔ×Æ=qvæw©/¤Şs0,ê‰ß¦zâ-`N) Nö¥$«b² 'ÎÅĞªïØçÖÔóHêv„=A¾'Î«ÑçÓÂâÓ§¯¬'ÎÏœ3§OßçêU¥fXú)¹˜§OF=q!-aaë‰7É3ƒh™‘ä\¤ûGN²ãi.;pÁ ³º)5HOÕ»q¢¬âgz@•ªè8ÁïêaæE<Õtq·fib)p][ ¼' ²yÀ€pæ_©Ö¸E
¥Š[t0
°‚‹	ù—ï‚ˆ›‘(¸d†‚Õ
éR
†sÀÒ)æ}-Õ]&É¼RÌ[Vó].Í¼o$Ùò¹Ì[A™÷#™·¢¦^É˜÷cÈ<yæ­¬ÑWÉ0ï[cŞĞæı”{
ĞV.táv“fÌ«‰˜·ª–PkÌÛA·#qéµ©fĞjÇÁ`«_y’Bâ)ZÆºØ¬'¹ö.Ôpó¥Tñ²ÖhOuAØ˜Š«Œ hWH¡F£|›<A×DÀAšá‚µE[ŞšÁö;Ã¶-ÛŸÖê]»Á»©=ıOY]
ÉjO,ªâÖ`Ü¤ö„R²ÚÓpÆIjOk2 ÚÓZü…ö´6~“ÚÓ:Éºò]Ïƒ¬=0ÒR ³~^ÃØ@ë¼¡i9ßKeG0n0¶nÄĞª_Èğ‘šzcIİ°`lEgx‡Fß$#…L
›æHá×ÜmœºúÎÆ†r“ÛÌD°9¹³…–0JJ9ú~0|i:>¶ŒNıNko'¶¼qŒOÇ_c¿úÔWl³®#§ª€(íı…I9×­¦›ÛríkEÙ6-`½+2gÃ Pó½Ü £›Y(è0úWF¯PC¦ê,í¶dóRs=!«¸­Ïõ9–X^Ø¶¢l#ßÑ.ˆëé""]¶MĞ…ıh;ÅwûŒ4	î#Áßr•­¥RKSÙíhÜ)’àÎZÂ.&Áï)AR‘K¨_Ğ‚ô©]%ÅŠa×xyê,‡Öv/ŒÒÖ[vØ|à+>œvëy ‚ğİ`Fª)úÀ…“zgÂI~_7½2‰‘\yÏÀ<¢ÇE)Ç•'"_'‡ ú¿°Û!.:QÏ.\ê”|ÆßWÚÑµxš’˜¸å@|K»B qB\qƒIh‡/Š¬Kò-{‰#®—¸ˆïÊH|ŒÊclFâ?™Ä»s$ş{®­„b¡±±ÜÕæv5‰‹$>^K˜`‚gÓEŞ¢54×šÔ×?®[¦ıô£o“‰1<ÌÙáLôTL*hªuÊ>\¿(Ê>aô3~³5Â£ßŠE1]®—EttJÏõÄˆ¼^íVÊ±ZüŞHÑu­B]¾0µÆõ¢$v×›e“;ÀŠr¢q7ù:/JÄõ¢Ù@”}QNR û3¢üÙD99G”<	6¸)&ÍİùËIpª²‡’YTÅíÉ¸ÉI¥d'Á½'9	îÍ L‚ûğ“à¾øMN‚û	$ûË÷ ²öÀHKÌ	`8	¤u>X‰&Á_¤²‡0n0	VZÕñ''ÁC5õa’ºaÁ$ˆ ¹_q¸F?B¢ûåÒl }ô »Á_O8’ÅUúUªtÃ¢¥Ò_)…õhÍü˜tK~“dÇæ¶ä8mÉßlÉñšúkÉßaKä§ó5úI>ın|:9‡Oÿä*¬M-åfwŠ‘éTşr:?MK8]J9ú1âh+v>BK<õ‹ğäv04ó¼¶5Ñ^BDPråà@g~™åõ¶ŞÌ²ƒ˜è6Vbåñ<ÚÁ;mŒ9Øfî,c<ÑÍi½¦¥¥§ëñõ2L3Ø#î.Ô¸3Ø®Ô<N¬*îL†´fláPp–pılùã¸ñ"0şÜã9Ÿ§ÀŸİ&ºrD7ÍLc×Mƒ‘“º'î¼k¡§¿à¦îÜĞR×ÜÖĞÚæ.4Ñ]‰îb-áİ$®rÕ€’N:ªc%[¥H¾Öµİcõ”Ô%C¼ºÑ«CğyÙ<º`9©·_nÖ§¦‰wi€9Yq—†9Úb~¹ }…|¯ô˜#®Ç\@æW%0gÇ¿Z¹F’ùOË¤}e3èK5¤®-Ş(¹–YÄ½ÿO©øu‹zÿ´3%­+^¯%Ü RÆ±¿$ÙLŒc71´ªcº™ĞûoÖÔ·Hêv„ã‚|ï¿U£ß–¡ĞßF¡Ûs(4}…Ê]µ03,w…îŒ(t—–p·Qh²œR©‹ocøN¯š;it+R.h€r¡BŸm˜–ŸpäåêEŠH··ÓB;4€ã‘{±™wï`$B‹Cİ'ô¹_¾x!®'‘À=˜!ÑCŠÉÿÇÛ{ÖQ$ÑÂä"ç`L0#”ÁØ&‘ƒX‚¹’®laK2-ËÆ€ÉpÉ9³„]X2KZâ’—°À’sÎy‰Kïœªîé™î‘î{ßïÏ\«İiNÕtUWWW=0ÑÂü.é´'n¯^|<’a ?dÒÿN3Ğ<zT{,Ë@s,Éfç2Ğ”æ%=¡­Ÿ´4oÌ@(òô”V:` 91ÚäM§›grh¾<ªïîì¨í€Ÿ÷³–sô¼ğ‚e °y‡Gi¸c†lŒkÏ(§{J|¸”%ÙòRâg“Í‘ãõXš°å²4£ÌÂãO¯íŞÀ›ğì‘¦;pä>DbÌÁqÈgıMÆMÅéÁ™Ê'j§©¨`s6sì¼±:	R2/•cuĞ&fõ—…É_‘ç«ÕQ×³º¬şZŠÕ)£^Wê½ğÇ\–?ŞÌáùóø×¤»ªjó–å·¼£#¼kùc9I2TÛ“J	Ãd -ˆ»¬”è3o¿K¤mÉ)	ß—º–rÊ¢’¶$È5{ˆÉ½zôL’daÆ‘866T\à	a&IÊ8,k8jÅq6©¸-ÍKÚ8Š‘#îäèT9$·0D'Îì{f Š²M`Á±y/â‚^2ï—ãàóÀBıåù‘çÔõ< D|œâÊÌO”BŸJ³ÿ;™ù»H„ßÜ2ñÿ²ÌÉÌ2KŞç:ÂÊeNfÎ#Í¾d³Hf~ÅÒŠ¶¹ä}­­¿‘Ö-(‹d&Šü’÷?­şmÀÒóZ–ş.‡¥Êcé¦ÚBcW}UµùŞ²ô¥Ô~²,ı(¯¶0,Š$2È%<©¿ZBÔÙQ‚ˆÑ]Cƒ«¸D˜¼Î8DbÛ›,™¸'ÈØa™J5°2vö`X¨op:”í8¬Äú©ˆ¶»Ä©.hiøs¨©dı^ÍÏ_¹’ù¥_Ä˜/üM¿{¾D]Ï—Bğå)¾äÚ4ÇóœøIŸÍg	9ÊÃS¢…IÈåı¹±¡£¦»ØÔ4±¶ÎÌÍF8(š‡¿ÜJÏ«ƒÌ'ƒ„[iU2ó³nz+QÂ­ô¬“ŞJ/Èl¥â/¶Òã7½•^#L­<“Áå0]{`äMLûHø^\ç¼„ã>§ùe²K²nô9-ÅÒŠ¶Eø9-­­—‘Ö-(‹>'ùk}Ëjõå¤º^ë[ÿ"ø66+è ‹Î·Í‹,07ùwx­o™åJöğÆ‹r°É«N>ÇíİWÖW‘³ş”Qt¨UÙO‚À‚Ò÷j,sëĞbÉ:Ä W#´ëÕ¥ëÿA®F²ëEÛ*dÊÉ°É°kDZSÇZ+K¤…¥îÚ¹D¥ø-N"­£­G["-	E©c-­¾–¨.b?•1ì98P]"oÍk¨+TÕ×VÕšõÙßI%i%Ø@G¨’ZÛgÊ±–—æ”ˆ»¼$†Nœ1mˆÕüqPİ/^H†	İé IÊlñD ÄåÇøD¨÷hIq<ˆ[YSqâÅ9evø|Oœx±|8K=^9çÄ­pâ%Ïzy;ùQ7À‘'^)Ë‰—‚ÒÀ¾¨…½9ö%ó`ïªï®«/ÔT›û†öt„-ìÊöVxúÏ97w¹ƒ ·œ«¥j"V‚%®~bÆñTàk–ŸË-Th	za¡U˜	5–tx±Kˆ¨$ä%¢TvÊõ6›ßNn
¦Œ<“xMßúmˆß—Ñ„wïÍ&	ZÉŒ-GCàÓpS¡Ş8y÷4D]OC!
h8! áfŠğæ³4Ü"‡†KåÑ°º¾³¦¡º¾Şlii¸•£áÖ:Â6–†½BÃDÛ#º8ÈMV±wÃ­€~²Õ‰³b	O<ĞÏ#r¾Aª<.h.Èå»¡í;–×&äFÿ@¥iÀæÛ•Ì¶åÀÆ‹Æ`·	ÌÛÉs{6êz°=€½C ö
ÅNØìsÀ^:ìæúÆ®®î†F³‹{Wön:Âîì·Üe+1[9ÇC«Ë#IR…*xÉ´ZF8åB1ìc6h+Ï7˜¥|€}Ò\–(t$@’ÉW‡
8¶§?¤é‘«\ô‰tÔÖíY<>Ä·—¾­j'-tÌb´nŠ$êWT.€ÆŸ¦ÿ‰Ø°¥GTM{D^âY2{”#/ Éû'!ìòÜË“u=y…^ ïŞ)ò.‰õp¢4S]a_ş;ĞšF›[V´-ãt…şê
‹ËktÚA°(/“Ö8`—XLØm¤ug\¡kÃU¢Îuºq„*o\?ÚLÒ¡—uCOÎz	ºÇ½lzh®ıûéĞSV^Ò²òÔV^nxí´ŞôZnîã/µÓ~dšj§ªdögİ´vŠQBíÔ°NZ;`´Óéü…v:ˆß´v:CÈ?Sx&@×	äMyã/ÅÜN¨s>Hšç+z0&ZÔRò6³Yæ”·å3›ÈC´ßCp§õ.-Íc3—Ö†»s\ÚèŸŠ}×áJí¨T¡=)=´ ,Ò|Qä5ß£´úÑ)æ:Æ2’vàõ²uª+ÁR%dEÇRÇæ±Ô22Óã<K­róñ:à	©O´26ªØ0Úœ¤Ã­ä†;9o¸ee¸Süp+…ÃªÃ–ît;\3†ƒÉlÚ¬JX\z:+á[1kœËLä¹M#h ZPÇ6%5FÁ|W±§oãšÑæßÊn~gæÍo9™ßY~~+‡ó;[çwNj~çÚù­.7Î§²cRïD¦®±1Ïd~®Èœ§óXÅÍãü¼y,/ó¸ÀÏc•ô<öCÿYçq¡ÌC”ÃUç›¼oj°‚tq‘íßQ‘{™hz±6½Dš®qÜä5ÛIHN’]æ/l²öv6—ÉxÔŞæ¯RßÒ¥Úş2)Èczo–ä$ãoì.ù2V”Y]Î2÷A­ù ®ĞÎ¯”Î“f+I³«Ø,ÚF^­€äÇt¶¾VZ· ,ú˜Pä?¦ë´úßSÄ¼ŞÓLU•µ£Í:Èj7æQme™åMjk¤©Æ¥ófğ2`¸t®"Íoaó[øo;t]“Kçâ ĞLœ;2`Ø caÀ„cneU® “ïš|7z¿ß;ù¾ÜîÂ?;1w°KêüÅ’úOü’xö}—Îåî,Ò«Ê$îqH/Šq7³ËÖ:U•Õ£Í½ŠÄZ„û>íâ~÷Z1Ü(òÂ´ú¿tÄdC¸š•N²ç`C¸6¥cÜ8öœØT¨kèªÂÁãC¬İàÃüånğíşßÒ½w{­İíå»:î<¹Çôã.,\ÕÇ½¬Ã#YÖ&,¶`Õ”c+.¯5rn™]!_¶dcy²+ìŒ3Oá½c-èq´B€Iy>!o)>ê`B >i¹Ğ0Rp–fş£] É+óêbòÍ>ÃÆÉÇ7B¦ü,ËÜ7;*ùf¹ <§}?ïúşIôBf¸Õe¸ÓÃ­“î%îe;Ü:íópá-ôô¶Ï…Tw´Ï›ïºÀâg?ùF_a¯6Û]uµyUyy4yù5íõuËË£/Ğnºy#3Å‘2Å7ÓSDı”gü[ÚÙÛÉ™'‡Ûİ‚d—L)è (“ìÀºK&ùNz’µæ]äºœä{Úïûv’ëf'ùAf’kÈ$?LOõS»´³¥³„ÚkJ³OØ,Zj?Õ©¬Ç©|¦­ÿk§²^üí£ÈûŸkõ/t°äÛ_Ë~û_²çàÛ}ûõ5õhÑd¾bu|û_ó—ßş7Úıÿ¤ûÖö5èÈİ‘8‡¹+GìÑ?8
_iênıTzìÁİî[vù@9#\bùp(& ß£.ÉóG™Š| ¨¼1>ĞŸ8B*^ÜÏú¿ ­mú5 õ#€j;šº›ë;Ío ß@h÷sT)@4Glƒóªó_‘èDS{è‚8'êd1á$‡åÃa‚ùÄ˜ÌV³Í<òœWFLP×c"/	Læã)LæÇß˜ôÒÌWe1YÕ¦©Œ0©©/vÔw5tš…XL³0É4‹h÷‹ZL:‰	XÅzôˆŸ/£sB+âlº6<#.Î€ÿ)ÓëNîÑXÊ’¨¡Xjƒ¿'×SóÀw±_¾n´”Ãïã»¸ »„<—ôø¢n ğ]*Àwi`™ ßu,¾Ëæà»A„o]W.××Ô˜å,¾Ë;|WĞîW´øî|5´¾ 6ËzzÄ HáŒiÓÑŒHCÔÖkKD.yu»Ä×¬aÊ—(™•ËaŠ÷‰1]EĞ\U«yLQ×c* Ó)L©˜¯®/=Ò7«Ê*æ£ebkøf‰b¾¦6]KšfsÄè2k³I¢˜×8Å|”T§^GÛ–/ã‡rY—ı%ëşº2­õXæ¤|mF\ŒÑŞ×Wfq[İõ¤Y%›Eâb–V´ÕQ\Tiëjiİ‚²H3G‘×Ìk´z­TW£Mÿm ™×ë õN3oàß¡ÑfŒÌ²Ñbå§>ÔÌ›tÀf0ÔÌ×—æ-lÖÌ†ÔÌ7dÕ”f¾ÿVÍ|cüšù&,f>–¿ĞÌ7Å¯ÓÌÇé\Æg‘®”ILpHÇšùfŠD#áŞ\»ØÂÂİÃ"/·Ôê[éˆ‰tŞÀ.[³ç`¡mJ/äÏ‰ˆ²ÓQWh¬7Û°:ÚVşr¡İV»o“î[Ûk §Ë¦d{å*š3,ËéÀdÜÑ†xr7¿Õ#Ü†°7AÍ Îp¯¢0B<üñ‹ÆÉ^¤G³–S{åœçpœì—ïîñ˜äo‚âšÜ…ÃÕÓ$ÅÆ•KFhâÙ…ØA±é¹S°%Éx|Ò_FÒu¾F¸CZÀ0z08ÉİOÈéŒæÓ[˜‚kWˆcÀtÓ)!?'+@Z¤£èpäÔ±†$í ä.Å]ÅÆ×GMõ‰Ç¤ñúSi3¢q7­Îö.‰ÜÁŸÖZ$)Pd!–‹·2‹\¤äŞ÷¥»6NlR*œÀ$ä¦BÔ*õX
¯ğ›íÈN]ü‰`~,N/«Æküh…0òÜISôÔøküÎváp‘2wQ~Ş5ø\ªìç²[ÎçÒ}.ÕõMİÕµµfwû¹´»ÏeíşOös¹rG-ˆ¶{	GÊ„r51£Ò—°­å_*»»Áa#Úgñ–5#KôL‚{…2Q@g	Nc]›Cc¯(£*>Ú²à°7C|\20
*çp…©ğbê*ô5íİé,Ñ<zú9rÏˆtÄªdö*G:À“no!Ú>òœèI‡ºtBnßé(#Šm‡4û¿ó+êd‰À«–‰w±ÌÉÉ–DNÒ_Ôºæ¨±Ì1)‡96Œ˜Ã¹‡˜É–9zøKÒ~Úıé>T¤d¦²nÚúşCë{/ë¤­ï},€@êç/Ò4ü¦­ïûÜFttíA—wèÓS ÓÔ4¨s¡8Õ¡V&;“u#Õá –V´mDY6K[(­[P©(ò²ì ­~p€ÅvşÇgMWw>sˆÅÿPşR–¦İ.İ·¶¯J-ïÀŠƒ ST“›‡Ö/n©¼)—69r˜	–9Seú¨aS†¯lD‡Äiå=&^(´ª²j#u:D’O7§X’†€¡‹2ß-oÓaG¨9C”CCqœZ4š»]r·qî±zØóA‰Ë(±²M´±Ö $™õ˜—Ì‘,n=ÜñG}”pÖÑò<Æóêzş‚¿J)ş¢Î}¬Òä8ßllVç®—‰ï›%:÷	ÚôDi*:7Mbb±‡3Z9‰m¥{œSºO–ú\PNÑN•,(´¥#4ÍŠSÅ UWh—,É½¸XS¢ç4öi­P5õætåõñäõ3´·3-¯ÏxÎbÍäûi—:›en%Bı”çíì\ıÜg×(ÍÎc³è³;_§2S¹@[ÿÙNeBüÙ¡Èkìjõ‹¤ºjìóß±Æ~‰²™ÓØÿÂ¿C½IfùWK1æÍBıRğ20\›¥ùßØ<­±o>¤Æ~9«¦4ö+ø·jìWâŸĞØ¯b	È«ù‹òü:ıZËuY¤[dwHÇûõŠÄ„ûíâF÷1Ü(ò«ÜMZıf1ÑØ7´«Ü?Øs ±oÉUnÉ4wO¬®k®*vv7˜[X*û­üå2w›ö»ôßÚş<šiôæw÷ÿ”äFóJes—`=cìé^†™m…w£aƒÇ2¦^YŒ¼›}‰9¹Ÿ.S:°Y³}@Œ-<î£ÿTÏ/Ñu4‘ ®óöhølºWØh*wğ…3‹!,™;Y>Ü"4ãEìŸh…èxò¼[ ¥ua»Çò¶S*ïUÄï(º‘¥èı9İ*¦hgGc]g'¸,Eÿå(ú öÿ¥èétE$åîÜÔûaÓrâ‹ñÒ	‰ÓôJ²»ë°aâ Èw¬µo°·ƒyüºm¢#w¯Kœ±Ë£’ièA Jæ‘rô 1=ş-”xTyz ®§‡ z<Ğã?Š×=6¶ôx2‡[Çôhèjêlnê®2OYz<íèñŒöÿ¬¥Ç± P2Œà[›cWxxKl;Èp”ÌxCªù÷Lz'K>t¡_“ºnAÄÃ:	Wnô<—©i«dB8$óaxÁŠqœáœõ\D¾vÉ<_
@ ¦Â‚ÿ‹ò|ÉSu=VPáå€
¯(J¯TØÄRáµ*lS¡ª
ŞÖÅ*óº¥Â
ojÿoY*ĞmŞ:¦Ófö	÷•HæJä—ëà°#âÛ¹,1`ö8»Å–åO.ˆ§şs‚f,$uEŸJ.—§RGÙô`’S¾~YÛ‘Lüj«è…³`®|m=Œé+æQÉJñ+ÍÛ‰[É¼SŒ€0&ã»BÀ÷äù¾'#êz2
]@Æ2~¨0q¬%ãÇ9dlÉXÛØĞ]hè¨6ŸX2~êÈø™öÿ_KFı24¹ÄÜèg\s\t©Íj˜¹0µ·vÚ<z;y2ìÄ™›kkæ/ôÂp¢q"(I˜V’3ÑÌ?àºN/’Ğª©Vi>ÀçÛ–ÌåÀÇ‹Çà)°%Ï¯=ø¨ëÁ4ş7)ğ©ÿOÁùÖ7Û6«o*ûÎ7KÔãïµéÒ4c’¦ÁüÈ&‰v¼Ó’êÔÖö¿HAöØ9¹úš;ÿÊŞ=uœLê7–9õvûŒzû»öı‡ò”SoÇK³9ªóÔÛ9YZÑ¶õ­¹ğo´?ÜUîë[(òêí<Z}^©®êí|üw¬ŞÎ¯ƒìèÔÛøw¨ŞNY.Èÿ¢£Ç¢¨ºqÀ}şB:àÂ2`¨Şn&Íaó´z»Óêí¢¬šRoãßªŞVàŸPog	ÔÛ%øõvIü:õv)ËÒ2—éÍeË8¤cõvYEbgÂ½œv±¼…{çnyõv­¾¢˜¨·[Øõb%ö¨·»¤7ñäÎ‰…†úÚ®j³2«C»]…¿ÔnWÕîW“î[Ûûpÿo³âÀ4Ä]ç1”˜® *2ÖV«3:÷ŠË8•MJ´¸8‹Æ9uñ…AW\CĞ—¿D%×£ ñqnh]å%ú~½¬¶š±ÀŠmu3äŠ££<“ÌÙü2.4…È¸)ˆZ`ím°é"˜Ğy ¦›ıé#f1VîLˆ~íE'êŒô…Ckë…!Â%-œŒ…¯·Ÿ–j—ÊÎ\Î¾¿,±62$±`HyX€¡Æ™“×özŞ’"£w“¶%³:Ë‡Ó»Aæxu‰V³Íò\Sˆ*z7ê¼ƒÕq-ûÑ9½{må…Q«miYmVÛ5bµúzèyUM]f´eµu«­§İ±¬¶ ¯š:aü!’ìGrŒ²ş~ƒ=%©ïÀ9şÒo’VWÒMiN<Òæ†dD8J`3S‰M
aÇ§ÙËËĞcÀêöBl=Lj)±•ÀM>¯6 \ò¥$ à…SÄÒ”k7“¨ˆÈñx¦hÄüìówé¾z>ş!ù&Ö¸€°ã<±€1l ô¯’gµçÔõ\ dÔ\P«dª¸`+Ëõ9\°[¼àÔtkë:«Lƒå‚FÇMÚ}³å‚«•€‚Í+?†P·+àÒ(†¢zr#«‰ú•#ví“›+v¹Ñtón¹¡–9¡ÏmI¡ê“:8G:·ÿÕ%CÚĞL2»Ğ‡?éoÄxLM²BušYX¦¦*?à,İıe$ò'®†Èñ.ú`zØˆp“BºËQÓ¶Cã‚‘¹4ÃK³u»&·$
‹@éÒı‹àB®åUD]…enSĞœqà {|Õ©K	Mº×O% —ÀM¸ô…pP”yÇÙy‹C"qÚ¯ SÆj_iZ"6%_”Ì†åØ,³éFÂ ËsÏ¦¨ëÙTøl:6`ÓM•ÆlºµeÓñ9lº{Ä¦…º®ªîb}³™`Ùt3Ç¦›k÷[X6EÔîI­¸Ğ›YIœ<½®+æÙ—Ú\k©¥BrÅÛíL†ƒ°¯¡³Ç x¿¹é8>’ :6×Ti¹Èï)BAàÁ¡^¿¦*Ãêş ’ŸÖäiPèiVßYî)ñ6™Tó‹¨DşWï–O{!y‚ÏÚ'«­nìÒ‡Y[FÜ@øKf«rÜ JÄÜ°µğÁ6òlõÜ€º„¼à†mSÜ@Å¾MÉµoÖUì·‘‰mï›%ŠıÚtGi*Š=i÷Tè3;±E¢×ÿÉéõ;Kmêõ»hó]¥ {vR±şOÓªµ~7v–h­2¥İYæÔú=3j}»v½‡²¸Së·•fb³Èj½'K+Úö¢¹—¶Ş[Z· ,:,B‘Wë÷Ñê¥º½ÄÇj}AÙ;¹Ä¿Cµ¾MfÙiñ†²w¨Öwé€E0Të·“æİlVë÷R­ŸÄª)µ~2ÿVµ¾ÿ„Z¿K ÖOá/Ôú©øuj}¯Î¥/‹ôö2‰~‡t¬ÖOS$&îıµcáÃ"¯Öhõé:b¢Öï`—¯Aö¨õûrùZÜóæD8«»»jÍÖ†V?“¿ÔêĞŞgIï­íWÓ–C9Cò4Ù<÷‚üÀ}Ñ{&÷Sí/Lí9Gê¢`Qg7E˜ŞT ¹X…s>‰b ‹Ñ–,~Ty¬u€€$„<qÑPCÆ@2±Ğ.†nPo*_iäkd4bÂ‚ y,N#Bñ²r0ZÍ6³åyˆ "1ê°cY9Ôò«ÓˆS¨´£¥Ò9T*„Tª©k®.váæé‘–JG9*­½c©ôº;Yp¤RÛY’/iÉxı)QXœé8m«AkYÜ»Šç(r…¡â4$¶¨!p… maùG‹­X±8”A´zÈ2êMš÷šWÔ-Q³$¼’ãhĞ˜˜dÖ%ä÷é‡³7X¤,m²äŒDËÅÀ•¦Ñ•@–Ì±åè
Lcº'=^'xº¢®§«
t=1 ëIŠüÉ]w²t=%‡®!]›‘h PÓlNµt=ÍÑõtíıK×{AW`,~I¢™&Áv0	z ¥5¬"ø8àœQ˜:(X=}@aB VØ^¯ëÖZ‚¦’¼Ø ±7„ëq±«“]¨«Ù|²§Ş°†3€¾İÊ³7ÙqñØ›~eE]lÔmåÌˆtÄ
ÄÊ‘°Å¤;[ˆv<Ïõ¤C]O:¡Hw^@ºóÜÒílI÷çÒu†¤«ïªëª.ttš-é.r¤»X{¿Ä’®Òmß—54«ÚÄ˜ó©`©#¦Àd*ç8IÀZ9©ÇÀÛ.å-oí!†˜!*Í_"€ùF8÷-0^.øRö2yşÍŒº`A _ |…Bpe ğ.à«r îŠ¿®ÎªN„œ»Ú|øZíı:ğ/©oCì1ØÕ @'‰r'’PH¢	.(Õ‰»È`¶0=ıˆh·ƒP¼èyÉPÉégb)>ÇÖ[¢âÑ´$€ì)b[ÓÕ™$‘ˆ6(FÂŠRtéMt&şìÁÎ®oümÖbúƒP%ænöP‚7ş„Şëw§VÌm	Ñğ]ı=";q.™ëË‘Çd¿A~£<oòdG]Ov¡#È~s@ö(an	È¾«%û­9d/†dÇÿ®îÎªs›%ûíìwhïwZ²?™($	ƒÉ¥èƒêèÄsu¡ãw„’DP7NG•Ovs¢òÆf’†kjÍSYÊQûRf?vÈåF¢HT+ŒˆBM>Âí²˜áŠ`ê-¥.=Ä)VmæF©4ÿŒ(IèJæ®r”Š1%ïŞ#Ï{=%Q×SRHJŞPò~Åú€’»YJş+‡’İ!%¯»-%â/­ñkïHï¡ÚÎ1]‘uÓ^wè>ôº{”uÒ^w± êùãü…zşü¦½î,”çStí‘W"O§áíó³ÒÌïÑèŒ$Á"k“Úsl™lµv—×yen‡6)³C{A;~Q¡v;´viö›E;´—YZÑ6™[†W´õ«ÒºeÑE~ËğšV= ë–®oäĞµ'¤ku±º»¹®ºÎ¼iéú¹ex[{Gzom§S„ÿÂTn=l³5öŸˆB{«¨bHÒÌgÖBõg¡*ö~İK*ÔN±,êP/©®ÚSäJó.§›ÙğõKæ=–·5 ñWö¾pÓòüĞóêzxÁS<õ±âõIÀStz‹öıŸf¸êO2ãÏÒ\µ_†«ş«]åª=¥Ù¹\õ¥rÕrÕWÚúkËUSb®B‘çªo´úÿ®ÚËrÕ·9\55äªî".*5ãÒw–«¾w\õƒöş£åªóİG6„v(		h× T	›‰¢å¢ÏCòŠÖJø^\‚6`UbÊze/Í¿-yáÁI&–!°_â].Ùì¯ƒ‡Xƒ“óSÄ]„¡d~.Ç]@$æ®_„¯~•ço»P×s—Àîú=Å]tşCq›£&kØÛReN”‡æŞHËm¨íDÔª.3kÃ<07ù­Ïƒ ÷y¥÷ÖöÏU	Ã±$»d P„èâJä4\AÀ©–úÀ2)”-ì%–D+d7îûi¯¾âzF¸a§‘”: “§'¥®I,Ñ„8rÇÄÑ4ÑE‰³i4íÎ˜Ar	²zÕ@rNäÙ
Ï#!>­ıÂÌG$2Ë‘E,A–·Œ ä˜Ğ Õl³ <LÅÂ€ºĞB9za`=Si¸\DI±¨oÖ—5\î#[Ì7K—Útqi9ìÖ™%Ø&1]Ns¦Ë%¥>ÅâRÚÁÒRPÎ%aö–ˆ¸‰2«eYæ$ãş™5l9í{ye`'÷•f+°Y$WdiE›á¶’¶^YZ· ,’Œ(ò¶ËU´úªR]m—«ñß±ír„2àl—«óïĞvYY´ƒ’¡írpM0T‚:¤ùZl¶]NÒv¹6«¦l—£ø·Ú.×Á?a»Í(GëòÊÑzøu¶Ë1:—õ³HwÊ$*Ò±írEbP®$jÕîÁny‘Q£ÕkuÄÄvÙe§:öØ.g„.Lu«ª;‹Mõ…NSÏúXøËå©Qûo’ş[Û¯QÀà¶—mÏ)4ô=ÖƒÉX$
—•‰EDUğ¼,â€ÖNœcÈÒBOØ)%º—n*èÿ™$ ısQU=
ÕqPö )3İÀXÓÌ÷È,.D·&Y>ÜââÅeC´šm6’çÆ‚ˆ,.¨ ÅeË²Î|9VÜ4 TÑj\¡fÆ„ª­ïlhèîª5ã-¡&8Bm¦ıon	Õ-„’€Ëî¸³Y¥’c†t¡_ˆ¦0FÂÓÓÕox4Ê8µC—í1q,¡	²ÒlaÌ—*™-ËaŒ÷‹1ŞJĞİZÛxŒQ×c, ãÖ ãmƒ¶ ãn‹ñv9c\WÛÕXhê,ší-Æ;8ŒwÔşw²_œ‰5`°åûìÉ­½O3 7@§öLŸNË‰DËÖ;oÜ¶&¾¸u9ÀÛ—ªñSèÓ4`ãê¯Yñ„‘®,Pû{:aq¤UF¯Nn3¨öÉšªêšJ³sD¢Q2»”#€‰‰³«e7yîî‰ƒº8‚6ˆÓ"¥ë
ŞŸ|³YYé:I&¶§o–H×½´éŞÒT¤ëöè%sÖjöaÛDÊä¤ìDiG)»¯vT‚lÀµı
Ó
}ÉŞ³ƒ=%¢r²Ì¬“eNÂœ‘°]ÚoQÏIØiÖÍf‘„ÄÒŠ¶Ù\ò'këiİ‚²HÂ¢ÈKØı´ú©®v*ÿKØ^ä'aûøw(a÷“Yö[Ø±œJØi:àş2`(a§HsÃæi	{èv€USv:ÿV	;ˆBÂÎ`	$ìLşBÂ€_'agé\Ì"=U&qC:–°+‡îÙÚÅ!îÃb¸Qä%ì¡Zı01‘°½vQ9œ=öp.*+æ±èÄBsWU±±¡``;HÚ#ùKI{”s´ŒÓÚ~7ıËR—uÌ:h%ÃuX	ÆõN)ß–ndùs*üæpçÃÕæíÒ1SW ûô
¸-ĞÖ¦ÒÍ1œ\F|òµK¦ÄòáÄ'ˆWcÑ
÷áäy¼¼¦ˆOÔ`Åêq‚åG'>OTtN
¨Ğg©prš
uÕ]Í…îzsŠ¥Â©
§é8§[*œ*.Q.ã‚»ê%­æ¦í º m\S=ÛŞï×ä¸`N¦7ŞÈ†Nn=ËK[ÅY-ï7Úfâ$¦qI=$Q$¹åq¥9#"ñ(™3Ë‘ĞÄä9Ks¶<ÏñäA]OÁä97 Ïy
Ûùyú-y.È!Ï‘Ã|$uĞ›‘íûÏ–<:ò\¤ã\lÉÃ ÏVét¡äXÛ¥C¼ÚÛı.ÕCª© @’
{â Ñ„å8
\`R Xœg‹S˜§ ¦áQ¸9ıI­qD¯¿¤®½ÄU¶ &lÑ‚•	„~¼[áÓfTšK"Jº’ùK9JÅ˜’^*ÏË<%Q×SRHJş- äåŠğ%§YJ^™CÉ£†¦dmswSu'ÒN_e)yµ£ä5:Îµ–’7Ûƒm§S&%i4³;¾YÕ[[³˜Ã²$×XÃZ4  |‰éaó×XR0‘+ó.ÓşŒ¾Íƒ-,¡ì¹Ÿa¼;ì9¹R@Ív©Éƒ`ä^§.Í[ÍĞƒ{áy}®Ò\Há~e9Â´˜p×Énçp¨ë	'” án
w³ú€pû[Âİ’C¸£‡&\WwM}G}]½¹Õî6G¸Ûuœ;,á6´Şxª±&'’yN™F4ß$d7“ØöÑ*×Ld—T¤´D‡">ıÓaÅ–Swî:Õµ4øÌ$ş‡ä²‡{nÅùW¶“8QJo“óËÊ[BÉ¶·’Ô-¸ÔrúrÎ ©Å—Â>a´¬Tt›İìmĞ„OÇØgYÉÑ(n¨§®Ná Òı©×?Çš;#"ÅJæŸåÄ‹è.a»åyg Ôõ$º7` û”°÷d,=Ã@ÇÍ@Õ]ÕİõUUæ_–tôó°e èu,îš>~7D¸–ôS}=`
5HÒ=Ã
E{»V4ŸöØ­ğâ´ëv¨ö-âu	ùp3Ò‡·+8×æDóQ~FÚwzNIÎqØn¯3¦ßpşú"z[¦Ì<Ì#{8×+Ç MÌ
c<&ÏÇ={ ®g¡7Øã?)öàşí	%Û“¾Y)»‰=å›%û·§µé3ÒTöo<î£[ggy–’MÛqnÓöœTæ¦íymı‚dM£r¢´.Ù¸½ÈŞ’Øt™ÒK,s·ã3·—µïW”çİÆmPš½ÊfÑÆí5–V´ÀÄëÚúiİ‚²hã†"¿q{S«¿%Õuãö6ÿoÜŞÑANt·wùw¸q›!³|ÏâEúÄpãö¾ønÜfJóÙ<½q;iÈÛG¬šÚ¸}Ì¿uãö	ş‰Û§,ÁÆí3şbãö_üºÛç:—/²H “øÒ!oÜ¾R$N–ìVÚÅ7î“c¸Q”Ên¥Õ¿Õ“Û,»}ÇƒÛ)\Ï*ŞœX]ìn*Ôw"±+c·ö¹[ûQ;ÿI:omŸˆ6pÕƒ«Ğ.Ä—E.ª@¡´.¸êÏ²ä?LšÇ¸3Hï¿Â€Í–Üè”k¸§2'?=¸şü3ÇÎlÆø*H7Åòá6cx«x)ø­p&Ïßå-d3†ºTX
ş°<æ6csÔÊËÏ‰Ÿ4²ZdçByˆì©²õİİV¬5s³2ÓLñ—ÈÎ«Ï'·¶aC"ä6³î³w¢x*rwÈ}òÁø¤¤‚Ù$ÒC2ƒ`#çn›pÙÎÀ‹ÓJFD7I²sŠÊğççô2àómKf–>^<A´Âù”<–ğQ×ƒ/hüE8B*üè¢ŠÏbøYğ+rÀ?- ¿³¾¾³PßØh·à/áÀ_R;_Ê‚?ào®š’hÓ=bO%xGÜmg•ËUkï„)GºÓA•äZ›lu™†‘${ù•ŒT5œ;ÜõyÛ®Y•fée¾®s–Co£¼¬à»œ<—÷(£®GY`Ê+¤P¦´[QXÉ7;=+í–‰­ì›%Ònmºª4ÎkÍjl“¼3À!õ™ªcuí`¤¨œXƒÿ†œX’ñ1à:½¸â˜­3{ä)#G›5ÙeEÛYN^¬Å¿Cy1[f¼¶1Øí¬´¼ ¤¥¯#gïOH&ièê‰ Í~‰yˆô½.Ëœ =;{z=ízŒëšÁ¥{µÅF.ÈEÉ4KÂI|ëõ3c*cT¦Ç8'#Ì7Ğ1ªdŒdj‡I³j6‹„yâv.¥K­¶®“Ö-(‹„9Š¼0¯×ê)"5Z"Qú›tóqšóˆs¸Ì²Åç¼P˜o¨n$†Âüi¾1›§…ùùC
óMX5%ÌÇòoæ›âŸæãXa>¿æğë„ùf:—Í³H)“ØÂ!ó-‰÷VÚÅÖîb¸Qä…ù6Z½UGL„ùQvÕÛ–=ÂüÏáÑNíÄ&\ è.T×˜6Ö‡ÔÙ¿”:Ûkÿ;Hÿ­íLîüÿSd!¹¿!(Î¿#§”‘4|É’Ù‰åÃI¼o¼îŒV³Í.òÜU^N$ê bÜÍrŸó»+&íæG[Ì÷ÈÁüÂóºêÆê¦Î®ó'‹ùó½´ÿ½-æÛŠ¤ç™/§$Â¾s*¯Ê®«G÷qrC“ŞÉS‘P…§eH-åt‚Ôì!É©—ÌÄrHâ-b$÷òìğH¢®GR ’’]ú¦Å Éc,’İ9H^#YÕÜ\×Ø‰ÌÒ“,’“’=Úÿ~ÉG÷ò’?¡L_M	wÓ´)Ã×æâ‚ÎAEF”µoúMëu‰#’lÔ]J5åKÒ_\ÆíC¸>ZjRQ‚Ğœá¹ 8tR…³q•‚0&¼ï›7ÉJ3%""QC8ÉrD€1{…|}òì÷DD]OD¡
ˆ8- âş
²	ˆX²DÈ!âÅ9KP}Sb/u˜é–ˆƒˆ3´ÿ™–ˆËºôà‚¸TĞåK-ÕÙh»z%ŠGÖÇ;+È—Æ(¾Ó ~uNMÅ'£õTO‘U›£im "^	èé#¾¤Î$+WTrã×Ôã|BüCGS^}
C¡Mbœ^iÃD&v×L°İ8 ›) welx´" JfV9 =b8P¸á yìyu=O‘Á³8DivhÀÇZ8,‡'.‰y"ñğ>ÜòÄü¥‡÷‘ÚÿQÒ(ô9JÉÍºiozxÃ:iï Üå/„ûqøM{x/hœ Ï=&èÚc"/	LNJaÂ¸ª'ëœOQLœMå8™ì©¬©a§±´¢í/ÔN×ÖgHë”EjŠ¼^p¦V?+ Àñ– gçà¯9egSWW=ÜjÎ±8—¿ÔÎÓşÏ—ş[Û)£°LbØˆ*š„2Ã¿t¤–èÜÂˆÒİß?ÍÅĞÅ®Ò\À2ÒS/™?³|8i·ˆYùB!ØEò¼Ø“u=Ùí’Ùèæú}Ó¿H`‘¼4ÉKsì®k.«:ÌeÉ¿9$/×ş¯°H.œ^Ş$–!‹‰®s"q€+.?fC5JN¦¢¯Á¡Ô@„a©ã–*0£g ™è/BÔZiˆ^Ì³ÙY+ïß©Á?}H¯qz)GÃŒÊE,«Ë£ÔeÜw0Å£[®_´úÈôv&VY£ À¹Wš+#F òH/V@„˜®¸F×zF@]ÏBY0Âu#ü]	u}À'ZF¸!‡.‹¡¦¦P?ôfs£e„›#Ü¬ıÿÃ2Â©¼××Í=3 ætŞ<cøîŞbšü-QD²]Ï`µ©³6Ìş§ü[˜p```5ëçÇ£_9Œõ*%7ÈéDW¥¹%¢_¿dn-G Sã6¡Ãíò¼ÃSu=5^PãÎ€ÿT´î
¨q’¥Æİ9Ôø[LbmwmusmÑÜc©q¯£Æ}Úÿı–È‡ÃÍĞ¨¸³àÿK~;î`›ŞgğcãÒ†4PÁã™Bj·fàÆª3
õwÀÁÜf».¤ânÚ€Î¿Š"¿EĞV%ı=YšÛ$îÜ	î€uÑPy<®4Dô#`%ó¯rôv1ıÊ=$Ï‡=ıP×ÓOú=’¢IÿV|õÍ.Ï’N–‰=æ›%†¤Çµé¤©’hYà±IOß~ƒf–y‚KÒ•Î’ô¤4 %é)íái)PKÒ3ü÷Ğ–¤gÙeEÛUÎXñÿ-I§È”Ÿ·SÆvòªĞ’ô‚ü¢œ=³q–$Ñë%v”(
§Jç/³Ì™’®Î˜’^Ñ¾_u}Ór¤éî5´µÍµ†³~ncÒk™QN“Q^OrMÆ˜ô†ò¦Œ’Lîtiö›EZÌÛ
İµÔbŞÑÖïJë”EZŠ¼1é=­ş~ŠNX:Æ¤uë}>Ê£Ï2Ë=}®IŸè€ŸÊ€¡^y¦4ÿŒÍÓÆ¤¿iLú/«¦ŒIŸóo5&}Â˜ô%K o~Å_è›_ã×“¾Ñ¹ü/‹ôY2‰oÒ±1é;EâzÂı½vñƒ…ûúny¥ñG­ş“˜“Î¶kêÏì90&İÀ5u©Ìç7±±±¶¹¾¶¹ÁüÂ°&ıÊ_j¿é ¿Ë ­í—É~Ü3V%	ŒÇØ{î%NìIcÃxŞÓ78!«RáŒ\,®İŒñ á!¸Ls#Ç¥ùJ˜=›+©]µÜ®â‰4ÿC‚Àm/‰­&3{“ùƒ/ÑF‰	WÖ•ÑFO¼lÎ‰V³Í\òœOk{Bİ s,›óp„Ô)Ç¼øÎ'Í|õs,‰ægõ€D7æ¨¶¶¾&¿:³ €Dò—$ZHXXhmŸÛº±è>“®+PÿòmÔ.%ø-ï­Û[èËUÎü4¬·s9€ËXx~âJ¯—1i?³$Ô«õäFoÎJˆŸÒsCÁ"^ŸÒPÍäL,ñBeøOÙP±¼oÏ(T.J³8˜2B¶ãfâ“á B^2‹–ã  sÀbBû
y.î9 u’‚–8`I%ĞRœk9`é¸)‡ª;::Š0ù.c9`YÇËé Ë[XN&£1¯ñ…YŸ#‰ÍƒX,”Á§ËĞ–ÒMûL‘Wo“b©+ñn‹yHîÎ‡¤ŞšÊ<ú¢YÎLİŒ6 z² 0Ø%X–z4=ìR›uk£oÒÌiáÏYœäœÏ^[°¡ÆVˆx„D)™ËñèóÈJÂ+ËsÏ#¨ëyDˆY5Å#T®VSğÍnÎ*WçÉÄV÷Íåj¤6]CšfNéÜdºY“mİê§[­%õyX¶¶v0J
ÊİØ[‡½%ZÄù2«Ñ,s*Î­åc]í{=å}gB¹@ša³HùXŸ¥m·QVjë¤uÊ"åE^ù¨ÒêÕR]•Äş;vK©ÕAnwÊGÿ•Ã?Ë,ë-äPo•°Q•¥y›§•;†T>šY5¥|´ğoU>6Ä?¡|lÄ(óÊÇ&øuÊÇXË¦Y¤/’IŒsHÇÊÇxEâNÂ=A»ØÌÂ}g7Š¼ò±¹VßBGL”‹íº¶%{$Û?Ó:aÏ‰5ÅæBcwC“ÙŠõ!Ø¶æ/Û6Ú«ôßÚ¾/=SF‡æ
{Ù_ÜÒ°Šiœ(Í(J¯çNäë¤eÁ÷™#^•Víè•»JÈ¯ÕKß("ïóp¦ÒlËÁ3Rƒ¯S2m,ÎŠ…7‹W„íĞj¶Ù^;ÈkÈ™êpaEØÑò™;³ÚIß~ç İK,º»ä {WŒnwWCU4³«Ew7‡îîÚ»E—!İi.×øNÉx ‹«ı½ŒÉØ¤ÉEHêé@ìjïv¬üâëˆ:‘ÖìèTD}÷æ(bñ *Íø|[„%,>^<O}/yîíÁG]¾ 	ğ÷	ÀŸ¨àì€ÿ~!ü»cğëàw\SxµüN~—ö_´à/‰mcÊÍÊe„-±^%’Xf¿ÆGğTŸMŞ	pô"$é‡Ë>üÆ'U¢ hô/ÕÂ-KØH³ ¤ö„8Tâ¼.7ä‘‡ÑRùÿnNÂLî>§ŒáÇ¤»3fº#– JfR9– 9b–˜,ÌĞ#Ïı<K ®g	¡1XbJÀS•d½KüÕ²D_KÜ³DswGU±¦Ødú-KLs,±¿öo,K¤Î% \°Äµ‚ºZ×?,bÜşLåÎTgÄ\Ä‹Ÿ©„äc W¹—ÌFÅ°.²/q6ƒ?“¾cÍ@8ß°d¦—/>(PÏçL8êzÀA ~@
pš|f) J3•æñß±4?˜-+ÚîuÒ|6ÿ¥ù¥ò‡ØA°
ß›–æ<78T<, ğe–Â‡çPø¾˜ÂÉØ–ÂGò—G`GiÿGKÿ¡¶ÀQJæÖMa€ğ¬Ä:é#°cY ­à8şB+8¿é#°şåy’'ºöD—NNAÒ¯éœO•fË21â¢Ö'T§±q¢äıMŞèt–9İğşŒnx†ö}¦âítÃË¥ÙYlFİp|L;eÎV"?@Eåmy®´lAY¤¢È+*çiõóÂ^a	{Aaÿ¶£º¹»»¾w¹,a/ä/•‹´ÿ‹¥ÿÖö/õhÍ†Bèq‰&‘]²P1Üc§:€]à}6'’WP’n…4óyæŠº
.ÁÕ¶Jî{¸,œ‰è)8"€%;çÂ$€øê$1ÒlÀAÆ·7IÒ±æ:$b+Æø¤B…Ğeˆ0‰k_Ä"£7]\ûbùpz€Î¹ö%¼z©</ó‹ºc…z¼ö•âX~Å—+1®ˆ}¥%ö•9Ä~0g®kªo,@+½ÊûjGìk´ÿk-±_ ±·¢ü’}²Û•Ê)89±¦gÂ \¸;•¨˜Î+…„äB-'ƒéĞë.M¯=sKEŸK‡OÊ	è*¹-v¶3Å©ô:—™X´HnçÂ˜Ò"^.¸‘”âBX9’ÎœaBÌäy£')êz’
x!, éÍ
ù?’^eIzKIŠIÚÙU[èªn®2·Z’ŞæHz»ö‡%)ºÍ|¿’“Oï'Y;]XIaï"Ò&²6XYxf:•îÅÊ$…®Á©t¯g<dd0µº“Üµ’ ¶ChVpëŸJMlÿÁÎ)SgU`:TXå|æ$s“ß²®<«g$fd6×iú1±ÿ$ÇÄ½=8Ì¥Ø§Ó“ƒi©šÅ¦,ğb?âXİñ	€û]åø´È¹ß%œp·<ïñü€º„À¼ßğÃ}J¯û~¸ÚòÃ9üğpÎÖ¨©òÍ]æ_–tüğöÿ°å‡w¸“Dİ•K°ºâØÑÃ€ÔŒ~¦ó°éı”ìy¯?EÇŸ~W/âf$Ùf|êšä¨·ÓÚéÈ–úúy”éC*»ÇzğÆµ=GÖ»¬ô-…Í1w¹Œ5û3ùèüä‘ˆ¼Ä÷³Ê‘ĞæÜÏÂ>&ÏÇ=yQ×“WèÅûYyŸPøŸÈ{%ïS9ä}$Ç®PWÕÔØ „O[ò>ãÈû¬öÿœ%ïq¼z-"šzÈÙ™Ââ?˜>Uö¹áìeºPSÃ›É™³,Ù(a$foÁeSk‘˜ÙWiÈÀ÷.™Ê‘ÄdxQğ’<_öd@]OÁdx% Ã«
Ók®µdx=‡ÿ&–¶gKjŞqêğÄjó†%Ä›ü¥Bü–ğ¶Œ*Ä©ôX7­cˆP!~—uÒ
ñ{,€Bü>¡€ß´Bü¡àñ‘<?ö¨ kŠ¼&Pù$…
}Â>Õ9¦¨8¥õ:™ìY72h~ÎÒŠ¶G©¸~¡­¿”Ö-(‹W©âJíû+­şµT÷Ú÷Â@˜î¢}¯_“èßßp¤dN—9ıeNÿ~,£«½—}•ë¥Ù÷¹¯òƒ¾Êã|•µõOöU_E^ÿY«ÿ¢ƒ%ÆÂ,7ıÊcáâº¶¹±¾¾©±ÓüfyéwşRÿCûŸ£^uğ|<~Õ.OÍx<á|„³©õ«Gş&*iöÒ´z½qß­sb³py}
S¡ÁÁ•D4z	1<ÖÌ‰Id•a¾fÉÌÅòá”a¼qüÏV³Í<òœW^OŒˆ¨Àn#¤çÇß@eiæ«ßhQ_ÕÔŸÈA7»ëjÌB¬íÂü%ê‹hÿ‹ZÔOwF‹ÄcÆš 2—×»Šp4³Šœ0Ñ¹d:ŠÓ§"/×[â$V˜¦òSR¬œÃ—­O·6À[tY­Ä•f±ˆ d*ÊÑXÄôX\(±„<—ôô@İ `Ğc©€K+^Ëô¸ÉÒcÙz<Ó£
ÛĞ†®†f³œ¥Çò+hÿ+ZzÌA»"“F1¨„şÌşõ)ƒ2Ôp
ÍCêcO›"ÂĞ#‘Gí´Í&)±$ì8 µÛÅ– 2¼êS8BÔ/’§]Ø r°¬J(Ïhè7åèkv¼LJB(H.ZµÔo2o'•Ö^¥7ıH-5G{CñN¥Y)¢>áÆ·rÔò1õWº¯*ÏÕ<õQ×S_È	ê¨¿ºRgd@ı›-õ×È¡şSÃHÔ³¦¥ÿZü¥D][G%#„•ã”Ì:¬›–¨"”¨£Y'-Q×e$êzü…Dƒß´D]_ğ¨”çtíQ‘×*U)T(Q«uÎ5ŠŠ“¨ÿÉÖ²n$QëXZÑö4ÅP½¶nÖ-(‹$*Š¼jÔêM	n±$hÎ!Á39`SwC]Uc·i±Ø¿\7Òş7–ş[Ûï
LA"Ilœ	‰Ä ‘ıé Kš"G“:"I\PÕ;+½ƒüøì¾Bì
r£7	Ä¼ƒãíh[è’Üáÿ
ª¦ßàãm%é“t’yñ°­4›ğÅ2vBU2cY>œ(jñÇ³©0È8y÷l‚ºM„`“	)6¡]g3Evó€r·ZÊm‘C¹gsDY¡¹ĞÑİÑh¶´”ÛÊQnkíK¹zuÛÄ8Bì—p¡hé¨h†R·èØ¥nœì  @X·ínMß!{,‰ÂÔÍH!GÏlìEöUpÙQBVÂ.I,qDa–±v8Ü7‘es €€ÇX1eŸ¢N5ŒãÅ¹?%»èFÆæô£§1ö.IÚ&ÀûdJ+[Í$}óP¹{Ğ—FŠL+WS‹İê¿ÕãÜ×e³“r‚ƒ
›J[’rWšÖˆ¿HĞ’Ù¶¶1µ	gm'Ïí=¡®ç/ağ×í¨ôß)à¯Û,íœÃ_ÏÅüUßÕÙXì¬k2»XşÚÕñ×nÚÿî–¿&$ü5!IÏHGoDéò)™ÄçÊÌ¡’ÈaŸµ;~€õp†\H8E–—¤\¼ˆ‘‘"‰PaN]‹BZCD¹¸bvHmMXM$U&•Ôûü£Ôú \ÇôéW…¼èe+ªÑ¡\5Ú+aİÂ» À ›ìÇ‘{•±½=@ãÆšöˆH±’Ù£x1ıIXgOyîåu=	G€öh%ğÄ€n·´o=3P¡£«ª£·á–:ujÿ]–çG%á¢èÙ}Œ3vUò‹ƒeW×J¼0¦*¡üAË±Èá†ÅIïàt‚¢–ó„°¯X´é¾œo dÔ¡S{¥)Fğó}+´üxõşIüdyöxøQ×Ã/xşıø§(<Søï°ğ÷æÀÿÂ0ÊU­é³èç/•«i:Âş2B¨\qDeİ´r…!Båj€uÒÊÕt@¹ä/”«øM+W3ä9Ë£‚®=*òš@åÀ*T®Ò9¬¨8åêN™ìlÖ”«CXZÑö"•«CµõaÒºe‘r…"ïu¸V?Bªë‰í‘üwpbÛ0Ú¥ƒ¼äNlæßá‰í?e–ÇØ7Â–÷¥Ğ9¿¤+eñîùÇ±«„»¤ûãYæì#/gì#'hï'f±»[š”‹İÉúZ¯»S´õ©»WbìPäÓÓ´úé:Xb¹Ç²ïì9Ø©¿š£˜ªá]PİdÎd}ìÔÏâ/Ó³µÿs¤ÿÖöq¿€Qd ”ğ2³îµ¦:fa¡†¶20­0“[txğälÂl¶q\H„:½=c=ué_ C7"…%[3ç'JÕ®GÌëu›t6RÏ'p²öøœÚÖ~£&U{ËdËÌ¯nwµr®êrtØ$1C1aïİIúBİĞª–‡Üâ µ÷ÎUA³BÒ‹ª	row+áõ×nGôwĞ­Mö¶nùvçÆãt/`¶tJK§ƒiÄAÄ†P“Øœˆ¦1Aúh™^’OŞY¼è‰‹øn4X§=l³8a,	P¹PœZœQ€ï@‹Læ¦ãfZrM}Ú"ç+”ÇÄõÄeTñf¹Ü”“œ3Ôœ@ó¬¨
6ts.<³Aá'S2ç±|¸
¾X VH(Ï?Ë§"¶6Ô>I,µÚ…É9ì]¤_ØÅÁ|¯ı‚/Éù‚_Ëù‚›;ê«škÍ_ìüW÷_ªı_f¿`ô¥Öç?Z=¢t¹mwaû&Ù ± ½¥ó-‹·5ÆòÔP+H¥•v)Î…ED³rÙºÊ™¢pª#é >`tQÿKq«4‹ÈBJæòrd$1Y®‚\)Ï«<YP×“EpY®N‘…nD×(l×J3J×ñßPªmş®«÷ëN(]Ï¿C¡tŸ¼ÆvğÆëi¡DWîuÀ›ü<ßÈºrß/]Üìç™¸rÿC›Ş"MÅ•Û…pƒƒûŞÌ­l™8t¿åºo“V<6¸]»¹C
ÊD?º“%2ñ™Ú?YædâÛ™x—v}·2¹Ó'ş%Íîa³HŸ¸WQ}‡2ñ>m}¿´nAY¤O Èëhõ¥H÷`éjG›‡twéÎ#İƒ2ËG<éŞı¹ÿ­>*†ŞCÒü16Oûs¿7¤?÷ã¬šòçşÿVî'ğOøs?Éh~OñšßÓøuşÜÏè\Í"ı°Lâ9‡tìÏı¼"ñ>á~A»xÑÂı~7Š¼
ò’VYGLTGìö
{T¸€-ïü<N,6ÔÔaÓi^e+("¯ñ—ŠÈë:Ê2ŠÆ'ÚZœ ˜äTÜìí¹Ş%b»ÿV²˜±ÆÙ¬—~Äº MB8dXÍ†.Ò7C7¹æMN)#:øª¸ÉòáDŞ:^£ŞF+dº“ç»òr":P7€kÔ{–èx_1ù @şßùsÿp(ä«jêêjj:ÌGùòŸè(ŸZä7€bç’}¤²=‹Pà¥;› ‹‹ã?n‚MÁ_n‚Õ¾H;!|Äp?;ö‘.úm`¼ÖW¤{XÎùŒF00eÄÈÉı3GVØİ^Ôâx©Ôl6ÌlpóŒ:&ÊËC2Uu|ÎÄ›•Ó·$p.$˜ª£~ª[Ñ!““Rî-ÁËêBÉêÑ¦w|ÜƒJóYÄ2¤N~Ë±È³ÌçÂ,_ÈóKÏ2¨ëYFx ,óUÀ2_+1¿	XæQË2ÿËa™†b™Îºb]CSMÑ|kYæ;Ç2ßë(?X–™E›ò12™ƒU9 -ÑàUÂ;0KM²)nIÍÍò:‹)ï ¸pöê N;ú¹¡ îÓ¢SC0º-ƒù1Ÿo[2?•/ƒÿ³Àş‹<õà£®_Ğø¿¥À§Nñ»Âò‡4SbÕ)DÌ2WPÊÆ»˜Á¢™ÿ‰Eùc'æâß¡fñ˜¼ÌÜü/œàbéø8ÜîÎƒÿÃ°ór¨”\_Cò®Ëô‰VK¨N<æco‰˜~\F˜ŸeNº’HwÚØĞ”<ÿ±Lµ[àÓ¡˜*ñƒ^˜­ á/í(‹ê(‹É(¡”åX8™eİ´Ã„v”ÅY'mGY‚¦KòÒt)ü¦í(Kãoœ½ÊsY\Vht¼*(¾œ%ƒ“ÆËëœWPdœŞó„LvEÖô•”æŸQ¯¬­W‘Ö-(‹ôyA¼ªV_- Ã“–#rÈğß¡ÈĞÑÔPİÙ ¯åÕ-Fò—‚xeM¥µßö€FoOá0bZì…øâmè
]Š“X0û!ÜI_q1rD"§İ™íFÜ.ôÉúlÖâ¬2²˜o‹ Ÿ,NãÅão{”Ğxyö”F]OiA”^7Ei~ë),cğŸ²à¯ŸşçCÊâBGC¡ªÁTZğ7pàWé(Õü«¾Èbê:ÌÓÁ­3iĞW<@®ÙÀÓPBªå–Ò¹·ÜÉŒ‚§„"î²±Ôì]næûgŠ`“³Fç÷Ê1–ìÖ%¿ïKS™ÏAûgÒè+NŞT@çµ!Ua¦ƒKMD-ÂƒãÚrÔR1µê„NõòlğÔB]O-ÔjLQ‹[&Å±Yšù­N´$z'©ö|ÁOË¼7d™[¿Èlx6Ò6Vvpş3Òl6‹>ü±,­hû’ş¦Úzœ´nAYôá£Èøãµú„€÷µ¼·Yï}5¤ŞU¬n®ï¨1›[ŞÛÂñŞ–:ÊV–÷˜6†§FBhÊBÄ£Â‡}š|Ãs&˜ÂÌôA‰lÃĞS6ã¹Ó`£hƒ€Ö&\DbWñ×aÇTé­X‡|4H# R—‘$rN*÷0éâÆ•#¶-R‹€Ï
J#/m2KœØÑtk@óË¯«4[GüIKf›rü	4cşlÎÜVm?Q×ó§ü¹]ÀŸÛ+Ö;”ãOo¤Ş1ÃŸÏÉ¼wJóç×şÜYØ%ËŸÏK³]sùs7åÏoÈŸ»këvËŸßÄü‰"ÏŸ{hõ?üù‚åÏ=søóCëÕõ5Íf/ËŸ{;şÜGG™hùó‰9¢Y1a«ˆ&é¶*º°wı]’A0ÁˆdOã£‘Îû7d@¨ÿš°·ÀËÈ}Ã«Œ¶Ü…³—kú5«’İ‰Zkäta4§õİJ³oÄq¥d
å8øÄ×!¼Ö)Ï.Ïq¨ë9N@ÇëVô&•ã8Ÿibr†ã^”y÷¤9îÛŒ’¸Ÿ0%`‚—,LÍa‚ïÈ.\Ê”•öîµlĞÇ_ª‰ı:Î4'T9ZÉìÏºi5…j¢a´š8À¨‰Óù5q¿i5q†À>SxğÑµ_^àÏJÏã¶uÎ)6NZ¼,“=˜u#i1›¥mßók<D[*­[PIù¯ñ0­~x@ˆW,!È!ÄC}uMµÅbG¡ÆiÉp©&­£#£´¶¯q;(%ª?ÈíRê*±ú¡&êš7Ñ<$k·×<¤…‹:é/íòÅ!$"d@/A
uœ1%N3£7òõKæX–§7‰ø»;Nˆ~¼<Oğ¤G]Oz¤?1Ezê')N'ÔxÕRã”jü85ºªju5ĞOµÔ8ÍQãtåK=em”J4S 8ÎŞœ'f™E)ˆÅR?Ş]¨)¨Jœ •Ûz+¬~gXgû&Uš3#xù>¸Y^¼ZïÙì9ò<×Ã‹º^ÁğÀ{¾¾ø¼¯YxÿœïOCÁ[S]]Õ‰°æBïEŞ‹u”K,¼:æTÇNïeÆzX*\bŞ¦sa“„½¹“‚ï
F8Ö°IÆœCn¥ùK„>_·dşZ}¼yŒş¥‚ûeòü›Gu=ú'Ğ¿<…>Õì+—+¥Ù0j¶¿|{HVÀ×eŞW³Ì©Ù?g„Ê5:Àµyß°ä½.‡¼¿”*5æï–À×ó—BåçF'*­dnbİ´PÁ@¡P¹™uÒBå,€P¹…¿*·â7-TnØo—ç|tíÁ——øw¦À§Pù§Îù.ÅÆ	•7e²w³n$TîaiEÛ¯*÷jëû¤uÊ"¡‚"/Tî×ê„xËâ_9„øm¨ï¬¾£±XW…—Z2<Ä_
•‡u”Gd”Öö÷ÙeHM~>hU¢ª%
œjrËOè§SìÑiË/C{"ZişÍá3Â‚¯U2²|8a7Œ¿§Ç„˜Ëó?¤¨ëI*°¤O¤HÊïéI}ÿ§¤Ù0ßSCbÉ{š=$Ä[æıËÜ÷ô{f[ğ¬ğ\–gŞ‘fÏçòÌÊ3g^ÔÖ/Yù#æyyY«¿ğÌ»–g^Íá™9æâà¨£ª¦	ëÌk–g^w<ó†ò¦å™-É3šuQö–ğ\€üdzKÑM$›­,µrgn“*Nnl:+´hĞ"ŞŠƒs/™·Ë1^#fŒw„%Ş•ç{1P×3†`Æx?ÅÔ">Ğ—ü0€ò=åG9PÎ9”…†ºÚ®†ó±…òå§:ÊgJšş¶PÇaÉeÄ¿) I…æ´	=ôª‡İ¹ÜTbO`Z÷ŸºË¨?[ƒsD¸ıo>ß¶d>/>^<ÿıKy~åÁG]¾ 	ğ¿ÀÿFaù_ şûüosÀŸk(ğ«››jªk««Íwüïø?è(?Zğo ó€Ìæ%²Æ?ñÕŸ{g_PÃ‰”½5+‰M-¦:°:Â^M_àà„¦³ÇtöjĞkÛµÜŞÀÊè±¨÷Üä€ÁèØî 1Ğìàèô§ˆf©d~.G3àÓì¡Ö¯òüÍÓu=Í„ ÙïÍşP4çhÌY|`i6'ÊÃ#‹¹‡¢YMsc]u¡»ÙÌÅV8²˜›¿”Wóàe^¥µ}ª^ëH{Ïi¶±H1kív&‘Y0‘‹­¹»°5Äê0Ğó*ò`OÅÅï†G¥.
5²h#Û¹™ÉH.¾ ÎrX>œäÂ»Æx/€V8å‘çBòJr‚ºox/ÌR7
Q$ğşĞâ½XŞóïawÿµ¦Â"¾8©¨-¡ã,)ã„ŠG+™¥X7­¨a PQ[šuÒŠÚ2,€¢¶,¡¨-‡ß´¢¶¼ ²‚<WôØ k¼,°Y)…µ•uÎ«(6NQûH&»*ëFŠÚj,­h›w~İÚzuiİ‚²HQC‘º#µú!>¶„X3‡óÅøU]µ]MU5f-K†µùKÆ¥£¬#£´¶_Îİ?n\Ú„ã)CXrP`¯+a=Ã½ÁÄà†Æ<6fDƒ”MÃ÷k['{}-Ÿn˜ÉWtëï7ş6é9‚¦P½´ñ€Ó'şf4_!óÉ¤vcùpŸPŠ?™õ„!ÆÈs}Ï¨ëÙB [T¦Ø‚ÊŞŠa•4FÙkL”½jö0Ğ'2ï–9eoşùİ7I¾«Õê²|÷©4«Ïå»å»ÈwÚºÉòİ1ß¡Èó]³Vo	øî3Ëwæğİ‚Cj(õHUWWm6²|·±ã»Mt”±–ïşlÏ( 8%cá°vØ„ıÜ&\8+cğœÖå¢Ù
ªÃ*ÙÔŞŸÉœwÙ~6ÆïºI_`5›FÜF@y³·›˜ÛÆŸMçfÛP×s› nÛ<ÅmÔ ·Pä¶èó_KŸ­rè³ĞPô©mh*qÛØlmé³£O«²­¥Ï¥*E}dl]&9ƒú­wHrÕ5z\ºzº
p×¶®7™œØOpÍ›v÷.ä¶ó¡)¢v|"oM?Œd^ÒUùŠ~[D&âR2Û•# ŠÉ´½hyîèÉ„ºL‚;È´S@¦À]2}nÉ´k™’LÕÈÅU0»Y2íîÈÔ®£ìaÉÔg?#Ñâu*­¦BéU?DDZZ.´¸¼—ŠÑ.ç3%QÆ\33 …Ü©#¸~–•æOâ|Å’Ù³âxÛñ½ë½å¹Gu=â!Ÿ˜BœËğ¾ŠEAš³7%Ëp{H–á/dŞ,sËğ"É2Ì/¯K($ıÒ’´;‡¤‹–UêÌ$KÔÉü¥jÔ£ãì'ã„ªG+™)¬›V0P¨Me´jÔË¨F}ü…jÔß´j4M`ß_Æƒ®=øò²  >EÔtó bãT£¯d²3X7Rf²´¢m1Š¨´õ,iİ‚²H5B‘QjõƒB|m	qp!*†ú¶êš;š
İf¶%Ã!ü¥jt¨r˜ŒÒÚ~¤ı¶Byd?1»ÍJ?¦Ä‘·;—Z+Ù….O>©•È¹Js8ç—Ñ{øŞ%sË‡Ó{ AüÁ)Ô>JG{š£®§¹à
š“¢9¿‡’tl@†o,Ë!ÃâC‘¡©®X‹{µ]æxK†NÔQN²dXdH¿ÇR† Ã²k†Ú00ˆ%éä!N©dN)‡f#tª`sš<O÷¡®GH^ t¦Îı¬ ¡ÿY„ÎÎAh‰¡ªïèljª©j4çX„Îu§£œoÚÃúeõmX`<í•µÛñ”	!JÔ}šY¹yµÛiY¸ïÃCŞ‘ë‚\¾ÒÀ•/ƒ{¡Àz‘</öà¢®WĞ¸—¤Àåzÿ}í¿J³aÖûæd½¿”=$‹Ó·2ïËXæÖû%3ëıßt€Ëê}g©wEõ–*»Ş×›+-ı®â/×û«uœkdœp½çh%s-ë¦×{®÷×±Nz½ÿ;°Ş_Ï_¬÷7à7½Şß(°ß$Ï›=øèÚƒ//ğÿ‘Ÿëı-:ç[·Ş/“½u£õşv–V´-Íõşm}§´nAY´Ş£È¯÷ÿÔêw„øÁâîB,3ÔgÔ	•·±¹©ËÜcÉp/¹Şß§£Ü/£´¶3Û›dƒŞtÜ‚×5:»]P£§Ó¥hŒÆµ¹înêìmÀÄ$Ü¾Äâ"W7–ä7áÌ{ñ°Ë=ÀÉf‚€la,nññ×÷ ş!y>ì u=È`€GRÀÅÿßŠÖ£M~´4y,‡&Ë)ƒkêj«ëêæqK“ÿ8š<¡£<iir4ıÓ²åF 6NËÆƒ¬îšC °aUµ!Re“¨[ÃĞ”Ç£Ü©=Zs,"™Ãq²F£¹Vš§"BğÍKæér„ 1!<+Ïç<!P×B!O‚Ëà
Ñ‹Ò¬Ìe°—Ø6ùZ’¿Ì2· .—Y _Ñ®_hü³¥ñk94^¾ìØ`^·T~ƒ¿\ ßÔqŞ’qÂ£á¤†uÓ 
ÀwX'½ ¾Ë,€ïñàûøM/€àÊó#;ºö°ËËöS°süDçü©bãÀ_d²Ÿ±n´ ş—¥m+pü\[!­[P-€(òå¾Ôê_Iu½ğ5ÿûK÷¶@FÊ¢ùFÇZqşmî\dÉˆÈ¿Ã	¿Êd¿µ/ñŠsòª“Ïq÷–¾Óq¿à7Ë ?ä0ÀJC}ä°Õ4!Z‰ùÑ’ÿ'şráıYGùEFim/âv(œSèİ¯®~\Ù°a°Ÿ#zz°æL±rp6•DëÍ˜,+Í¯œAf5å›•Ìo,n5ÅKÆñïÂGÈs¦Äêº›9pÓœøÿ´Õ}.üæ–f¾úïèyX=¸˜±òÆŞ†æ®f„B6ó²N9æã/_GY@Fim¯	'ÎEØg“aöâÑö ™x_G%¶!ÅiH¼µ »Ë Æi–ÌB,5Ì8Fma´šm‘ç¢5Ô` j‹¨Uèû, ö‡Em‰ÔV
µ®îú®îš¦F³¤Em)‡ÚÒ:Ê2µC(ƒl²­Ş"N‘ÅU<Q{ôâ¡Ø½ºqGñDƒVÖ_ñEIÂÅFB‡¦09ÖvÁÃ“+ø67‡Ü¿¯4ËFà+—Ìrå(€·)°¼`¿‚<Wô@]O”'"VVlV	(0ÇR¨¾)²`åP`Õ¡Oçš««j‘Úz5K«ë(#-o©Mê‡§9œ;'÷ jC5ĞÛÜÙxu£ãbëã:…&º‘x’Ü¬ßL*k½TbÎ3	õ«ÕUX#¢_¾dÖ,GàÓb-¡ÂÚòåiº.h±N@‹ÑŠÒº-æ´´X/‡«E‹î®šú¦æú.3ÆÒb}G‹JeK^l¡5q¦x>Š°Óˆ}úO³6IüÍM¶¶A#ôkâ­ø0zGP*u#‘® 4$Rjt1wÂAD#é7 )ÓŒ^c‚&ÇãØJSQ‹ğ”Lu9j©˜Z5B§ZyÖyj¡®§–ÀjÕÔjPjÍe©Õ”C­CúÔÔW7 C›fK­G­u”R_ñ¶kyî!¶Í(Æ}¬fÎ@EkHØİ`00h´‰m&è‚Ÿ=®íJ¬1#'ñï(ÆGáçûAÄ³Â§Yi6hÁ—Ç­›r´ 1-Æ
6•ç8OÔõ´pA‹ñ)Z0¢ÃEi3ßlõù'ï»Wëæ–‰mî›%¶Ğ¦[JS‰èÀàÍÌ|lWw³[%ÑÖk² I*ğÛh­RŸØßnÚ–½%êæ<2¯6–9~ÍÌÉávÚ÷öÊeNKWšíÀf‘–º#K+ÚÖ¢–º“¶ŞYZ· ,ÒRQäµÔ]´ú®R]µÔİøï8¡Ïî:ÈÚN=mçß¡z:ŸÌr:ÔÓµÓê)÷Ò÷”Ã}ÃüÒ|/6O‡sÅ}/ñâÊ¤óˆÂ ×,ÜŠ3{³j*œÃ>ü[Ã9LÄ?Îa_–`?Qà/öøuH;u.]Y¤IÒq8‡nEbÂ=I»˜lá^'†EŞ*Ò£Õ÷Ó“pÚd
{tÆÑ\A–Î2èÄBUGc”3•- /öò—úbŸĞ/#èR«sk<#1º÷Ôc@—Í5¹ïŸ\èë5V%ÅäYÓ$X¢:ÛKˆP”õÁÆ%‚—ÌH§iP¦‘•fg•Q;ù¦¸#ÂòáÔN¼t¼\´šmä9]ŞO\dP7@ËÅ eA·+š¡°Ì€_È@ğëæ_]ÕT×ÕÜ}³,ğ:àÒ¶À÷‹5’3wEû¦Oåyhr ‹XXÓ¡ÕèµN‡œ½ŠöÆ	j× l¼(*çëÜ>1äO*Ï}âø'€WšÙÜ|?$Ø*7^5†ûPú0yîáF]·à¸à>RÁ8*€{a÷Ñ9p¯—wGCMgM#Bwcá.9¸Õ³póu÷É=Ğ!õš´n|$€5vJL’ØÓ›¸Eöˆ_%2$CBßàõÚ©ğW‘ªÑì>ÈCs=Í–ÌJT<õÒ#ïlTšã#´ùz%sB9´ñ¦1Ú'
Î'Éód6êz´> }J
m†>8U±8Mšé"~:ÿ=Tèƒ3Ø¾¢mŒ[ÊÏäßáR¾ˆ¼ÌYv(|gcÒK9…àÙ:ì92l1ßrµ}p.{KDÚ¢2Ây,s’pıŒ-ë|à‚€‹³\ôç.ªÌã¢$ìÁ…–‹.â/¥ÑÅ:Â%2B(8²e±nÚŠ…!B+Ö_Y'mÅº”:—ñRçoøM[±.:_!Ï+=µÑµ§¶¼&¨}UŠÚ´b]­s¾FQqúA…LöZÖôƒë”ŞP`ı][_/­[Pé(òë­~c@‚Å-	nÊ!AU	àuÛTÕÔUgn¶$ø)°nÑn•ZÛ?Ä‡¬7Œ%:ÃgÃ•ÑMqèÕ;¸îU2Å7lô{ÃCÌT4À±­Hªiøx5V-DaËNùg#
¸dÏ„e£ÉôJX¸İ%ºÈKÆªQ»s_?"ÑÔ1{úAtÌ¦×İ2x«šsÑx~œ¯Ë²š
¦£»]¨ètyª4·‚Œt$¬%s;Ë‡“@8^@îfºSÿô,…º¥„l`©»R,Å/ùn¥Á=Òl˜/Ùë´÷²‡„ù–yßÇ2÷%WgtÚûu€²<»¤4ûW.Ï>¨<[C}H[?ly¶&æYy}D«ÿ;àÙ¥,Ï>šÃ³uy<ÛTİÔXWW[o³<û¸ãÙÿèOX]Q›È‰…l¢R’!”Ÿf‚)fÁæÔ7HÓœ„oä*–°+’.°b:»€I[q¦¤ Ê\¯ö†¨Îşi‰ËŒEé§†Õâàe7	_Ï*&PãzÙ S.HEvÖ¼ş`rãæDÑ£âñM¥y2bk"_2O•ck!fë§…¡Ÿ‘ç³­Q×³µPlı\Š­yŞõ¼’é…€–¶Œğb#Ôç1B]±ª¦!\ÍK–^vŒğŠğªe„W°xgğ Ëİ<dĞP˜N7‘ıåb¨·ê²f³Ãéê‘ºâèÒjgtl¨&d›˜^ÅO³ŠŠ0 rÉ*µÆŞh°ë»ó\¬	’õêµˆ°D²d^/GX€ö!é›ò|Ëu=a…R ìÛ)Âr½zGaWš³^ùï±‡d½ZFæı>ËÜzÕÑ<>Ğ>8gYË9åpN#9gÙ`Ÿ–Ê´õ±åOøKİãSã3#Ô=8B˜±nZ÷À ¡îñ9ë¤u/X İãKşB÷ø
¿iİãküyşÏ®=ğò¢ şÛğÔ=¾Ó9¯¸8İc9™ì¬é?²´¢­‰ëøOÚúgiİ‚²H÷@‘_ÇÑê¿DXŞá·"4çn"jŠ]õuÕ]æwK‚?øKİcfaNüP÷8C	ljäËb¸[w]>e$•…W¾ÖTNoº}Å_(SúáëdNîRr`ÈÏĞ¹€Ê’PiæÂü²Š1@\2–§( øÃ›­pmFóÉ›Ë6u=ıcĞ~ºi²€¶ 4óÕW°$YˆÕûEK®ı¢á¯@³0[0I’Eu„Å,I6K91[(Ùì¦V>*U6Î³> oW•T•¦"Â“.™ÅËaˆùÇ.!è-)Ï¥<†¨€—0\FßpÙ Ã-†Ëå`¸a®J]ÓTÓİXÕi–·®à0\QGXÉbxšµ÷«AÍu½š*Q^“àô›‡"±Q¤@óHR†e”úÏH/¾{i	€‘ QSGØOhÚP¸‡*‚hÈ“D•6+G!%³J9‚ Œ˜ «
)V“çOÔõ„AÕS¡4©p­!Í†‘&>:Ëšì!YşV’y¯Å2'M6ÊH“µu€QÅW¶_'‡â+MjÌhKóuùKi²1FÆ¥	G*™õY7-M0H(M*Y'-M6`¤I!Mªñ›–&5y­<ë<ğèÚ//Êó”ğ”&:çFÅÅI“Ud²M¬I“f–V´mBiÒ¢­7”Ö-(‹¤	Š¼4ÙH«oaUK„Mrˆ06ï³«o`¦7\†kI°)¹tÓÆË­í£ìg'áâ$'ˆÜãUo´Œ¨4ØGf+Èy•Ìf,n…Çãas¡ÆòÜÒÓu=Mä½A“­R4¡Î¼µ¾Ä6L«Y˜Zs`Ú4×æR[×ÔÔØÜm¶µ0µ9˜¶Ó¶·0C×WqgÕ‹#Å=ıƒ²é™Ä›dºİğ®x´íMCæ¤HõÅ‚ƒÌ{Êå&%hyŠìDpuUU²SlU`lÙ’»Vğî‘…8”ÌåÈHb²ì$ÙY»x² ®'‹à²ìe7m÷€,#,YÚsÈ2.WhtÔÖ"øa½ÙÃ’åO,{ê{Y²|ä\)u-·Ñ°EÅ"GHuJ†mF¸šwS­yDv#}EMÂõ€ç†zYš‡¼š&P†Óò„ÿ-ƒTSöŠî$†5Ò´kıÈîö’èXs;y:ã“ºêî™Êâ-I×y3ØM¬Òì‘™¸–Ì>åÈˆc2Oï+Ï‚'3êz2İ@æ™)Š:•]ÒlQäcºÙC²v®.óîf™Eã3¢h’09à£‘–zrøhÂ°¢¨Öìg9i
)Š¦ê½2F(Š8RÉô±nZaPõ³NZMcDÑşü…(2øM‹¢|º<=ğèÚ//
àg¤€§(š©s>@qq¢h™ì,ÖDÑ,­hÛŒ¢è m}°´nAY$ŠPäEÑl­~H@„5-Í!Âæ¹ZtMuww¡¶ÓfIp8)ŠĞ”ZÛ{¨EÛŒ…šB®“VÊŒ’èGú!ëÚêå–Ú¦MÃ7% Y’İ±”^-£oVš£8‹Œ0ã›•ÌÑ,N˜á%ãÏé¡gIÇzª¢®§ª ª—¢*…Ùñ
Ã	ĞkY OÌz‹\™_ÛYİÙ\UoN²@Ÿì€>EG8Õ5.b²{.gĞ0d‘Ó4ä~0eKCÆfÓ!©àì\­nïGÕ‰Ú6¤øÃA®f¢•…Û…íŒ¼ÅQı§l‡²º#ª6<ß¨Ğ#?%MOzjÌÖÖL/6NsZÄ¤AÉœ^%@˜%Îf8Sgy–@]ÏBc°ÄÙKœ£;7`‰µ-Kœ—Ã[» Ö™ó-S\À_.€Ö1.”1Â#•ÌE¬›^ 1H¸ ^Ì:éğ`ü± ş¿éğRAä2yşÍã‚®=.ò¢Àåò.\ ¯Ğ9_©¸¸p”Lö*ÖÀ«YZÑ¶Àk´õµÒºeÑˆ"¿ ^§ÕÿaK„ësˆ°u®6ÓPè(2 Ë–7ò—àM:ÂÍ2BkûN›à—hÊĞa•GA7Š(ÌĞAfôC#°·ÎÃm¬¡Å–Y$«¬Q ƒ(¨Î{1±™ÓNá”&X~ä‡ÇŒX[¡ÓZŸFqR±}·1=FµÕˆù48k’¸¼²HÀç_ ;Ã’ähJŒS•æÄ$³ç’¹…åÃ-Ç€<şönîºM·{C]ÏcBGğØ)ãr|§åŸÙG[²ß•CömòÈ^Sƒ„555ænKö{ÙïÕî³dš=¾Øª
	‚#J•èûîpLÀü¬4{ÀkJ'—\wÆèâ’Qµ uFà~7¼B‰R‘‘4äÌE˜…M_¯KZ¯ËeŸøƒ¸,*ğ×`š`ºÌ­àMiféfĞÓ%~
4¥X~E–YsDOX2”£'°Œéù/¡äƒò|ÈÓu==…@ çÃ=Q´ÿĞs]KÏGsèÙ:ìZŠ£6KÑÇùËµô?:Æ2F¸–r¤’y’uÓk)	×Ò§X'½–>Í¬¥Ïğké³øM¯¥Ï	"ÏËóºö¸È‹—S¸Ğã%óËÒLı1^á¿‡¼úñ*;¨hÛÖ9d¼Æ¿C‡Œõäe_·cÁb»mèñ†û¦Œ[Î+ñ-v”,ôc¤ó·Yæ6m™Üw´ïw•ÖN>¬/ÍŞc³H>¼¯/µåÃÚúCiİ‚²H> ÈË‡´úÇcUZÆú$‡±¶Ï5BÔt×4"Z†ùÔ²Õgü¥|ø¯ğ¹ŒĞÚş¨w“K™“;Å¢{ß&Tb'No5
?‚\ğ4fÔÁ	ªVÊøÅ¾	ê„hYB§[vY	$+‡Şƒ›)¡PpDˆfY­oc°7innvî	^Š9E¢I_ğ-3+>‘+™/Y>ÜŠãâ+ù¾–ç7şK@]ÿ%eğ%ü/õ%pÅÿVaş. ä–ßçr‡Ü¿£©¶¾®¾Áü`	ù£#äO:ÂÏ–§d¯škŞ>¤td‚]œµë&Hp‚ó¹Í•iï) ™ó"ˆfÏSë®Óà”–wk(Ÿ\£›h¼Kõ#½¤İ(´á,’dâ¬4¿Däàû—Ì¯åÈ(brü&„ø]xr ®'‡àrÌÑ‚§oæÄß k.ü¤oª,9æfõàøfÇ<rTUW×Tª»Í<lã›yùËïj>a~¡µ}+÷\¬X˜Å	7 „·’””.uÖAG÷Äÿt°ß[¥Y€ƒdØš/™Y>[ãbB«Ùfay."Ó•c0Ôõ8
0ÀqÑ ÇÅô-+«-‹çà¸Ó°‚¯Á,a‘\’¿|KéKË¡àãH%³ë¦	ß²¬“|Ë± ‚oyşBğ­€ß´à[QYI+{\ĞµÇE^¸¬’Â…›ˆUuÎ«).NHÔÈdG°n$$VgiEÛÎ#µõÒºe‘@‘kjõµ"ÔZ"¬C„]ó˜¹¹³¶
—ÈšÌ(K‚uøKf­#¬+# ?/˜y$V­u7İ‹kàèîÜtÆ¯óô‘E{~I~·5½ĞC-ëd}Ğ‚¬gn­™ÅPÜNaÍ¤ (PÚ§°SÙ—Tz@•ÛÌV˜……I†êêwéàÏ†8A¼[5i r¤Y/˜ùZÉŒaùpğ‹?¤õ…U*å¹gÔõ#DÃT¥†ò¡Z®	hXgiX›CÃİr=tj::ëºM¥a½£aƒĞhixiXİBAÀœ«tpqÎ¾#fš:ÊÀ1,M Ğj¹àŠs|GŞ=C,&ë›Í%®ÓĞZ&„WÛ³s·†„>#MS=ßµdšËA×¡oĞ7”çFzÔõĞ–€~ã úM˜±ôõúMs ß=W4àâYUm­g¡ï Ÿ #lf¡7°¬è·¶„ …'al(V³RŞ[è1¾ß€Y!<¥‡y?@(¡‰l‹E½ÒD‚ğí¦EJ?1f©Gw’ 1K^~¢¶'½&á§ã=´:ŠÈÅÜßkå¾»§ˆÙBÇèÓ£j#eÿiØ»ÙnÉ\tgY=R‚ìNò[x——°ô˜åæCú©fæhıZ“èÎ¥,fJ1ŞÚEb¤Ù<â8’¸d¶(Çq vÌq[
¯m%Ï­=Ç¡®ç8a!pÜ6Çµ*?lp\ƒå¸¶kÏã¸îîææ¦†æ‚ÙÎrÜöãvĞv´· ª¬µGfHQU´mú?p‹MI=Å(L–™ú”{á;Œé4êi2‚y{;$Öš?Ës…zøÉbA6ít—
½â‰>ò—EÔª kŠ&‚Àš‚eŞ$fÉ®‰+4ìàs½Ûc§b9aˆïD¾‘ÜÄb‘ZS‰rsrSÚ…ÍJ8¹Ü•Öd›"ÍB·5d-s¹ bIÀ­QÕ¸%ÿ8âõÚx§[BNu+åª¯¾Îÿ)ï:€ë*®6	!”à8!4…$”„(*–d	Œ±M2¦ËàÂ{zOÅVãJrL‡G˜z/¡÷Bz!…„ôÒ{¯BÈ÷}g÷îm’Èdşùÿ™ÆsïÓzÛ=mÏÙ³ç¬‰Ï%½ûå”W‹öŸ@„yF8@,p F@İÀ¢l0ÂÁFè62]œa„6Ç‡0Ââ)ÕÇ¶èPÇ
Kø¦ú¸ÔÆX¦1²ê#GªEËY7©>b¬úxë$ÕÇ >–ù†úØƒwR}¬"U={\Ğu€‹>péKÀ…êc¿ÍyÀàâÕÇÙšì
ÖÍ©+Y:³ëªƒÖzH­;P–SQÔÇa«>’AB»CÂh-4MÛ{›JÍ¥èp‡‚ˆoªc6Â¸Fèìş;âc“¸Ñ08DwéuŒ”¸øvÆG£[Êº×Mab¶İ€šºøç¿¹%â­yœLEÆ/€p–w}÷fì¤´p÷4ÄìRì	ã·Z‚âÊ¹¸cé¥ºy¸çYtƒo}4A@¤ÔL¹Y>•š	8çnµHjka¡n ,!„uD‚°¨fi˜8*ƒë‡ëu¸^Rh*àò¾
²FG;\ãq}¬pœÃõ3ÜO‚£ 9Å¥˜zîĞPÆugØåÕ¹íÛ)RàòºÇÛÒˆsuÛ
Ônä$@ğ«Ìè:gGCáœ…ç$üHşşN%±Å„(¿ál÷2€Ñ1C£Œ vËUPv97¹´Ù4ê£ãsè%<kÑ	Ó¡ Í£÷D!ö$=OèEİ€^áè­eĞ{ŠÿÔzwpè=­ ½K§”§³£Ó‚Ïà›òôLã,‘•§	¹
Y7)O1HVÍ:Iyz O×óyz.ŞIyz r¾¸ ë }(àra.Ü‡¾Èæüa5³}è‹ù{²¸ÀKØ~f×2¿})ÿÎnCï¨o½Ì…“eÙmèËmØ+4ìK:Är%{‹şpËü^ôòÔ^ôÕ6À5†o¿Nì¤f×²Yn¸Î¾ì0®×[ëÔºe¹uEa¸Ñªß”!®¹¸>R@\¥BjocµİìHë¾¹NÜj#Ü¦:»·ÜĞ¢‰¨ Qƒ'Io±³¶ÃñÕV¼–Q :‘â[\xøÛd6Gì¸´‹vÈJ«ĞP•UÆxÆ"Ê]LÆ}Ô”Ó4ŞîtÜ>u\+¹ºô•¸rQšW,ş–pn$ÎµmÀ‘a,|Vtl&z¥]&ÕoC	ƒ’tP‡¥(#M¾uÌ‹WT‹ïu6 ×Ö¾Á’æšºr¥¾nÅôØ”GÕŞ3ŒÓ5ccè±ñn~\îæT×(<Yæ!y[]9df}#¸¹vM“°#ˆ¨6¨?ëÑ_ Óúpâ”H“6-£w°„ûGêëvå½¯v½Œ­0…k×$+
Ú„w¤«J=—Àï¦İ²VÎ”­SC
Ø&‘å2ÿ	Öñ-ná°Şíd›”VAV¬Ew°|*­\™_vî”`½KÏ»ƒxEİ ^Åê¯÷$Ä+µŠ{oïËH†d¸¿@2”§\vÚ£œlxo.;ÙkŒì²Ã‘jÑ#¬›\v0HvÙy”u’ËÎGY€eç1¾±ì|ïä²ó¸ òq=?à‚®\ô¡€Ë'p¡ÿ)›ó§.^<ÏÓd?Ãº9ñüY–Îìê¡xşœµş¼Zw ,'QÄó¬ú$ÌwHøb*Eâ¹ÚÖÖÒ^Â¯/9|™oŠç¯ØOj„Îîó¡ÚÕ××Ã«±ºŸn!óPÄ7I–PEšËsURÖ½Ç	Fª£vw'rP!‚°íez~)ƒÁÕï6 äw
f=%“İÉ•ø`ÀÜè«œqŠ3…Zô5–OÅ H3î¿®ç7 n  AğÍ3¾e ûv)R¾S€”jR*­m-³g7DßuHùGÊ÷m„§R–ÄQãQµ'!ı'p
™gc¸qàNÊ(U•‹ívñÙ™Ü(©ãu”cn×0z&[~<æÓÁß•‡íÕéùã [Ô°° ÛŸd`ûSûòŸe`»‹ƒíÏ`ÛKØ¾iÒĞÄ†è¼¿ä[±‰6È¯5HVìp(Ä&²nRì`”\l"ë¤bYÀØD¾›ˆw*6Q ù“€A×0úRÆ&& Ã³Óµ9ÿMÍ v2Ë&î$àB_µm¬Ÿa×'-\¸´›7ÑaÁ©FË]……KÇ£¿³¿X\íª|–e^	í‹•P÷î9?ö7(÷)M,¨\Ÿ‹Æ!nèùÔ»iˆ&‡è‡ şş‚ñ/aúû‹ü=é9’vğ
üËøwVß]Ã¾œÿ×0ø¤O¾!şã¾¯„ ßCí6b»œ ¥¼‚|ck½‰Zw ,'ÀQø¦V}3,N‰´§£çW±çŒOze‘¬èi-5Î®öÎŠ6gø¤gğMşja¦FèìŞ˜~ˆÿQ7tÍùÑnSÅ;iOË[“&“*¼BÉ9 ½§[œ™ÍêXÅó./ÓtÓá	|a”Z2÷ZôZ–Oµd y±¶Z!RÏ×Úr©£n¯àŞ78úó	šŞhHzS†ördğæ2,<ªİRjjl)—¢·82ØÒ“Á[m„·92`°ïKóNï·İi™bB¼án›ä	Ÿ‚ó,êríª—ÄÛÕùØ¦~{%„.+›% G%ï2êô|W@	ê”Æ@ÉV”¼Û öJ:JŞ[€’¡"”´"à¨¡–ïÖ%Ûx”lk#lçPr\ŞC˜f„—âC7AÈóŸø¹uÕí¥ø3Nüÿ›Äô$eâ{‡éäø¾ãµèıÓ Ÿ'ÀíEzĞ³> êE ?˜!À#Æîí°©€ ‡VKPí{›¢fG€³<¶Ø­ ëşŸ8½DS"šÄù“,ï$í=¹!o'ü7^ÅÉYçÕ­A=ìärÂƒ9‡İ–ã$"–§ãĞf?ÚÅzîøuˆàÁ;føcQïNşèrü1·€?F¦6£‹Ìã›¦À|dÉš
QÊ¬›40JÖØ•u’¦Àn,€)°;ß0öÀ;i
ì)ì¥gg º€Ñ—0{' ó,æÜes^¨fÏÿç¦À>ìoF×¨ãØ$X¨]”‹vÀ¾6Ö~kŠİîpmøşì!îuõz Ë¼¡qxj·û@à Ã²ßNY¤f³YNïféÌ®ˆÚøbk}ˆZw ,§£(äƒ=Ôª/Qu39–ò÷d.ƒe6Ô˜·8–óï¬Å±¯æz˜ ;–½´ dÃ–íc#`?GÉ=lš1Æ±•ÖæÆRKTaU¾iôÚ}¡³{=tvW2ÁóØ.d.Qu‘ån÷0x@Bñv·0’v)§?_”•:„#éÍzoè a.¶¤>êçtSú8AP‹X>•>häeË
1ÏJ=õáÒÇQ7b°ĞP‚¬¹…3lğÉ`d‡‘ÑŒLºLËå¶RCµ%:Üa$ò³ÆFîtîqÛ‘‰©2ğ3µerùìOã©JìoÅ65JÇFéz[Ş ˆ£yJÃF'5À
ÜínÕT×[­"•[½L>¬ÿl„;‡0B>îé`ø¸…ª5z®Cİ€0a€>îÂ4p•AØaë
¶jêÅ ):Úáì¾¹kƒ§A²‹‡Âv¬›\0Jv18u’‹Á‰,ÀbpßXNÆ;¹Ô’Sô<5 ]ÀèK˜Ó€ánÆé6ç30^~¨ÉÉº9ùyKgv­¦üüµ>[­;P–“Ÿ(
»çXõõ,ä°pnÖ†v7´UZf—fGç9œÏ7Ù6Â…¡³û>±óü•”MØS¸åŒp(¤/ÄZú”M Å–Èâ¦¡‡ioÉ¨³ˆ.7F2=ƒV£+¾?îG;šÀ4J3D?¤¿0É4-Ö.Ù}t?)%ì&d„eùTÂËóÎÅ"Kô¼4ê@"—%H„Âîrƒé¬ì°veÖÖ:*å––jskt•ÃÚÕk×Ø×:¬Õ%ãÄã£>?’eÈ°c¤‰P{
¢òŸÅQ÷±÷´ ŞœnT§÷WîÏtØ9¹*cØ˜â„sô*P7 ŒN\'fH†˜.<‹ıÏˆè<…ù….&H#!¿¯¯0Yªõ­õÑu9ú BjÑõÓÑp“§D7êyS Ôô!„ƒ>>’ nÄŞlØ»EÍL+º•¿'İˆ½Í$È^-ºgÕ¢n}Ín,,ÌG$Õ"^rp§{W˜î‘éK«‹»ÃtãKî±¦÷ª©.9ØÔ9 ¹ÚİÇ6ñëü÷«>¿ùëàÁÄ7?ä¾yFõŒrwë àqÛ­*¥håVÛEÛGí?ú‘¢>D3~4|ôÑÙã#µÓÀÓ\ö1öËôCÕ÷ã,óªô1©=û[×Ÿğ]o¬ÍzŞ`7÷ïËİ,®NàHÛ`¾üƒƒ35Êò©ä(Ç¦öOÛ(ŸÑ(ñä–ªÙgÙ,·à|Î wœÏ[ë/¨uÊrŠ‚Âş„UÿbM_rhÚŸ²ˆ«Â¶õÍÛE_¶A÷èùJz–i–OôŸ½Àá«6à×4`VX®æO±yò‡&½Àáë¬š¸ÀáüÛ.pø&~â‡o±ªÁ·ù†jğ¼ıßµ¹|/éÃ4‰ï{Hç/pxÚ q"ÁıŒuñîóàFQXßhÕd#Æ†JÉ­?fÏCå$®dŞ0"æ[ŞÓŞÛ^©6µE?a}˜)?å›«ûÏ¬ÿŸ«ÿÎî§ĞLé9™^7/NÑkA	»à ‰N7¶0ÀÎ·¬²‚¦YãıDAqqëC`ØtÜºÿI§~Â	ÜHÀà#ç‚3…|Ï-ê…ªPñE·ç`óàâJµaö¿_ğƒSk?AX‹~Éò©Ö~@3/Û…VğVêùN†êfPÙş[GÛ¤!Úï¿3ˆÿ^Í‚¸ÙÇUjÕê¸ÒI…Ì×`û˜«ËšõYæEÎÉ±0àVÄŸ¬û?«{lE$D}‘’/aó]µôvCºşkbºÔfÿfıı=MòÕ}Ö“ü&˜<Nã2ø?ÿaÔ~
©ı9kı¼£öSòÔ¢@íÿ´ê/d¨½ê¨ı_Ô~jÚ[Ûš[* öµo°££ö—áú9^¤ößZ´(7âx×6NW >Ã[q<š%zRN‘şÜj.•uj‚ù?@ÌT°¸Ëğ*=¸‰Çz««Á=ÄĞ…ûÅ¤§¡³ó·¾—êV¦ÂÜAŞIxt¯ÒğD	§À²õÑ†„DŠÛZô
–OÅ s6B+ätÕscÁTl€º„;°Á&Á…“65Tl¦fém,[!Çœï1¾™ùUì!f„^Í{s–yF8-µ*Î°^­âf}j6“Ír«âkX:³ëtîk­õjİ²Üªˆ¢@¸¯³ê¯·Áb1İï÷ì9#¦ÏÈno[o{©uvoôFÖ‡˜~“'Ü7[ÿoq„û´Û»(‘~ü‘Î¹p@œğÓunOB;º‚Ğ‘ËİçãGæßº=üew–Ü)Ü.¶…{Pqâø	dQ·ªpdçí¨ØW&[lh ÙJbóN‡ú55\`h©ÌzZ\RUm™£T³½u:J\ó”ú6ÑèÛõ|G TÔÍ ”úÎ¥ÒX«3Ø¿+ƒÛ‡Û­
p{f·pÍêí-÷Dïv¸}Çí{­ÿ­nñ2[ q9Yì`ªÖBà$6yº3³ÜõÑ69ÈqªµhÛé ‡Yç!·`ö>=ß ‡ºr ·}r4'>`_Vš•6'VhbÍbs¢Áš6ª©Ì‰×9f¤xd`œp§ï4jbëØ°8ÛÍjII3ËºjQA4¯¤âM¹[ÙU,*Vjrm,óæœÔq™ÙÖq»:6+­ƒ¿a¥ÉbY½m#{qògÎÑDu»hv6³k½W‰wäßY3mPãÎq@<]Ÿ=/³“<×(Òï0©İÎl—mólàs)Úæ[ëjİ²œhCQPøw±ê»&¾r7÷•…wä<ÿu{}İ°f¹gøºó²
ÿ^6`§Ì*ü#j¾7›'şó'Uø»X5¡ğ/äß¦ğïƒŸPø±
ÿ¾|Cáßo¯ğïos9 éQMâ@é¼ÂAâ‚û`ë¢Ûû‚<¸QV’ÅVı1^IwÒæPöœYI.¤´y[1{,ï)Í.ÏªâR‘%l‰5e)ßTı—ÙHË5Rg÷*·¦”úù”9@µHçD•FÌGtéÔSl»åÅöh,²¬<²Å
¶¤® wØİÙ_ÄÃ×±î_Æ)¥´~n-*±|*­_—Xe´ZõèYÑÇI+Aİ8!±ª‰oJ¬^ƒI_hvQZbEšXhK¬kºBM%±¨Ó‹&Æú£•l‹©‹½˜TuŠ©!k?¬ˆ© ¸Ù^AI2.ï@‰7FØq,Æ4¿Q–y¡uIjKâp&òÃ¸c„¤a#taîá­±Tÿãê<Ùÿ¥)µkÂú_eôëeÓ„š­f³œlZÃÒ™]—‘YÖZë#Ôºe9Ù„¢ ›´êG©ºIàuü¿Mòhär/›áßYÉ»J³<Ö!4syV6g¯³²iµšŸÀæIÙtÅ¤²éDVMÈ¦“ø·É¦“ñ²©ÆÈ¦Sø†l:o/›N³¹œ†ôMâé¼l:Ó q%Á}–uñ!î+óàFQMg[õslÄX6­u²i={ÎÈ¦«(›x2Ö3ÂòæææÖ¦ê¬Rt.«C Ç7ÒùÖıê¾³»[{¼b¯Ÿ§ÚÉEºÒ]j—Aá)1ªá'£ÒAáBô—Á'¢î-›[õÑ…4%røµè"–O%rğAy‘óa´Z]¬ç%š¾Dêf ‘s©#/ñ2ûêË3@=ÂõŠ ^jCC©¥R)7FW: ^åzµuê“ *”|d§BL€ÚÚØçÍÕæQ!€•YWy²¹»2§±½£¹amdæ0¿@4Â‹´m—^i¯¸R(ÆÛ@cuû#íüÈZ¤ŸgK»ÒG«CØòÑrÁ÷oâ8{Ö­ğâ5ŸhV×Ç©Ò@Š›[æ¯®Ía“à«E×M‡M@2Íë…Çô¼1`u6…`ó¦6?bà¾9ƒÍ#6o)Àæ59lV›Jmm¥èV‡ÍÛ<6o·îïpØ|Øä¹_ºº€0¦ä»BÆ˜OJ>ZŠJ•‘5ÌˆÎÌ»AB »M‹«Ê¢:â²´"ÜC›«,rıHÁìÀv[ËDjë¼Ò¶skô…UJ-!´Ã€ß23á¸º´»±”×gÊ°ñ1.8©Ê˜–×İO·ó1/0ÏîÌ¡p®EwM‡v€<ö»…ğ{ô¼7 uÚ…G ı¾Úï7¼<AûQí ıÚÚÛ\»¡<«)zÈ¡ıaöG¬ûGÚçÛıo
öÃ€J´”PÅ`z=À*÷ ê/&ãæc{»¹É‚”—Dvÿbá—BŸ?Àg…óqŠŞ»xËl:€Ç×ÃÈ½ä˜Ø\ÒX×XaêêgÁöu£HgèÜvCv_í=à8Ëò‘2Ì¤w°"&GpÀ¶°¨ZÂ$ybjş‹Ò)rOø£9ò!¾jÑcÓ‘P—'Ÿ‰p×óã|P7èäó‰ùpÓö“†ßO©YjÓv(Ş´ı4ÛÌèº.½i»N3şL¢?ê’Ÿµş>§ş‚ÉK{©Šª‘ìŞxcíól«jG«Ç/°Ìk×§4¼'¬ó/­{ï5û›å4¼/³tf×T9¾b­ŸTë”å4<•ã«VıkÆ:Ö1ÖSŒuc±JMåYmmÈøuÇXßğŒõMëş[±&ÀXAô $^ŸÌô/ebíÔzæq‰s¹ml¯”âdâí|Î±QqÑâ9	îƒY$$[|Æuh RÁ²ç/ã"¢lãX¢•¼ˆ’´Ézu¾“ò÷7Stx	0o{¤ Ğ0ô¸d)ªÀ(Â:«mb4ÎKE	!j¹‚y
É}+£•sÎ„‘H.Íıà±cqÏ:·6:Š€hÓÕp	²Ûúî•Â~5'>?é"Á•ê£oçx‘(®Eß™í</~W\ø==¿xu/Š„À‹O'x‡&à3F?ÍnJ›€Çib?ÍbğGÖôÇjšòÃTî©F?a›Ø¼ÙÛ€?U}úÀfü\fÏü‚¿ıRŞşKc­[¼]ó+şµk×Œíf!rKÖşø·8½G6>1<\Œ…ÅïØKÌõ'¨çß³Ì‹[Sææ¬ã?úiÂB§jh.ğY¥îX6EŸ6mô'vÖÚ¤ŒbÛâÏö·QvüÅ:û«:ë@™“%yµş–šÙ‰šÙß“3C}ç€ cëYëìê,ş “Ôì96Ë‰±çm*·s*ÿ´Ö/¸©Üc(
†ê¿¬ú‹	Än0§ĞP}Š1È¡/çßY„¬YnÈÿ²º;²†ê+ğp#’3TkjşJ6OªwNj¨nÌª	Cuşm†ê¦ø	Cu3–ÀP}ß0T7ÇÛª3l.¯Ö\bHŸ¢IÌd}B:o¨¾Æ q—Ü1ÖÅê¢e¹UE	wŒU½ª§ºUãì9c¨ŞÜ²».on­”+È½‘õéá›–ê›­ÿ·¨ÿÎîâ-{Q–€‡²Ó	ò´“›²~“Ò òRğ¾;Ÿî@İéåeá×¸Kˆ‚?ísÏªrf°%†”µcd/`-ÑX%˜›BiãK0Æ™)Aºï`	^ıv:ñÃQ0ªş¦ZºìğªNÃ1œí—ÏaKB&eNÖğÖ°|*s`/ğÖ ¼5z¾C0–9º\Ò[ã˜€ÄFUªÎPó.5ƒ*•8±.µÍèº'­K¦)¿;Ñ!u©÷X‡ïU‡i½t)„|ç±€Üšíc*?]}nÃ2/ ïM‰¡m­ûíÒÌq†š½Ï3GÊ¿ş~ã‹ûÈÛ[ë8¾¸/Ï(
|QoÕ?˜á‹3_4ğÅı|ÑØÒT*7öD/š<_4[ÿ³_l¿Ë„òŒH7_]Åù øÃa©’9RÇIâ½œùu«J}Ğ^¸·›B¿`êAgãÈA¹r¸
¥ÁrG)›A*;_P`ä?ÓÁš6H¢jü >pVG|v»k` ;–†—¦BÍÃ©|ËF["$ˆÑ¾7ıúŞÀ%Ki e²dÈÒZY®2r5"®·–C›ÜÃ™(“ S·ZJÈ*9™¿Üàvåğf@ï~Õ>x÷MÅç25x4ÑCë:±·²²Š{şÜ)rZRØß¯÷C“äğô«Æ&x}İâ*lY$0Ô½Ô­<’01*-ÖğUïP2.°¼oA,Lhçé¶æql#hNNÅÂdµ;Š“UÌîÃÛ„Ò’auµŠõQKN€(kQëtô™ m³õluƒ ÑC€tdø}£á3ü^à.œ“âô³4ß’œş@Ê]8×:ŞY›r7¿'wÎ7NĞëøwVøÆİÅ}¤ÚƒYwá®6ğnis¶Úí^(bö°¢ˆÙÓZïåDÌCyƒ¢ b:­úŞs1]"æá¼ˆ)•Úg5õ4GˆÙÇ‹˜EÖÿ¾NÄ<á¼V>3!NÉÄ‹*¸ËíM‘TuŞ‰–Ü¥)Ã+%F”}Kâ.vz!œj²C@%íPÍ[YŠ`Yš;wá½E8Ó9ÈlWŒñõDƒ~Ã´‚ÊƒˆÁ§ğq|Æá&GV
ÖGûå CÖĞéP,È*8PÏƒ# n`¡†YCŒÀsİéÅL®w˜<¤ “ä1ÙŞĞÚÓ[=+:Ôar‰ÇäRë™ÃäóÀ$/Ã.Æ¹ $bœ°†<Ašl$ò‚Sá.O-÷-u 2ZúÃân£IW2ôÂ"¶K?-o¹ÏkTªşN&xìm3JØâÂ0„£nG3ÈÚù&kaÍ íp«ÿ‘¿¢L£ß´¿!8# /ù}N©jÌ¡à•Ã>Ô@ÆÅÑúhyñ„4ÂØ¦C<€G|I(/ëÙºñÂ$_I pÕÓš=š¶€ÏÕÄúB³Øî·¦j*˜nLú~°¾D+Ø"¶óöïJsàAk=~<=ğyx8\òÛk:š¢ûÃÁ”ç«éá‰9Ÿ\ÿo½ü¼Ùé?rWWæ3/æÀxœ–klUÇW¸”BK[Jy¿A¨yŠ”ŞVĞQ¨¯Â ×ÛÙi;ívvÏîlËª ¢¸¼) HA©1&|1ÆÄDÁ ÑJ"1¢BFñvÏ²İ]§†OóåüîyÿÏ¬è²=cõ¾'l„¬ .ô™•‘ê‰¡`ïì"ÙWÅë¹¶qçìº™Ğ’¬Õ×4í°×±‚áÔ0C²í—síz#ç5
é.ôÁIHĞ/¢fÈ‹3ìX›°LÀ’-¨hæÚ–¥1¬§ĞG${2EÈ¨ñÚÇôVEl£ƒÍì%Yù’c\»Ü\öNuy;JŸÙPÔµSö¼[²i?ïášÓ@X¶Ğsÿ‹ÅœôÌQyíæÚÇÍ`®Ğ$Y;!a‡ı"—y€ı$»å;ÊµÖ2òŸÊÜ,ì‡üô,,»ø×¢W‰ ôŠ¹]b’lrÁI®å+‰ÙvoK½2p¨döäƒ\Ûy‰&ôü$DØÂu,#îc8àÉÖl[Ëµ“‹	)ô.>Ú;‡F–¬dü~®eüNĞ÷NT¿ßE	»ğ^ÉNi¸V“EØØÔàêÌh¥eû,›&ó>Àq’¿¸•kS³	/ôÑnÙ¨W‰ˆßñ6„âÄû'H¶ê´ÊíÓ›ÔË‰Bï™ÀcF…€Hf^-áÚ…Ü®1£IB’ä£ZÔ›íÏ[¶•Ôô"ÀÉj3ÛcË§Øt/\¢éNœ*ÙEŸÚšÚ)Ms/\8²õ8Cp©–3›)ôQÉË
f8¬
WèXõ¦ß²ë‰F+€Î’¬÷›¹6e_YŒ~XèCİÆ(¶ŒP POngKv¶`×ò†Û9Bs‡å7°K6ìê&•íâKS³u+-–>"Ùµ=¸Ö{,as…Ş¯³Æy€J6âGÕæ<$ûÇ„>èÿu5ÀÇ%ûã%×õ„ûÒv,ä|À’}»EµoxwbÊ…Ş¿ó…Ä'Ÿ’l@‰ÚÇ•…D<İÉ”Ät/=ø¬dµr­a/Aî	%M	.\$Ù•G”«	Déî®,;‰ËĞbÀç$«ÍV+¹Ì!hIªÄ˜UU¦áxÃv ‘Šğ< (‰¹¡ÚSä'ä¡wWHuÄŠ=ê|Q2Õ
®­`d!RË”ö(V’eÌRonáKS:Ó‰i@)°J²Á3síV!ÕBÏLP¬´$û- tù†='fR+ô,evŒ[ _²u% 3—ÒCõBÏq;•Ú€É&µ©[¹òÓ¦&hrc0$Yİe©KLØ½1F9äÈŒH6ôD×2"¨Aè#ïäPØ¸T²¿‹Ô¥l2	
½Wjâ¾ørûR™7YdöŠûœuLŒË —K6ó352›§õjª`R	Ú“†c†âÜ
À×$ûèˆ
jn-q+éâ%.¾ø†d]Q“sı
)ö*êX‡bØ¸ZuìÃ®}şË'1«5Ôúø¸PJVÖM=ôÃ0r¶.Mh]‚Äõ€$ûò;cKÂ6¦ææöWcà&ÀÍ’Jb{Å%k‹ĞóÜÿ1Ü
Ø,Ù8Ï.®+§Ã¾SÒ‘İ¸C²ÙYs¸¶ü,½ùfê¥^Kwî’¬¢M¤Öj"ŞrïgÒYÆİ€-’ıÓ¢„°²†¨=i¢–º{¸ğmÉ¾.W}3.jûÒ:}	Üx@²ü6åÔt0mlÜ®<¬’š¯PsâZİu:±=xğ¨dórÔò°‹Ä¼ãÎtŒŞ1Àã’¼¥üœÿ•˜ˆnB©|ğ¤d—Ú”T¿ÿ=Q§R…+ıwO¾'ÙŸ•J•>˜GÈ™ø/pñ,Á