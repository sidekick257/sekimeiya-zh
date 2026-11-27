init -100 python:
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
        artist="Âme",
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
        artist="Âme",
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
        artist="Âme",
        art="images/albumart/setsa.jpg",
        fname_noloop="music/original/setsa.ogg",
        fname_loop="music/setsa.ogg",
        loop_start=61.047,
        ))
    all_music_entries.append(MusicEntry(
        name="Shiro",
        artist="Âme",
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
    composer_details["Âme"] = [ComposerEntry(
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
