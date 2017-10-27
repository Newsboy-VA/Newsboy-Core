

import logging
import re

import sys
sys.path.append('base_classes')
from action_base import ActionBase

class NLU(object):
    ''' A class for performing basic Natural Language Understanding '''
    def __init__(self):
        self.name = "NLU"
        self.available_intents = list()

    def set_available_intents(self, module_intents_dict):
        ''' Sets the intents/actions that the assistant can perform '''
        self.available_intents = list()
        for (module, intent_list) in module_intents_dict.items():
            for intent_dict in intent_list:
                intent_matcher = IntentMatcher(intent_dict)
                intent_matcher.generate_regex()
                intent_matcher['module'] = module
                self.available_intents.append(intent_matcher)
        logging.debug("{}: Available intents now {}".format(
            self.name, self.available_intents))

    def find_intents_in_phrase(self, phrase):
        ''' Returns a list of matching intents '''
        matching_intents = []
        for intent_matcher in self.available_intents:
            if intent_matcher.is_intent_match(phrase):
                arguments_in_phrase = intent_matcher.find_all_arguments(phrase)
                intent = Intent({'function': intent_matcher['function'],
                                 'module': intent_matcher['module'],
                                 'arguments': arguments_in_phrase})

                matching_intents.append(intent)
        return matching_intents

    def find_args_for_intent(self, intent_function, phrase):
        ''' Returns a list of arguments found in the phrase to the given intent '''
        for intent_matcher in self.available_intents:
            if intent_matcher['function'] == intent_function:
                return intent_matcher.find_all_arguments(phrase)


class IntentMatcher(ActionBase):
    ''' A class to find arguments for a given intent '''
    def assert_items(self):
        super().assert_items()
        assert(isinstance(self['name'], str))
        if 'synonyms' not in self:
            self['synonyms'] = []
        assert(isinstance(self['synonyms'], list))

    def generate_regex(self):
        ''' Generates all the regular expressions '''
        # print(self)
        self.intent_regex = self.generate_intent_regex()
        self.argument_regex_dict = self.generate_argument_regex_dict()

    def generate_intent_regex(self):
        ''' Generates a regular expression which matches the name/synonyms '''

        pattern = "\\b("
        for word in [self['name'], *self['synonyms']]:
            pattern += "{}|".format(word)
        pattern = pattern[:-1]
        pattern += ")\\b"

        return re.compile(pattern, re.IGNORECASE)

    def generate_argument_regex_dict(self):
        ''' Generates a dictionary of the form {"argument": regex} '''

        argument_dict = dict()

        for (argument, parameters) in self['arguments'].items():
            if argument == 'number':
                argument_dict[argument] = \
                    self.generate_number_regex()
            else:
                if isinstance(parameters, dict):
                    entity_dict = parameters
                else:
                    entity_dict = dict()
                    for parameter in parameters:
                        entity_dict[parameter] = [parameter]
                argument_dict[argument] = \
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


class Intent(ActionBase):
    ''' A class to store intent parameters '''
    def is_full(self):
        ''' Returns True if all arguments have a value '''
        # print(self['arguments'].values())
        if None in self['arguments'].values():
            return False
        return True
