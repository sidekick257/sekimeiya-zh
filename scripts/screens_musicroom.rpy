init python:

    musicroom_entries = python_list()
    for entry in all_music_entries:
        if entry.show_in_musicroom:
            musicroom_entries.append(entry)

    class MusicRoom2(MusicRoom):
        def periodic(self, st):

            if st == self.st:
                return
            elif st < self.st:
                self.last_playing = None

            self.st = st

            current_playing = renpy.music.get_playing(self.channel)
            if current_playing is None:
                current_playing = ""

            if self.last_playing != current_playing:
                action = self.action.get(current_playing, None)
                renpy.run_action(action)

                self.last_playing = current_playing

        def play(self, filename=None, offset=0, queue=False):
            """
            Starts the music room playing. The file we start playing with is
            selected in two steps.

            If `filename` is an unlocked file, we start by playing it.
            Otherwise, we start by playing the currently playing file, and if
            that doesn't exist or isn't unlocked, we start with the first file.

            We then apply `offset`. If `offset` is positive, we advance that many
            files, otherwise we go back that many files.
            """

            if offset != 0 and self.shuffle:
                playlist = self.unlocked_playlist(filename, randomize=True)
            else:
                playlist = self.unlocked_playlist(filename)

            if not playlist:
                return

            if filename is None:
                filename = renpy.music.get_playing(channel=self.channel)

            entry = musicroom_entries[self.get_entry_idx(filename)]
            if entry.play_in_musicroom:
                ## Get the index of the song in the playlist
                idx = self.get_playlist_idx(filename, shuffled=self.shuffle)
                idx = (idx + offset) % len(playlist)

                if self.single_track:
                    playlist = [ playlist[idx] ]
                else:
                    playlist = playlist[idx:] + playlist[:idx]

                if queue:
                    renpy.music.queue(playlist, channel=self.channel, loop=self.loop)
                else:
                    renpy.music.play(playlist, channel=self.channel, fadeout=self.fadeout, fadein=self.fadein, loop=self.loop)

            else:
                ## This file cannot be played in the music room due to licensing. Play it momentarily to set the appropriate variables, then stop it
                idx = self.get_entry_idx(filename)
                entry = musicroom_entries[idx]
                renpy.music.play(entry.fname_noloop, channel=self.channel, fadeout=self.fadeout, fadein=self.fadein, loop=self.loop)

                self.pause()
            
            ## Copy this music context to the lowest one (main menu context) so that music continues to play when you press Start Game
            renpy.game.contexts[0].music = renpy.game.context().music

        def unlocked_playlist(self, filename=None, randomize=False):
            """
            Returns a list of filenames in the playlist that have been
            unlocked.
            """

            if randomize or self.shuffled is None:
                import random
                self.shuffled = python_list(self.playlist)
                random.shuffle(self.shuffled)

                if filename in self.shuffled:
                    self.shuffled.remove(filename)
                    self.shuffled.insert(0, filename)

            if self.shuffle:
                playlist = self.shuffled
            else:
                playlist = self.playlist

            return [ i for i in playlist if self.is_unlocked(i) ]

        def get_entry_idx(self, filename=None):
            if filename is None:
                filename = renpy.music.get_playing(channel=self.channel)

                if filename is None:
                    return -1

            for num, entry in enumerate(musicroom_entries):
                if entry.fname_noloop in filename:
                    return num

            return -1

        def get_playlist_idx(self, filename=None, shuffled=False):
            if filename is None:
                filename = renpy.music.get_playing(channel=self.channel)

                if filename is None:
                    return -1

            if shuffled:
                playlist = mr.shuffled
            else:
                playlist = mr.playlist

            for num, song in enumerate(playlist):
                if song in filename:
                    return num

            return -1

        def queue_if_playing(self):
            idx = self.get_entry_idx()

            if self.single_track:
                filename = musicroom_entries[idx].fname_noloop
                renpy.music.queue(filename, channel=self.channel, loop=self.loop)
            else:
                self.play(None, offset=1, queue=True)

        def set_song_position(self, position):
            filename = renpy.music.get_playing(channel=self.channel)
            if filename:
                if '>' in filename:
                    filename = filename.split('>')[1]
                filename = "<from {}>{}".format(position, filename)
                renpy.music.play(filename, channel=self.channel, fadeout=0, fadein=0, loop=self.loop)

                self.queue_if_playing()

        def stop(self):
            self.set_song_position(0)
            self.pause()

        def pause(self):
            ch = renpy.audio.audio.get_channel('music')
            ch.paused = False
            ch.context.pause = True

    class MusicRoomPlayEntry(Action, FieldEquality):
        """
        The action returned by MusicRoom.Play when called with a file.
        """

        identity_fields = [ "mr" ]
        equality_fields = [ "filename" ]

        def __init__(self, mr, entry):
            self.mr = mr
            self.entry = entry
            self.filename = entry.fname_noloop
            self.selected = self.get_selected()

        def __call__(self):
            self.mr.play(self.filename, 0)

        def get_sensitive(self):
            return True #self.mr.is_unlocked(self.filename)

        def get_selected(self):
            return renpy.music.get_playing(self.mr.channel) == self.filename

        def periodic(self, st):
            if self.selected != self.get_selected():
                self.selected = self.get_selected()
                renpy.restart_interaction()

            self.mr.periodic(st)

            return .1

    @renpy.pure
    class AudioPositionValue2(BarValue, DictEquality):
        """
        :doc: value

        A value that shows the playback position of the audio file playing
        in `channel`.

        `update_interval`
            How often the value updates, in seconds.
        """

        identity_fields = [ ]
        equality_fields = [ 'action', 'channel', 'update_interval' ]

        def __init__(self, channel='music', update_interval=0.1, action=None):
            self.channel = channel
            self.update_interval = update_interval
            self.action = action

            self.adjustment = ui.adjustment(
                range=0,
                value=0,
                changed=self.changed,
                step=1.0,
                force_step=False,
                #adjustable=False,
            )

        def get_adjustment(self):
            pos, duration = self.get_pos_duration()

            if duration > 0.0:
                self.adjustment.set_range(duration)
                self.adjustment.set_value(pos)
            return self.adjustment

        def periodic(self, st):
            self.get_adjustment()
            return self.update_interval

        def changed(self, value):
            mr.set_song_position(value)
            renpy.restart_interaction()

            renpy.run(self.action)

        def get_pos_duration(self):
            pos = renpy.music.get_pos(self.channel) or 0.0
            duration = renpy.music.get_duration(self.channel) or 0.0

            return pos, duration

    class MusicRoomPrev(Action, DictEquality):
        def __call__(self):
            if (renpy.music.get_pos() or 0.0) > 3:
                mr.set_song_position(0) #restart song
            else:
                mr.previous()

    mr = MusicRoom2(channel='music', shuffle=False, loop=True) 
    for entry in musicroom_entries:
        if entry.play_in_musicroom:
            mr.add(entry.fname_noloop, always_unlocked=True)

    def music_info(st, at, val):
        return Text("{:02.0f}:{:02.0f}".format(val//60, int(val%60)), style="barinformation_text"), 0

    def music_info_pos(st, at):
        return music_info(st, at, renpy.music.get_pos(channel='music') or 0.0)

    def music_info_dur(st, at):
        return music_info(st, at, renpy.music.get_duration(channel='music') or 0.0)

screen music():
    predict False ## Avoid predicting this screen
    tag menu
    key "game_menu" action Return()

    style_prefix "music"   

    add "gui/music/background.png":
        xalign 0.55
        yalign 0.5

    window:
        background None
        padding (0,0,0,0)
        xanchor 0.0
        xpos 0.05
        yalign 0.5

        python:
            composer_entry = python_list()
            if mr.get_entry_idx() > -1:
                composer = musicroom_entries[mr.get_entry_idx()].artist
                composer_entry = composer_details[composer]

        hbox:
            spacing 40
            xpos 23
            frame:
                background "gui/music/outline.png"
                padding (0,0,0,0)
                xsize 285
                ysize 285

                button style "art":
                    xalign 0.5
                    yalign 0.5
                    if mr.get_entry_idx() == -1:
                        background "#000"
                    else:
                        background musicroom_entries[mr.get_entry_idx()].art

            vbox:
                if mr.get_entry_idx() == -1:
                    textbutton("No Song Playing") style "currentname"
                    textbutton("") style "currentcomposer" xpos 1
                else:
                    textbutton(musicroom_entries[mr.get_entry_idx()].name) style "currentname"
                    textbutton(musicroom_entries[mr.get_entry_idx()].artist) style "currentcomposer" xpos 1

                null height 21
                hbox:
                    xpos -6

                    for num, composer in enumerate(composer_entry):
                        if num > 0:
                            null width 40

                        if composer.twitter:
                            button:
                                background "gui/music/icon_twitter.png"
                                hover_background "gui/music/icon_twitter_hover.png"
                                xsize 40
                                ysize 40
                                action OpenURL(composer.twitter)

                        if composer.website:
                            button:
                                background "gui/music/icon_soundcloud.png"
                                hover_background "gui/music/icon_soundcloud_hover.png"
                                xsize 40
                                ysize 40
                                action OpenURL(composer.website)

                null height 22

                if mr.get_entry_idx()>=0:
                    if musicroom_entries[mr.get_entry_idx()].play_in_musicroom:
                        hbox:
                            xpos -6
                            spacing 10
                            button:
                                background "gui/music/icon_mute.png"
                                xsize 40
                                ysize 40
                                ypos -1
                            bar:
                                style "music_slider_2"
                                ysize 40
                                xsize 190
                                value Preference("music volume")
                            button:
                                ypos -1
                                background "gui/music/icon_volume.png"
                                xsize 40
                                ysize 40
                    else:
                        text "{size=-7}This song can't be played in the music room.{/size}"

                if musicroom_entries[mr.get_entry_idx()].unused:
                    text "{size=-5}{color=#f00}UNUSED{/color}{/size}" yoffset 10
                if musicroom_entries[mr.get_entry_idx()].exclusive:
                    text "{size=-5}{color=#fff}PC Exclusive{/color}{/size}" yoffset 10

    if mr.get_entry_idx()>=0 and musicroom_entries[mr.get_entry_idx()].play_in_musicroom:
        vbox:
            xanchor 0.0
            xpos 0.05
            yalign 0.838

            hbox:
                spacing 25
                ypos -17
                xpos 26
                window:
                    style "barinformation"
                    add DynamicDisplayable(music_info_pos)

                bar:
                    style "music_slider"
                    value AudioPositionValue2(channel='music', update_interval=0.1)
                    xsize 585
                    ysize 40

                window:
                    style "barinformation"
                    add DynamicDisplayable(music_info_dur)

            hbox:
                xalign 1.08

                button:
                    background "gui/music/icon_previous.png"
                    selected_background "gui/music/icon_previous_hover.png"
                    hover_background "gui/music/icon_previous_hover.png"
                    xsize 40
                    ysize 40
                    action MusicRoomPrev()
                button:
                    if renpy.music.get_pause():
                        background "gui/music/icon_play.png"
                        hover_background "gui/music/icon_play_hover.png"
                    else:
                        background "gui/music/icon_pause.png"
                        hover_background "gui/music/icon_pause_hover.png"
                    xsize 40
                    ysize 40
                    action PauseAudio("music", value="toggle")
                button:
                    background "gui/music/icon_stop.png"
                    hover_background "gui/music/icon_stop_hover.png"
                    xsize 40
                    ysize 40
                    action Function(mr.stop)
                button:
                    background "gui/music/icon_skip.png"
                    selected_background "gui/music/icon_play.png"
                    hover_background "gui/music/icon_skip_hover.png"
                    xsize 40
                    ysize 40
                    action mr.Next()
                button:
                    background "gui/music/icon_shuffle.png"
                    selected_background "gui/music/icon_shuffle_hover.png"
                    hover_background "gui/music/icon_shuffle_hover.png"
                    xsize 40
                    ysize 40
                    action mr.ToggleShuffle()
                button:
                    background "gui/music/icon_loop.png"
                    selected_background "gui/music/icon_loop_hover.png"
                    hover_background "gui/music/icon_loop_hover.png"
                    xsize 40
                    ysize 40
                    action mr.ToggleSingleTrack()

    frame:
        style "music_frame"
        xsize 355
        ysize 442
        xanchor 1.0
        xpos 0.93
        yalign 0.695

        viewport:
            yinitial 0.0
            scrollbars "vertical"
            mousewheel True

            vbox:

                for num, entry in enumerate(musicroom_entries):
                    button:
                        style "songname"
                        action MusicRoomPlayEntry(mr, entry)
                        if renpy.music.get_playing():
                            selected entry.fname_noloop in renpy.music.get_playing()

                        vbox:
                            text "{:02d}. {:s}".format(num+1, entry.name):
                                style "songname_text"
                            text entry.artist.upper():
                                style "songname_text"
                                size 11
                                xoffset 1

                    if num != len(musicroom_entries)-1:
                        button style "line"

    button:
        style "return_to_title_button"
        xalign 0.93
        yalign 0.9939
        action Return()

style music_frame:
    padding gui.frame_borders.padding
    left_padding 0
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)

style music_slider:
    right_bar Frame("gui/slider/music_bar.png")
    left_bar Frame("gui/slider/music_bar_left.png")
    thumb "gui/slider/music_thumb.png" yalign 0.5
    thumb_offset 20

style music_slider_2:
    right_bar Frame("gui/slider/music_bar_2.png")
    thumb "gui/slider/music_thumb_2.png" 
    hover_thumb "gui/slider/music_thumb_2_hover.png" 
    hover_left_bar Frame("gui/slider/music_bar_2_left_hover.png")
    thumb_offset 20
    left_bar Frame("gui/slider/music_bar_2_left.png")
    yalign 0.5

style barinformation:
    background None
    padding (0,0,0,0)
    xsize 33
    ysize 40
    xanchor 0
    yalign 0.5

style barinformation_text:
    font "fonts/Cabin-Bold2.ttf"
    size 13
    yalign 0.5
    color "#FFF"
    ypos 18

style return_to_title_button:
    hover_sound "sounds/sys2.wav"
    background "gui/music/button.png"
    hover_background "gui/music/button_hover.png"
    activate_sound "sounds/sys3.wav"
    padding (0, 0, 0, 0)
    xsize 300
    ysize 37

style songname:
    background None
    selected_background "gui/music/flower.png"
    padding (40, 15, 15, 14)
    xsize 340

style songname_text:
    hover_color "#c4c4c4"
    selected_color "#30E6FF"
    color "#FFF"    
    size 18
    font "fonts/Acumin-BdPro.otf"
    yalign 0.5   

style currentname:
    background None

style currentname_text:
    font "fonts/Cabin-SemiBold.ttf"
    size 33
    color "#FFF"

style currentcomposer:
    background None

style currentcomposer_text:
    font "fonts/Cabin-SemiBold.ttf"
    size 24
    color "#33cbff"  

style line:
    left_margin 40
    right_margin 40
    xminimum 50
    ysize 1
    xpos 0
    xsize 2733
    background "#000"

style space:
    xpos 15
    xsize 261
    ysize 11
    background None

style icon:
    xsize 40
    ysize 40

style art:
    xsize 273
    ysize 273
