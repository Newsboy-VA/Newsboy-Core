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

    def get_weather(self):
        weather_data = feedparser.parse("http://www.rssweather.com/wx/nz/christchurch/rss.php")
        weather_summary = weather_data['entries'][0]['summary_detail']['value']
        return weather_summary


if __name__ == "__main__":
    with GreetingsModule() as module:
        pass
