init -1 python:
    map_displayed_floor = None
    minimap_displayed_floor = None
    map_position_history = []
    minimap_position_history = [[],[]]
    map_position_count = 7

    minimap_dim = 300
    map_dev_line_num = -1
    map_dev_counter = 0
    map_alternator_counter = 0
    
    """
    # The minimap alternates between two images. That's because the indator positions update instantly,
    # which causes indicators to move during transitions. By alternating, we allow indicators to be buffered.
    """

    def ChangeMapScroll(dir=1):
        val = map_displayed_floor
        valid_floors = [i for i,x in enumerate(persistent.map_unlocked) if x>0]
        if len(valid_floors) == 0 or val not in valid_floors:
            return NullAction()
        idx = (valid_floors.index(val)+dir)%len(valid_floors)
        val = valid_floors[idx]

        return SetVariable("map_displayed_floor", val)

    def UnlockMap(floor):
        if not persistent.map_unlocked:
            persistent.map_unlocked = [0]*9

        if floor[-1].lower() == "b":
            persistent.map_unlocked[int(floor[:-1])] = 2
        elif persistent.map_unlocked[int(floor)] != 2:
            persistent.map_unlocked[int(floor)] = 1

    def MapResetPositions():
        global map_position_history, minimap_position_history
        map_position_history = []
        for temp in range(map_position_count):
            map_position_history.append([0, 0, None])
        
        map_alternator_counter = 0
        minimap_position_history = [map_position_history.copy(), []]
    MapResetPositions()

    def MapSetPosition(x, y, floor, transition=False):
        global map_position_history, minimap_position_history, map_alternator_counter
        map_position_history.insert(0, (x, y, floor))
        if len(map_position_history)>map_position_count:
            map_position_history.pop()
        
        map_alternator_counter = 1 - map_alternator_counter
        minimap_position_history[map_alternator_counter] = map_position_history.copy()
        
        MinimapHandleVisibility()
        
    def MinimapHandleVisibility():
        global map_position_history, minimap_displayed_floor, map_alternator_counter
        
        ## Update the minimap, whether it's displayed in-game or only in the info hud
        map_crop_x = map_position_history[0][0]-minimap_dim/2
        map_crop_y = map_position_history[0][1]-minimap_dim/2

        current_floor = store.map_position_history[0][2]
        minimap_displayed_floor = "F1"

        if current_floor is None and persistent.map_unlocked[1]==2:
            minimap_displayed_floor = "F1b"
        elif current_floor is None:
            minimap_displayed_floor = "F1"
        elif current_floor==0 and persistent.map_unlocked[1]==2:
            minimap_displayed_floor = "F0b"
        elif current_floor==1 and persistent.map_unlocked[1]==2:
            minimap_displayed_floor = "F1b"
        elif current_floor==6 and persistent.map_unlocked[6]==2:
            minimap_displayed_floor = "F6b"
        elif current_floor==0:
            minimap_displayed_floor = "F0"
        elif current_floor==1:
            minimap_displayed_floor = "F1"
        elif current_floor==2:
            minimap_displayed_floor = "F2"
        elif current_floor==3:
            minimap_displayed_floor = "F3"
        elif current_floor==4:
            minimap_displayed_floor = "F4"
        elif current_floor==5:
            minimap_displayed_floor = "F5"
        elif current_floor==6:
            minimap_displayed_floor = "F6"
        elif current_floor==7:
            minimap_displayed_floor = "F7"
        elif current_floor==8:
            minimap_displayed_floor = "F8"

        tf = Transform(crop=(map_crop_x, map_crop_y, minimap_dim, minimap_dim), zoom=0.5, xanchor=0.5, yanchor=0.5, xpos=0.921, ypos=0.876)
        renpy.display.image.images[('minimap_proxy{}'.format(map_alternator_counter),)].transform = [tf]

        ## Actually show the minimap if it's visible
        if persistent.minimap and persistent.notified_map_unlock and not TipOrbVisible() and map_position_history[0][2] != None:
            hide_lowest_context("minimap_proxy{}".format(1-map_alternator_counter), layer="screens")
            show_lowest_context("minimap_proxy{} {}".format(map_alternator_counter, minimap_displayed_floor), layer="screens", zorder=-1)
        else:
            hide_lowest_context("minimap_proxy0", layer="screens")
            hide_lowest_context("minimap_proxy1", layer="screens")

    #############
    ## Copied from exports.py.
    ## Only difference is that it uses the lowest context scene list rather than current context
    ## This is important so when MinimapHandleVisibility is called from settings, it handles properly
    #############
    def show_lowest_context(name, at_list=[ ], layer=None, what=None, zorder=None, tag=None, behind=[ ], atl=None, transient=False, munge_name=True):
        """
        :doc: se_images
        :args: (name, at_list=[ ], layer='master', what=None, zorder=0, tag=None, behind=[ ])

        Shows an image on a layer. This is the programmatic equivalent of the show
        statement.

        `name`
            The name of the image to show, a string.

        `at_list`
            A list of transforms that are applied to the image.
            The equivalent of the ``at`` property.

        `layer`
            A string, giving the name of the layer on which the image will be shown.
            The equivalent of the ``onlayer`` property. If None, uses the default
            layer associated with the tag.

        `what`
            If not None, this is a displayable that will be shown in lieu of
            looking on the image. (This is the equivalent of the show expression
            statement.) When a `what` parameter is given, `name` can be used to
            associate a tag with the image.

        `zorder`
            An integer, the equivalent of the ``zorder`` property. If None, the
            zorder is preserved if it exists, and is otherwise set to 0.

        `tag`
            A string, used to specify the image tag of the shown image. The
            equivalent of the ``as`` property.

        `behind`
            A list of strings, giving image tags that this image is shown behind.
            The equivalent of the ``behind`` property.
        """

        default_transform = renpy.config.default_transform

        if renpy.game.context().init_phase:
            raise Exception("Show may not run while in init phase.")

        if not isinstance(name, tuple):
            name = tuple(name.split())

        if zorder is None and not renpy.config.preserve_zorder:
            zorder = 0

        sls = renpy.game.contexts[0].scene_lists #scene_lists()
        key = tag or name[0]

        layer = renpy.default_layer(layer, key)

        if renpy.config.sticky_positions:
            if not at_list and key in sls.at_list[layer]:
                at_list = sls.at_list[layer][key]

        if not at_list:
            tt = renpy.config.tag_transform.get(key, None)
            if tt is not None:
                if not isinstance(tt, list):
                    at_list = [ tt ]
                else:
                    at_list = list(tt)

        if what is None:
            what = name
        elif isinstance(what, basestring):
            what = tuple(what.split())

        if isinstance(what, renpy.display.core.Displayable):

            if renpy.config.wrap_shown_transforms and isinstance(what, renpy.display.motion.Transform):
                base = img = renpy.display.image.ImageReference(what, style='image_placement')

                # Semi-principled, but mimics pre-6.99.6 behavior - if `what` is
                # already a transform, do not apply the default transform to it.
                default_transform = None

            else:
                base = img = what

        else:

            if renpy.config.image_attributes:
                new_what = renpy.game.context().images.apply_attributes(layer, key, name)
                if new_what is not None:
                    what = new_what
                    name = (key,) + new_what[1:]

            base = img = renpy.display.image.ImageReference(what, style='image_placement')

            if not base.find_target() and renpy.config.missing_show:
                result = renpy.config.missing_show(name, what, layer)

                if isinstance(result, renpy.display.core.Displayable):
                    base = img = result
                elif result:
                    return

        for i in at_list:
            if isinstance(i, renpy.display.motion.Transform):
                img = i(child=img)
            else:
                img = i(img)

            # Mark the newly created images unique.
            img._unique()

        # Update the list of images we have ever seen.
        renpy.game.persistent._seen_images[name] = True # @UndefinedVariable

        if tag and munge_name:
            name = (tag,) + name[1:]

        if renpy.config.missing_hide:
            renpy.config.missing_hide(name, layer)

        sls.add(layer, img, key, zorder, behind, at_list=at_list, name=name, atl=atl, default_transform=default_transform, transient=transient)


    def hide_lowest_context(name, layer=None):
        """
        :doc: se_images

        Hides an image from a layer. The Python equivalent of the hide statement.

        `name`
             The name of the image to hide. Only the image tag is used, and
             any image with the tag is hidden (the precise name does not matter).

        `layer`
             The layer on which this function operates. If None, uses the default
             layer associated with the tag.
        """

        if renpy.game.context().init_phase:
            raise Exception("Hide may not run while in init phase.")

        if not isinstance(name, tuple):
            name = tuple(name.split())

        sls = renpy.game.contexts[0].scene_lists #scene_lists()
        key = name[0]

        layer = renpy.default_layer(layer, key)

        sls.remove(layer, key)

        if renpy.config.missing_hide:
            renpy.config.missing_hide(name, layer)




    def MapSetInitialPosition():
        global map_displayed_floor
        if len(map_position_history)==0 or map_position_history[0][2] is None:
            map_displayed_floor = 1
        elif persistent.map_unlocked[map_position_history[0][2]]:
            map_displayed_floor = int(map_position_history[0][2])
        else:
            map_displayed_floor = 1

    def MapGetPosition(floor):
        global map_position_history, map_dev_line_num, map_dev_counter
        x, y = GetMousePos()

        x = int((x-310)/0.97-29)
        y = int(y/0.97-4)

        if x<0 or x>620:
            x=0
            y=0
            floor=None

        map_position_history[0] = (x, y, floor)
        out = "$ MapSetPosition({}, {}, {})".format(x, y, floor)

        #import pyperclip as clipboard
        #clipboard.copy(out, out)

        node = renpy.game.script.lookup(renpy.game.contexts[0].current)
        fname = node.filename
        line_num = node.linenumber

        ## Get the file's contents andabsolute location
        f = renpy.file(fname.replace('game/',''))
        contents = f.readlines()
        path = f.name
        f.close()

        ## Insert the map position
        next_line = contents[line_num]
        indent = " "*(len(next_line)-len(next_line.lstrip()))
        out = indent+out+"\n"

        if map_dev_line_num==line_num:
            contents[line_num+map_dev_counter-2] = out
        else:
            contents.insert(line_num+map_dev_counter-1, out)
            map_dev_line_num = line_num
            map_dev_counter += 1

        ## Save the file
        contents = "".join([y.replace('\r','') for y in contents])
        f = open(path, "w")
        f.write(contents)
        f.close()

image position0_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[0][0]-13
    yoffset map_position_history[0][1]-13
    alpha 1.0
    zoom 1.0

image position1_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[1][0]-13
    yoffset map_position_history[1][1]-13
    alpha 0.8
    zoom 0.891

image position2_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[2][0]-13
    yoffset map_position_history[2][1]-13
    alpha 0.6
    zoom 0.794

image position3_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[3][0]-13
    yoffset map_position_history[3][1]-13
    alpha 0.5
    zoom 0.707

image position4_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[4][0]-13
    yoffset map_position_history[4][1]-13
    alpha 0.4
    zoom 0.630

image position5_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[5][0]-13
    yoffset map_position_history[5][1]-13
    alpha 0.3
    zoom 0.561

image position6_indicator:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset map_position_history[6][0]-13
    yoffset map_position_history[6][1]-13
    alpha 0.2
    zoom 0.5



image minimap_indicator00:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][0][0]-13
    yoffset minimap_position_history[0][0][1]-13
    alpha 1.0
    zoom 1.0

image minimap_indicator01:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][1][0]-13
    yoffset minimap_position_history[0][1][1]-13
    alpha 0.8
    zoom 0.891

image minimap_indicator02:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][2][0]-13
    yoffset minimap_position_history[0][2][1]-13
    alpha 0.6
    zoom 0.794

image minimap_indicator03:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][3][0]-13
    yoffset minimap_position_history[0][3][1]-13
    alpha 0.5
    zoom 0.707

image minimap_indicator04:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][4][0]-13
    yoffset minimap_position_history[0][4][1]-13
    alpha 0.4
    zoom 0.630

image minimap_indicator05:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][5][0]-13
    yoffset minimap_position_history[0][5][1]-13
    alpha 0.3
    zoom 0.561

image minimap_indicator06:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[0][6][0]-13
    yoffset minimap_position_history[0][6][1]-13
    alpha 0.2
    zoom 0.5



image minimap_indicator10:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][0][0]-13
    yoffset minimap_position_history[1][0][1]-13
    alpha 1.0
    zoom 1.0

image minimap_indicator11:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][1][0]-13
    yoffset minimap_position_history[1][1][1]-13
    alpha 0.8
    zoom 0.891

image minimap_indicator12:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][2][0]-13
    yoffset minimap_position_history[1][2][1]-13
    alpha 0.6
    zoom 0.794

image minimap_indicator13:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][3][0]-13
    yoffset minimap_position_history[1][3][1]-13
    alpha 0.5
    zoom 0.707

image minimap_indicator14:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][4][0]-13
    yoffset minimap_position_history[1][4][1]-13
    alpha 0.4
    zoom 0.630

image minimap_indicator15:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][5][0]-13
    yoffset minimap_position_history[1][5][1]-13
    alpha 0.3
    zoom 0.561

image minimap_indicator16:
    "gui/map/position.png"
    xalign 0.5
    xalign 0.5
    xoffset minimap_position_history[1][6][0]-13
    yoffset minimap_position_history[1][6][1]-13
    alpha 0.2
    zoom 0.5

layeredimage current_map0:
    #always:
    #    Solid("#0004", xoffset=-minimap_dim//2, yoffset=-minimap_dim//2, xsize=620+minimap_dim, ysize=710+minimap_dim)
    
    group floor:
        attribute F0:
            "gui/map/F0.png"
        attribute F0b:
            "gui/map/F0b.png"
        attribute F1:
            "gui/map/F1.png"
        attribute F1b:
            "gui/map/F1b.png"
        attribute F2:
            "gui/map/F2.png"
        attribute F3:
            "gui/map/F3.png"
        attribute F4:
            "gui/map/F4.png"
        attribute F5:
            "gui/map/F5.png"
        attribute F6:
            "gui/map/F6.png"
        attribute F6b:
            "gui/map/F6b.png"
        attribute F7:
            "gui/map/F7.png"
        attribute F8:
            "gui/map/F8.png"

    if persistent.mappos and len(minimap_position_history[0])>6 and minimap_position_history[0][6][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator06"
    if persistent.mappos and len(minimap_position_history[0])>5 and minimap_position_history[0][5][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator05"
    if persistent.mappos and len(minimap_position_history[0])>4 and minimap_position_history[0][4][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator04"
    if persistent.mappos and len(minimap_position_history[0])>3 and minimap_position_history[0][3][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator03"
    if persistent.mappos and len(minimap_position_history[0])>2 and minimap_position_history[0][2][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator02"
    if persistent.mappos and len(minimap_position_history[0])>1 and minimap_position_history[0][1][2]==minimap_position_history[0][0][2]:
        pos (10, 0)
        "minimap_indicator01"
    if len(minimap_position_history[0])>0:
        pos (10, 0)
        "minimap_indicator00"

layeredimage current_map1:
    #always:
    #    Solid("#0004", xoffset=-minimap_dim//2, yoffset=-minimap_dim//2, xsize=620+minimap_dim, ysize=710+minimap_dim)
    
    group floor:
        attribute F0:
            "gui/map/F0.png"
        attribute F0b:
            "gui/map/F0b.png"
        attribute F1:
            "gui/map/F1.png"
        attribute F1b:
            "gui/map/F1b.png"
        attribute F2:
            "gui/map/F2.png"
        attribute F3:
            "gui/map/F3.png"
        attribute F4:
            "gui/map/F4.png"
        attribute F5:
            "gui/map/F5.png"
        attribute F6:
            "gui/map/F6.png"
        attribute F6b:
            "gui/map/F6b.png"
        attribute F7:
            "gui/map/F7.png"
        attribute F8:
            "gui/map/F8.png"

    if persistent.mappos and len(minimap_position_history[1])>6 and minimap_position_history[1][6][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator16"
    if persistent.mappos and len(minimap_position_history[1])>5 and minimap_position_history[1][5][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator15"
    if persistent.mappos and len(minimap_position_history[1])>4 and minimap_position_history[1][4][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator14"
    if persistent.mappos and len(minimap_position_history[1])>3 and minimap_position_history[1][3][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator13"
    if persistent.mappos and len(minimap_position_history[1])>2 and minimap_position_history[1][2][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator12"
    if persistent.mappos and len(minimap_position_history[1])>1 and minimap_position_history[1][1][2]==minimap_position_history[1][0][2]:
        pos (10, 0)
        "minimap_indicator11"
    if len(minimap_position_history[1])>0:
        pos (10, 0)
        "minimap_indicator10"

image display_map:
    LiveComposite(
        (620, config.screen_height),
        (0,0), ConditionSwitch(
            "map_displayed_floor==0 and persistent.map_unlocked[1]==2", "gui/map/F0b.png",
            "map_displayed_floor==1 and persistent.map_unlocked[1]==2", "gui/map/F1b.png",
            "map_displayed_floor==6 and persistent.map_unlocked[6]==2", "gui/map/F6b.png",
            "map_displayed_floor==0", "gui/map/F0.png",
            "map_displayed_floor==1", "gui/map/F1.png",
            "map_displayed_floor==2", "gui/map/F2.png",
            "map_displayed_floor==3", "gui/map/F3.png",
            "map_displayed_floor==4", "gui/map/F4.png",
            "map_displayed_floor==5", "gui/map/F5.png",
            "map_displayed_floor==6", "gui/map/F6.png",
            "map_displayed_floor==7", "gui/map/F7.png",
            "map_displayed_floor==8", "gui/map/F8.png",
            "map_displayed_floor is not None", "gui/map/position{}.png".format(map_displayed_floor),
            "map_displayed_floor is None and persistent.map_unlocked[1]==2", "gui/map/F1b.png",
            "map_displayed_floor is None", "gui/map/F1.png",
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>6 and map_position_history[6][2]==map_displayed_floor", "position6_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>5 and map_position_history[5][2]==map_displayed_floor", "position5_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>4 and map_position_history[4][2]==map_displayed_floor", "position4_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>3 and map_position_history[3][2]==map_displayed_floor", "position3_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>2 and map_position_history[2][2]==map_displayed_floor", "position2_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "persistent.mappos and len(map_position_history)>1 and map_position_history[1][2]==map_displayed_floor", "position1_indicator",
            "True", Null(),
            predict_all=False),
        (0,0), ConditionSwitch(
            "len(map_position_history)>0 and map_position_history[0][2]==map_displayed_floor", "position0_indicator",
            "True", Null(),
            predict_all=False),
        )

image minimap_proxy0 = LayeredImageProxy("current_map0")
image minimap_proxy1 = LayeredImageProxy("current_map1")

screen minimap(show_text=False):
    predict False ## Avoid predicting this screen
    $ if len(map_position_history)==0: MapResetPositions()

    if len(map_position_history)>0 and map_position_history[0][2] != None and persistent.map_unlocked[map_position_history[0][2]]:
        $ store.map_displayed_floor = map_position_history[0][2]
        button:
            mouse "imagemap"
            background "#0004"
            activate_sound "sounds/sys6.wav"
            hover_background "#3334"
            padding (4,4,4,4)
            add "minimap_proxy{} {}".format(store.map_alternator_counter, store.minimap_displayed_floor):
                xalign 0.5
                yalign 0.5
            action [ShowMenu("map"), Hide("info_hud")]
    else:
        if show_text:
            button:
                xsize int(minimap_dim*0.5)
                ysize int(minimap_dim*0.5)
                text "Not Available" xalign 0.5 yalign 0.5

screen map():
    predict False ## Avoid predicting this screen
    tag menu

    ## Set map_displayed_floor on show
    timer 0.01 action Function(MapSetInitialPosition)

    key "focus_up" action ChangeMapScroll(1)
    key "viewport_up" action ChangeMapScroll(1)
    key "focus_down" action ChangeMapScroll(-1)
    key "viewport_down" action ChangeMapScroll(-1)

    #if config.developer:
    #    key "mousedown_1" action Function(MapGetPosition, map_displayed_floor)

    use game_menu(_("Map"), padded=(40, 35, 40, 20)):
        style_prefix "map"

        if not persistent.map_unlocked[1]:
            frame:
                background None
                xfill True
                yfill True

                text "Currently unavailable":
                    xalign 0.5
                    yalign 0.5
        else:
            frame:
                background None
                padding (0,0,0,0)
                xanchor 1.0
                xpos 0.85
                ypos 50

                add "display_map":
                    zoom 0.7
            vbox:
                xanchor 0.0
                xpos 0.15
                yalign 0.5
                spacing 9
                if persistent.map_unlocked[8]:
                    textbutton "UPPER BEDROOMS" text_ypos 8 action SetVariable("map_displayed_floor", 8) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[7]:
                    textbutton "F7 - ATTICS" text_ypos 8 action SetVariable("map_displayed_floor", 7) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[6]:
                    textbutton "F6 - OFFICES" text_ypos 8 action SetVariable("map_displayed_floor", 6) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[5]:
                    textbutton "F5 - OFFICES" text_ypos 8 action SetVariable("map_displayed_floor", 5) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[4]:
                    textbutton "F4 - OFFICES" text_ypos 8 action SetVariable("map_displayed_floor", 4) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[3]:
                    textbutton "F3 - OFFICES" text_ypos 8 action SetVariable("map_displayed_floor", 3) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[2]:
                    textbutton "F2 - OFFICES" text_ypos 8 action SetVariable("map_displayed_floor", 2) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[1]:
                    textbutton "F1 - CRYSTAL FLOOR" text_ypos 8 action SetVariable("map_displayed_floor", 1) activate_sound "sounds/sys21.wav"
                if persistent.map_unlocked[0]:
                    textbutton "MECHANICAL ROOM" text_ypos 8 action SetVariable("map_displayed_floor", 0) activate_sound "sounds/sys21.wav"

style map_button is gui_button:
    background "gui/map/button_idle.png"
    selected_background "gui/map/button_selected.png"
    padding (80, 15, 0, 10)
    xsize 267
    ysize 38

style map_button_text:
    hover_color u'#cce6ff'
    idle_color u'#c4c4c4'
    selected_color u'#ffffff'
