# This needs to be set to true to enable analytics.
default persistent.analytics = True

## @CHECK: Make sure preferences are reflected by update_preferences
## TODO: Save backlog of events and resend when analytics if the connection fails the first time

# Initialize this to a unique cid.
default persistent.analytics_cid = None

default persistent.analytics_backlog = python_list()

init -50 python in analytics:
    import store
    from store import persistent, config, preferences
    import uuid
    from mixpanel import Mixpanel
    import re
    from urllib.request import urlopen
    from urllib.parse import quote as parseurl
    import pygame_sdl2
    import os
    import sys
    import requests
    import json
    import time
    from collections import OrderedDict

    import threading
    import ssl

    from requests.exceptions import ConnectionError

    ## Alpha
    #project_id = "2312892"
    #project_token = "ab8806ed027b3ac0d4938c067520f5b6"

    ## Beta
    project_id = "2340739"
    project_token = "06b3ad69c4c945756c81e237455bae87"

    mp = Mixpanel(
        project_token,
        "R2FtZVN0YXRlUmVhZGVyLmJmZDY1NS5tcC1zZXJ2aWNlLWFjY291bnQ6OThQS3FJOHI0MUFSMWpteXJQSmZCUnhXZk9wWFZIdjE="
    )

    def SavePersistent():
        renpy.persistent.update(True)
        renpy.persistent.save_MP()
        print("saved persistent")

    # Create a cid if needed.
    if persistent.analytics_cid is None:
        persistent.analytics_cid = str(uuid.uuid4())

    if persistent.analytics_logged is None:
        persistent.analytics_logged = python_dict()

    if "c5 answers" not in persistent.analytics_logged:
        persistent.analytics_logged["c5 answers"] = python_dict()

    if "c5 answers times" not in persistent.analytics_logged:
        persistent.analytics_logged["c5 answers times"] = python_dict()

    if "scenes" not in persistent.analytics_logged:
        persistent.analytics_logged["scenes"] = python_dict()

    if "post" not in persistent.analytics_logged:
        persistent.analytics_logged["post"] = python_dict()

    if persistent.analytics_retrieved is None:
        persistent.analytics_retrieved = python_dict()

    if "c5 answers" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["c5 answers"] = default_c5_answers

    if "c5 answers times" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["c5 answers times"] = default_c5_answers_times

    if "scenes" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["scenes"] = default_scenes

    if "prefs" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["prefs"] = default_prefs

    if "post" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["post"] = default_post

    if "playtimes" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["playtimes"] = default_playtimes

    if "other" not in persistent.analytics_retrieved:
        persistent.analytics_retrieved["other"] = default_other

    if persistent.copy_detected is None:
        persistent.copy_detected = False


    def CopyCheck():
        ## Turns out steam doesn't like hidden files
        #check1 = os.path.exists(os.path.join(renpy.config.gamedir, "init.bin"))
        #if not check1:
        #    persistent.copy_detected = True
        #    return

        fn1 = os.path.join(renpy.config.gamedir, "version.txt")
        if os.path.exists(fn1):
            os.remove(fn1)

        fn2 = os.path.join(renpy.config.gamedir, "python-packages/version.txt")
        if os.path.exists(fn2):
            with open(fn2, "r") as f:
                id = f.read()
            check2 = (id == HardwareID())
            if check2 is False:
                persistent.copied_uuid = id
        else:
            with open(fn2, "w") as f:
                f.write(HardwareID())
            check2 = True

        if not check2:
            persistent.copy_detected = True


    def HardwareID():
        import subprocess
        uuid = "0000000000000"
        try:
            if sys.platform in ["win32", "cygwin"]:
                ## Windows
                uuid = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split("\n")[1].strip()
            elif sys.platform == "darwin":
                ## MacOS
                uuid = subprocess.check_output("ioreg -d2 -c IOPlatformExpertDevice | awk -F\" '/IOPlatformUUID/{print $(NF-1)}'".split(), shell=True)
            elif sys.playform == "linux":
                try:
                    uuid = subprocess.check_output("uuidgen".split(), shell=True)
                except:
                    try:
                        uuid = subprocess.check_output("cat /proc/sys/kernel/random/uuid".split(), shell=True)
                    except:
                        try:
                            uuid = subprocess.check_output("dbus_uuidgen".split(), shell=True)
                        except:
                            uuid = subprocess.check_output("blkid".split(), shell=True)
        except:
            pass

        return uuid

    def UpdatePlayer():
        if config.developer:
            return
        CopyCheck()

        total_answers, correct_answers, percentage_correct = store.c5_answers.GetScore()

        data.update({
            "Platform": pygame_sdl2.get_platform(),
            "Time (In-Game)": int(persistent.playtime["game"]),
            "Time (Search)": int(persistent.playtime["search"]),
            "Time (Notes)": int(persistent.playtime["notes"]),
            "Time (Other)": int(persistent.playtime["other"]),
            "Time (Total)": int(persistent.playtime["total"]),
            "Time (Unfocused)": int(persistent.playtime["unfocused"]),
            "Time (All)": int(persistent.playtime["all"]),
            "Number of Sessions": int(persistent.num_sessions),
            "Pirate": persistent.copy_detected,
            "Pirated UUID": persistent.copied_uuid,
            "Version": config.version,

            "C5 Answers Correct": correct_answers,
            "C5 Answers Total": total_answers,
            "C5 Answers Percent": percentage_correct,
            #"Pref C5 Questions Enabled": persistent.enable_c5_questions,

            "Pref Fullscreen": renpy.game.preferences.fullscreen,
            "Pref Resolution": "{} x {}".format(*renpy.get_physical_size()),

            "Pref Sprite Darken": persistent.sprite_darken,
            "Pref Sprite Darken Fade": persistent.sprite_darken_transition,
            "Pref Sprite Darken Amount": int(persistent.sprite_dark_tint*100),

            "Pref Skip Unseen": preferences.skip_unseen,
            "Pref Skip Choices": preferences.skip_after_choices,

            "Pref Transitions": preferences.transitions,

            "Pref Volume Music": int(preferences.get_volume("music")*100),
            "Pref Volume SFX": int(preferences.get_volume("sfx")*100),
            "Pref Volume System": int(preferences.get_volume("system")*100),
            "Pref Volume Mute Defocus": preferences.mute_audio_defocus,

            "Pref Minimap": persistent.minimap,
            "Pref Map Prev Positions": persistent.mappos,
            "Pref Map Fade": persistent.minimap_fade,
            "Pref Click Short Pauses": persistent.pref_click_short_pauses,

            "Pref Textbox Style": persistent._gui_preference["textbox_style"],
            "Pref Textbox Width": int(persistent._gui_preference["textbox_width"]*100),
            "Pref Textbox Opacity": int(persistent._gui_preference["textbox_opacity"]*100),

            "Pref Text Outline": persistent._gui_preference["dialogue_outline_idx"]+1,
            "Pref Text Speed": int(preferences.text_cps),
            "Pref Text Auto": int(preferences.afm_time),

            "Pref Font": persistent._gui_preference["font"],
            "Pref 24 Hour Format": persistent.time_format_24,

            "Pref Speaker Indicator": persistent._gui_preference["speaker_indicator"],
            "Pref Color Text": persistent._gui_preference["colored_text"],
            "Pref Color Speaker": persistent._gui_preference["colored_speaker"],
        })

        mp.people_set(persistent.analytics_cid, data)#, meta=meta)


    def UpdatePreferences():
        mp.people_set(persistent.analytics_cid,
            {
                "Pref Fullscreen": renpy.game.preferences.fullscreen,
                "Pref Resolution": "{} x {}".format(*renpy.get_physical_size()),

                "Pref Sprite Darken": persistent.sprite_darken,
                "Pref Sprite Darken Fade": persistent.sprite_darken_transition,
                "Pref Sprite Darken Amount": int(persistent.sprite_dark_tint*100),

                "Pref Skip Unseen": preferences.skip_unseen,
                "Pref Skip Choices": preferences.skip_after_choices,

                "Pref Transitions": preferences.transitions,

                "Pref Volume Music": int(preferences.get_volume("music")*100),
                "Pref Volume SFX": int(preferences.get_volume("sfx")*100),
                "Pref Volume System": int(preferences.get_volume("system")*100),
                "Pref Volume Mute Defocus": preferences.mute_audio_defocus,

                "Pref Minimap": persistent.minimap,
                "Pref Map Prev Positions": persistent.mappos,
                "Pref Click Short Pauses": persistent.pref_click_short_pauses,

                "Pref Textbox Style": persistent._gui_preference["textbox_style"],
                "Pref Textbox Width": int(persistent._gui_preference["textbox_width"]*100),
                "Pref Textbox Opacity": int(persistent._gui_preference["textbox_opacity"]*100),

                "Pref Text Outline": persistent._gui_preference["dialogue_outline_idx"]+1,
                "Pref Text Speed": int(preferences.text_cps),
                "Pref Text Auto": int(preferences.afm_time),

                "Pref Font": persistent._gui_preference["font"],
                "Pref 24 Hour Format": persistent.time_format_24,

                "Pref Speaker Indicator": persistent._gui_preference["speaker_indicator"],
                "Pref Color Text": persistent._gui_preference["colored_text"],
                "Pref Color Speaker": persistent._gui_preference["colored_speaker"],
            })
        UpdatePlayer()


    def SendChapterTime(chapter_name, time_taken):
        if config.developer:
            return

        mp.people_set(persistent.analytics_cid,
            {
                "Time ({})".format(chapter_name): int(time_taken),
            })
        UpdatePlayer()
        SavePersistent()


    def SendC5Answer(question, answer, time_taken):
        if question in persistent.analytics_logged["c5 answers"]:
            return

        persistent.analytics_logged["c5 answers"][question] = True

        if config.developer:
            return

        mp.track(persistent.analytics_cid, "C5 Answer",
            {
                "Question": question,
                "Answer": answer,
                "Time Taken": time_taken,
            })

        UpdatePlayer()
        SavePersistent()


    def SendPostGameVote(vote_dict):
        if config.developer:
            return

        mp.people_set(persistent.analytics_cid, vote_dict)
        SavePersistent()


    def SendSceneEvent(scene_name):
        if config.developer:
            return

        if scene_name in persistent.analytics_logged["scenes"]:
            return

        mp.track(persistent.analytics_cid, "Scene",
            {
                "Scene": scene_name,
            })

        persistent.analytics_logged["scenes"][scene_name] = True
        UpdatePlayer()
        SavePersistent()

    def GetDefaultStats():
        persistent.analytics_retrieved["c5 answers"] = default_c5_answers
        persistent.analytics_retrieved["c5 answers times"] = default_c5_answers_times
        persistent.analytics_retrieved["scenes"] = default_scenes
        persistent.analytics_retrieved["prefs"] = default_prefs
        persistent.analytics_retrieved["post"] = default_post
        persistent.analytics_retrieved["playtimes"] = default_playtimes
        persistent.analytics_retrieved["other"] = default_other

        from collections import OrderedDict
        sorted_dict = OrderedDict(sorted(persistent.analytics_retrieved["other"]["Correct Percentage"].items()))
        persistent.analytics_retrieved["other"]["Correct Percentage"] = sorted_dict

        store.Histogram.cache.clear()
        store.RankingVoteDisplayable.cache.clear()

init python:
    if persistent.last_updated_stats is None or persistent.last_updated_stats < analytics.default_last_updated_stats:
        persistent.last_updated_stats = analytics.default_last_updated_stats
        analytics.GetDefaultStats()
