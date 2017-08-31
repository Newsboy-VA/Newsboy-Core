#!/usr/bin/env python3


from os import environ, path, system

import threading
import argparse
import pyaudio
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *



parser = argparse.ArgumentParser(description='Listen for audio input.')
parser.add_argument('--model-dir', type=str, default="/home/newsboy/simple_response_network/pocketsphinx/model")
parser.add_argument('--data-dir', type=str, default="/home/newsboy/simple_response_network/sphinx-base/test/data")
parser.add_argument('-hmm', type=str, default="en-us/en-us")
parser.add_argument('-lm', type=str, default="en-us/en-us.lm.bin")
parser.add_argument('-dict', type=str, default="en-us/cmudict-en-us-short.dict")
parser.add_argument('-logfn', type=str, default="/dev/null")
parser.add_argument('-ack', default=False, action='store_true')
#parser.add_argument('--input-source', type=int, default=0)

args = parser.parse_args()


config = Decoder.default_config()
config.set_string('-hmm', path.join(args.model_dir, args.hmm))
config.set_string('-lm', path.join(args.model_dir, args.lm))
config.set_string('-dict', path.join(args.model_dir, args.dict))
config.set_string('-logfn', args.logfn)
#config.set_string('-hmm', path.join(args.model_dir, "en-us/en-us"))
#config.set_string('-lm', path.join(args.model_dir, "en-us/en-us.lm.bin"))
#config.set_string('-dict', path.join(args.model_dir, "en-us/cmudict-en-us-short.dict"))
#config.set_string('-logfn', "/dev/null")
decoder = Decoder(config)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024)
stream.start_stream()

in_speech_bf = False
decoder.start_utt()
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
        if decoder.get_in_speech() != in_speech_bf:
            in_speech_bf = decoder.get_in_speech()
            if not in_speech_bf:
                decoder.end_utt()
                if args.ack:
                    stream.stop_stream()
                phrase = decoder.hyp().hypstr
                print(phrase)
#                system("espeak -v mb-en1 -s 110 -p 1 \"{}\"".format(phrase))
                if args.ack:
                    input()
                    stream.start_stream()
                decoder.start_utt()
    else:
        break
decoder.end_utt()
