
import os
import os.path
import json
import re


class NLU(object):
    '''  '''
    def __init__(self, module_dir="../modules"):
        self.module_dir = module_dir
        self.intent_list = []
        self.update_intent_list()

    def update_intent_list(self):
        ''' Iterates through modules and finds the intents '''
        for listing in os.listdir(self.module_dir):
            module = os.path.join(self.module_dir, listing)
            if os.path.isdir(module):
                # print(module)
                entities_file = open(os.path.join(module, "entities.json"))
                entities_json = json.load(entities_file)['entities']
                entities_file.close()
                # print(entities_json)
                intents_file = open(os.path.join(module, "intents.json"))
                intents_json = json.load(intents_file)['intents']
                intents_file.close()
                # print(intents_json)
                for intent_dict in intents_json:
                    intent_ob = Intent(intent_dict, entities_json)
                    self.intent_list.append(intent_ob)

    def find_intent(self, phrase):
        ''' Returns a list of matching intents '''
        matching_intents = []
        for intent in self.intent_list:
            if intent.intent_match(phrase):
                matching_intents.append(intent)

        return matching_intents


class Intent(object):
    '''  '''
    def __init__(self, intent_json, entities_json):
        self.name = intent_json['name']
        self.synonyms = intent_json['synonyms']
        self.callback = intent_json['function']
        self.arguments = dict()
        for intent_arg in intent_json['arguments']:
            for entity in entities_json:
                if entity['name'] == intent_arg:
                    self.arguments[intent_arg] = entity['parameters']

        self.regex = self.generate_regex()

    def generate_regex(self):
        ''' Generates a pattern which matches on any argument '''
        pattern = "\\b(?P<intent>{}".format(self.name)
        for syn in self.synonyms:
            pattern += "|{}".format(syn)
        pattern += ")\\b"

        for arg, parameters in self.arguments.items():
            pattern += "\\b|\\b(?P<{}>{}".format(arg, parameters[0])
            for param in parameters[1:]:
                pattern += "|{}".format(param)
            pattern += ")\\b"

        return re.compile(pattern, re.IGNORECASE)

    def full_match(self, phrase):
        ''' Returns True if the word_list fills all the arguments '''
        match = self.regex.search(phrase)
        if match is None:
            return False
        return None not in match_dict.values()

    def intent_match(self, phrase):
        ''' Returns True if the word_list contains the intent '''
        match = self.regex.search(phrase)
        if match is None:
            return False
        match_dict = match.groupdict()
        return match_dict['intent'] is not None

    def list_missing_arguments(self, phrase):
        ''' Returns a list of missing arguments '''
        missing_arguments = []
        match = self.regex.search(phrase)
        if match is None:
            return self.arguments.keys()

        for (arg, parameter) in match_dict.items():
            if not arg == 'intent':
                if parameter is None:
                    missing_arguments.append(arg)

        return missing_arguments

    def __repr__(self):
        string_representation = "{}(".format(self.callback)
        for arg in self.arguments.keys():
            string_representation += "{}, ".format(arg)
        if len(self.arguments) != 0:
            string_representation = string_representation[:-2]
        string_representation += ")"

        return string_representation


nlu = NLU()
print(nlu.find_intent("Hello"))
print(nlu.find_intent("What's the time"))
print(nlu.find_intent("How are you today?"))
print(nlu.find_intent("Can you tell me the time?"))
print(nlu.find_intent("set timer for ten minutes"))
print(nlu.find_intent("set timer for ten"))

# def deconstruct(client_response):
#     response_keywords = []
#     for word in client_response:
#         if word is an_intent:
#             response_keywords.append(word)
#         else if word is an entity:
#             response_keywords.append(word)
#
#     return response_keywords
#
# def is_intent(word):
#     if word in


# def get_intent(user_response):
#     phrase_matches = []
#
#     for phrase in self.phrase_dict.keys():
#         is_match = True
#
#         if isinstance(phrase, tuple):
#             for word in phrase:
#                 if word not in user_response:
#                     is_match = False
#         else:
#             if phrase not in user_response:
#                 is_match = False
#
#         if is_match:
#             phrase_matches.append(phrase)
#
#     if phrase_matches != []:
#         print(phrase_dict[phrase_matches[-1]])
#
#         return phrase_dict[phrase_matches[-1]]
#

# phrase_dict = {
#     ('hello'): hello,
#     ('hi'): hello,
#     ('morning'): morning,
#     ('how', 'you'): how_are_you,
#     ('good-bye'): goodbye,
#     ('bye'): goodbye,
#     ('thanks'): thanks,
#     ('thankyou'): thanks,
#
#     ('time'): current_time,
#     # ('date'): current_date,
#     ('day'): current_day,
#     ('weather'):  current_weather,
#
#     ('play', 'music'): play_music,
#     ('stop', 'music'): stop_music,
# }
#
# full_intents_dict = {}
#
#
# def populate_intent_dict():
#     for module in modules:
#         for intent in module.intents:
#             full_intents_dict[ tuple( intent['name'], *intent['synonyms'])] =
#                 intent['parameters']


# class Entity(object):
#     def __init__(self, entity_json):
#         self.name = entity_json['name']
#         self.parameters = entity_json['parameters']
