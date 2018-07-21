#!/usr/bin/env python3

import logging
import os.path
import inspect
import random
import json
import time
import psutil
from datetime import datetime

import sys
sys.path.append('base_classes')
from module_base import VAModuleBase


class GreetingsModule(VAModuleBase):

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def greeting(self):
        for entity in self.entities_json:
            if entity['name'] == 'greeting':
                response = random.choice(entity['parameters'])
            if response == "@time_specific":
                hour = int(time.strftime("%H"))
                if hour < 12:
                    response = "Good morning"
                elif hour < 18:
                    response = "Good afternoon"
                else:
                    response = "Good evening"
        return response.capitalize()

    def farewell(self):
        for entity in self.entities_json:
            if entity['name'] == 'farewell':
                response = random.choice(entity['parameters'])
        return response.capitalize()

    def compliment(self):
        return "You're welcome"

    def check_state(self):
        core_temp_high = psutil.sensors_temperatures()['coretemp'][0][2]
        core_temp_current = psutil.sensors_temperatures()['coretemp'][0][1]
        battery_perc = psutil.sensors_battery()[0]
        uptime = datetime.now()-datetime.fromtimestamp(psutil.boot_time())

        state = random.choice(['BATT','TEMP','UPTIME'])

        if state == 'BATT':
            if battery_perc < 30:
                response = "A bit drained. I only have {:.1f}% of battery left.".format(battery_perc) + (" Can you plug me in soon","")[psutil.sensors_battery()[2]]
            else:
                response = "Pretty good. I currently have {:.1f}% of battery.".format(battery_perc)

        elif state == 'TEMP':
            if core_temp_current/core_temp_high > 0.65:
                response = "I am feeling a rather hot and bothered right now. My internal core temperature is currently {}!".format(core_temp_current)
            elif core_temp_current/core_temp_high > 0.4:
                response = "Not too bad. I have a internal temperature of {}".format(core_temp_current)
            else:
                response = "I am pretty relaxed right now. My internal core temperature is only {}".format(core_temp_current)

        elif state == 'UPTIME':
            if uptime.total_seconds()/(60*60) > 12:
                response = "Gee, I'm tired. I've been up for {}".format(str(uptime).split('.', 2)[0])
            else:
                response = "I've only been up for {} so I'm wide awake.".format(str(uptime).split('.', 2)[0])
        return response


if __name__ == "__main__":
    with GreetingsModule() as module:
        pass
