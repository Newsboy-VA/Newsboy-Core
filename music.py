#!/usr/bin/python3
import sys, getopt
import vlc
import pafy
import time
from random import randint
#
# phrase_dict = {
#     ('play', 'music'): play_music,
#     ('stop', 'music'): stop_music,
# }


music = {   'jazz'          : "https://www.youtube.com/watch?v=neV3EPgvZ3g",
            'christian'     : "https://www.youtube.com/watch?v=qCZAynQU_-8",
            'programming'   : "https://www.youtube.com/watch?v=0r6C3z3TEKw",
            'acoustic'      : "https://www.youtube.com/watch?v=q7sZsoLujs0"
        }

class VLC_player(object):
    """docstring for VLC_player."""
    def __init__(self):
        super(VLC_player, self).__init__()
        self.i      = vlc.Instance()
        self.player = self.i.media_player_new()
        self.player.audio_set_volume(100)



    def play(self, media=None, randomPos=True):
        if media is not None:                    # <----------------- please check this
            self.add_media(media)

        if randomPos is True:
            pos = randint(0, 9)
            print(pos)
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

def main(argv):
    vlc_player = VLC_player();

    try:
        opts, args = getopt.getopt(argv,"hg:",["genre="])
    except getopt.GetoptError:
        print("music.py -g <genre>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("music.py -g <genre>")
            sys.exit()
        elif opt in ("-g", "--genre"):
            print(arg)
            url = music[arg]

            vlc_player.play(url)
            time.sleep(1)

    while vlc_player.player.is_playing():
        #do nothing
        pass

    print("done")


if __name__ == '__main__':
    main(sys.argv[1:])
