init -15 python:
    ## =========================
    ## DEFAULT BINDINGS
    ## =========================
    default_keybinding_actions = {
        'dismiss': 'SCROLL DOWN',
        'game_menu': 'ESC',

        'skip': 'CTRL',
        'toggle_skip': 'TAB',
        'hide_windows': 'SPACE',
        'toggle_afm': 'A',
        #'self_voicing': '1',
        #'accessibility': '2',
        'screenshot':'F12',

        'history_btn': 'SCROLL UP',
        'info_hud': 'MIDDLE CLICK',
        
        'viewport_up': 'PAGE UP',
        'viewport_down': 'PAGE DOWN',
        'toggle_fullscreen': 'F',
    }

    ## =========================
    ## DEFINE KEYS
    ## =========================
    allowed_keybind_shortcuts = {
        'MIDDLE CLICK':['mouseup_2'],
        'SCROLL UP':['mousedown_4'],
        'SCROLL DOWN':['mousedown_5'],
        'CTRL': ['K_LCTRL','K_RCTRL'],
        'SHIFT':['K_LSHIFT','K_RSHIFT'],
        'ALT':['K_LALT','K_RALT'],
        'CMD':['K_LSUPER','K_RSUPER'],
        'ESC':['K_ESCAPE'],
        'SPACE': ['K_SPACE'],
        'END':['K_END'],
        'HOME':['K_HOME'],
        'DEL':['K_DELETE'],
        'BACKSPACE':['K_BACKSPACE'],
        'TAB':['K_TAB'],
        'INSERT':['K_INSERT'],
        'PAGE UP':['K_PAGEUP'],
        'PAGE DOWN':['K_PAGEDOWN'],
        'CLEAR':['K_CLEAR'],
        #'RETURN':['K_RETURN'], #reserved for advancing text
        'PAUSE':['K_PAUSE'],
        'KEYPAD .':['K_KP_PERIOD'],
        'KEYPAD /':['K_KP_DIVIDE'],
        'KEYPAD *':['K_KP_MULTIPLY'],
        'KEYPAD -':['K_KP_MINUS'],
        'KEYPAD +':['K_KP_PLUS'],
        'KEYPAD ENTER':['K_KP_ENTER'],
        'KEYPAD =':['K_KP_EQUALS'],
        #'UP':['K_UP'],
        #'DOWN':['K_DOWN'],
        #'RIGHT':['K_RIGHT'],
        #'LEFT':['K_LEFT'],
        '!': ['K_EXCLAIM'],
        '"': ['K_QUOTEDBL'],
        '#': ['K_HASH'],
        '€': ['K_EURO'],
        '$': ['K_DOLLAR'],
        '&': ['K_AMPERSAND'],
        "'": ['K_QUOTE'],
        '(': ['K_LEFTPAREN'],
        ')': ['K_RIGHTPAREN'],
        '*': ['K_ASTERISK'],
        '+': ['K_PLUS'],
        ',': ['K_COMMA'],
        '-': ['K_MINUS'],
        '.': ['K_PERIOD'],
        '/': ['K_SLASH'],
        ':': ['K_COLON'],
        ';': ['K_SEMICOLON'],
        '<': ['K_LESS'],
        '=': ['K_EQUALS'],
        '>': ['K_GREATER'],
        '?': ['K_QUESTION'],
        '@': ['K_AT'],
        '[': ['K_LEFTBRACKET'],
        '[[': ['K_LEFTBRACKET'],
        '\\': ['K_BACKSLASH'],
        ']': ['K_RIGHTBRACKET'],
        '^': ['K_CARET'],
        '_': ['K_UNDERSCORE'],
        '`': ['K_BACKQUOTE'],
    }

    for char in 'abcdefghijklmnopqrstuvwxyz':
        allowed_keybind_shortcuts[char.upper()] = ['K_'+char]

    for fn_key_num in [1,2,3,4,5,6,7,8,9,10,12,13,14,15]: #F11 is reserved
        # F keys
        allowed_keybind_shortcuts['F'+str(fn_key_num)] = ['K_F'+str(fn_key_num)]

    for char in '012345789':
        allowed_keybind_shortcuts[char] = ['K_'+char]
        allowed_keybind_shortcuts['KEYPAD '+char] = ['K_KP'+char]

    ## =========================
    ## KEY FUNCTIONS
    ## =========================

    def getAllBindableKeys():
        rv = python_list()
        for shortcut in allowed_keybind_shortcuts.keys():
            rv += allowed_keybind_shortcuts[shortcut]
        return rv

    def getShortcutBoundToAction(baction, kind="key"):
        if kind == "key":
            rv = persistent.keybinds[baction]
            if rv == "[":
                rv = "[["
            return rv

        return persistent.padbinds[baction]

    def getActionBoundToShortcut(shortcut):
        for baction in default_keybinding_actions.keys():
            shortcut2 = persistent.keybinds[baction]
            if shortcut == shortcut2:
                return baction
        return None

    def getKeysFromAction(baction):
        return allowed_keybind_shortcuts[getShortcutBoundToAction(baction, "key")]
        #return config.keymap[baction]

    def getShortcutFromKey(key):
        for shortcut, keys in allowed_keybind_shortcuts.items():
            if key in keys:
                return shortcut
        return None

    def setKeyBinding(baction,key):
        shortcut = getShortcutFromKey(key)

        # See if anything else has this keybinding. If so, swap
        baction2 = getActionBoundToShortcut(shortcut)
        if baction2 and baction2 != baction:
            shortcut2 = persistent.keybinds[baction]
            persistent.keybinds[baction2] = shortcut2

        persistent.keybinds[baction] = shortcut
        updateCustomBindings()

    def setPadBinding(baction, display_key):
        actions = pad_actions[baction]
        display_key = display_key.upper()

        if display_key in pad_buttons:  
            key = pad_buttons[display_key]
        elif display_key in pad_axes:  
            key = pad_axes[display_key]

        ## Remove old keys tied to this action
        for bound_key, bound_baction in config.pad_bindings.items():
            if len(bound_baction)>0 and bound_baction[0] == baction:
                config.pad_bindings[bound_key] = []

        ## Add new key to this action
        config.pad_bindings[key] = actions
        if baction in ["viewport_down", "viewport_up"]:
            config.pad_bindings["repeat_"+key] = actions
        else:
            config.pad_bindings["repeat_"+key] = []
        persistent.padbinds[baction] = display_key
        
        ## Allow the B button to close the menu if no other valid actions can be taken
        if key == "pad_b_press":
            config.pad_bindings[key].append("game_menu")

    def updateCustomBindings():
        for baction in default_keybinding_actions.keys():
            saved_binding = persistent.keybinds[baction]
            config.keymap[baction] = allowed_keybind_shortcuts[saved_binding].copy()

            if baction=='dismiss':
                config.keymap[baction].append('mouseup_1') #left click
                config.keymap[baction].append('K_RETURN') #enter
            if baction=='game_menu':
                config.keymap[baction].append('mouseup_3') #right click
            if baction=='toggle_fullscreen':
                config.keymap[baction].append('K_F11') #right click

        renpy.clear_keymap_cache()

    def enableEnterSelect(val=True):
        if val:
            if 'K_RETURN' not in config.keymap["button_select"]:
                config.keymap["button_select"].append('K_RETURN')
            if 'K_KP_ENTER' not in config.keymap["button_select"]:
                config.keymap["button_select"].append('K_KP_ENTER')
        else:
            if 'K_RETURN' in config.keymap["button_select"]:
                config.keymap["button_select"].remove('K_RETURN')
            if 'K_KP_ENTER' in config.keymap["button_select"]:
                config.keymap["button_select"].remove('K_KP_ENTER')

        renpy.clear_keymap_cache()

    ## =========================
    ## SET UP DEFAULT KEYBINDS IF THEY DON'T EXIST
    ## =========================
    if not hasattr(persistent, 'keybinds') or persistent.keybinds is None:
        persistent.keybinds = python_dict()

    for baction in default_keybinding_actions.keys():
        if baction not in persistent.keybinds:
            persistent.keybinds[baction] = default_keybinding_actions[baction]

    updateCustomBindings()



    ## =========================
    ## KEYBINDINGS EXISTING FEATURES
    ## =========================
    def EnableDismiss():
        config.keymap['dismiss'] = allowed_keybind_shortcuts[persistent.keybinds['dismiss']].copy() + ['mouseup_1', 'K_RETURN']
        renpy.clear_keymap_cache()

    def DisableDismiss():
        config.keymap['dismiss'] = python_list()
        renpy.clear_keymap_cache()

    def DisableMenu():
        persistent.last_game_menu = persistent.game_menu
        persistent.game_menu = None

        config.keymap['info_hud'] = python_list()
        if not config.rollback_enabled:
            config.keymap['history_btn'] = python_list()

        renpy.clear_keymap_cache()

    def EnableMenu(val=None):
        if val:
            persistent.last_game_menu = val
        elif not persistent.game_menu:
            persistent.last_game_menu = "save"

        config.keymap['info_hud'] = getKeysFromAction('info_hud')
        if not config.rollback_enabled:
            config.keymap['history_btn'] = getKeysFromAction('history_btn') #["mousedown_4", "K_PAGEUP", "K_AC_BACK"]

        persistent.game_menu = persistent.last_game_menu
        renpy.clear_keymap_cache()

    EnableDismiss()

    ## Prevent scroll from rolling back
    config.rollback_enabled = config.developer
    config.keymap['rollforward'] = python_list()
    config.keymap['director'] = python_list()
    config.keymap['accessibility'] = python_list()
    config.keymap['self_voicing'] = python_list()
    config.keymap['clipboard_voicing'] = python_list()
    config.keymap['debug_voicing'] = python_list()
    config.keymap['help'] = python_list()
    renpy.clear_keymap_cache()

    ## Scroll up for history
    if False and config.developer:
        config.keymap['history_btn'] = python_list()
    else:
        config.keymap['history_btn'] = getKeysFromAction('history_btn')
        config.keymap['rollback'] = python_list()

    ## =========================
    ## KEYBINDINGS FOR NEW SCREENS/FEATURES
    ## =========================

    config.keymap['viewport_up'] = [ 'K_UP', 'repeat_K_UP', 'mousedown_4', "K_PAGEUP", "repeat_K_PAGEUP" ]
    config.keymap['viewport_down'] = [ 'K_DOWN', 'repeat_K_DOWN', 'mousedown_5', "K_PAGEDOWN", "repeat_K_PAGEDOWN" ]

    ## Focus
    #config.keymap['focus_left'] = python_list()#[ 'K_LEFT', 'repeat_K_LEFT' ]
    #config.keymap['focus_right'] = python_list()#[ 'K_RIGHT', 'repeat_K_RIGHT' ]
    #config.keymap['focus_up'] = python_list() #['shift_K_TAB', 'repeat_shift_K_TAB']#[ 'K_UP', 'repeat_K_UP' ]
    #config.keymap['focus_down'] = python_list() #['K_TAB', 'repeat_K_TAB'] #[ 'K_DOWN', 'repeat_K_DOWN' ]

    config.keymap['input_focus_up'] = ['shift_K_TAB', 'repeat_shift_K_TAB']#[ 'K_UP', 'repeat_K_UP' ]
    config.keymap['input_focus_down'] = ['K_TAB', 'repeat_K_TAB']

    ## Input
    config.keymap['input_backspace'] = [ 'K_BACKSPACE', 'repeat_K_BACKSPACE' ]
    config.keymap['input_enter'] = [ 'K_RETURN', 'K_KP_ENTER', 'repeat_K_RETURN', 'repeat_K_KP_ENTER' ]
    config.keymap['input_left'] = [ 'noshift_K_LEFT', 'repeat_noshift_K_LEFT' ]
    config.keymap['input_right'] = [ 'noshift_K_RIGHT', 'repeat_noshift_K_RIGHT' ]
    config.keymap['input_up'] = [ 'noshift_K_UP', 'repeat_noshift_K_UP' ]
    config.keymap['input_down'] = [ 'noshift_K_DOWN', 'repeat_noshift_K_DOWN' ]
    config.keymap['input_delete'] = [ 'K_DELETE', 'repeat_K_DELETE' ]
    config.keymap['input_home'] = [ 'K_HOME' ]
    config.keymap['input_end'] = [ 'K_END' ]
    config.keymap['input_undo'] = ['ctrl_K_z']
    config.keymap['input_redo'] = ['ctrl_K_y']
    config.keymap['input_copy'] = [ 'ctrl_K_INSERT', 'ctrl_K_c' ]
    config.keymap['input_cut'] = ['ctrl_K_x']
    config.keymap['input_paste'] = ['ctrl_K_v', 'repeat_ctrl_K_v', 'shift_K_INSERT', 'repeat_shift_K_INSERT']
    config.keymap['input_bold'] = ['ctrl_K_b']
    config.keymap['input_italic'] = ['ctrl_K_i']
    config.keymap['input_underline'] = ['ctrl_K_u']
    config.keymap['input_move_word_right'] = ['ctrl_K_RIGHT', 'repeat_ctrl_K_RIGHT']
    config.keymap['input_move_word_left'] = ['ctrl_K_LEFT', 'repeat_ctrl_K_LEFT']
    config.keymap['input_move_start'] = ['ctrl_K_HOME', 'repeat_ctrl_K_HOME']
    config.keymap['input_move_end'] = ['ctrl_K_END', 'repeat_ctrl_K_END']
    config.keymap['input_select_all'] = ['ctrl_K_a']
    config.keymap['input_select_left'] = ['shift_K_LEFT', 'repeat_shift_K_LEFT']
    config.keymap['input_select_right'] = ['shift_K_RIGHT', 'repeat_shift_K_RIGHT']
    config.keymap['input_select_up'] = ['shift_K_UP', 'repeat_shift_K_UP']
    config.keymap['input_select_down'] = ['shift_K_DOWN', 'repeat_shift_K_DOWN']
    config.keymap['input_select_word_left'] = ['ctrl_shift_K_LEFT', 'repeat_ctrl_shift_K_LEFT']
    config.keymap['input_select_word_right'] = ['ctrl_shift_K_RIGHT', 'repeat_ctrl_shift_K_RIGHT']
    config.keymap['input_select_line_left'] = ['shift_K_HOME', 'repeat_shift_K_HOME']
    config.keymap['input_select_line_right'] = ['shift_K_END', 'repeat_shift_K_END']
    config.keymap['input_select_start'] = ['ctrl_shift_K_HOME', 'repeat_ctrl_shift_K_HOME']
    config.keymap['input_select_end'] = ['ctrl_shift_K_END', 'repeat_ctrl_shift_K_END']
    config.keymap['input_erase_word_left'] = [ 'ctrl_K_BACKSPACE', 'repeat_ctrl_K_BACKSPACE' ]
    config.keymap['input_erase_word_right'] = [ 'ctrl_K_DELETE', 'repeat_ctrl_K_DELETE' ]

    def ToggleInfoHud():
        ## Can't be used on title screen, game menu, or selection screens
        if not store.main_menu and not renpy.context()._menu:
            for x in renpy.game.contexts[0].scene_lists.layers['screens']:
                if x.tag in ['input', 'MapSelect', 'CharacterSelect']:
                    return

            persistent.playtime_static = persistent.playtime.copy()
            ToggleScreen("info_hud", Dissolve(0.1))()
            renpy.sound.play('sounds/sys25.wav', channel="system")

    def ToggleFullscreen():
        renpy.toggle_fullscreen()
        ChangedResolutionCallbacks()

    config.underlay[0].keymap['info_hud'] = ToggleInfoHud
    config.underlay[0].keymap['toggle_fullscreen'] = ToggleFullscreen



    ################
    ## Controller buttons
    ###############

    default_padbinding_actions = {
        "dismiss": "A",
        "toggle_afm": "B",
        "history_btn": "X",
        "hide_windows": "Y",
        "game_menu": "START",
        "info_hud": "BACK",
        "toggle_skip": "LT",
        "viewport_up": "RT",
        "viewport_down": "RB",
    }

    from collections import OrderedDict
    pad_buttons = OrderedDict()
    pad_buttons["A"] = "pad_a_press"
    pad_buttons["B"] = "pad_b_press"
    pad_buttons["X"] = "pad_x_press"
    pad_buttons["Y"] = "pad_y_press"
    pad_buttons["LB"] = "pad_leftshoulder_press"
    pad_buttons["RB"] = "pad_rightshoulder_press"
    pad_buttons["BACK"] = "pad_back_press"
    pad_buttons["START"] = "pad_start_press"
    pad_buttons["LSB"] = "pad_leftstick_press"
    pad_buttons["RSB"] = "pad_rightstick_press"
    pad_buttons["GUIDE"] = "pad_guide_press"
    
    pad_axes = OrderedDict()
    pad_axes["LEFT STICK X"] = None
    pad_axes["LEFT STICK Y"] = None
    pad_axes["RIGHT STICK X"] = None
    pad_axes["RIGHT STICK Y"] = None
    pad_axes["LT"] = "pad_lefttrigger_pos"
    pad_axes["RT"] = "pad_righttrigger_pos"
    
    pad_actions = {
        "dismiss": ["dismiss", "button_select", "bar_activate", "bar_deactivate"],
        "hide_windows": ["hide_windows"],
        "game_menu": ["game_menu"],
        "history_btn": ["history_btn"],
        "info_hud": ["info_hud"],
        "toggle_skip": ["toggle_skip"],
        "toggle_afm": ["toggle_afm"],
        "viewport_down": ["viewport_down", "viewport_rightarrow"],
        "viewport_up": ["viewport_up", "viewport_leftarrow"],
    }

    from pygame_sdl2 import JOYHATMOTION, JOYAXISMOTION, JOYBUTTONDOWN

    store.joystick_x = 0
    store.joystick_y = 0

    class JoystickEventWatcher(renpy.Displayable):
        def __init__(self):
            renpy.Displayable.__init__(self)
            renpy.config.pass_joystick_events = True

        def render(self, width, height, st, at):
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            if ev.type == JOYAXISMOTION:
                if ev.axis == 0:
                    store.joystick_x = ev.value
                elif ev.axis == 1:
                    store.joystick_y = ev.value

            mouse_pos = pygame.mouse.get_pos()
            x = GuiElementInverseScaling(mouse_pos[0])
            y = GuiElementInverseScaling(mouse_pos[1])
            joystick_dist = math.sqrt(store.joystick_x**2 + store.joystick_y**2)

            if joystick_dist>0.1:
                ## Move the cursor
                x += int(20.0*abs(store.joystick_x)*store.joystick_x/joystick_dist)
                y += int(20.0*abs(store.joystick_y)*store.joystick_y/joystick_dist)

                ## Set the cursor within the window
                x = max(0, min(1280-1, x))
                y = max(0, min(720-1, y))

                pygame.event.set_grab(True)
                pygame.mouse.set_pos((GuiElementScaling(x), GuiElementScaling(y)))
                pygame.event.set_grab(False)

    ## Joystick handling on all screens, let's go
    config.underlay.append(JoystickEventWatcher())

    ## Allow for custom button assignment
    class ControllerEventWatcher(renpy.Displayable):
        def __init__(self, baction):
            renpy.Displayable.__init__(self)
            self.baction = baction
            renpy.config.pass_joystick_events = True

        def render(self, width, height, st, at):
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            binding = None

            if ev.type == JOYBUTTONDOWN:
                binding = pad_buttons.items()[ev.button]
            elif ev.type == JOYAXISMOTION and abs(ev.value) > .6:
                if pad_axes.values()[ev.axis]:
                    binding = pad_axes.items()[ev.axis]
            #elif ev.type == JOYHATMOTION and (ev.value != 0):
            #    binding = "h{}.{}".format(ev.hat, ev.value)

            if binding:
                old_baction = None
                old_key = None

                if binding[0] in persistent.padbinds.values():
                    idx = persistent.padbinds.values().index(binding[0])
                    if binding[1] != persistent.padbinds.keys()[idx]:
                        old_baction = persistent.padbinds.keys()[idx]
                        old_display_key = persistent.padbinds[self.baction]

                setPadBinding(self.baction, binding[0])

                if old_baction:
                    setPadBinding(old_baction, old_display_key)

                ## Some screen stuff to finish off
                store.keybind_button_focused = None
                store.mouse_visible = True
                Hide("controls_set_pad")()

    ## =========================
    ## SET UP CONTROLLER KEYS
    ## =========================
    if not hasattr(persistent, 'padbinds') or persistent.padbinds is None:
        persistent.padbinds = python_dict()

    for key in pad_actions.keys():
        if key not in persistent.padbinds:
            persistent.padbinds[key] = default_padbinding_actions[key]

    config.pad_bindings = {
        "pad_a_press" : [],
        "pad_b_press" : [],
        "pad_x_press" : [],
        "pad_y_press" : [],
        "pad_guide_press" : [],
        "pad_start_press" : [],
        "pad_back_press" : [],

        "pad_righttrigger_pos" : [],
        "repeat_pad_righttrigger_pos" : [],
        "pad_rightshoulder_press" : [],
        "repeat_pad_rightshoulder_press" : [],
        "pad_lefttrigger_pos" : [],
        "repeat_pad_lefttrigger_pos" : [],
        "pad_leftshoulder_press" : [],
        "repeat_pad_leftshoulder_press" : [],

        ## DPad and joysticks
        "pad_dpleft_press" : ["focus_left", "bar_left"], #"viewport_leftarrow" ],
        "repeat_pad_dpleft_press" : ["focus_left", "bar_left"], #"viewport_leftarrow" ],
        "pad_dpright_press" : ["focus_right", "bar_right"], #"viewport_rightarrow" ],
        "repeat_pad_dpright_press" : ["focus_right", "bar_right"], #"viewport_rightarrow" ],
        "pad_dpup_press" : ["focus_up", "bar_up"], #, "viewport_uparrow" ],
        "repeat_pad_dpup_press" : ["focus_up", "bar_up"], #, "viewport_uparrow" ],
        "pad_dpdown_press" : ["focus_down", "bar_down"], #, "viewport_downarrow" ],
        "repeat_pad_dpdown_press" : ["focus_down", "bar_down"], #, "viewport_downarrow" ],

        "pad_leftx_neg"  : [],
        "pad_rightx_neg" : [],
        "pad_leftx_pos"  : [],
        "pad_rightx_pos" : [],
        "pad_lefty_neg"  : [],
        "pad_righty_neg" : [],
        "pad_lefty_pos"  : [],
        "pad_righty_pos" : [],
        "repeat_pad_leftx_neg"  : [],
        "repeat_pad_rightx_neg" : [],
        "repeat_pad_leftx_pos"  : [],
        "repeat_pad_rightx_pos" : [],
        "repeat_pad_lefty_neg"  : [],
        "repeat_pad_righty_neg" : [],
        "repeat_pad_lefty_pos"  : [],
        "repeat_pad_righty_pos" : [],
    }

    for baction, display_key in persistent.padbinds.items():
        setPadBinding(baction, display_key)