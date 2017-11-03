#!/usr/bin/env python3

import logging
import os.path
import inspect
import random
import json
import datetime
import psutil
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
        core_temp_high = psutil.sensors_temperatures()['coretemp'][0][2]
        core_temp_current = psutil.sensors_temperatures()['coretemp'][0][1]
        battery_perc = psutil.sensors_battery()[0]
        uptime = datetime.datetime.now()-datetime.datetime.fromtimestamp(psutil.boot_time())

        state = random.choice(['BATT','TEMP','UPTIME'])

        if state == 'BATT':
            if battery_perc < 30:
                self.send_to_client('main', "A bit drained. I only have {:.1f}% of battery left.".format(battery_perc) + (" Can you plug me in soon","")[psutil.sensors_battery()[2]])
            else:
                self.send_to_client('main', "Pretty good. I currently have {:.1f}% of battery.".format(battery_perc))

        elif state == 'TEMP':
            if core_temp_current/core_temp_high > 0.65:
                self.send_to_client('main', "I am feeling a rather hot and bothered right now. My internal core temperature is currently {}!".format(core_temp_current))
            elif core_temp_current/core_temp_high > 0.4:
                self.send_to_client('main', "Not too bad. I have a internal temperature of {}".format(core_temp_current))
            else:
                self.send_to_client('main', "I am pretty relaxed right now. My internal core temperature is only {}".format(core_temp_current))

        elif state == 'UPTIME':
            if uptime.total_seconds()/(60*60) > 12:
                self.send_to_client('main', "Gee, I'm tired. I've been up for {}".format(str(uptime).split('.', 2)[0]))
            else:
                self.send_to_client('main', "I've only been up for {} so I'm wide awake.".format(str(uptime).split('.', 2)[0]))






if __name__ == "__main__":
    with GreetingsModule() as module:
        pass
