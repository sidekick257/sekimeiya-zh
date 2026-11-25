## This file contains options that can be changed to customize your game.
##
## Lines beginning with two '#' marks are comments, and you shouldn't uncomment
## them. Lines beginning with a single '#' mark are commented-out code, and you
## may want to uncomment them when appropriate.
init python:
    config.console = True


define config.layers = [ 'master', 'snow_layer', 'master_overlay', 'transient', 'screens', 'overlay', 'credits0', 'credits1', 'credits2', 'credits3' ]

#define config.mouse = {
#    'default' : [('gui/cursor0.png', 0, 0)],
#    'button': [('gui/cursor1.png', 0, 0)],
#    'input': [('gui/cursor2.png', 4, 1)],
#    'drag': [('gui/cursor3.png', 16, 17)],
#    }

init -100 python:
    config.developer = "auto"
    #persistent.log_nvl_overflow = False
    #config.profile = True

    ## Turn off auto if we quit the game with auto mode on
    preferences.afm_enable = False
    persistent.runtime_start_time = time.time()

    def UpdatePlaytime():
        current_time = time.time()
        t = current_time - persistent.runtime_start_time
        persistent.runtime_start_time = current_time
        ctx = renpy.game.context()

        if renpy.display.interface.keyboard_focused:
            ## Game is currently focused

            if ctx.current is None or "main_menu" in ctx.current[0]:
                return
            elif "game_definitions.rpy" in ctx.current[0]:
                if persistent.game_menu == 'search':
                    persistent.playtime['search'] += t
                elif persistent.game_menu == 'notes':
                    persistent.playtime['notes'] += t
                else:
                    persistent.playtime['other'] += t
            else:
                persistent.playtime['game'] += t

            persistent.playtime['session'] += t
            persistent.playtime['total'] += t

        else:
            persistent.playtime['unfocused'] += t

        persistent.playtime['all'] = persistent.playtime['total'] + persistent.playtime['unfocused']


    def GuiElementScaling(val, cast_int=True):
        ## Get a multiplier for adjusting gui element size depending on screen size
        if renpy.display.draw:
            return GuiDpiCompensate(val*renpy.display.draw.get_physical_size()[0]/1280.0, cast_int=cast_int)
        else:
            return val

    def GuiElementInverseScaling(val, cast_int=True):
        ## Get a multiplier for adjusting gui element size depending on screen size
        if renpy.display.draw:
            return GuiDpiCompensate(val*1280.0/renpy.display.draw.get_physical_size()[0], cast_int=cast_int)
        else:
            return val

    def GuiDpiCompensate(val, cast_int=True):
        if renpy.display.interface is None:
            ## We must be at startup before the graphics are created. Create a temporary interface
            renpy.display.core.Interface()

        scale = renpy.display.interface.dpi_scale

        if cast_int:
            return int(round(val*scale))
        return val*scale

    ##########################################################################
    # Auto indicator
    def auto_indicator():
        if preferences.afm_enable and not renpy.get_screen("auto_indicator"):
            renpy.show_screen("auto_indicator")
        elif not preferences.afm_enable and renpy.get_screen("auto_indicator"):
            renpy.hide_screen("auto_indicator")

    config.overlay_functions.append(auto_indicator)


    def OpenGameMenuNew():
        renpy.call_in_new_context("_game_menu_new")

    def ContextCallback():
        search.current_idx = -1


init python:
    ## Correct minimap on loaded
    config.after_load_callbacks.append(MinimapHandleVisibility)

    ## Clear search and notes if the fonts/settings change
    config.change_language_callbacks.append(notes.Repopulate)
    config.change_language_callbacks.append(search.Clear)

    def ChangedResolutionCallbacks():
        for c in config.change_language_callbacks:
            c()

    ## Fonts
    config.font_replacement_map["fonts/Cabin-Regular2.ttf", False, True] = ("fonts/Cabin-RegularItalic2.ttf", False, False)
    config.font_replacement_map["fonts/Cabin-Medium2.ttf", False, True] = ("fonts/Cabin-MediumItalic2.ttf", False, False)
    config.font_replacement_map["fonts/Cabin-Bold2.ttf", False, True] = ("fonts/Cabin-BoldItalic2.ttf", False, False)
    ## Chinese font overridetranslate zh_cn style default:

translate zh_cn style default:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style say_dialogue:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style say_thought:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style menu_choice:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style button_text:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style label_text:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style pref_label:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style radio_button_text:
    font "IBMPlexSansSC-Text.ttf"

translate zh_cn style check_button_text:
    font "IBMPlexSansSC-Text.ttf"

define config.game_menu_action = OpenGameMenuNew
define config.context_callback = ContextCallback

# How many milliseconds to wait between commands while skipping (default = 5)
define config.skip_delay = 0
define config.end_splash_transition = Dissolve(0.5)
define config.periodic_callback = UpdatePlaytime

## Don't show the ugly ADV box during transitions
define config.empty_window = nvl_show_core

#define config.debug_text_overflow = True

## Basics ######################################################################

## A human-readable name of the game. This is used to set the default window
## title, and shows up in the interface and error reports.
##
## The _() surrounding the string marks it as eligible for translation.

define config.name = _("The Sekimeiya: Spun Glass")


## Determines if the title given above is shown on the main menu screen. Set
## this to False to hide the title.

define gui.show_name = False


## The version of the game.

define config.version = "1.07"
define config.main_menu_music = "<loop 10.707 to 165.468>music/roomwithnowindows.ogg"


## Text that is placed on the game's about screen. To insert a blank line
## between paragraphs, write \n\n.

define gui.about = _("")

define gui.choice_button_text_idle_color = '#FFFFFF'
## A short name for the game used for executables and directories in the built
## distribution. This must be ASCII-only, and must not contain spaces, colons,
## or semicolons.

define build.name = "TheSekimeiya"


## Sounds and music ############################################################

## These three variables control which mixers are shown to the player by
## default. Setting one of these to False will hide the appropriate mixer.

define config.has_sound = True
define config.has_music = True
define config.has_voice = False


define config.default_music_volume = 0.7
define config.default_sfx_volume = 1.0

## To allow the user to play a test sound on the sound or voice channel,
## uncomment a line below and use it to set a sample sound to play.

# define config.sample_sound = "sample-sound.ogg"
# define config.sample_voice = "sample-voice.ogg"

define config.enter_sound = None #"sounds/sys1.wav"
define config.exit_sound = None

## Uncomment the following line to set an audio file that will be played while
## the player is at the main menu. This file will continue playing into the
## game, until it is stopped or another file is played.

# define config.main_menu_music = "main-menu-theme.ogg"



## Transitions #################################################################
##
## These variables set transitions that are used when certain events occur.
## Each variable should be set to a transition, or None to indicate that no
## transition should be used.

## Entering or exiting the game menu.
define config.enter_transition = dissolve
define config.exit_transition = dissolve

## Entering or exiting a replay (ie. tip)
define config.enter_replay_transition = dissolve
define config.exit_replay_transition = dissolve

## Between screens of the game menu.
define config.intra_transition = Dissolve(0.2)


## A transition that is used after a game has been loaded.
define config.after_load_transition = None


## Used when entering the main menu after the game has ended.

define config.end_game_transition = dissolve
define config.end_splash_transition = dissolve

## A variable to set the transition used when the game starts does not exist.
## Instead, use a with statement after showing the initial scene.

## Window management ###########################################################
##
## This controls when the dialogue window is displayed. If "show", it is always
## displayed. If "hide", it is only displayed when dialogue is present. If
## "auto", the window is hidden before scene statements and shown again once
## dialogue is displayed.
##
## After the game has started, this can be changed with the "window show",
## "window hide", and "window auto" statements.

define config.window = "auto"


## Transitions used to show and hide the dialogue window

define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)


## Preference defaults #########################################################

## Controls the default text speed. The default, 0, is infinite, while any other
## number is the number of characters per second to type out.

default preferences.text_cps = 196


## The default auto-forward delay. Larger numbers lead to longer waits, with 0
## to 30 being the valid range.

default preferences.afm_time = 5


## Save directory ##############################################################
##
## Controls the platform-specific place Ren'Py will place the save files for
## this game. The save files will be placed in:
##
## Windows: %APPDATA\RenPy\<config.save_directory>
##
## Macintosh: $HOME/Library/RenPy/<config.save_directory>
##
## Linux: $HOME/.renpy/<config.save_directory>
##
## This generally should not be changed, and if it is, should always be a
## literal string, not an expression.

define config.save_directory = "IW-1510512572"


## Icon ########################################################################
##
## The icon displayed on the taskbar or dock.

define config.window_icon = "gui/window_icon.png"


## Platforms ###################################################################
##
## Information for steam and so on

define config.steam_appid = 1432500

## Steam Deck support
define _renpysteam.keyboard_mode = "once" # Show the on-screen keyboard only when you first try to type.
define _renpysteam.keyboard_baseline = False # Don't shift when the keyboard is shown


## Build configuration #########################################################
##
## This section controls how Ren'Py turns your project into distribution files.

init python:

    ## The following functions take file patterns. File patterns are case-
    ## insensitive, and matched against the path relative to the base directory,
    ## with and without a leading /. If multiple patterns match, the first is
    ## used.
    ##
    ## In a pattern:
    ##
    ## / is the directory separator.
    ##
    ## * matches all characters, except the directory separator.
    ##
    ## ** matches all characters, including the directory separator.
    ##
    ## For example, "*.txt" matches txt files in the base directory, "game/
    ## **.ogg" matches ogg files in the game directory or any of its
    ## subdirectories, and "**.psd" matches psd files anywhere in the project.

    ## Classify files as None to exclude them from the built distributions.

    build.executable_name = "The_Sekimeiya_Spun_Glass"
    build.package("Script Only", "directory", "scriptonly")
    build.package("no-zip Windows", "directory", "windows all")
    build.package("no-zip Mac", "directory", "mac all")
    build.package("no-zip Linux", "directory", "linux all")
    build.package("no-zip Windows Mac Linux", "directory", "windows mac linux all")
    build.package("dlc", "directory", "dlc", dlc=True)

    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**.psd', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('**/desktop.ini', None)
    build.classify('**.md', None)
    build.classify('**.rpe.py', None)
    build.classify('version.txt', None)
    build.classify('game/python-packages/version.txt', None)
    build.classify('logFile.txt', None)
    build.classify('temp/**', None)
    build.classify('game/cache/**', None)
    build.classify("game/scripts/processing/*.*py", None)
    build.classify("game/images/*.exe", None)

    ## To archive files, classify them as 'archive'.

    build.archive("scripts", "scriptonly")
    build.archive("scripts", "all")
    build.archive("sprites", "all")
    build.archive("devbook", "dlc")
    build.archive("images", "all")
    build.archive("gui", "all")
    build.archive("music", "all")
    build.archive("sounds", "all")
    build.archive("videos", "all")

    # Put script files into the scripts archive.
    build.classify("game/*.*py*", "scripts")
    build.classify("game/scripts/*.*py*", "scripts")
    build.classify("game/scripts/processing/timelines.drawio", "scripts")

    build.classify("game/images/sprites/**.*png", "sprites")
    build.classify("game/images/albumart/**.*png", "images")
    build.classify("game/images/albumart/**.*jpg", "images")
    build.classify("game/images/albumart/**.*jpeg", "images")
    build.classify("game/images/effects/**.*png", "images")
    build.classify("game/images/*.*png", "images")
    build.classify("game/images/*.*jpg", "images")
    build.classify("game/images/*.*jpeg", "images")

    build.classify("game/devbook/*.*png", "devbook")
    build.classify("game/devbook/*.*jpg", "devbook")
    build.classify("game/devbook/*.*jpeg", "devbook")
    build.classify("DevelopmentBook.pdf", "dlc")

    build.classify("game/gui/**", "gui")

    build.classify("game/music/**.*ogg", "music")
    build.classify("game/music/**.*mp3", "music")

    build.classify("game/sounds/**.*mp3", "sounds")
    build.classify("game/sounds/**.*wav", "sounds")
    build.classify("game/sounds/**.*ogg", "sounds")

    build.classify("game/movies/**.*ogv", "videos")
    build.classify("game/movies/**.*webm", "videos")

    ## Files matching documentation patterns are duplicated in a mac app build,
    ## so they appear in both the app and the zip file.

    build.documentation('*.html')
    build.documentation('*.txt')

## Set this to a string containing your Apple Developer ID Application to enable
## codesigning on the Mac. Be sure to change it to your own Apple-issued ID.

# define build.mac_identity = "Developer ID Application: Guy Shy (XHTE5H7Z42)"


## A Google Play license key is required to download expansion files and perform
## in-app purchases. It can be found on the "Services & APIs" page of the Google
## Play developer console.

# define build.google_play_key = "..."


## The username and project name associated with an itch.io project, separated
## by a slash.

# define build.itch_project = "renpytom/test-project"
