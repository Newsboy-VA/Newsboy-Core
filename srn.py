#!/usr/bin/env python3


import stt
from phrases import phrase_dict


cs = stt.ContinousSpeech(model_dir="/home/newsboy/simple_response_network/pocketsphinx/model",
                         data_dir="/home/newsboy/simple_response_network/sphinx-base/test/data",
                         hmm="en-us/en-us",
                         lm="en-us/en-us.lm.bin",
                         dictionary="en-us/cmudict-en-us-short.dict",
                         wait_to_resume=True)

def run(speech_data):

    phrase_matches = []

    for phrase in phrase_dict.keys():
        is_match = True

        if isinstance(phrase, tuple):
            for word in phrase:
                if word not in speech_data:
                    is_match = False
        else:
            if phrase not in speech_data:
                is_match = False

        if is_match:
            phrase_matches.append(phrase)

    if phrase_matches != []:
        phrase_dict[phrase_matches[-1]](cs)


def main():

    while True:
        if cs.new_data_available():
            speech_data = cs.get_latest_speech_data()
            print(speech_data)
            run(speech_data)
            cs.resume()


if __name__=="__main__":
    main()
