# Image definitions for snow particles:

init python:
    def Snow(intensity, fast=False):
        renpy.hide(name="snow_effect", layer="snow_layer")

        if (intensity == 0):
            snow_type = None
        elif (intensity == 1):
            snow_type = "light_snow"
        elif (intensity == 2):
            snow_type = "heavy_snow"
        elif (intensity == 3):
            snow_type = "blizzard"
        else:
            raise Exception("Snow(intensity) requires intensity to be 0, 1, 2 or 3")

        if snow_type:
            if fast:
                snow_type += "_fast"

            renpy.show(name=snow_type, layer="snow_layer", tag="snow_effect")


    def RandomizeSnow():
        for group in renpy.game.contexts[-1].scene_lists.layers['snow_layer'][0].displayable.child.target.children:
            if group is None or group.particles is None:
                continue

            for particle in group.particles:
                particle[1].xstart = random.randint(0, 1280)
                particle[1].ystart = random.randint(0, 720)

#########

image light_snow = Fixed(
    #SnowBlossom2("snowflake_large", 20, xspeed=(20, 50), yspeed=(100, 200), start=10.0, fluttering=50),
    SnowBlossom2("snowflake_normal", 25, xspeed=(15, 35), yspeed=(75, 150), start=10.0, fluttering=50),
    SnowBlossom2("snowflake_small",  25, xspeed=(10, 25), yspeed=(50, 100), start=10.0, fluttering=20, flutteringspeed=0.02)
    )

image heavy_snow = Fixed(
    SnowBlossom2("snowflake_large",   20, xspeed=(80, 200), yspeed=(200, 400), start=10.0, fluttering=25),
    SnowBlossom2("snowflake_normal", 100, xspeed=(60, 140), yspeed=(150, 300), start=10.0, fluttering=25),
    SnowBlossom2("snowflake_small",  100, xspeed=(40, 100), yspeed=(100, 200), start=10.0, fluttering=10, flutteringspeed=0.02)
    )

image blizzard = Fixed(
    SnowBlossom2("snowflake_blizzard_large", 40, xspeed=(1200, 1400), yspeed=(600, 700), start=1.0, horizontal=True),
    SnowBlossom2("snowflake_blizzard_normal",40, xspeed=(800, 900), yspeed=(400, 450), start=1.0, horizontal=True),
    SnowBlossom2("snowflake_blizzard_small", 40, xspeed=(500, 600), yspeed=(250, 300), start=1.0, horizontal=True),
    "fog"
    )

image light_snow_fast = Fixed(
    #SnowBlossom2("snowflake_large", 20, xspeed=(20, 50), yspeed=(100, 200), start=10.0, fluttering=50, fast=True),
    SnowBlossom2("snowflake_normal", 25, xspeed=(15, 35), yspeed=(75, 150), start=10.0, fast=True, fluttering=50),
    SnowBlossom2("snowflake_small",  25, xspeed=(10, 25), yspeed=(50, 100), start=10.0, fast=True, fluttering=20, flutteringspeed=0.02)
    )

image heavy_snow_fast = Fixed(
    SnowBlossom2("snowflake_large",   20, xspeed=(80, 200), yspeed=(200, 400), start=10.0, fast=True, fluttering=25),
    SnowBlossom2("snowflake_normal", 100, xspeed=(60, 140), yspeed=(150, 300), start=10.0, fast=True, fluttering=25),
    SnowBlossom2("snowflake_small",  100, xspeed=(40, 100), yspeed=(100, 200), start=10.0, fast=True, fluttering=10, flutteringspeed=0.02)
    )

image blizzard_fast = Fixed(
    SnowBlossom2("snowflake_blizzard_large", 40, xspeed=(1200, 1400), yspeed=(600, 700), start=1.0, horizontal=True),
    SnowBlossom2("snowflake_blizzard_normal",40, xspeed=(800, 900), yspeed=(400, 450), start=1.0, horizontal=True),
    SnowBlossom2("snowflake_blizzard_small", 40, xspeed=(500, 600), yspeed=(250, 300), start=1.0, horizontal=True),
    "fog"
    )

image fog:
    "effects/fog.png"
    xtile 4
    ytile 3

    alpha 0.8
    xalign 0.0
    zoom 8.020

    block:
        yoffset -64*8
        xoffset -64*8

        parallel:
            linear 1.5 xoffset 0
        parallel:
            linear 1.5 yoffset 0
        repeat

##################


image snowflake:
    alpha renpy.random.random()*0.25 + 0.25
    choice:
        "effects/snow1.png"
    choice:
        "effects/snow2.png"
    choice:
        "effects/snow3.png"
    choice:
        "effects/snow4.png"

image snowflake_small:
    "snowflake"
    zoom 0.20

image snowflake_normal:
    "snowflake"
    zoom 0.30

image snowflake_large:
    "snowflake"
    zoom 0.50

image snowflake_blizzard:
    alpha renpy.random.random()*0.5 + 0.5
    "effects/snow_blizzard_cluster.png"
    #choice:
    #    "effects/snow_blizzard1.png"
    #choice:
    #    "effects/snow_blizzard2.png"

image snowflake_blizzard_particle:
    "snowflake_blizzard"

    #xtile 3
    #ytile 3

    #LiveComposite(
    #    (64, 64),
    #    (0, 0), "snowflake_blizzard",
    #    (0, 32), "snowflake_blizzard",
    #    (32, 0), "snowflake_blizzard",
    #    (32, 32), "snowflake_blizzard",
    #)

image snowflake_blizzard_small:
    "snowflake_blizzard_particle"
    zoom 0.75

image snowflake_blizzard_normal:
    "snowflake_blizzard_particle"
    zoom 0.95

image snowflake_blizzard_large:
    "snowflake_blizzard_particle"
    zoom 1.5


# This bit is required for the SnowBlossom2 effect by Nyaatrap (or at least used in his cool dress-up demo):
init -100 python:

    import random, math

    class SnowBlossomFactory2(renpy.python.NoRollback):

        rotate = False

        def __setstate__(self, state):
            self.start = 0
            vars(self).update(state)
            self.init()

        def __init__(self, image, count, xspeed, yspeed, border, start, fluttering, flutteringspeed, fast, rotate=False):
            self.image = renpy.easy.displayable(image)
            self.count = count
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.border = border
            self.start = start
            self.fluttering = fluttering * random.uniform(0.8, 1.2)
            self.flutteringspeed = flutteringspeed * random.uniform(0.8, 1.2)
            self.fast = fast
            self.rotate = rotate
            self.init()

        def init(self):
            self.starts = [ random.uniform(0, self.start) for _i in xrange(0, self.count) ] # W0201
            self.starts.append(self.start)
            self.starts.sort()

        def create(self, particles, st):

            def ranged(n):
                if isinstance(n, tuple):
                    return random.uniform(n[0], n[1])
                else:
                    return n

            if not particles and self.fast:
                rv = [ ]

                for _i in xrange(0, self.count):
                    rv.append(SnowBlossomParticle2(
                        self.image,
                        ranged(self.xspeed),
                        ranged(self.yspeed),
                        self.border,
                        st,
                        self.fluttering,
                        self.flutteringspeed,
                        random.uniform(0, 100),
                        fast=True,
                        rotate=self.rotate))
                return rv

            if particles is None or len(particles) < self.count:
                # Check to see if we have a particle ready to start. If not,
                # don't start it.
                if particles and st < self.starts[len(particles)]:
                    return None

                rv = python_list()

                for _i in xrange(0, max(1, self.count//100)):
                    rv.append(SnowBlossomParticle2(
                        self.image,
                        ranged(self.xspeed),
                        ranged(self.yspeed),
                        self.border,
                        st,
                        self.fluttering,
                        self.flutteringspeed,
                        random.uniform(0, renpy.config.screen_width),
                        fast=False,
                        rotate=self.rotate))

                return rv

        def predict(self):
            return [ self.image ]


    class SnowBlossomParticle2(renpy.python.NoRollback):

        def __init__(self, image, xspeed, yspeed, border, start, fluttering, flutteringspeed, offset, fast, rotate):

            # safety.
            if yspeed == 0:
                yspeed = 1

            self.image = image
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.border = border
            self.start = start
            self.fluttering = fluttering
            self.flutteringspeed = flutteringspeed
            self.offset = offset
            self.rotate = rotate
            self.angle = random.uniform(0, 3.14)
            self.fast = fast

            self.reset(initial=True)

        def reset(self, initial=False):
            if not self.rotate:
                sh = renpy.config.screen_height
                sw = renpy.config.screen_width
            else:
                sw = renpy.config.screen_height
                sh = renpy.config.screen_width

            if self.yspeed > 0:
                self.ystart = -self.border
            else:
                self.ystart = sh + border


            travel_time = (2.0 * self.border + sh) / abs(self.yspeed)

            xdist = self.xspeed * travel_time

            x0 = min(-xdist, 0)
            x1 = max(sw + xdist, sw)

            self.xstart = random.uniform(x0, x1)

            if initial and self.fast:
                self.ystart = random.uniform(-self.border, sh + self.border)
                self.xstart = random.uniform(0, sw)

        def update(self, st):
            to = st - self.start
            self.angle += self.flutteringspeed

            xpos = self.xstart + to * self.xspeed + math.sin(self.angle)*self.fluttering
            ypos = self.ystart + to * self.yspeed

            if not self.rotate:
                sh = renpy.config.screen_height
            else:
                sh = renpy.config.screen_width

            if ypos > sh + self.border:
                self.reset()
                xpos = self.xstart
                ypos = self.ystart
                self.start = st
                #return None

            if ypos < -self.border:
                self.reset()
                xpos = self.xstart
                ypos = self.ystart
                self.start = st
                #return None

            if not self.rotate:
                return int(xpos), int(ypos), to + self.offset, self.image
            else:
                return int(ypos), int(xpos), to + self.offset, self.image


    def SnowBlossom2(d,
                    count=10,
                    border=50,
                    xspeed=(20, 50),
                    yspeed=(100, 200),
                    start=0,
                    fluttering=0,
                    flutteringspeed=0.02,
                    fast=False,
                    horizontal=False):

        """
        :doc: sprites_extra

        The snowblossom effect moves multiple instances of a sprite up,
        down, left or right on the screen. When a sprite leaves the screen, it
        is returned to the start.

        `d`
            The displayable to use for the sprites.

        `border`
            The size of the border of the screen. The sprite is considered to be
            on the screen until it clears the border, ensuring that sprites do
            not disappear abruptly.

        `xspeed`, `yspeed`
            The speed at which the sprites move, in the horizontal and vertical
            directions, respectively. These can be a single number or a tuple of
            two numbers. In the latter case, each particle is assigned a random
            speed between the two numbers. The speeds can be positive or negative,
            as long as the second number in a tuple is larger than the first.

        `start`
            The delay, in seconds, before each particle is added. This can be
            allows the particles to start at the top of the screen, while not
            looking like a "wave" effect.

        'fluttering'
            The width of fluttering in pixel.

        'flutteringspeed'
            The speed of fluttering.

        `fast`
            If true, particles start in the center of the screen, rather than
            only at the edges.

        `horizontal`
            If true, particles appear on the left or right side of the screen,
            rather than the top or bottom.
            """

        # If going horizontal, swap the xspeed and the yspeed.
        if horizontal:
            xspeed, yspeed = yspeed, xspeed

        return Particles(SnowBlossomFactory2(
            image=d,
            count=count,
            border=border,
            xspeed=xspeed,
            yspeed=yspeed,
            start=start,
            fluttering=fluttering,
            flutteringspeed=flutteringspeed,
            fast=fast,
            rotate=horizontal))