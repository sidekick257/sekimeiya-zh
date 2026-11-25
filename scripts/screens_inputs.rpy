screen CharacterSelect(prompt, show_timeline=False):

    predict False ## Avoid predicting this screen
    default character = None
    default timeline = None

    style_prefix "charsel"

    add "bg inputchar"

    hbox:
        xalign 0.5
        yalign 0.5

        grid 3 3:
            xalign 0.5
            xoffset 68
            yoffset 5
            for char_name in ["atsuki", "shiroya", "miiya", "sai", "akaro", "katei", "erina", "isla", "naomi"]:
                button:
                    action SetScreenVariable("character", char_name)
                    frame:
                        has vbox
                        add "gui/input/{}.png".format(char_name) yoffset 15

        null width 100

        vbox:
            xsize 500
            xalign 0.5
            xoffset 25
            yalign 0.5
            spacing 8

            if show_timeline:
                showif character:
                    vbox:
                        at timeline_prompt_tf
                        spacing 8

                        text prompt xalign 0.5 xsize 500 size 25 text_align 0.5 outlines [ (3, "#191b1c", 0, 0), (2, "#011c2c", 0, 0),  (1, "#000000", 0, 0) ]
                        add "gui/input/prompt_underline.png" xalign 0.5

                    frame:
                        background None
                        xsize 250
                        ysize 330
                        xalign 0.5

                        at timeline_frame_tf

                        has vbox

                        button:
                            style "charsel_timeline_button"
                            background "gui/input/world1.png"
                            hover_background "gui/input/world2.png"
                            selected_background "gui/input/world2.png"
                            action SetScreenVariable("timeline", "a")
                            xsize 250
                            ysize 90
                            xalign 0.5
                            if character:
                                text character.capitalize()+" A" style "charsel_text_glow"
                        button:
                            background "gui/input/world1.png"
                            hover_background "gui/input/world2.png"
                            selected_background "gui/input/world2.png"
                            action SetScreenVariable("timeline", "b")
                            xsize 250
                            ysize 90
                            xalign 0.5
                            if character:
                                text character.capitalize()+" B" style "charsel_text_glow"
                        button:
                            background "gui/input/world1.png"
                            hover_background "gui/input/world2.png"
                            selected_background "gui/input/world2.png"
                            action SetScreenVariable("timeline", "c")
                            xsize 250
                            ysize 90
                            xalign 0.5
                            if character:
                                text character.capitalize()+" C" style "charsel_text_glow"

                    button:
                        at timeline_confirm_tf
                        style "charsel_confirm_button"
                        selected False

                        if character and timeline:
                            background "gui/input/confirm.png"
                            hover_background "gui/input/confirm2.png"
                            activate_sound "sounds/sys23.wav"
                            action Return(character+" "+timeline)

                else:
                    text prompt xalign 0.5 xsize 500 size 25 text_align 0.5 outlines [ (3, "#191b1c", 0, 0), (2, "#011c2c", 0, 0),  (1, "#000000", 0, 0) ] 
                    add "gui/input/prompt_underline.png" xalign 0.5

                    null height 40

                    button:
                        style "charsel_confirm_button"
                        selected False

            else:
                text prompt xalign 0.5 xsize 500 size 25 outlines [ (3, "#191b1c", 0, 0), (2, "#011c2c", 0, 0),  (1, "#000000", 0, 0) ] 
                add "gui/input/prompt_underline.png" xalign 0.5

                null height 40

                button:
                    style "charsel_confirm_button"
                    selected False

                    if character:
                        action Return(character)
                        hover_background "gui/input/confirm2.png"
                        activate_sound "sounds/sys23.wav"
                        background "gui/input/confirm.png"

transform timeline_frame_tf:
    alpha 0.0
    on show:
        linear .3 alpha 1.0

transform timeline_prompt_tf:
    yoffset 173
    on show:
        linear .3 yoffset 40

transform timeline_confirm_tf:
    yoffset -113
    on show:
        linear .3 yoffset 0

style charsel_frame is frame:
    background "gui/input/flower.png"
    hover_background "gui/input/flower2.png"
    selected_background "gui/input/flower2.png"
    xsize 175
    ysize 175

style charsel_confirm_button is button:
    background "gui/input/confirm0.png"
    hover_background "gui/input/confirm2.png"
    selected_background "gui/input/confirm4.png"
    xalign 0.5
    xsize 310
    ysize 50

    #xsize 310
    #ysize 50
    #xalign 0.5

style charsel_vbox is vbox:
    xalign 0.5
    yalign 1.0

style charsel_text_glow:
    xalign 0.5
    yalign 0.5
    yoffset -7
    size 33
    outlines [(17,'#77d0ff02',0,0), (16,'#77d0ff04',0,0), (15,'#77d0ff06',0,0), (14,'#77d0ff08',0,0), (13,'#77d0ff0a',0,0), (12,'#77d0ff0c',0,0), (11,'#77d0ff0e',0,0), (10,'#77d0ff10',0,0), (9,'#77d0ff12',0,0), (8,'#77d0ff14',0,0), (7,'#77d0ff16',0,0), (6,'#77d0ff18',0,0), (5,'#77d0ff1a',0,0), (4,'#77d0ff1c',0,0), (3,'#77d0ff1e',0,0), (2,'#77d0ff20',0,0), (1,'#77d0ff40',0,0)]

default map_selection_name = None
default is_map_selected = False
default map_hover = None

screen MapSelect(prompt, number=4):
    predict False ## Avoid predicting this screen

    default map_zoom = 1
    if number==3:
        $ map_zoom = 0.90
    elif number==4:
        $ map_zoom = 0.92

    add "bg inputmap"

    hbox:
        xalign 0.5
        yalign 0.5

        fixed:
            xsize 640
            ysize 720

            if number==1:
                fixed:
                    style_prefix "mapsel"
                    xfit True
                    yfit True
                    xalign 0.5
                    xoffset 51
                    yalign 0.5

                    use MapSelectButton(9, 98, 130, 108, "storeroom", map_zoom)
                    use MapSelectButton(174, 71, 132, 135, "living room", map_zoom)
                    use MapSelectButton(74, 214, 65, 56, "bathroom", map_zoom)
                    use MapSelectButton(174, 214, 86, 56, "kitchen", map_zoom)
                    use MapSelectButton(174, 279, 132, 104, "bedrooms", map_zoom)
                    use MapSelectButton(9, 279, 130, 104, "bedrooms", map_zoom)

                    add im.Crop("gui/map/F7.png", (206, 0, 350, 390)) zoom map_zoom

            elif number==2:
                fixed:
                    style_prefix "mapsel"
                    xfit True
                    yfit True
                    xalign 0.5
                    xoffset 30
                    yalign 0.5

                    use MapSelectButton(10, 120, 171, 67, "storeroom", map_zoom)
                    #use MapSelectButton(492, 596, 80, 90, "mechanical room", map_zoom)
                    use MapSelectButton(492, 575, 80, 129, "mechanical room", map_zoom)
                    use MapSelectButton(381, 36, 35, 24, "bathroom", map_zoom)
                    use MapSelectButton(424, 36, 32, 24, "bathroom", map_zoom)
                    use MapSelectButton(471, 101, 137, 86, "hall b rooms", map_zoom)
                    use MapSelectButton(471, 195, 137, 87, "hall b rooms", map_zoom)
                    use MapSelectButton(471, 290, 137, 86, "hall b rooms", map_zoom)
                    use MapSelectButton(471, 384, 137, 87, "hall b rooms", map_zoom)
                    use MapSelectButton(471, 479, 137, 88, "hall b rooms", map_zoom)
                    use MapSelectButton(256, 370, 140, 94, "hall b rooms", map_zoom)

                    add "gui/map/F1b.png" zoom map_zoom

            elif number==3:
                fixed:
                    style_prefix "mapsel"
                    xfit True
                    yfit True
                    xalign 0.5
                    xoffset 30
                    yalign 0.5

                    use MapSelectButton( 11, 123, 171, 67, "storeroom", map_zoom)
                    use MapSelectButton(493, 578, 80, 121, "mechanical room", map_zoom)
                    use MapSelectButton(392,  39, 32, 24, "bathroom", map_zoom)
                    use MapSelectButton(432,  39, 32, 24, "bathroom", map_zoom)
                    use MapSelectButton(472, 104, 137, 86, "hall b rooms", map_zoom)
                    use MapSelectButton(472, 198, 137, 87, "hall b rooms", map_zoom)
                    use MapSelectButton(472, 293, 137, 86, "hall b rooms", map_zoom)
                    use MapSelectButton(472, 387, 137, 87, "hall b rooms", map_zoom)
                    use MapSelectButton(472, 482, 137, 88, "hall b rooms", map_zoom)
                    use MapSelectButton(257, 373, 140, 94, "hall b rooms", map_zoom)
                    use MapSelectButton(257, 135, 66, 127, "hall a rooms", map_zoom)
                    use MapSelectButton( 47, 198, 135, 87, "hall a rooms", map_zoom)
                    use MapSelectButton( 47, 293, 137, 86, "hall a rooms", map_zoom)
                    use MapSelectButton( 47, 387, 137, 87, "hall a rooms", map_zoom)
                    use MapSelectButton(257, 475, 140, 95, "hall a rooms", map_zoom)
                    use MapSelectButton( 47, 482, 137, 88, "security room", map_zoom)
                    use MapSelectButton(257, 270, 140, 95, "event room", map_zoom)
                    use MapSelectButton(171, 578, 314, 121, "lobby", map_zoom)
                    use MapSelectButton(331, 135, 66, 55, "cleaning room", map_zoom)
                    use MapSelectButton(331, 198, 66, 64, "staff room", map_zoom)

                    add "gui/map/F1b.png" zoom map_zoom

            elif number==4:
                fixed:
                    style_prefix "mapsel"
                    xfit True
                    yfit True
                    xalign 0.5
                    xoffset 32
                    yalign 0.5

                    use MapSelectButton(53, 71, 67, 547, "f1 stairs", map_zoom)
                    use MapSelectButton(426, 71, 45, 547, "f3 stairs", map_zoom)
                    use MapSelectButton(128, 71, 290, 541, "inside partitions", map_zoom)
                    use MapSelectButton(53, 618, 419, 81, "outside partitions", map_zoom)

                    add im.Crop("gui/map/F2.png", (137, 0, 481, 710)) zoom map_zoom

        vbox:
            xsize 640
            yalign 0.5
            yoffset -30
            xoffset -20
            text prompt text_align 0.5 xalign 0.5 xsize 500 size 25 outlines [ (3, "#191b1c", 0, 0), (2, "#011c2c", 0, 0),  (1, "#000000", 0, 0) ] 
            add "gui/input/prompt_underline.png" xalign 0.5

            null height 290

            button:
                xsize 310
                ysize 50
                xalign 0.3
                xoffset 66
                #style "charsel_button2"
                background "gui/input/confirm0.png"
                selected False
                activate_sound "sounds/sys23.wav"
                hover_background "gui/input/confirm2.png"
                if is_map_selected:
                    background "gui/input/confirm.png"
                    action [SetVariable("is_map_selected", False), Return(map_selection_name), SetVariable("map_selection_name", None)]
                #text "Confirm" xalign 0.5 yalign 0.5

screen MapSelectButton(x,y,w,h,name,map_zoom=1):
    predict False ## Avoid predicting this screen
    default color_idle = "#0000"
    default color_hover = "#F004"
    default color_selected = "#F009"
    default color_hover_selected = "#F009"

    button pos (int(round(x*map_zoom)),int(round(y*map_zoom))) xysize (int(round(w*map_zoom)),int(round(h*map_zoom))):
        action [SetVariable("map_selection_name", name), SetVariable("is_map_selected", True)]
        hovered SetVariable("map_hover", name)
        unhovered SetVariable("map_hover", None)
        if map_hover==name:
            if map_selection_name==name:
                background color_hover_selected
            else:
                background color_hover
        elif map_selection_name==name:
            background color_selected
        else:
            background color_idle

screen ToggleC5Questions:
    add "gui/input/questions_toggle_prompt.png"

    hbox:
        ypos 540
        xalign 0.5
        spacing 170
        imagebutton auto "gui/input/enable_questions_%s.png":
            hover_sound "sounds/sys2.wav"
            activate_sound "sounds/sys15.wav"
            action [SetVariable("persistent.enable_c5_questions", True), Return()]
        imagebutton auto "gui/input/disable_questions_%s.png":
            hover_sound "sounds/sys2.wav"
            activate_sound "sounds/sys15.wav"
            action [SetVariable("persistent.enable_c5_questions", False), Return()]
