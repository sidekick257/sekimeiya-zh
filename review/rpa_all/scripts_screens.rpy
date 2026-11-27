
################################################################################
## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

translate ru style default:
    font "fonts/arial.ttf"

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing True # ESSENTIAL for multiple resolution compatability
    mouse "input"
    layout "greedy"
    caret At(Solid("#fff", xsize=1, xoffset=1), caret_blink)

transform caret_blink:
    alpha 1.0
    block:
        alpha 1.0
        pause .5
        alpha 0.0
        pause .5
        repeat

transform caret_solid:
    alpha 1.0
    block:
        alpha 1.0
        pause .5
        repeat

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True
    
style gui_text:
    properties gui.text_properties("interface")
    outlines [(0, "#0009", 1, 1)]

style button:
    properties gui.button_properties("button")
    mouse "button"
    hover_sound "sounds/sys2.wav"
    activate_sound "sounds/sys3.wav"

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")




style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    left_gutter 6
    right_gutter 6
    thumb_offset 6

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    top_gutter 6
    bottom_gutter 6
    thumb_offset 6

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Transform(Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile), alpha=0.7)



style popup_frame:
    padding (7,7,7,7)
    background Frame("gui/frame_3.png", Borders(15, 15, 15, 15), tile=gui.frame_tile)

style popup_button is button:
    xfill True

style popup_button_text is button_text:
    color '#FFF'
    hover_color '#cce6ff'

style titled_frame:
    background Frame("gui/titled_frame.png", gui.titled_frame_borders, tile=gui.frame_tile)

style frame_title:
    xfill True
    xalign 0.5
    bottom_padding 8

style frame_title_text:
    size 16
    ypos 4
    xalign 0.5

    font "fonts/Acumin-BdPro.otf"

transform tf_dropdown_menu:
    on appear:
        alpha 0
        linear 0.05 alpha 1.0
    on show:
        alpha 0
        linear 0.05 alpha 1.0
    on hide:
        linear 0.05 alpha 0.0


################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say


screen say(who, what):
    style_prefix "say"

    vbox:
        if who:
            window:
                id "namebox"
                style "namebox"
                text who id "who"

        window:
            id "window"
            text what id "what"

    ## If there's a side image, display it above the text. Do not display on the
    ## phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0  size (200, 200)

## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    #xfill True
    #yalign 1.0

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)
    padding gui.namebox_borders.padding

style say_vbox is window:
    xsize gui.dialogue_width
    yalign gui.textbox_yalign

style say_window is window:
    xsize gui.dialogue_width
    #ysize gui.textbox_height
    yminimum gui.textbox_height

style namebox is window:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    yalign 0.0

    #background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    #padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")
    outlines gui.dialogue_outline[gui.preference("dialogue_outline_idx")]
    #xpos gui.dialogue_xpos
    #xsize gui.dialogue_width
    ypos gui.dialogue_ypos


## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input


screen input(prompt="", hint_text="", initial_text=""):

    window:

        style "nvl_window2"

        text prompt xalign 0.5 yalign 0.4
        text hint_text:
            xalign 0.5
            yanchor 0.0
            ypos 305
            size 20
            color "#888"

        #input id "input" xalign 0.5 yalign 0.35
        input2:
            id "input"
            xalign 0.5
            yalign 0.35
            caret_ysize 35
            max_chars 10
            initial_value initial_text
            copypaste True
            paste_single_line True
            force_caps True
            tight_render True

    use quick_menu

style input_prompt is default:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width
    color "#fff"
    size 30

style input_solid is caret_solid

## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items, bad_end=False, spacing=None):
    style_prefix "choice"

    vbox:
        if spacing:
            spacing spacing

        for idx, val in enumerate(items):
            button:
                text val.caption style "choice_button_text":
                    if val.chosen:
                        color "#888"
                action val.action
                if bad_end:
                    style "choice_button_bad"


## When this is true, menu captions will be spoken by the narrator. When false,
## menu captions will be displayed as empty buttons.
define config.narrator_menu = True

style choice_vbox is vbox:
    xalign 0.5
    ypos 0.5
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is button:
    activate_sound "sounds/sys23.wav"
    properties gui.button_properties("choice_button")

style choice_button_bad is choice_button:
    hover_background Frame("gui/button/choice_hover2_background.png", border=gui.choice_button_borders)

style choice_button_text is button_text:
    properties gui.button_text_properties("choice_button")
    outlines gui.dialogue_outline[gui.preference("dialogue_outline_idx")]


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    # scroll up for search
    key "history_btn" action [SetVariable("persistent.game_menu", "search"), Function(_invoke_game_menu)] activate_sound "sounds/sys6.wav"
    #key "history_btn" action [Function(search.UpdateMessages), ShowMenu("search")] activate_sound "sounds/sys6.wav"

    ## Ensure this appears on top of other screens.
    zorder -100

    ## Overwrite the default action of loading "Save"
    #key "game_menu" action ShowMenu("save")

    #mousearea:
    #    area (0, 0.8, 1.0, 0.2)
    #    hovered Show("buttons", transition=Dissolve(0.1))
    #    unhovered Hide("buttons", transition=Dissolve(0.1))

    showif persistent.minimap and persistent.notified_map_unlock and not TipOrbVisible() and map_position_history[0][2] != None:
        button:
            at tip_orb_fadein_tf
            xanchor 0.5
            yanchor 0.5
            xpos 0.921
            ypos 0.876
            xsize minimap_dim//2+8
            ysize minimap_dim//2+8

            mouse "imagemap"
            background "#0004"
            activate_sound "sounds/sys6.wav"
            hover_background "#3334"
            padding (0,0,0,0)
            
            action ShowMenu("map")

screen buttons():
    hbox:
        style_prefix "quick"

        xalign 0.5
        yalign 1.0

        #textbutton _("") action Rollback()
        #textbutton _("History") action ShowMenu('history')
        textbutton _("Search") action [Function(search.UpdateMessages), ShowMenu('search')]
        textbutton _("Notes") action ShowMenu('notes')
        textbutton _("Map") action ShowMenu('map')
        textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Save") action ShowMenu('save')
        #textbutton _("") action QuickSave()
        #textbutton _("") action QuickLoad()
        textbutton _("Settings") action ShowMenu('preferences')

## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

style quick_button is default
style quick_button_text is button_text

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.button_text_properties("quick_button")


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():
    hbox:
        yalign 1.004
        xalign 0.5
        spacing gui.navigation_spacing

        style_prefix "navigation"
        #textbutton _("History") action ShowMenu("history")

        if persistent.started:
            ## Don't allow access to search and notes until at least 1 line is read
            imagebutton auto "gui/navigation/search_%s.png" action [Function(EnableMenu, "search"), Function(search.UpdateMessages), ShowMenu("search")]
            imagebutton auto "gui/navigation/notes_%s.png":
                if not persistent.notes:
                    action [Function(EnableMenu, "notes_tutorial"), ShowMenu('notes_tutorial')]
                else:
                    action [Function(EnableMenu, "notes"), ShowMenu('notes')]
            imagebutton auto "gui/navigation/map_%s.png" action [Function(EnableMenu, "map"), ShowMenu("map")]


        if config.developer or persistent.finished:
            imagebutton auto "gui/navigation/chart_%s.png":
                if not persistent.chart:
                    action [Function(EnableMenu, "chart_tutorial"), ShowMenu('chart_tutorial')]
                else:
                    action [Function(EnableMenu, "chart"), ShowMenu('chart')]
            imagebutton auto "gui/navigation/tips_%s.png" action [Function(EnableMenu, "tips"), ShowMenu('tips')]

        if main_menu:
            imagebutton auto "gui/navigation/load_%s.png" action ShowMenu("load")
        else:
            if config.developer:
                button:
                    text "SPRITES" ypos 15
                    action [Function(EnableMenu, "sprites_menu"), ShowMenu('sprites_menu')]
            if not _in_replay:
                imagebutton auto "gui/navigation/save_%s.png" action [Function(EnableMenu, "save"), ShowMenu("save")]


        imagebutton auto "gui/navigation/settings_%s.png" action [Function(EnableMenu, "preferences"), ShowMenu("preferences")]

        if main_menu:
            imagebutton auto "gui/navigation/start_%s.png" action Start()
        else:
            imagebutton auto "gui/navigation/main_menu_%s.png" action MainMenu()

        #if _in_replay:
        #    textbutton _("End Replay") action EndReplay(confirm=True) text_color "#000000"


style navigation_button is gui_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text is gui_button_text:
    properties gui.button_text_properties("navigation_button")

style navigation_image_button is gui_button

## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu
image main_menu = Movie(play="movies/ts.webm")
screen main_menu:

    ## This ensures that any other menu screen is replaced.
    tag menu

    style_prefix "mainmenu"

    if persistent.mainmenu6:
        add "gui/main_menu_end.png"
    elif persistent.mainmenu5:
        add "gui/main_menu_c5.png"
    elif persistent.mainmenu4:
        add "gui/main_menu_c4.png"
    elif persistent.mainmenu3:
        add "gui/main_menu_c3.png"
    elif persistent.mainmenu2:
        add "gui/main_menu_c2.png"
    else:
        add "main_menu"

    hbox:
        xalign 0.5
        yalign 0.985
        text _("Trinitite Team © 2021") style "nvl_label2"

    frame:
        background Transform(Frame("gui/nvl4.png", 120, 120), alpha=0.3, xoffset=120)
        xalign 1.0
        xsize 400
        yfill True

        vbox:
            xalign 0.9
            yalign 0.5
            if config.developer:
                yoffset 70
            spacing 0
            if not config.developer:
                if not persistent.finished:
                    
                    null height 60
                    yoffset 110
                else:
                    if unlocked_devbook:
                        yoffset 55
                    else:
                        yoffset 70
                
            textbutton _("Start"):
                action Start()
                activate_sound "sounds/sys4.wav"
            textbutton _("Load") action ShowMenu("load") activate_sound "sounds/sys6.wav"
            textbutton _("Settings") action ShowMenu("preferences") activate_sound "sounds/sys6.wav"

            null height 30

            if config.developer or persistent.finished:
                textbutton _("Music Room") action [ShowMenu("music"), If(renpy.music.get_playing() and ('roomwithnowindows' in renpy.music.get_playing() or 'snowstorm' in renpy.music.get_playing()), Function(renpy.music.stop), NullAction())] activate_sound "sounds/sys1.wav"
                textbutton _("Gallery") action ShowMenu("gallery") activate_sound "sounds/sys6.wav"
                if unlocked_devbook:
                    textbutton _("Development Book") action ShowMenu("devbook") activate_sound "sounds/sys6.wav"
                textbutton _("Stats") action ShowMenu("answers_screen1") activate_sound "sounds/sys6.wav"             
                textbutton _("Credit Links") action ShowMenu("credits") activate_sound "sounds/sys6.wav"

            #if config.developer:
            #    textbutton _("Debug") action Start("debug") activate_sound "sounds/sys6.wav"
            #if _in_replay:
            #    textbutton _("End Replay") action EndReplay(confirm=True) text_color "#fff"
            textbutton _("Streaming Policy") activate_sound "sounds/sys5.wav" action Show('streaming_policy', transition=Dissolve(0.2))
            textbutton _("Privacy Policy") activate_sound "sounds/sys5.wav" action Show('privacy_policy', transition=Dissolve(0.2))
            textbutton _("Quit") action Quit()

    if config.version[0] == "0":
        text _("Beta " + config.version) style "mainmenu_button_text" xanchor 0.0 xpos 23 yalign 0.985
    else:
        text _("Version " + config.version) style "mainmenu_button_text" xanchor 0.0 xpos 23 yalign 0.985

    frame:
        #background Transform(Frame("gui/nvl2.png", 120, 120), alpha=0.3, xoffset=120)
        background None
        xalign 1.0
        ysize 120
        yalign 1.0
        yoffset 30
        left_padding 180

        hbox:
            yalign 0.5
            spacing 15
            ## @CHECK: Fix these urls
            imagebutton auto "gui/title/book_%s.png":
                if achievement.steam:
                    action OpenURL("https://store.steampowered.com/app/1567090")
                else:
                    action OpenURL("https://trinitite-team.itch.io/development-book-the-sekimeiya-spun-glass")
                tooltip _("Development Book")
                hover_sound "sounds/sys2.wav"
                activate_sound "sounds/sys11.wav"
            imagebutton auto "gui/title/discord_%s.png":
                action OpenURL("https://discord.gg/GkEDsu4")
                tooltip _("Discord")
                activate_sound "sounds/sys11.wav"
                hover_sound "sounds/sys2.wav"
            imagebutton auto "gui/title/twitter_%s.png":
                action OpenURL("https://twitter.com/TrinititeTeam")
                tooltip _("Twitter")
                activate_sound "sounds/sys11.wav"
                hover_sound "sounds/sys2.wav"
            imagebutton auto "gui/title/steam_%s.png":
                action OpenURL("https://store.steampowered.com/app/1432500/The_Sekimeiya_Spun_Glass/")
                tooltip _("Purchase / Review")
                activate_sound "sounds/sys11.wav"
                hover_sound "sounds/sys2.wav"

    $ tooltip = GetTooltip()
    if tooltip:
        hbox:
            xsize 200
            xalign 1.0
            yalign 0.93
            text "[tooltip]" xalign 0.5 color "#fff" size 15

    if gui.show_name:
        vbox:
            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

    ## Show logo on everything except mainmenu2 and mainmenu6
    if persistent.mainmenu3 or not persistent.mainmenu2:
        if not persistent.mainmenu6:
            if not persistent.mainmenu4 and persistent.mainmenu3:
                add "gui/logo_noshadow.png":
                    xalign 0.5
                    xoffset -12 #keep the diamond centered
                    yalign 0.02
                    zoom 0.8
            else:
                if persistent.mainmenu2:
                    add "gui/logo.png":
                        xalign 0.5
                        xoffset -12 #keep the diamond centered
                        yalign 0.02
                        zoom 0.8

screen streaming_policy():
    modal True
    for k in ['game_menu', 'dismiss']:
        key k action Hide('streaming_policy', transition=Dissolve(0.2))
    
    if config.version[0] == "0":
        add "images/policy.png"
    else:
        add "images/policy2.png"


screen privacy_policy():
    modal True
    for k in ['game_menu', 'dismiss']:
        key k action Hide('privacy_policy', transition=Dissolve(0.2))

    add "gui/privacy_policy.png"

style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

#style mainmenu_frame:
#    yfill True


style mainmenu_text:
    text_align 0.5
    #properties gui.text_properties("main_menu", accent=True)

style mainmenu_title:
    properties gui.text_properties("title")

style mainmenu_version:
    properties gui.text_properties("version")


style mainmenu_button is navigation_button:
    xalign 0.5

style mainmenu_button_text is navigation_button_text:
    outlines [(5, '#00000008', 0, 0), (4, '#0001', 0, 0), (3, '#0001', 0, 0), (2, '#0001', 0, 0), (1, '#000d', 1, 1)]
    color "#fff"
    hover_color "#b9d6fc"
    size 22
    xalign 1.0

## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When
## this screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0, padded=True):

    style_prefix "game_menu"

    frame:
        style "game_menu_outer_frame"

        add "gui/header_{}.png".format(title):
            xalign 0.5
            yoffset -30

        vbox:
            frame:
                style "game_menu_content_frame"
                if padded == True:
                    left_margin 40
                    right_margin 20
                    top_margin 63
                elif type(padded) is tuple:
                    margin padded

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":
                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        side_yfill True

                        transclude

                elif scroll == "vbox":
                    vbox:
                        transclude

                else:
                    transclude

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

    use navigation

    if main_menu:
        key "game_menu" action ShowMenu("main_menu") activate_sound "sounds/sys14.wav"
    else:
        key "game_menu" action Return() activate_sound "sounds/sys26.wav"

style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 30
    top_padding 30
    background gui.game_menu_background

style game_menu_navigation_frame:
    xfill True
    yalign 1.0

#style game_menu_viewport:
#    xsize 1280-200

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

#style game_menu_side:
    #spacing 10

style game_menu_label:
    xpos 50
    ysize 120

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    #xpos gui.navigation_xpos
    xalign 1.0
    yalign 1.0
    #yoffset -30


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("Version [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]")


## This is redefined in options.rpy to add text to the about screen.
define gui.about = ""


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size



screen credits:
    tag menu
    key "game_menu" action Return()

    style_prefix "credits"

    default art_w1   = 170
    default staff_w1 = 170
    default spec_w1  = 170

    default cred_grid_spacing = 20
    default cred_h1 = 150
    default cred_h2 = 230
    default cred_w1 = 470
    default cred_w2 = 470

    add "gui/credits/background.png":
        xalign 0.55
        yalign 0.5

    hbox:
        xalign 0.5
        yalign 0.5
        yoffset (159-53)/2 # offset the header and footer
        spacing cred_grid_spacing

        ## @CHECK: Make sure these links are correct
        vbox:
            spacing cred_grid_spacing
            frame:
                xsize cred_w1
                ysize cred_h1
                vbox:
                    spacing 8
                    label _("MAIN STAFF") style "credits_frame_title" xoffset -4
                    hbox:
                        textbutton _("Adri") action OpenURL("https://twitter.com/TrinititeTeam") xsize staff_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Director, Producer, Scenario")
                    hbox:
                        textbutton _("Arsym") action OpenURL("https://twitter.com/TrinititeTeam") xsize staff_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Assistant Producer, Programming")
                    hbox:
                        textbutton _("godotwashere") action OpenURL("https://twitter.com/TrinititeTeam") xsize staff_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Assistant Director, Editor")

            frame:
                xsize cred_w1
                ysize cred_h2
                vbox:
                    spacing 8
                    label _("SPECIAL THANKS") style "credits_frame_title" xoffset -4
                    hbox:
                        textbutton _("Hunter O'Connell") action OpenURL("https://www.facebook.com/chris.cwej.series/") xsize spec_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Supporter")
                    hbox:
                        textbutton _("XxX_LORD_ULTRA_SH\nADOW_DEATH_XxX") action NullAction() xsize spec_w1 text_xalign 1.0 text_hover_color '#FFFFFF' text_size 15 hover_sound None activate_sound None
                        text _("Supporter")
                    hbox:
                        textbutton _("Jake H.") action OpenURL("https://twitter.com/futotorofu") xsize spec_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Scripting, Interpreter, Testing")
                    hbox:
                        textbutton _("Aexis") action OpenURL("https://twitter.com/Aexis_Skyen") xsize spec_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Initial Testing")
                    hbox:
                        textbutton _("Ren'Py") action OpenURL("https://renpy.org/") xsize spec_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Engine")

        vbox:
            spacing cred_grid_spacing
            #frame:
            #    xsize cred_w2
            #    ysize cred_h1
            #    vbox:
            #        label _("MUSIC") style "credits_frame_title" xoffset -4
            #        null height 42
            #        textbutton _("Available in Music Room") action [ShowMenu("music"), If(renpy.music.get_playing() and ('roomwithnowindows' in renpy.music.get_playing() or 'snowstorm' in renpy.music.get_playing()), Function(renpy.music.stop), NullAction())] xalign 0.5

            frame:
                xsize cred_w2
                ysize cred_h1+cred_h2+cred_grid_spacing
                vbox:
                    spacing 8
                    label _("ART") style "credits_frame_title" xoffset -4
                    hbox:
                        textbutton _("Resuta") action OpenURL("https://twitter.com/rstresuta") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Character Design, Sprites")
                    hbox:
                        textbutton _("Foxeleos") action OpenURL("https://twitter.com/foxeleos") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Background Art")
                    hbox:
                        textbutton _("Shinasty\n(Anastasia Ermakova)") action OpenURL("https://www.artstation.com/shinasty") xsize art_w1 text_xalign 1.0 text_size 15 activate_sound "sounds/sys11.wav"
                        text _("Extra Background Art")
                    hbox:
                        textbutton _("TEKILAO") action OpenURL("https://www.artstation.com/mion") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Extra Background Art")
                    hbox:
                        textbutton _("KU") action OpenURL("https://twitter.com/KeeUUU_") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("CGs, Cover Art")
                    hbox:
                        textbutton _("Kurigura") action OpenURL("https://twitter.com/kurigura3") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("CGs")
                    hbox:
                        textbutton _("SthreeP") action OpenURL("https://twitter.com/HimeCUTie") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("CGs")
                    hbox:
                        textbutton _("WhiteCharisma") action OpenURL("https://twitter.com/WhiteCharism") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Trailer")
                    hbox:
                        textbutton _("Re.Alice") action OpenURL("https://realiceworks.weebly.com/") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("UI, Logo")
                    hbox:
                        textbutton _("ChinYan Lim") action OpenURL("https://allenlimcy.artstation.com/") xsize art_w1 text_xalign 1.0 activate_sound "sounds/sys11.wav"
                        text _("Initial Title Screen")

    button:
        style "return_to_title_button"
        xalign 0.93
        yalign 0.9939
        action Return()

    button:
        style "full_credits_button"
        xalign 0.07
        yalign 0.9939
        action Call("final_credits", from_current=True)

style full_credits_button:
    background "gui/fullcredits2.png"
    hover_background "gui/fullcredits1.png"
    activate_sound "sounds/sys19.wav"
    hover_sound "sounds/sys2.wav"
    padding (0, 0, 0, 0)
    xsize 300
    ysize 37


style credits_frame is titled_frame

style credits_frame_title:
    xfill True
    xalign 0.5
    padding (0,0,0,10)

style credits_frame_title_text is frame_title_text:
    xalign 0.5
    xoffset 4
    ypos 2

style credits_vbox:
    spacing 0

style credits_hbox:
    spacing 15

style credits_text:
    yalign 0.5
    yoffset 1
    size 16
    font "fonts/Cabin-Medium2.ttf"
    color "#ddd"

style credits_button:
    padding (0,0,0,0)
    yoffset 0

style credits_button_text:
    size 18
    font "fonts/Cabin-Medium2.ttf"
    color "#fff"
    hover_color "#b9d6fc"
    text_align 1.0


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

init -10 python:
    try:
        import _renpysteam
    except:
        class SingletonSteamClass(object):
            initialized = False
        class SingletonAchievementClass(object):
            def grant(self, val):
                pass
        
        _renpysteam = SingletonSteamClass()
        achievement = SingletonAchievementClass()

    #layout.ARE_YOU_SURE = "Are you sure?"
    layout.DELETE_SAVE = "Delete save?"
    layout.OVERWRITE_SAVE = "Overwrite save?"
    layout.LOADING = "Load?\n\nUnsaved progress will be lost."
    #layout.QUIT = "Are you sure you want to quit?"
    layout.MAIN_MENU = "Return to main menu?\nThis will lose unsaved progress."
    #layout.END_REPLAY = "Are you sure you want to end the replay?"
    #layout.SLOW_SKIP = "Are you sure you want to begin skipping?"
    #layout.FAST_SKIP_SEEN = "Are you sure you want to skip to the next choice?"
    #layout.FAST_SKIP_UNSEEN = "Are you sure you want to skip unseen dialogue to the next choice?"

    def GetPlayTime(type='total', static=False):
        if static:
            playtime = int(persistent.playtime_static[type])
        else:
            playtime = int(persistent.playtime[type])

        #time_clipped = min(int(total_playtime), 3599940) # Max of 999:59:00
        return "{:02d}h {:02d}m {:02d}s".format(playtime//3600, (playtime//60)%60, playtime%60)

    def add_json_to_save(json):
        json["chapter"] = str(store.chapter)
        json["scene"] = store.scene_title
        json["total_playtime"] = GetPlayTime('total')

    renpy.config.save_json_callbacks.append(add_json_to_save)

screen save_slot(slot, json, ax):
    fixed:
        xsize 350
        ysize 220

        frame:
            background Frame("gui/frame_tab_save.png", Borders(22, 22, 22, 22), tile=False)
            padding (0,0,0,0)
            xsize 70
            ysize 155
            xpos 0

            vbox:
                xsize 38
                spacing 0
                imagebutton auto "gui/save/save_%s.png" action FileSave(slot, True) padding (10,10,10,10)
                if FileLoadable(slot):
                    imagebutton auto "gui/save/load_%s.png":
                        action FileLoad2(slot, True) padding (10,10,10,10)
                        activate_sound None
                    imagebutton auto "gui/save/delete_%s.png":
                        action FileDelete(slot, True) padding (10,10,10,10)

        button:
            xsize 300
            ysize 220
            xpos 50
            if ax:
                action ax
                activate_sound None
            else:
                action ShowMenu('save_slot_menu', slot)

            frame:
                background Frame("gui/frame_idle.png", Borders(20, 90, 20, 20), tile=False)
                hover_background Frame("gui/frame_hover.png", Borders(20, 90, 20, 20), tile=False)
                padding (5,15,5,10)

                vbox:
                    if FileLoadable(slot):
                        add AlphaMask(FileScreenshot(slot), "gui/screenshot_mask.png") xalign 0.5 #FileScreenshot(slot) xalign 0.5
                    else:
                        add AlphaMask(Solid("#000", xsize=config.thumbnail_width, ysize=config.thumbnail_height), "gui/screenshot_mask.png") xalign 0.5

                    null height 10

                    hbox:
                        null width 5

                        vbox:
                            hbox:
                                frame:
                                    style "slot_info_frame"
                                    xsize 80
                                    if json and "chapter" in json:
                                        text "Chapter {}".format(json["chapter"])
                                    else:
                                        text "Chapter"
                                frame:
                                    style "slot_info_frame"
                                    if json and "scene" in json:
                                        text json["scene"]
                                    else:
                                        text ""

                            hbox:
                                frame:
                                    style "slot_info_frame"
                                    xsize 80
                                    text "Playtime"
                                frame:
                                    style "slot_info_frame"
                                    if json and "total_playtime" in json:
                                        text json["total_playtime"]
                                    else:
                                        text ""

screen save_slot_menu(slot, page=None):
    modal True
    predict False
    
    for k in ['game_menu', 'dismiss']:
        key k action [Hide('save_slot_menu', transition=Dissolve(0.2)), ShowMenu('save')]
    
    window:
        background "#0008"
        xsize 1.0
        ysize 1.0
        
        frame:
            style_prefix "save_popup"
            xalign 0.5
            yalign 0.5
            padding (15,15,15,15)

            vbox:
                xalign 0.5
                xsize 200
                yalign 0.5
                spacing 15

                textbutton "Save":
                    action [ Hide('save_slot_menu', config.exit_yesno_transition), FileSave(slot, False, page) ]
                textbutton "Load":
                    action [ Hide('save_slot_menu', config.exit_yesno_transition), FileLoad2(slot, False, page) ]
                    activate_sound None
                textbutton "Cancel":
                    action [ Hide('save_slot_menu', config.exit_yesno_transition) ]

style save_popup_frame is popup_frame
style save_popup_button_text is popup_button_text:
    size 24
    xalign 0.5
    text_align 0.5

screen save():
    tag menu
    predict False

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu("Save", padded=(0, 32, 0, 20)):
        ## This ensures the input will get the enter event before any of the
        ## buttons do.
        #order_reverse True

        if store._in_replay:
            frame:
                xfill True
                yfill True
                background None

                text "Save and load are disabled during tip segments.":
                    xalign 0.5
                    yalign 0.5
        else:
            ## Buttons to access other pages.
            window:
                background "gui/subheading.png"
                padding (0,0,0,0)
                xfill True

                hbox:
                    style_prefix "page"

                    xalign 0.5
                    yoffset 12

                    spacing gui.page_spacing

                    ## range(1, 10) gives the numbers from 1 to 9.
                    for page in range(1, 19):
                        textbutton "[page]" action FilePage(page)

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5
                yoffset 20

                spacing 40 #gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):
                    $ slot = i + 1
                    $ json = FileJson(slot, empty=None)

                    if main_menu:
                        use save_slot(slot, json, FileLoad2(slot, True))

                    else:
                        if not FileLoadable(slot):
                            use save_slot(slot, json, FileSave(slot, True))
                        else:
                            use save_slot(slot, json, None)

            key "viewport_down" action FilePageNext(max=18, wrap=True, auto=False, quick=False)
            key "viewport_up" action FilePagePrevious(max=18, wrap=True, auto=False, quick=False)

## Even though I don't have a separate load screen, I need this so it doesn't break renpy
## Also keeping this for the main menu. It doesn't like to load "save" for whatever reason
screen load():
    tag menu
    predict False
    use save()


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 50
    ypadding 3

style page_label_text:
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.button_text_properties("page_button")

style slot_text:
    font gui.interface_text_font
    size 13

style slot_button is gui_button:
    padding (0,0,0,0)
    #margin (20,20,20,20)
    #properties gui.button_properties("slot_button")
    background None
    hover_background None

style slot_image_button is gui_button

style slot_button_text is gui_button_text:
    properties gui.button_text_properties("slot_button")

style slot_info_frame is gui_frame:
    #background "#0004"
    background None
    xfill True
    margin (2,2,2,2)
    padding (5,2,5,2)

## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

init python:
    store.preferences_changed = False

    class GuiChanged(Action, FieldEquality):
        def __call__(self):
            store.preferences_changed = True
            renpy.restart_interaction()

    class SoundMixerValue(MixerValue):
        def __init__(self, mixer, feedback_sound=None):
            self.mixer = mixer
            self.feedback_sound = feedback_sound

        def set_mixer(self, value):
            _preferences.set_volume(self.mixer, value)
            if self.feedback_sound:
                renpy.sound.play(self.feedback_sound, channel=self.mixer)

            store.preferences_changed = True
            renpy.restart_interaction()

        def get_adjustment(self):
            return ui.adjustment(
                range=1.0,
                value=_preferences.get_volume(self.mixer),
                changed=self.set_mixer)

        def get_style(self):
            return "slider", "vslider"

    class GuiValue(BarValue):
        """
        :doc: value

        A bar value that allows the user to adjust the value of a field
        on an object.

        `object`
            The object.
        `field`
            The field, a string.
        `range`
            The range to adjust over.
        `style`
            The styles of the bar created.
        `offset`
            An offset to add to the value.
        `step`
            The amount to change the bar by. If None, defaults to 1/10th of
            the bar.
        """

        def __init__(self, name, range, style="bar", offset=0, step=None):
            self.range = range
            self.style = style
            self.offset = offset
            self.name = name
            self.prefs = persistent._gui_preference

            if step is None:
                if isinstance(range, float):
                    step = range / 10.0
                else:
                    step = max(range / 10, 1)

            self.step = step

        def changed(self, value):
            store.preferences_changed = True
            value += self.offset

            self.prefs[self.name] = value
            # gui.rebuild()
            # renpy.restart_interaction()
            RebuildCore()
            
        def get_adjustment(self):
            value = self.prefs[self.name]
            value -= self.offset

            return ui.adjustment(
                range=self.range,
                value=value,
                changed=self.changed,
                step=self.step)

        def get_style(self):
            return self.style, "v" + self.style

    class GuiSetPreference(Action, DictEquality):
        """
        :doc: gui_preference

        This Action sets the gui preference with `name` to `value`.

        `rebuild`
            If true, the default, :func:`gui.rebuild` is called to make
            the changes take effect. This should generally be true, except
            in the case of multiple gui.SetPreference actions, in which case
            it should be False in all but the last one.

        This is a very slow action, and probably not suitable for use
        when a button is hovered.
        """

        def __init__(self, name, value, rebuild=True):
            self.name = name
            self.value = value
            self.rebuild = rebuild

        def __call__(self):
            store.preferences_changed = True
            prefs = persistent._gui_preference

            prefs[self.name] = self.value
            #rebuild()
            RebuildCore()

        def get_selected(self):
            prefs = persistent._gui_preference
            return prefs.get(self.name, gui.not_set) == self.value

    class GuiTogglePreference(Action, DictEquality):
        """
        :doc: gui_preference

        This Action toggles the gui preference with `name` between
        value `a` and value `b`. It is selected if the value is equal
        to `a`.

        `rebuild`
            If true, the default, :func:`gui.rebuild` is called to make
            the changes take effect. This should generally be true, except
            in the case of multiple gui.SetPreference actions, in which case
            it should be False in all but the last one.

        This is a very slow action, and probably not suitable for use
        when a button is hovered.
        """

        def __init__(self, name, a, b, rebuild=True):
            self.name = name
            self.a = a
            self.b = b
            self.rebuild = rebuild

        def __call__(self):
            store.preferences_changed = True
            prefs = persistent._gui_preference

            if prefs[self.name] == self.a:
                prefs[self.name] = self.b
            else:
                prefs[self.name] = self.a

            #rebuild()
            RebuildCore()

        def get_selected(self):
            prefs = persistent._gui_preference
            return prefs.get(self.name, gui.not_set) == self.a

    def RebuildCore():
        #######
        ## The core part of gui.rebuild() with most of the fat trimmed out
        #######
        language = _preferences.language
        tl = renpy.game.script.translator
        
        renpy.ast.redefine([ "store.gui" ])
        if renpy.config.new_translate_order:
            renpy.translation.new_change_language(tl, language)
        else:
            renpy.translation.old_change_language(tl, language)
        for i in renpy.config.change_language_callbacks:
            i()


    preview_dialogue = python_list()
    d_temp = _NVLEntry()
    d_temp.current = 0
    d_temp.who = chr_nar
    d_temp.what = "Her face brightened the instant she laid eyes on them."
    d_temp.who_id = "who2"
    d_temp.what_id = "what2"
    d_temp.window_id = "window2"
    preview_dialogue.append(d_temp)

    d_temp = _NVLEntry()
    d_temp.current = 0
    d_temp.who = chr_isl
    d_temp.what = "\"Wow, just look at how pretty they are!\""
    d_temp.who_id = "who0"
    d_temp.what_id = "what0"
    d_temp.window_id = "window0"
    preview_dialogue.append(d_temp)

    d_temp = _NVLEntry()
    d_temp.current = 0
    d_temp.who = chr_sai
    d_temp.what = "\"I'm also a bit fascinated by these. According to the description, this one was found a week ago at {time=14:30} in the nearby mountains.\""
    d_temp.who_id = "who1"
    d_temp.what_id = "what1"
    d_temp.window_id = "window1"
    preview_dialogue.append(d_temp)


screen preferences_general:
    window:
        style "pref_window_segment"
        style_prefix "pref"
        xalign 0.5
        yalign 0.5
        yoffset -15

        default general_h1 = 210 #260
        default general_h2 = 210
        default general_w1 = 360
        default general_w2 = 345
        default general_w3 = 360

        hbox:
            spacing 2
            vbox:
                xsize general_w1
                spacing 6

                #if renpy.variant("pc"):
                titledframe:
                    ysize general_h1

                    title _("DISPLAY")

                    if display_resolution_base == 0:
                        if renpy.game.preferences.fullscreen:
                            $ SetScreenVariable('display_resolution_base',1280//16)()
                        else:
                            $ SetScreenVariable('display_resolution_base', renpy.game.preferences.physical_size[0]/16.0*renpy.display.interface.dpi_scale)()

                    hbox:
                        label "{} x {}".format(
                                int(display_resolution_base*16),
                                int(display_resolution_base*9)
                            ) xsize 120 xpos 4 text_style "pref_checkbox_button_text" text_color "#fff"
                        bar value ScreenVariableValue("display_resolution_base", offset=50, range=70, step=5, force_step=True) xsize 200 style "slider_slider" tooltip _("Select a 16:9 resolution (press \"Apply\" to apply the change)")

                    hbox:
                        spacing 10
                        checkbox:
                            # ypos 2:
                            text _("Fullscreen")
                            tooltip _("Toggle fullscreen")
                            action [Preference("display", "toggle"), GuiChanged(), ChangedResolutionCallbacks]

                        null width 20
                        textbutton "Apply" style "pref_button" selected False xsize 80:
                            tooltip _("Set window size to the value specified")
                            action [Preference("display", display_resolution_base*16.0/1280/renpy.display.interface.dpi_scale), GuiChanged(), ChangedResolutionCallbacks] activate_sound "sounds/sys10.wav"
                        textbutton "Default" style "pref_button" selected False xsize 80:
                            tooltip _("Set window size to 1280 x 720")
                            action [Preference("display", 1.0/renpy.display.interface.dpi_scale), SetScreenVariable("display_resolution_base", 1280//16), GuiChanged(), ChangedResolutionCallbacks] activate_sound "sounds/sys10.wav"

                titledframe:
                    ysize general_h2
                    title _("SPRITE DARKENING")
                    
                    checkbox:
                        text _("Darken sprites when not speaking")
                        tooltip _("If a character is speaking, darken all other sprites")
                        action [ToggleField(persistent, "sprite_darken"), GuiChanged()]
                    
                    checkbox:
                        text _("Enable fading")
                        if persistent.sprite_darken:
                            tooltip _("When the sprites darken, fade the the dark effect smoothly (enabled) or change color instantly (disabled)")
                            action [ToggleField(persistent, "sprite_darken_transition"), GuiChanged()]
                        else:
                            color "#969696"
                    
                    hbox:
                        label _("Darkness") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 18 xpos 4 ypos -7 style "slider_label":
                            if not persistent.sprite_darken:
                                text_color "#969696"
                        if persistent.sprite_darken:
                            bar:
                                style "slider_slider"
                                value FieldValue(persistent, "sprite_dark_tint", 1.0, step=0.05, action=RegisterSpriteParts)
                                bar_invert True
                                xsize 200
                                ypos -2
                                tooltip _("How dark sprites should become when they're not speaking")

            vbox:
                xsize general_w2
                spacing 6
                style_prefix "check"
                
                titledframe:
                    ysize general_h1
                    title _("SKIP")
                    
                    checkbox:
                        text _("Skip text you haven't read yet")
                        tooltip _("While skipping, skip over new text")
                        action [Preference("skip", "toggle"), GuiChanged()]
                    checkbox:
                        text _("Continue skipping after choice")
                        tooltip _("While skipping, continue skipping after making a choice")
                        action [Preference("after choices", "toggle"), GuiChanged()]
                
                titledframe:
                    ysize general_h2
                    title _("MINIMAP")
                    
                    checkbox:
                        text _("Always display the minimap")
                        tooltip _("Display the minimap in the bottom right corner at all times")
                        action [ToggleVariable("persistent.minimap", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]
                    checkbox:
                        text _("Update minimap with a dissolve")
                        tooltip _("When the map position changes, the minimap should update smoothly (enabled) or instantly (disabled)")
                        if persistent.minimap:
                            action [ToggleVariable("persistent.minimap_fade", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]
                    checkbox:
                        text _("Display previous map positions")
                        tooltip _("Show past positions as smaller, more transparent circles")
                        action [ToggleVariable("persistent.mappos", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]

                    # textbutton _("Always display the minimap"):
                    #     tooltip _("Display the minimap in the bottom right corner at all times")
                    #     action [ToggleVariable("persistent.minimap", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]
                    # textbutton _("Update minimap with a dissolve"):
                    #     tooltip _("When the map position changes, the minimap should update smoothly (enabled) or instantly (disabled)")
                    #     if persistent.minimap:
                    #         action [ToggleVariable("persistent.minimap_fade", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]
                    # textbutton _("Display previous map positions"):
                    #     tooltip _("Show past positions as smaller, more transparent circles")
                    #     action [ToggleVariable("persistent.mappos", true_value=None, false_value=None), Function(MinimapHandleVisibility), GuiChanged()]

            vbox:
                xsize general_w3
                spacing 6
                
                titledframe:
                    ysize general_h1
                    title _("VOLUME")
                    
                    hbox:
                        label _("Music") text_size 18 text_font "fonts/Cabin-Medium2.ttf" xsize 100 xpos 2 ypos -4
                        bar value Preference("music volume") xsize 200 tooltip _("Music volume")

                    hbox:
                        label _("Sound") text_size 18 text_font "fonts/Cabin-Medium2.ttf" xsize 100 xpos 2 ypos -4
                        bar value SoundMixerValue("sfx", "sounds/doorclosing3.wav") xsize 200 tooltip _("Sound effect volume (eg. doors, alarms, footsteps)")

                    hbox:
                        label _("System") text_size 18 text_font "fonts/Cabin-Medium2.ttf" xsize 100 xpos 2 ypos -4
                        bar value SoundMixerValue("system", "sounds/sys3.wav") xsize 200 tooltip _("System sounds (eg. menus opening and closing, buttons, etc)")

                    if config.has_voice:
                        hbox:
                            label _("Voice") xsize 100
                            bar value Preference("voice volume") xsize 200

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    #if config.has_music or config.has_sound or config.has_voice:
                    #    null height gui.pref_spacing
                    #
                    #    textbutton _("Mute All"):
                    #        action Preference("all mute", "toggle")
                    #        style "mute_all_button"

                    textbutton _("Mute if the game isn't focused"):
                        style "mute_all_button"
                        yoffset -6
                        tooltip _("If the game is minimized or unfocused, mute all audio")
                        action [Preference("mute on defocus", "toggle"), GuiChanged()]

                titledframe:
                    ysize general_h1
                    title _("OTHER")

                    checkbox:
                        text _("Click through short pauses")
                        tooltip _("If a pause is shorter than 3 seconds, you can click to skip it")
                        action [ToggleField(persistent, "pref_click_short_pauses"), GuiChanged(), ChangedResolutionCallbacks]
                    
                    if len(store.languages)>1:
                        hbox:
                            label _("Language"):
                                ypos 12
                            button:
                                xpos 12
                                action Show("preferences_language")
                                text store.languages.current.name:
                                    font "fonts/arial.ttf"
                                    size 16
                    
                    #if persistent.enable_c5_questions is not None:
                    #    textbutton _("Enable questions in Chapter 5"):
                    #        tooltip _("Answer questions related to the plot of the game in Chapter 5")
                    #        action ToggleField(persistent, "enable_c5_questions")

    if GetTooltip():
        text GetTooltip() size 16 ypos 530 yanchor 0.5 xalign 0.5
                            

screen preferences_language:
    modal True
    predict False

    style_prefix "pref"

    window:
        background "#000c"
        xsize 1.0
        ysize 1.0
        
        button:
            ## Hide modal if you click outside of it
            action Hide("preferences_language")
            style "pref_window_segment"
            background None
            xsize 1.0
            ysize 1.0
            
            titledframe:
                xalign 0.5
                yalign 0.5
                xsize 250
                
                title _("LANGUAGE")

                for lang_code, details in store.languages.items():
                    checkbox:
                        text details.name
                        action [Language(lang_code), Function(search.__init__), Hide("preferences_language")]
                        font details.font

screen preferences_text:
    vbox:
        window:
            style "pref_window_segment"
            style_prefix "pref"
            #left_margin 40
            #right_margin 20
            xalign 0.5
            yalign 0.5


            default w1=410
            default w2=160
            default w3=220
            default w4=360
            default h1=170
            default h2=170

            hbox:
                spacing 2
                vbox:
                    frame:
                        xsize w1
                        ysize h1
                        ypos 12
                        xpos -9

                        vbox:
                            spacing 8
                            label("TEXTBOX") style "frame_title"
                            hbox:
                                style_prefix "radio"
                                spacing 23
                                xpos 20
                                label _("Style") text_font "fonts/Cabin-Medium2.ttf" xsize 75 text_size 15 ypos 8
                                textbutton "1" action GuiSetPreference("textbox_style", 1) ypos 6 activate_sound "sounds/sys9.wav"
                                textbutton "2" action GuiSetPreference("textbox_style", 2) ypos 6 activate_sound "sounds/sys9.wav"
                                textbutton "3" action GuiSetPreference("textbox_style", 3) ypos 6 activate_sound "sounds/sys9.wav"
                                textbutton "4" action GuiSetPreference("textbox_style", 4) ypos 6 activate_sound "sounds/sys9.wav"
                                
                            hbox:
                                xpos 20
                                label _("Width") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 15 ypos 8
                                bar value GuiValue("textbox_width", range=1.0, style="slider_slider") ypos 5
                            hbox:
                                xpos 20
                                label _("Opacity") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 15 ypos 8
                                bar value GuiValue("textbox_opacity", range=1.0, style="slider_slider") ypos 7

                    frame:
                        xsize w1
                        ysize h2
                        ypos 12
                        xpos -9

                        vbox:
                            spacing 8
                            label _("TEXT")  style "frame_title"
                            hbox:
                                style_prefix "radio"
                                spacing 23
                                xpos 20
                                label _("Outline") text_font "fonts/Cabin-Medium2.ttf" xsize 75 text_size 15 ypos 8
                                textbutton "1" action GuiSetPreference("dialogue_outline_idx", 0) ypos 6 activate_sound "sounds/sys9.wav"
                                textbutton "2" action GuiSetPreference("dialogue_outline_idx", 1) ypos 6 activate_sound "sounds/sys9.wav"
                                textbutton "3" action GuiSetPreference("dialogue_outline_idx", 2) ypos 6 activate_sound "sounds/sys9.wav"
                            hbox:
                                xpos 20
                                label _("Text Speed") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 15 ypos 8
                                bar value Preference("text speed") style "slider_slider" ypos 5
                            hbox:
                                xpos 20
                                label _("Auto Delay") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 15 ypos 8
                                bar value Preference("auto-forward time", range=10) style "slider_slider" ypos 7

                vbox:
                    frame:
                        xsize w2
                        ysize h1
                        ypos 12
                        xpos -9
                        vbox:
                            style_prefix "radio"
                            spacing 6
                            label _("FONT") style "frame_title"
                            null height 0
                            textbutton "Regular" action GuiSetPreference("font", "fonts/Cabin-Regular2.ttf") xfill True
                            textbutton "Medium" action GuiSetPreference("font", "fonts/Cabin-Medium2.ttf") xfill True
                            textbutton "Bold" action GuiSetPreference("font", "fonts/Cabin-Bold2.ttf") xfill True

                    frame:
                        xsize w2
                        ysize h2
                        ypos 14
                        xpos -9
                        vbox:
                            style_prefix "radio"
                            spacing 6
                            label _("TIME FORMAT") style "frame_title"
                            null height 0
                            textbutton "12-Hour" action [SetField(persistent, "time_format_24", False), GuiChanged(), renpy.style.rebuild] xfill True
                            textbutton "24-Hour" action [SetField(persistent, "time_format_24", True), GuiChanged(), renpy.style.rebuild] xfill True

                vbox:
                    frame:
                        xsize w3
                        ysize h2
                        ypos 14
                        xpos -9
                        vbox:
                            style_prefix "check"
                            spacing 6
                            label _("COLOR") style "frame_title"
                            null height 0
                            textbutton "Colored Text" action GuiTogglePreference("colored_text", True, False) xfill True
                            textbutton "Colored Speaker" action GuiTogglePreference("colored_speaker", True, False) xfill True
                    frame:
                        xsize w3
                        ysize h1
                        ypos 12
                        xpos -9
                        vbox:
                            style_prefix "radio"
                            spacing 6
                            label _("SPEAKER INDICATOR") style "frame_title"
                            null height 0
                            textbutton "Symbol" action GuiSetPreference("speaker_indicator", "symbol") xfill True
                            textbutton "None" action GuiSetPreference("speaker_indicator", "none") xfill True


                vbox:
                    frame:
                        xsize w4
                        ysize h1
                        ypos 12
                        xpos -9
                        vbox:
                            style_prefix "radio"
                            spacing 8
                            label _("SPRITE VISIBILITY") style "frame_title"
                            textbutton _("Fade out text on sprite change") action [ToggleField(persistent, "sprite_change_text_dim_enabled"), GuiChanged()] ypos 4
                            hbox:
                                label _("Opacity") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 18 xpos 4 ypos -3 style "slider_label":
                                    if not persistent.sprite_change_text_dim_enabled:
                                        text_color "#969696"
                                if persistent.sprite_change_text_dim_enabled:                                                
                                    bar:
                                        value FieldValue(persistent, "sprite_change_text_opacity", 0.7, step=0.05, action=RegisterSpriteParts)
                                        bar_invert False
                                        xsize 200
                                        style "slider_slider"
                                        ypos 2

                            hbox:
                                label _("Pause") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 18 xpos 4 ypos -9 style "slider_label":
                                    if not persistent.sprite_change_text_dim_enabled:
                                        text_color "#969696"
                                if persistent.sprite_change_text_dim_enabled:                                            
                                    bar:
                                        value FieldValue(persistent, "sprite_change_pause_duration", 1.0, step=0.05, action=RegisterSpriteParts)
                                        bar_invert False
                                        xsize 200
                                        style "slider_slider"
                                        ypos -3

                    frame:
                        xsize w4
                        ysize h2
                        ypos 14
                        xpos -9
                        vbox:
                            style_prefix "radio"
                            spacing 8
                            label _("PREVIOUS TEXT") style "frame_title"
                            hbox:
                                label _("Opacity") text_font "fonts/Cabin-Medium2.ttf" xsize 100 text_size 18 xpos 4 style "slider_label"
                                bar:
                                    value FieldValue(persistent, "prev_nvl_text_opacity", 1.0, step=0.05, action=RegisterSpriteParts)
                                    bar_invert False
                                    xsize 200
                                    style "slider_slider"
                                    ypos 5
                            textbutton _("Fade out previous text") action [ToggleField(persistent, "prev_nvl_text_fadein_enabled"), GuiChanged()]

        window:
            style "nvl_window_main"
            yfill False
            ysize 200
            ypos 21
            #background gui.nvl_background1
            if gui.preference("textbox_style")==1:
                background Transform(Frame(im.MatrixColor("gui/nvl.png",im.matrix.colorize('#148acf', '#fff')), 120, 120), alpha=gui.preference("textbox_opacity"))

            window:
                style "nvl_window"
                top_padding 0.16 # keeps a distance of 20 pixels to the top border
                #background gui.nvl_background2
                if gui.preference("textbox_style")>1:
                    background Transform(Frame(im.MatrixColor("gui/nvl{}.png".format(gui.preference("textbox_style")),im.matrix.colorize('#148acf', '#fff')), 120, 120), alpha=gui.preference("textbox_opacity"))
                has vbox:
                    spacing 6+gui.preference("textbox_width")*(10-6) #gui.nvl_spacing

                #use nvl_dialogue(sample_dialogue)
                for d_count, d in enumerate(preview_dialogue):
                    window:
                        if d_count < len(preview_dialogue)-1:
                            at nvl_text_opacity(store.nvl_text_alpha * persistent.prev_nvl_text_opacity)
                        else:
                            at nvl_text_opacity(store.nvl_text_alpha)
                        style "nvl_entry"
                        id d.window_id

                        fixed:
                            ypos -13
                            yfit gui.nvl_height is None

                            if d.who and d.who.indicator():
                                fixed:
                                    ysize 20
                                    text d.who.indicator():
                                        #id d.who_id
                                        style "nvl_label"
                                        if gui.preference("colored_speaker") and d.who.color:
                                            color d.who.color
                                        else:
                                            color "#fff"
                                        if gui.preference("speaker_indicator") == "circle":
                                            size 52
                                            yoffset -22
                                            xoffset 3

                            text d.what:
                                id d.what_id
                                style "nvl_dialogue"

                                if gui.preference("colored_text"):
                                    color d.who.color


screen preferences:
    tag menu
    predict False

    default display_resolution_base = 0

    use game_menu(_("Settings"), scroll="vbox", padded=False):
        window:
            background "gui/subheading.png"
            yoffset 33
            padding (0,0,0,0)
            xfill True

            hbox:
                xalign 0.5
                yoffset 9.05
                spacing 65

                textbutton _("GENERAL") action SetVariable("persistent.pref_screen", "general") text_size 23
                textbutton _("TEXT") action SetVariable("persistent.pref_screen", "text") text_size 23
                textbutton _("CONTROLS") action SetVariable("persistent.pref_screen", "controls") text_size 23

        window:
            background None
            padding (0,0,0,0)
            ysize 600
            yoffset 40

            showif persistent.pref_screen == "general":
                use preferences_general

            showif persistent.pref_screen=="text":
                use preferences_text

            showif persistent.pref_screen == "controls":
                window:
                    style "pref_window_segment"
                    xalign 0.5

                    use preferences_controls

style pref_label is gui_label
style pref_label_text is gui_label_text:
    color '#fff'
style pref_vbox is vbox

style pref_button is button:
    background Frame("gui/button/round_button_idle.png", 10, 10)
    hover_background Frame("gui/button/round_button_hover.png", 10, 10)
    padding (12, 10, 10, 6)

style pref_button_text is button_text:
    idle_color "#fff"
    xalign 0.5

style pref_checkbox_button is gui_button:
    xpos 3
    activate_sound "sounds/sys10.wav"

style pref_checkbox_button_text:
    idle_color "#fff"
    size 18
    ypos 0.35
    yoffset 5
    font "fonts/Cabin-Medium2.ttf"

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is pref_checkbox_button
style radio_button_text is pref_checkbox_button_text
style radio_vbox is pref_vbox:
    xfill True

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is pref_checkbox_button
style check_button_text is pref_checkbox_button_text
style check_vbox is pref_vbox:
    xfill True

style slider_label is pref_label:
    yoffset 5
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    bottom_margin gui.pref_spacing

style pref_label_text:
    yalign 0.0

#style pref_vbox:
#    xsize 225

style pref_frame is titled_frame:
    padding (10,10,10,10)
    margin (5,5,5,5)

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style radio_button_text:
    properties gui.button_text_properties("radio_button")
    xoffset 9

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.button_text_properties("check_button")
    xoffset 9

style slider_bar:
    xsize 240

style slider_slider:
    xsize 240

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 5

style slider_button_text:
    properties gui.button_text_properties("slider_button")

style pref_window_segment:
    left_margin 40
    right_margin 20
    background None



## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

init -5 python:
    class RollbackConfirm(Action, DictEquality):
        def __init__(self, history_entry, confirm=True):
            self.history_entry = history_entry
            self.confirm = confirm

        def __call__(self):
            if self.confirm:
                layout.yesno_screen("Jump back to this message?", RollbackConfirm(self.history_entry, confirm=False))

            else:
                checkpoints = renpy.get_identifier_checkpoints(self.history_entry.rollback_identifier)
                renpy.rollback(force=True, checkpoints=checkpoints)
                renpy.restart_interaction()
                ui.close()

screen history():
    ## Depricated. Use `screen search` instead
    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0):

        style_prefix "history"

        for h in _history_list:
            button:
                hover_background "#ddd8"
                xsize 1000
                left_padding 0

                #if h.who != "choice":
                action RollbackConfirm(h)

                vbox:
                    $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)

                    null height 10

                    if h.who and h.who != "choice" and h.who.indicator():
                        ## Take the color of the who text from the Character, if set.
                        hbox:
                            $ symbol = h.who.indicator() or "." ## Used to bypass the initialization check which expects d.who to be a string
                            label symbol:
                                xsize 1
                                text_color h.who.color
                                if hasattr(h, 'what_args') and "size" in h.what_args:
                                    text_size h.what_args["size"]

                            text what:
                                if hasattr(h, 'what_args') and "color" in h.what_args:
                                    color h.what_args["color"]
                                if hasattr(h, 'what_args') and "size" in h.what_args:
                                    size h.what_args["size"]
                    else:
                        text what:
                            if hasattr(h, 'what_args') and "color" in h.what_args:
                                color h.what_args["color"]

                    null height 10

        if not _history_list:
            label _("The dialogue history is empty.")


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.



screen preferences_advanced():
    modal True

    add "assets/ui/yesno/overlay.png"

    default focusedBinding = None

    fixed:
        xalign 0.5
        yalign 0.09
        yanchor 0.0

        fit_first True
        add "assets/ui/settings/advanced/card.png"

        fixed:
            xpos 64
            ypos 46
            xsize 437
            ysize 751

            vbox:
                spacing 13

                xpos 190
                ypos 380

                for bname in [
                        "backlogKey",
                        "skipKey",
                        "statMenuKey",
                        "qSaveKey",
                        "qLoadKey",
                        "hideUIKey"]:
                    fixed:
                        fit_first True

                        if focusedBinding == bname:
                            imagebutton:
                                idle "assets/ui/settings/advanced/button_shortcut_selected.png"
                                sensitive False
                        else:
                            imagebutton:
                                hovered systemButtonHover
                                idle "assets/ui/settings/advanced/button_shortcut_idle.png"
                                hover "assets/ui/settings/advanced/button_shortcut_hover.png"
                                action [
                                        SetScreenVariable("focusedBinding",bname),
                                        SetVariable("mouse_visible",False),
                                        Show("preferences_setKey",bname=bname)]

                        text getattr(_preferences,bname):
                            font "assets/fonts/rubik/Rubik-Medium.ttf"
                            color "#FFFFFF"
                            size 22

                            xalign 0.5
                            ypos 1

init python:
    keybind_button_focused = None

screen preferences_controls():
    default width=160
    default width2=160
    default width3=240
    default width4=160
    default color1="#0002"
    default color2="#0007"
    default gamepadexists = GamepadExists()

    frame:
        #if gamepadexists:
        #    yoffset 10
        #else:
        yoffset 60
        ypos -21
        padding (0,0,0,0)
        xpos -9
        vbox:
            style_prefix "help"
            null height 10
            hbox:
                xpos 16
                if gamepadexists:
                    label _("GAMEPAD") xsize width2 style "frame_title"
                label _("RESERVED") xsize width style "frame_title" ypos -2
                label _("CUSTOM") xsize width4 style "frame_title" ypos -2
                label _("DESCRIPTION") xsize width3 style "frame_title"

            frame:
                background color2
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('dismiss')
                    label _("Left Click   /   Return") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('dismiss')
                    label _("Advance text") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('hide_windows')
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('hide_windows')
                    label _("Hide user interface") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color2
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('game_menu')
                    label _("Right Click") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('game_menu')
                    label _("Open game menu") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('history_btn')
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('history_btn')
                    label _("Open search menu") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color2
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('info_hud')
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('info_hud')
                    label _("Display scene information") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        label _("") text_font "fonts/Cabin-Medium.ttf" xsize width2
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('skip')
                    label _("Skip text (while held down)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color2
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('toggle_skip')
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('toggle_skip')
                    label _("Skip text (toggle)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('toggle_afm')
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('toggle_afm')

                    label _("Auto mode (toggle)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color2
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('viewport_up')
                    label _("Scroll Up") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('viewport_up')
                    label _("Viewport up (search, notes)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        use controls_configure_pad('viewport_down')
                    label _("Scroll Down") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('viewport_down')

                    label _("Viewport down (search, notes)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color2
                hbox:
                    if gamepadexists:
                        label _("") text_font "fonts/Cabin-Medium.ttf" xsize width2
                    label _("F11") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('toggle_fullscreen')
                    label _("Toggle fullscreen") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            frame:
                background color1
                hbox:
                    if gamepadexists:
                        label _("") text_font "fonts/Cabin-Medium.ttf" xsize width2
                    label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
                    use controls_configure_button('screenshot')
                    label _("Take screenshot") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            #frame:
            #    background color1
            #    hbox:
            #        if gamepadexists:
            #            label _("") text_font "fonts/Cabin-Medium.ttf" xsize width2
            #        label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
            #        use controls_configure_button('accessibility')
            #        label _("Accessibility options") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0
            #frame:
            #    background color2
            #    hbox:
            #        if gamepadexists:
            #            label _("") text_font "fonts/Cabin-Medium.ttf" xsize width2
            #        label _("") text_font "fonts/Cabin-Medium.ttf" xsize width
            #        use controls_configure_button('self_voicing')
            #        label _("Self-voicing (toggle)") text_font "fonts/Cabin-Medium.ttf" xsize width3 text_xalign 0.0

            #if gamepadexists:
            #    textbutton _("Calibrate Gamepad") text_font "fonts/Cabin-Medium.ttf" action GamepadCalibrate()

screen controls_configure_button(baction):
    fixed:
        xsize 160
        ysize 30
        ypos -2

        if baction==keybind_button_focused:
            imagebutton:
                idle Frame("gui/button/round_button_selected.png", 10, 10)
                sensitive False
        else:
            imagebutton:
                idle Frame("gui/button/round_button_idle.png", 10, 10)
                hover Frame("gui/button/round_button_hover.png", 10, 10)
                activate_sound "sounds/sys11.wav"
                action [
                    SetVariable("mouse_visible",False),
                    SetVariable("keybind_button_focused",baction),
                    Show("controls_set_key",baction=baction),
                    ]

        text getShortcutBoundToAction(baction, "key"):
            xalign 0.5
            ypos 8


screen controls_set_key(baction):
    modal True
    predict False

    key 'K_RETURN' action NullAction()
    for k in ['game_menu', 'dismiss']:
        key k action [
        SetVariable("keybind_button_focused",None),
        SetVariable("mouse_visible",True),
        Hide("controls_set_key")
        ]

    for k in getAllBindableKeys():
        key k action [
            Function(setKeyBinding, baction, k),
            SetVariable("keybind_button_focused",None),
            SetVariable("mouse_visible",True),
            Hide("controls_set_key")
            ]
    
    window:
        background None
        xsize 1.0
        ysize 1.0


screen controls_configure_pad(baction):
    fixed:
        xsize 160
        ysize 30
        ypos -2

        if baction+"_pad"==keybind_button_focused:
            imagebutton:
                idle Frame("gui/button/round_button_selected.png", 10, 10)
                sensitive False
        else:
            imagebutton:
                idle Frame("gui/button/round_button_idle.png", 10, 10)
                hover Frame("gui/button/round_button_hover.png", 10, 10)
                activate_sound "sounds/sys11.wav"
                action [
                    SetVariable("mouse_visible",False),
                    SetVariable("keybind_button_focused",baction+"_pad"),
                    Show("controls_set_pad",baction=baction),
                    ]

        text getShortcutBoundToAction(baction, "pad"):
            xalign 0.5
            ypos 8


screen controls_set_pad(baction):
    modal True
    predict False

    window:
        background None
        xsize 1.0
        ysize 1.0
    add ControllerEventWatcher(baction)

style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 8

style help_button_text:
    properties gui.button_text_properties("help_button")

style help_frame:
    ypadding 8
    top_padding 6
    bottom_padding 2

style help_label_text:
    #size gui.text_size-1
    xalign 0.5
    yalign 0.5
    text_align 0.5
    color "#FFF"

style help_hbox:
    spacing 30



# The screen that we use to indicate that self-voicing is enabled.
screen _self_voicing():
    zorder 1500

    if _preferences.self_voicing == "clipboard":
        $ message = _("Clipboard voicing enabled. Press 'shift+C' to disable.")
    elif _preferences.self_voicing == "debug":
        $ message = _("Self-voicing would say \"[renpy.display.tts.last]\". Press 'alt+shift+V' to disable.")
    else:
        $ message = _("Self-voicing enabled. Press 'v' to disable.")
        #$ message = "Self-voicing enabled. Press '{}' to disable.".format(getShortcutBoundToAction('self_voicing'))

    text message:
        alt ""

        xpos 10
        ypos 10
        color "#fff"
        outlines [ (1, "#0008", 0, 0)]



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:
        top_padding 110

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                imagebutton auto "gui/confirm_yes_%s.png" activate_sound "sounds/sys8.wav" action yes_action hover_sound "sounds/sys2.wav" 
                imagebutton auto "gui/confirm_no_%s.png" action no_action hover_sound "sounds/sys2.wav" activate_sound "sounds/sys16.wav"

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame("gui/confirm_frame.png", gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5
    xsize 544


style confirm_prompt_text:
    text_align 0.5
    yalign 0.5
    size 23
    layout "subtitle"
    font "fonts/Cabin-Medium.ttf"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.button_text_properties("confirm_button")



screen display_message(message):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:
        top_padding 110

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                imagebutton auto "gui/confirm_ok_%s.png" action Hide("display_message") hover_sound "sounds/sys2.wav" activate_sound "sounds/sys9.wav"

    ## Right-click and escape answer "no".
    key "game_menu" action Hide("display_message")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            ysize 50
            spacing 12
            text _("SKIPPING") ypos (50-12)/2 #text height=12
            add "gui/skip_indicator.png" yalign 0.5 at rotate_skip_indicator

transform rotate_skip_indicator:
    subpixel True
    block:
        rotate 0
        linear 1.0 rotate 90
        repeat

style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Auto indicator screen #######################################################
##
## The auto_indicator screen is displayed to indicate that aut mode is active

screen auto_indicator():
    zorder 100
    style_prefix "skip"

    frame:
        hbox:
            spacing 6
            text _("Auto")

## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 10.0 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear 1.0 alpha 1.0
    on hide:
        linear 1.0 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl

screen nvl(dialogue, items=None):
    window:
        style "nvl_window_main"

        if hide_textbox_bg or store.explanation:
            background None
        else:
            background gui.nvl_background1

        window:
            style "nvl_window"
            top_padding 0.08 # keeps a distance of 20 pixels to the top border
            if store.explanation:
                xsize 640
                xpos 0
                padding (80, 0, 120, 0)

            if hide_textbox_bg:
                background None
            if store.explanation and gui.preference("textbox_style")==1:
                background Transform(Frame("gui/nvl4.png", 120, 120), alpha=gui.preference("textbox_opacity"))
            else:
                background gui.nvl_background2

            has vbox:
                id "nvl_vbox_widget"
                spacing 6 + gui.preference("textbox_width")*(10-6) #gui.nvl_spacing

            ## Displays dialogue in either a vpgrid or the vbox.
            if gui.nvl_height:
                vpgrid:
                    cols 1
                    yinitial 1.0

                    use nvl_dialogue(dialogue)

            else:
                use nvl_dialogue(dialogue)

            ## Displays the menu, if given. The menu may be displayed incorrectly if
            ## config.narrator_menu is set to True, as it is above.
            for i in items:
                textbutton i.caption:
                    action i.action
                    style "nvl_button"

    if persistent.log_nvl_overflow:
        python:
            ## Overflow check
            widget = renpy.get_widget(None, "nvl_vbox_widget")
            widget_width = 1100-(120*2) # min_textbox_width - padding
            rend = widget.render(widget_width,0,0,0)

            if rend.height > 650:
                current_label = renpy.game.contexts[0].current
                current_node = renpy.game.script.lookup(current_label)
                output = "File: {}, Line: {}, Height: {}\n{}\n".format(current_label[0], current_node.linenumber, int(rend.height), dialogue[-1][1])

                log(output)


transform nvl_text_opacity(value):
    alpha value

transform nvl_text_opacity_fadeout(value):
    linear 0.5 alpha value

init -20 python:
    textappeardissolve = Dissolve(0.1)
    prevtextdissolve = Dissolve(0.2)
    
    def FadeInTextCallback(x, **kwargs):
        ## Fade in text on max speed. Handles {w} and other breaking tags.
        if x=='show_done':
            if _preferences.text_cps==0:
                renpy.transition(textappeardissolve)
            elif persistent.prev_nvl_text_fadein_enabled and persistent.prev_nvl_text_opacity < 1.0 and not store.sprite_changed_disable_prev_fade and store.nvl_dialogue_count_changed:
                renpy.transition(prevtextdissolve)

            store.sprite_changed_disable_prev_fade = False
            store.nvl_dialogue_count_changed = False

    config.all_character_callbacks.append(FadeInTextCallback)

screen nvl_dialogue(dialogue):
    for d_count, d in enumerate(dialogue):
        window:
            if store.sprite_changed_disable_prev_fade or d_count <= len(dialogue)-2:
                at nvl_text_opacity(store.nvl_text_alpha * persistent.prev_nvl_text_opacity)
            else:
                at nvl_text_opacity(store.nvl_text_alpha)
            style "nvl_entry"
            id d.window_id

            if d.who and d.who.bg_color:
                background Frame(
                    im.MatrixColor("gui/c2_logic_frame.png", im.matrix.tint(d.who.bg_color[0], d.who.bg_color[1], d.who.bg_color[2])),
                    30,30)
                padding (20,5,20,5)

            fixed:
                yfit gui.nvl_height is None

                if d.who and not d.who.bg_color and d.who.indicator():
                    fixed:
                        ysize 20
                        text d.who.indicator():
                            #id d.who_id
                            style "nvl_label"
                            if gui.preference("colored_speaker") and d.who.color:
                                color d.who.color
                            else:
                                color "#fff"

                            if gui.preference("speaker_indicator") == "circle":
                                size 52
                                xoffset 3
                                if hasattr(d, 'what_args') and "size" in d.what_args:
                                    yoffset int(d.what_args["size"]*0.4-33)
                                else:
                                    yoffset -22

                            elif hasattr(d, 'what_args') and "size" in d.what_args:
                                size d.what_args["size"]

                            if hasattr(d, 'who_args') and "outlines" in d.who_args:
                                outlines d.who_args["outlines"]
                            elif hasattr(d, 'what_args') and "outlines" in d.what_args:
                                outlines d.what_args["outlines"]

                text d.what:
                    id d.what_id
                    style "nvl_dialogue"
                    if d.who and d.who.bg_color:
                        xpos 0

                    if "color" in d.what_args:
                        color d.what_args["color"]
                    elif gui.preference("colored_text") and not d.who.bg_color:
                        color d.who.color

    python:
        if len(dialogue) != store.nvl_dialogue_count:
            store.nvl_dialogue_count_changed = True

        store.nvl_dialogue_count = len(dialogue)

## This controls the maximum number of NVL-mode entries that can be displayed at
## once.


style nvl_window is default
style nvl_entry is default

define gui.dialogue_text_xalign = 0.0

style nvl_label is say_label

style nvl_dialogue is say_dialogue:
    line_spacing 3-1*(gui.preference("dialogue_outline_idx")==2) ## Take off an extra pixel if outline 3 is used

style nvl_button is button
style nvl_button_text is button_text

style nvl_window_main:
    xfill True
    yfill True

style nvl_window:
    #xfill True
    yfill True

    xsize gui.nvl_window_width
    xpos gui.nvl_window_xpos
    padding gui.nvl_borders.padding

style nvl_window2:
    xfill True
    yfill True

    background "gui/phone/nvl2.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    #xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    #min_width gui.nvl_name_width
    text_align gui.nvl_name_xalign
    outlines gui.dialogue_outline[gui.preference("dialogue_outline_idx")]

style nvl_label2:
    size 15
    outlines [(1, "#0004", 2, 2), (1, "#0009", 1, 1)]
    
style nvl_label3:
    size 10
    outlines [(1, "#0004", 2, 2), (1, "#0009", 1, 1)]

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    #xsize gui.nvl_text_width
    #min_width gui.nvl_text_width
    text_align gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    #xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    #xsize gui.nvl_thought_width
    #min_width gui.nvl_thought_width
    text_align gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.button_text_properties("nvl_button")



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 450

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    hbox:
        style_prefix "quick"

        xalign 0.5
        yalign 1.0

        textbutton _("Back") action Rollback()
        textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Menu") action ShowMenu()

style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"
style nvl_window2:
    variant "small"
    background "gui/phone/nvl2.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 340

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_image_button is button

style pref_vbox:
    variant "small"
    xsize 400

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_pref_vbox:
    variant "small"
    xsize None

style slider_pref_slider:
    variant "small"
    xsize 600






screen info_hud:
    style_prefix "info"
    default width1 = 140
    default bg = None

    zorder 200

    key "dismiss" action Hide("info_hud")
    key "history_btn" action Hide("info_hud")
    key "game_menu" action Hide("info_hud")
    key "hide_windows" action Hide("info_hud")
    key "toggle_afm" action Hide("info_hud")
    key "skip" action Hide("info_hud")
    key "toggle_skip" action Hide("info_hud")

    for item in renpy.game.contexts[0].scene_lists.layers["master"]:
        if item.tag == "bg":
            $ bg = item.displayable

    frame:
        xfill True
        yfill True
        padding (0,0,0,0)

        if _menu:
            background None
        else:
            background bg


        frame:
            xfill True
            yfill True
            background "#0008"


    vbox:
        yanchor 1.0
        ypos 0.975
        at tf_slide_xpos(-1.5, 0.018)

        hbox:
            vbox:
                xsize width1
                text _("In-game")
            use monospaced_text(GetPlayTime('game', static=False))
        hbox:
            vbox:
                xsize width1
                text _("Search")
            use monospaced_text(GetPlayTime('search', static=False))
        hbox:
            vbox:
                xsize width1
                text _("Notes")
            use monospaced_text(GetPlayTime('notes', static=False))
        hbox:
            vbox:
                xsize width1
                text _("Other")
            use monospaced_text(GetPlayTime('other', static=False))
        hbox:
            vbox:
                xsize width1
                text _("Total")
            use monospaced_text(GetPlayTime('total', static=False))

        text _("")

        hbox:
            vbox:
                xsize width1
                text _("Unfocused")
            use monospaced_text(GetPlayTime('unfocused', static=False))
        hbox:
            vbox:
                xsize width1
                text _("All")
            use monospaced_text(GetPlayTime('all', static=False))

        text _("")

        hbox:
            vbox:
                xsize width1
                text _("Session")
            use monospaced_text(GetPlayTime('session', static=False))

        text _("")

        hbox:
            vbox:
                xsize width1
                text _("BGM")
            text bgm_name
        if bgm_credits_name not in ["", None]:
            hbox:
                vbox:
                    xsize width1
                    text _("Credits")
                text bgm_credits_name
        hbox:
            vbox:
                xsize width1
                text _("Scene")
            text store.scene_title

    button:
        background None
        xanchor 0.5
        yanchor 1.0
        ypos 0.991
        
        if persistent.minimap:
            xpos 0.921
        else:
            at tf_slide_xpos(1.5, 0.921)
        
        use minimap(show_text=True)

    timer 1.0 repeat True action Function(renpy.restart_interaction)

transform tf_slide_xalign(x1, x2):
    xalign x1
    on show:
        linear .05 xalign x2
    on hide:
        linear .05 xalign x1

transform tf_slide_xpos(x1, x2):
    xpos x1
    on show:
        linear .05 xpos x2
    on hide:
        linear .05 xpos x1

style info_text:
    outlines [(2, "#0004", 0, 0), (1, "#0009", 1, 1), (1, "#000", 0, 0)]


## Monospaced number #########################################
##
## Creates a text displayable for the number `num` of `length` digits with equal
## spacing between digits. The number is terminated with the string `terminate`
screen monospaced_number(num, length=3, terminate=None, text_color=gui.idle_color):
    $ strnum = str(num).zfill(length)
    use monospaced_text(text=strnum, length=length, terminate=terminate, text_color=text_color)


screen monospaced_text(text, length=12, terminate=None, width=22, text_color="#fff"):
    style_prefix "info"
    $ char_size = width
    $ width -= 3
    hbox:
        for i in range(length):
            if (i < len(text)):
                text text[i]:
                    size char_size
                    if text[i] != ":":
                        min_width width
                    text_align 0.5
                    color text_color
            else:
                null width width

        if terminate != None:
            text terminate:
                size char_size
                color text_color
