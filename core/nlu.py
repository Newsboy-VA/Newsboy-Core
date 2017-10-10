



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

full_intents_dict = {}


def populate_intent_dict():
    for module in modules:
        for intent in module.intents:
            full_intents_dict[ tuple( intent['name'], *intent['synonyms']) ] =  intent['parameters']

def is_intent(word):
    if word in

def deconstruct(client_response):
    response_keywords = []
    for word in client_response:
        if word is an intent:
            response_keywords.append(word)
        else if word is an entity:
            response_keywords.append(word)

    return response_keywords



def get_intent(user_response):
    phrase_matches = []

    for phrase in self.phrase_dict.keys():
        is_match = True

        if isinstance(phrase, tuple):
            for word in phrase:
                if word not in user_response:
                    is_match = False
        else:
            if phrase not in user_response:
                is_match = False

        if is_match:
            phrase_matches.append(phrase)

    if phrase_matches != []:
        print(phrase_dict[phrase_matches[-1]])

        return phrase_dict[phrase_matches[-1]]
