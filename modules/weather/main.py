#!/usr/bin/env python3

import logging
import os.path
import inspect
import random
import json
import time
import feedparser

import sys
sys.path.append('base_classes')
from module_base import VAModuleBase


class WeatherModule(VAModuleBase):

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def get_weather(self):
        # look into using metservice data: https://github.com/arfar/metservice-api-py
        weather_data = feedparser.parse("http://www.rssweather.com/wx/nz/christchurch/rss.php")
        weather_summary = weather_data['entries'][0]['summary_detail']['value']
        return weather_summary


if __name__ == "__main__":
    with WeatherModule() as module:
        pass
