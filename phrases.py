import tts
from time import strftime
from num2words import num2words
import random
import music
import feedparser


voice = tts.ESpeak()
vlc_player = music.VLC_player()

def hello(cs):
    voice.say("Hello.")

def morning(cs):
    voice.say("Good morning.")

def how_are_you(cs):
    voice.say("I don\'t have feelings.")

def goodbye(cs):
    voice.say(random.choice([
        "Farewell.",
        "Goodbye.",
        "See you later.",
        "Ta ta for now",
        "I hope you come back soon.",
    ]))

def thanks(cs):
    voice.say("You're welcome.")

def current_time(cs):
    voice.say(strftime("It is %I:%M %P"))

def current_date(cs):
    voice.say("It is the {} of {}".format(num2words(int(strftime("%d")), ordinal=True), strftime("%B")))

def current_day(cs):
    voice.say(strftime("It is %A"))

def current_weather(cs):
    weather_data = feedparser.parse("http://www.rssweather.com/wx/nz/christchurch/rss.php")
    weather_summary = weather_data['entries'][0]['summary_detail']['value']
    voice.say(weather_summary)

def play_music(cs):
    voice.say("What kind of music?")
    cs.resume()
    while not cs.new_data_available():
        pass
    speech_data = cs.get_latest_speech_data()
    print(speech_data)
    if speech_data in music.music.keys():
        vlc_player.play(music.music[speech_data])
    elif speech_data in ['anything', 'any']:
        choice = random.choice(list(music.music.keys()))
        voice.say("I'm going to play some {} music for you.".format(choice))
        vlc_player.play(music.music[choice])


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
    ('date'): current_date,
    ('day'): current_day,
    ('weather'):  current_weather,

    ('play', 'music'): play_music,
}
