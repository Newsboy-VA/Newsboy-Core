#!/usr/bin/env python3

import subprocess

class ESpeak(object):
    ''' A class which performs text-to-speech using espeak '''
    def __init__(self, voice='mb-en1', speed=110, pitch=1, amplitude=100):
        self.v = voice
        self.s = speed
        self.p = pitch
        self.a = amplitude

    def say(self, text, speed_adjust=0, pitch_adjust=0, amplitude_adjust=0):
        ''' Say the text '''
        # print("Saying \"{}\"".format(text))
        # print("Running " + str(['espeak',
                        # '-v', str(self.v),
                        # '-s', str(self.s + speed_adjust),
                        # '-p', str(self.p + pitch_adjust),
                        # '-a', str(self.a + amplitude_adjust),
                        # "\"{}\"".format(text)
                        # ]))

        subprocess.run(['espeak',
                        '-v', self.v,
                        '-s'+str(self.s + speed_adjust),
                        '-p'+str(self.p + pitch_adjust),
                        '-a'+str(self.a + amplitude_adjust),
                        "\"{}\"".format(text)
                        ])

if __name__ == "__main__":
    voice = ESpeak()
    voice.say("Hello")
