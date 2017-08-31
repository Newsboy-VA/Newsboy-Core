#!/usr/bin/env python3

import stt

from os import environ, path

import subprocess
import threading
import pyaudio
from pocketsphinx.pocketsphinx import Decoder
#from sphinxbase.sphinxbase import *





class ContinousSpeech(object):
    ''' A class which continuously performs speech-to-text '''
    def __init__(self, model_dir, data_dir, hmm, lm, dictionary, logfn='/dev/null', input_source_index=1, wait_to_resume=False):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.hmm = hmm
        self.lm = lm
        self.dictionary = dictionary
        self.logfn = logfn
        self.input_source_index = input_source_index
        self.wait_to_resume = wait_to_resume

        self.all_speech_data = []

        self.is_running = True
        self.wait_to_resume_lock = threading.Lock()
        self.cst = threading.Thread(target=self.start_listening, name="ContinuousSpeechThread")
        self.cst.start()

    def start_listening(self):
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

        self.wait_to_resume_lock.acquire()

        while self.is_running:
            buf = stream.read(1024, exception_on_overflow=False)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        if self.wait_to_resume:
                            stream.stop_stream()

                        phrase = decoder.hyp().hypstr
                        if phrase != "":
                            self.all_speech_data.append(phrase)

                            if self.wait_to_resume:
                                #print("waiting")
                                self.wait_to_resume_lock.acquire()
                                #print("resuming")

                        if self.wait_to_resume:
                            stream.start_stream()
                        decoder.start_utt()
            else:
                break
        decoder.end_utt()

    def data_available(self):
        ''' Returns whether there is data available '''
        return self.all_speech_data != []

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
        self.wait_to_resume_lock.release()

    def stop(self):
        ''' Stop streaming. Note that this cannot be undone '''
        self.is_running = False
        self.cst.join()


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


class Speech(IO):
    """docstring for Speech."""


    def __init__(self, model_dir="/home/newsboy/simple_response_network/pocketsphinx/model",
                       data_dir="/home/newsboy/simple_response_network/sphinx-base/test/data",
                       hmm="en-us/en-us",
                       lm="en-us/en-us.lm.bin",
                       dictionary="en-us/cmudict-en-us-short.dict",
                       input_source_index=1):
        super(self.__class__, self).__init__()

        # Input
        self.stt = ContinousSpeech( model_dir=model_dir,
                                    data_dir=data_dir,
                                    hmm=hmm,
                                    lm=lm,
                                    dictionary=dictionary,
                                    input_source_index=input_source_index,
                                    wait_to_resume=True)
        # Output
        self.tts = ESpeak()


    def write(self):
        self.tts.say(question_str)

    def read(self, blocking=True):
        while not self.stt.data_available():              # <------- Maybe have time out and also only accept expected response
            if blocking is False:
                return None

        user_response = self.stt.get_latest_speech_data()


        return user_response

    def resume_reading(self):
        self.stt.resume()

    def stop_reading(self):
        ''' Stop reading. Note that this cannot be undone '''
        self.stt.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Listen and repear audio input.')
    parser.add_argument('--model-dir', type=str, default="/home/newsboy/simple_response_network/pocketsphinx/model")
    parser.add_argument('--data-dir', type=str, default="/home/newsboy/simple_response_network/sphinx-base/test/data")
    parser.add_argument('-hmm', type=str, default="en-us/en-us")
    parser.add_argument('-lm', type=str, default="en-us/en-us.lm.bin")
    parser.add_argument('-dictionary', type=str, default="en-us/cmudict-en-us-short.dict")
    parser.add_argument('-logfn', type=str, default="/dev/null")
    parser.add_argument('--input-source-index', type=int, default=1)
    #parser.add_argument('--wait-to-resume', default=False, action="store_true")
    #parser.add_argument('--repeat', default=False, action="store_true")

    args = parser.parse_args()

    speech_io = Speech( model_dir=args.model_dir,
                        data_dir=args.data_dir,
                        hmm=args.hmm,
                        lm=args.lm,
                        dictionary=args.dictionary,
                        input_source_index=args.input_source_index,
                        )

    while True:
        text = speech_io.read()
        print(text)
        speech_io.write(text)
        speech_io.resume_reading()

    speech_io.stop_reading()
