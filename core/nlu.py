
import os
import os.path
import json
import re

import sys
sys.path.append('base_classes')
from action_base import ActionBase

class NLU(object):
    ''' A class for performing basic Natural Language Understanding '''
    def __init__(self, module_dir="modules"):
        self.module_dir = module_dir
        self.available_intent_list = []
        self.update_available_intent_list()

    def update_available_intent_list(self):
        ''' Iterates through modules and finds the intents '''
        for listing in os.listdir(self.module_dir):
            module = os.path.join(self.module_dir, listing)
            if os.path.isdir(module):
                # print(module)
                entities_file = open(os.path.join(module, "entities.json"))
                entities_json = json.load(entities_file)['entities']
                entities_file.close()
                # print(entities_json)
                intents_file = open(os.path.join(module, "actions.json"))
                intents_json = json.load(intents_file)['actions']
                intents_file.close()
                # print(intents_json)
                for intent_dict in intents_json:
                    intent_matcher = IntentMatcher(intent_dict)
                    intent_matcher.generate_regex(entities_json)
                    self.available_intent_list.append(intent_matcher)

    def find_intents_in_phrase(self, phrase):
        ''' Returns a list of matching intents '''
        matching_intents = []
        for intent_matcher in self.available_intent_list:
            if intent_matcher.is_intent_match(phrase):
                arguments_in_phrase = intent_matcher.find_all_arguments(phrase)
                intent = Intent({'function': intent_matcher['function'],
                                 'arguments': arguments_in_phrase})
                matching_intents.append(intent)

        return matching_intents

    def find_args_for_intent(self, intent_function, phrase):
        ''' Returns a list of arguments found in the phrase to the given intent '''
        for intent_matcher in self.available_intent_list:
            if intent_matcher['function'] == intent_function:
                return intent_matcher.find_all_arguments(phrase)


class Intent(ActionBase):
    ''' A class to store intent parameters '''
    def is_full(self):
        ''' Returns True if all arguments have a value '''
        # print(self['arguments'].values())
        if None in self['arguments'].values():
            return False
        return True


class IntentMatcher(ActionBase):
    ''' A class to find arguments for a given intent '''
    def __init__(self, *args):
        super().__init__(*args)
        assert(isinstance(self['name'], str))
        if 'synonyms' not in self:
            self['synonyms'] = []
        assert(isinstance(self['synonyms'], list))

    def generate_regex(self, entities_json):
        ''' Generates all the regular expressions '''
        # print(self)
        self.intent_regex = self.generate_intent_regex()
        self.argument_regex_dict = \
            self.generate_argument_regex_dict(entities_json)

    def generate_intent_regex(self):
        ''' Generates a regular expression which matches the name/synonyms '''

        pattern = "\\b("
        for word in [self['name'], *self['synonyms']]:
            pattern += "{}|".format(word)
        pattern = pattern[:-1]
        pattern += ")\\b"

        return re.compile(pattern, re.IGNORECASE)

    def generate_argument_regex_dict(self, entities_json):
        ''' Generates a dictionary of the form {"argument": regex} '''

        argument_dict = dict()

        for intent_arg in self['arguments']:
            if intent_arg == 'number':
                argument_dict[intent_arg] = \
                    self.generate_number_regex()
            for entity in entities_json:
                if entity['name'] == intent_arg:
                    if isinstance(entity['parameters'], dict):
                        entity_dict = entity['parameters']
                    else:
                        entity_dict = dict()
                        for parameter in entity['parameters']:
                            entity_dict[parameter] = [parameter]
                    argument_dict[intent_arg] = \
                        self.generate_argument_regex(entity_dict)

        return argument_dict

    def generate_argument_regex(self, entity_dict):
        ''' Generates a regular expression which matches the argument '''
        pattern = "\\b("

        for word, synonyms in entity_dict.items():
            pattern += "(?P<{}>".format(word.replace(" ", "_"))
            for synonym in synonyms:
                pattern += "{}|".format(synonym)
            pattern = pattern[:-1]
            pattern += ")|"
        pattern = pattern[:-1]
        pattern += ")\\b"

        return re.compile(pattern, re.IGNORECASE)

    def generate_number_regex(self):
        ''' Generates a regular expression which matches a number '''
        pattern = "\\b(?P<number>\\d+)\\b"

        return re.compile(pattern, re.IGNORECASE)

    def is_intent_match(self, phrase):
        ''' Returns True if the word_list contains the intent '''
        return self.intent_regex.search(phrase) is not None

    def is_full_match(self, phrase):
        ''' Returns True if the word_list fills all the arguments '''
        if not self.is_intent_match(phrase):
            return False
        if None in self.find_all_arguments(phrase).values():
            return False
        return True

    def find_argument(self, argument, phrase):
        ''' Returns the value of the given argument, None if not present '''
        match = self.argument_regex_dict[argument].search(phrase)
        if match is not None:
            match_dict = match.groupdict()
            if argument == 'number':
                return match_dict['number']

            else:
                for word, synonym in match_dict.items():
                    # NOTE: It may not behave as you want if there are more
                    # than one synonym in a phrase.
                    if synonym is not None:
                        return word
        return None

    # def match_arguments(self, phrase):
    #     ''' Identifies arguments in phrase and adds them to argument_dict '''
    #     self['arguments'].update(self.find_all_arguments(phrase))

    def find_all_arguments(self, phrase):
        ''' Returns a dictionary of arguments and their values '''
        all_arguments = dict()
        for argument in self.argument_regex_dict.keys():
            all_arguments[argument] = self.find_argument(argument, phrase)

        return all_arguments

    def find_missing_arguments(self, phrase):
        ''' Returns a list of missing arguments '''
        missing_arguments = []

        for argument, value in self.find_all_arguments(phrase).items():
            if value is None:
                missing_arguments.append(argument)

        return missing_arguments


# nlu = NLU("./modules")

if __name__ == "__main__":
    nlu = NLU()
    print(nlu.find_intents_in_phrase("Hello"))
    print(nlu.find_intents_in_phrase("What's the time"))
    print(nlu.find_intents_in_phrase("How are you today?"))
    print(nlu.find_intents_in_phrase("Can you tell me the time?"))
    print(nlu.find_intents_in_phrase("start a timer for ten minutes"))
    print(nlu.find_intents_in_phrase("create timer for ten"))
    phrase = "set a timer for 10"
    # print(nlu.find_intents_in_phrase(phrase)[0].find_args_for_intent(phrase))
