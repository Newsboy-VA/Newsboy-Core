#!/usr/bin/env python3


try:
    from .base_io import BaseIO
except SystemError:
    from base_io import BaseIO

from os import environ, path
import subprocess
import threading
import pyaudio
from pocketsphinx.pocketsphinx import Decoder
import speech_recognition


class SpeechRecognition(object):
    ''' A class which performs speech-to-text using sphinx or google '''
    def __init__(self, local=True):
        self.recognizer = speech_recognition.Recognizer()
        # self.recognizer.dynamic_energy_threshold = True
        if local:
            self.decode = self.recognizer.recognize_sphinx
        else:
            self.decode = self.recognizer.recognize_google

    def listen(self, keyword_entries=None):
        ''' Send request to the speech recognition server '''
        with speech_recognition.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            # print("Say something!")
            audio = self.recognizer.listen(source)

        try:
            return self.decode(audio)
            # return self.decode(audio, keyword_entries=keywords, show_all=True)

        except speech_recognition.UnknownValueError:
            print("Unable to understand audio")
        except speech_recognition.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return ""



class ContinousSpeech(object):
    ''' A class which continuously performs speech-to-text '''
    def __init__(self, model_dir, hmm, lm, dictionary, logfn='/dev/null', input_source_index=1, wait_to_resume=False):
        self.model_dir = model_dir
        #self.data_dir = data_dir
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

        decoder = Decoder(config)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        # rate=44100
                        rate=16000,
                        input=True,
                        output=False,
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
                                # print("waiting")
                                self.wait_to_resume_lock.acquire()
                                # print("resuming")

                        if self.wait_to_resume:
                            stream.start_stream()
                        decoder.start_utt()
            else:
                break
        decoder.end_utt()

    def listen(self, local=True):
        ''' Starts streaming. Pauses until self.resume has been called '''

        config = Decoder.default_config()
        config.set_string('-hmm', path.join(self.model_dir, self.hmm))
        config.set_string('-lm', path.join(self.model_dir, self.lm))
        config.set_string('-dict', path.join(self.model_dir, self.dictionary))
        config.set_string('-logfn', self.logfn)

        decoder = Decoder(config)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        # rate=44100
                        rate=16000,
                        input=True,
                        output=False,
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
                            return phrase

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
        subprocess.run(['espeak',
                        '-v', self.v,
                        '-s'+str(self.s + speed_adjust),
                        '-p'+str(self.p + pitch_adjust),
                        '-a'+str(self.a + amplitude_adjust),
                        "\"{}\"".format(text)
                        ])


class SpeechIO(BaseIO):
    """docstring for SpeechIO."""

    def __init__(self,
                 model_dir="./models",
                 hmm="en-us/en-us",
                 lm="en-us/en-us.lm.bin",
                 dictionary="en-us/cmudict-en-us.dict",
                 input_source_index=0):

        super(self.__class__, self).__init__()

        # Input
        # self.stt = ContinousSpeech(model_dir=model_dir,
        #                            hmm=hmm,
        #                            lm=lm,
        #                            dictionary=dictionary,
        #                            input_source_index=input_source_index,
        #                            wait_to_resume=True)

        self.stt = SpeechRecognition(local=False)
        # Output
        self.tts = ESpeak()

    def write(self, text):
        self.tts.say(text)

    def read(self, blocking=True):
        # while not self.stt.data_available():
        #     if blocking is False:
        #         return None

        # user_response = self.stt.get_latest_speech_data()
        user_response = self.stt.listen()

        return user_response

    def resume_reading(self):
        pass  # self.stt.resume()

    def stop_reading(self):
        ''' Stop reading. Note that this cannot be undone '''
        # self.stt.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Listen and repear audio input.')
    parser.add_argument('--model-dir', type=str, default="./models")
    parser.add_argument('-hmm', type=str, default="en-us/cmusphinx-en-us-5.2")
    parser.add_argument('-lm', type=str, default="en-us/en-70k-0.2-pruned.lm")
    parser.add_argument('-dictionary', type=str,
                        default="en-us/cmudict-en-us.dict")
    parser.add_argument('-logfn', type=str, default="/dev/null")
    parser.add_argument('--input-source-index', type=int, default=0)

    args = parser.parse_args()

    speech_io = SpeechIO(model_dir=args.model_dir,
                         hmm=args.hmm,
                         lm=args.lm,
                         dictionary=args.dictionary,
                         input_source_index=args.input_source_index,
                         )

    while True:
        text = speech_io.read()
        print(text)
        # speech_io.write(text)
        speech_io.resume_reading()

    speech_io.stop_reading()
