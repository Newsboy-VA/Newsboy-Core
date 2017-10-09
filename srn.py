#!/usr/bin/env python3

from user_io.text_io import TextIO
from user_io.speech_io import SpeechIO
from question import Question

from time import strftime
# from num2words import num2words
import random
import music
import feedparser




vlc_player = music.VLC_player()





def hello(user_io):
    user_io.write("Hello.")

def morning(user_io):
    user_io.write("Good morning.")

def how_are_you(user_io):
    user_io.write("I don\'t have feelings.")

def goodbye(user_io):
    user_io.write(random.choice([
        "Farewell.",
        "Goodbye.",
        "See you later.",
        "Ta ta for now",
        "I hope you come back soon.",
    ]))

def thanks(user_io):
    user_io.write("You're welcome.")

def current_time(user_io):
    user_io.write(strftime("It is %I:%M %P"))

# def current_date(user_io):
#     user_io.write("It is the {} of {}".format(num2words(int(strftime("%d")), ordinal=True), strftime("%B")))

def current_day(user_io):
    user_io.write(strftime("It is %A"))

def current_weather(user_io):
    weather_data = feedparser.parse("http://www.rssweather.com/wx/nz/christchurch/rss.php")
    weather_summary = weather_data['entries'][0]['summary_detail']['value']
    user_io.write(weather_summary)

def play_music(user_io):
    data = Question(io=user_io).ask("What kind of music?")


    if data in music.music.keys():
        vlc_player.play(music.music[data])
    elif data in ['anything', 'any']:
        choice = random.choice(list(music.music.keys()))
        user_io.write("I'm going to play some {} music for you.".format(choice))
        vlc_player.play(music.music[choice])

def stop_music(user_io):
    vlc_player.stop()





phrase_dict = {
    ('hello'): hello,
    ('hi'): hello,
    ('morning'): morning,
    ('how', 'you'): how_are_you,
    ('good-bye'): goodbye,
    ('bye'): goodbye,
    ('thanks'): thanks,
    ('thankyou'): thanks,

    ('time'): current_time,
    # ('date'): current_date,
    ('day'): current_day,
    ('weather'):  current_weather,

    ('play', 'music'): play_music,
    ('stop', 'music'): stop_music,
}





def main():

    # text_io = TextIO()
    #
    # general_q = Question(phrase_dict=phrase_dict,io=text_io);
    # while True:
    #     general_q.ask("")



    import argparse

    parser = argparse.ArgumentParser(description='Listen and repeat audio input.')
    parser.add_argument('--model-dir', type=str, default="./models")
    #parser.add_argument('--data-dir', type=str, default="/home/newsboy/simple_user_network/sphinx-base/test/data")
    parser.add_argument('-hmm', type=str, default="en-us/cmusphinx-en-us-5.2")
    parser.add_argument('-lm', type=str, default="en-us/en-70k-0.2-pruned.lm")
    parser.add_argument('-dictionary', type=str, default="en-us/cmudict-en-us.dict")
    parser.add_argument('-logfn', type=str, default="/dev/null")
    parser.add_argument('--input-source-index', type=int, default=0)
    #parser.add_argument('--wait-to-resume', default=False, action="store_true")
    #parser.add_argument('--repeat', default=False, action="store_true")

    args = parser.parse_args()

    speech_io = SpeechIO( model_dir=args.model_dir,
                        #data_dir=args.data_dir,
                        hmm=args.hmm,
                        lm=args.lm,
                        dictionary=args.dictionary,
                        input_source_index=args.input_source_index,
                        )



    general_q = Question(phrase_dict=phrase_dict,io=speech_io);
    while True:
        general_q.ask("")


    speech_io.stop_reading()


if __name__=="__main__":
    main()
