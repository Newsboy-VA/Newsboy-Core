#!/usr/bin/env python3

import logging
import os.path
import inspect
import random
import json
import time

import sys
sys.path.append('base_classes')
from module_base import VAModuleBase


class GreetingsModule(VAModuleBase):
    def __init__(self):
        module_path = os.path.dirname(inspect.getfile(inspect.currentframe()))

        super().__init__(module_path)

        entities_file = open(os.path.join(module_path, "entities.json"))
        self.entities_json = json.load(entities_file)['entities']
        entities_file.close()

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def greeting(self):
        for entity in self.entities_json:
            if entity['name'] == 'greeting':
                greeting_response = random.choice(entity['parameters'])
            if greeting_response == "@time_specific":
                hour = int(time.strftime("%H"))
                if hour < 12:
                    greeting_response = "Good morning"
                elif hour < 18:
                    greeting_response = "Good afternoon"
                else:
                    greeting_response = "Good evening"
        return greeting_response.capitalize()

    def farewell(self):
        for entity in self.entities_json:
            if entity['name'] == 'farewell':
                farewell_response = random.choice(entity['parameters'])
        return farewell_response.capitalize()

    def compliment(self):
        return "You're welcome"

    def check_state(self):
        return "I don't have feelings"



if __name__ == "__main__":
    with GreetingsModule() as module:
        pass
