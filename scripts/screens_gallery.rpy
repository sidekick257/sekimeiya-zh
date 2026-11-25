define cg = 0
define gallery_current = 1
define gallery_shown = 0
define gallery_page = 1

screen cgs:
    tag menu
    button:
        xsize 1280
        ysize 720
        padding (0,0,0,0)
        activate_sound None
        if gallery_shown == 1:
            add "images/bg cg8-1.png"
        elif gallery_shown == "11":
            add "images/bg cg8-2.png"
        elif gallery_shown == "12":
            add "images/bg cg8-3.png"
        elif gallery_shown == "13":
            add "images/bg cg8-4.png"
        elif gallery_shown == 2:
            add "images/bg cg5-3.png"
        elif gallery_shown == "21":
            add "images/bg cg5-4.png"
        elif gallery_shown == 3:
            add "images/bg cg2-3.png"
        elif gallery_shown == "31":
            add "images/bg cg2-2.png"
        elif gallery_shown == "32":
            add "images/bg cg2.png"
        elif gallery_shown == 4:
            add "images/bg cg9-2.png"
        elif gallery_shown == "41":
            add "images/bg cg9-1.png"
        elif gallery_shown == 5:
            add "images/bg cg4-2.png"
        elif gallery_shown == "51":
            add "images/bg cg4.png"
        elif gallery_shown == 6:
            add "images/bg cg1.png"
        elif gallery_shown == "61":
            add "images/bg cg1-1.png"
        elif gallery_shown == "62":
            add "images/bg cg1-2.png"
        elif gallery_shown == "63":
            add "images/bg cg1-3.png"
        elif gallery_shown == "64":
            add "images/bg cg1-4.png"
        elif gallery_shown == "65":
            add "images/bg cg1-5.png"
        elif gallery_shown == 7:
            add "images/bg cg7.png"
        elif gallery_shown == "71":
            add "images/bg cg7-3.png"
        elif gallery_shown == 8:
            add "images/bg cg6.png"
        elif gallery_shown == "81":
            add "images/bg cg6-6.png"
        elif gallery_shown == "82":
            add "images/bg cg6-7.png"
        elif gallery_shown == "83":
            add "images/bg cg6-4.png"
        elif gallery_shown == "84":
            add "images/bg cg6-5.png"
        elif gallery_shown == "85":
            add "images/bg cg6-2.png"
        elif gallery_shown == 9:
            add "images/bg cg3-1.png"
        elif gallery_shown == "91":
            add "images/bg cg3-2.png"
        elif gallery_shown == "92":
            add "images/bg cg3-3.png"
        elif gallery_shown == "93":
            add "images/bg cg3-4.png"            
        elif gallery_shown == 10:
            add "images/bg cg10.png"
        elif gallery_shown == 11:
            add "images/bg cg11-1.png"
        elif gallery_shown == "111":
            add "images/bg cg11-2.png"
        elif gallery_shown == "112":
            add "images/bg cg11-3.png"
        elif gallery_shown == "113":
            add "images/bg cg11-4.png"
        elif gallery_shown == "114":
            add "images/bg cg11-5.png"
        elif gallery_shown == "115":
            add "images/bg cg11-6.png" 
        elif gallery_shown == 20:
            add "gui/main_menu2.png"
        elif gallery_shown == "201":
            add "gui/main_menu3.png"
        elif gallery_shown == 21:
            add Transform("gui/main_menu_c1b.png", xalign=0.5)
        elif gallery_shown == "211":
            add "gui/main_menu_c1.png" at tf_cover_art_panning
        elif gallery_shown == 22:
            add "images/bg cg12.png"
        elif gallery_shown == 23:
            add "images/bg cg5.png"    
        elif gallery_shown == "231":
            add "images/bg cg5-2.png"
        elif gallery_shown == 24:
            add "images/bg cg13.png"    
        elif gallery_shown == "241":
            add "images/bg cg13-2.png"
            
            
        else:
            add "images/bg atsukis.png"

        if gallery_shown in [10, 22, "13", "21", "32", "41", "51", "65", "71", "85", "93", "115", "201", "211", "231", "241"]:
            action Show('gallery', transition=Dissolve(0.2))
        else:
            action SetVariable('gallery_current', gallery_current+1), SetVariable('gallery_shown', str(cg)+str(gallery_current))

transform tf_cover_art_panning:
    yalign 0.5
    subpixel True
    block:
        pause 2.0
        ease 5.0 yalign 0.0
        pause 2.0
        ease 10.0 yalign 1.0
        pause 2.0
        ease 5.0 yalign 0.5
        repeat

screen gallery:
    predict False 
    tag menu
    key "game_menu" action Return()

    style_prefix "gallery"   
    
    add "gui/gallery/background.png"
    vbox:
        xalign 0.5
        yalign 0.54
        spacing 10
        hbox:
            spacing 10
            if store.gallery_page == 1:
                button:
                    background "gui/gallery/cg1-1.png"
                    hover_background "gui/gallery/cg1-2.png"
                    action SetVariable('cg', 1), SetVariable('gallery_shown', 1), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg22-1.png"
                    hover_background "gui/gallery/cg22-2.png"
                    action SetVariable('cg', 22), SetVariable('gallery_shown', 22), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg23-1.png"
                    hover_background "gui/gallery/cg23-2.png"
                    action SetVariable('cg', 23), SetVariable('gallery_shown', 23), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                
                button:
                    background "gui/gallery/cg3-1.png"
                    hover_background "gui/gallery/cg3-2.png"
                    action SetVariable('cg', 3), SetVariable('gallery_shown', 3), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))

            else:
                button:
                    background "gui/gallery/cg6-1.png"
                    hover_background "gui/gallery/cg6-2.png"
                    action SetVariable('cg', 6), SetVariable('gallery_shown', 6), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg7-1.png"
                    hover_background "gui/gallery/cg7-2.png"
                    action SetVariable('cg', 7), SetVariable('gallery_shown', 7), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg9-1.png"
                    hover_background "gui/gallery/cg9-2.png"
                    action SetVariable('cg', 9), SetVariable('gallery_shown', 9), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg24-1.png"
                    hover_background "gui/gallery/cg24-2.png"
                    action SetVariable('cg', 24), SetVariable('gallery_shown', 24), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))


        hbox:
            spacing 10
            if store.gallery_page == 1:
                button:
                    background "gui/gallery/cg4-1.png"
                    hover_background "gui/gallery/cg4-2.png"
                    action SetVariable('cg', 4), SetVariable('gallery_shown', 4), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))               
                button:
                    background "gui/gallery/cg8-1.png"
                    hover_background "gui/gallery/cg8-2.png"
                    action SetVariable('cg', 8), SetVariable('gallery_shown', 8), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg5-1.png"
                    hover_background "gui/gallery/cg5-2.png"
                    action SetVariable('cg', 5), SetVariable('gallery_shown', 5), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg11-1.png"
                    hover_background "gui/gallery/cg11-2.png"
                    action SetVariable('cg', 11), SetVariable('gallery_shown', 11), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))

            else:
                button:
                    background "gui/gallery/cg10-1.png"
                    hover_background "gui/gallery/cg10-2.png"
                    action SetVariable('cg', 10), SetVariable('gallery_shown', 10), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg2-1.png"
                    hover_background "gui/gallery/cg2-2.png"
                    action SetVariable('cg', 2), SetVariable('gallery_shown', 2), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg21-1.png"
                    hover_background "gui/gallery/cg21-2.png"
                    action SetVariable('cg', 21), SetVariable('gallery_shown', 21), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
                button:
                    background "gui/gallery/cg20-1.png"
                    hover_background "gui/gallery/cg20-2.png"
                    action SetVariable('cg', 20), SetVariable('gallery_shown', 20), SetVariable('gallery_current', 1), Show('cgs', transition=Dissolve(0.2))
    hbox:
        yalign 0.9
        xalign 0.5
        
        button:
            style "gallery_page_button"
            xoffset 7
            action SetVariable('gallery_page', 1)
        button:
            style "gallery_page_button"
            xoffset -7
            action SetVariable('gallery_page', 2)
    button:
        style "return_to_title_button"
        xalign 0.93
        yalign 0.9939
        action Return()


style return_to_title_button:
    hover_sound "sounds/sys2.wav"
    background "gui/music/button.png"
    hover_background "gui/music/button_hover.png"
    activate_sound "sounds/sys3.wav"
    padding (0, 0, 0, 0)
    xsize 300
    ysize 37   

style gallery_button:
    xsize 273
    ysize 178 
    activate_sound "sounds/sys20.wav"

style gallery_page_button:
    background "gui/gallery/diamond.png"
    hover_background "gui/gallery/diamond2.png"
    selected_background "gui/gallery/diamond2.png"
    xsize 55
    ysize 70
