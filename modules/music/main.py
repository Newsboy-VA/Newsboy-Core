#!/usr/bin/env python3

import logging
import os.path
import inspect
import json
import vlc
import pafy
import time
import random


import sys
sys.path.append('base_classes')
from module_base import VAModuleBase


class MusicModule(VAModuleBase):
    def __init__(self):
        module_path = os.path.dirname(inspect.getfile(inspect.currentframe()))

        super().__init__(module_path)
        self.vlc_player = VLC_Player()
        self.music_sources = {
            'jazz'          : "https://www.youtube.com/watch?v=neV3EPgvZ3g",
            'christian'     : "https://www.youtube.com/watch?v=qCZAynQU_-8",
            'programming'   : "https://www.youtube.com/watch?v=0r6C3z3TEKw",
            'acoustic'      : "https://www.youtube.com/watch?v=q7sZsoLujs0"
        }


    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def play_music(self, genre):
        if genre in ['anything', 'any']:
            genre = random.choice(list(self.music_sources))
            self.send_to_client('main', "I'm going to play some {} music for you.".format(genre))
            self.vlc_player.play(self.music_sources[genre])
        else:
            self.send_to_client('main', "Playing some {}".format(genre))
            self.vlc_player.play(self.music_sources[genre])

    def stop_music(self):
        self.vlc_player.stop()
        return "Music stopped"



class VLC_Player(object):
    """docstring for VLC_Player."""
    def __init__(self):
        super(VLC_Player, self).__init__()
        self.i      = vlc.Instance()
        self.player = self.i.media_player_new()
        self.player.audio_set_volume(100)



    def play(self, media=None, randomPos=True):
        if media is not None:                    # <----------------- please check this
            self.add_media(media)

        if randomPos is True:
            pos = random.randint(0, 9)
            self.player.set_position(pos)

        self.player.play()

    def stop(self):
        if self.player.is_playing() == 1:
            self.player.stop()


    # def next(self):
        # if self.player.next_available():

    def add_media(self, media):
        print(media)
        audio = pafy.new(media).getbestaudio()
        print(audio)
        url = audio.url
        print(url)
        self.player.set_media(self.i.media_new(url))

        # media=i.media_new(video)
        # media_list = i.media_list_new([self.i.media_new(video)]) #A list of one movie
        #
        # self.list_player =  self.i.media_list_player_new()

        # #Create a new MediaListPlayer instance and associate the player and playlist with it
        # list_player.set_media_player(player)
        # list_player.set_media_list(media_list)

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)



if __name__ == "__main__":
    with MusicModule() as module:
        pass
