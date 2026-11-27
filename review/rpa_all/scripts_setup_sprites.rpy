## @TODO: Dark/normal sprites are still not predicted correctly all the time. It's a 50/50.

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
    transform_position(5,5)