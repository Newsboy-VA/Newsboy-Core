#!/usr/bin/env python3


from os import environ, path, system

import threading
import pyaudio
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


class ContinousSpeech(object):
    ''' A class which transcribes what it hears '''
    def __init__(self, model_dir, data_dir, hmm, lm, dictionary, logfn='/dev/null', input_source_index=1):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.hmm = hmm
        self.lm = lm
        self.dictionary = dictionary
        self.logfn = logfn
        self.input_source_index = input_source_index

        self.all_speech_data = []

        self.cst = threading.Thread(target=self.start_listening, name="ContinuousSpeechThread")
        self.cst.start()

    def start_listening(self, wait_to_resume=False):
        ''' Starts streaming. Pauses until self.resume has been called '''

        config = Decoder.default_config()
        config.set_string('-hmm', path.join(self.model_dir, self.hmm))
        config.set_string('-lm', path.join(self.model_dir, self.lm))
        config.set_string('-dict', path.join(self.model_dir, self.dictionary))
        config.set_string('-logfn', self.logfn)
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
                        input_device_index=self.input_source_index,
                        frames_per_buffer=1024)
        stream.start_stream()

        in_speech_bf = False
        decoder.start_utt()

        while True:
            buf = stream.read(1024, exception_on_overflow=False)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        if wait_to_resume:
                            stream.stop_stream()
                        phrase = decoder.hyp().hypstr
                        print("\"{}\"".format(phrase))

                        if phrase != "":
                            self.all_speech_data.append(phrase)
        #                system("espeak -v mb-en1 -s 110 -p 1 \"{}\"".format(phrase))
                        if wait_to_resume:
                            #input()
                            stream.start_stream()
                        decoder.start_utt()
            else:
                break
        decoder.end_utt()

    def get_all_speech_data(self):
        ''' Retrieves all the recorded speech '''
        all_data = self.all_speech_data
        self.all_data.clear()
        return all_data

    def get_latest_speech_data(self):
        ''' Retrieves the latest recorded speech '''
        return self.all_speech_data.pop(-1)

    def resume(self):
        ''' Resume getting speech data. Only used if wait_to_resume==True '''



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Listen for audio input.')
    parser.add_argument('--model-dir', type=str, default="/home/newsboy/simple_response_network/pocketsphinx/model")
    parser.add_argument('--data-dir', type=str, default="/home/newsboy/simple_response_network/sphinx-base/test/data")
    parser.add_argument('-hmm', type=str, default="en-us/en-us")
    parser.add_argument('-lm', type=str, default="en-us/en-us.lm.bin")
    parser.add_argument('-dictionary', type=str, default="en-us/cmudict-en-us-short.dict")
    parser.add_argument('-logfn', type=str, default="/dev/null")
    #parser.add_argument('-ack', default=False, action='store_true')
    parser.add_argument('--input-source-index', type=int, default=1)

    args = parser.parse_args()

    cs = ContinousSpeech(model_dir=args.model_dir,
                         data_dir=args.data_dir,
                         hmm=args.hmm,
                         lm=args.lm,
                         dictionary=args.dictionary,
                         logfn=args.logfn,
                         input_source_index=args.input_source_index)

    cs.start()
