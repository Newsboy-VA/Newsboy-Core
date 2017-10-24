#!/usr/bin/env python3

import logging
import os.path
import inspect

from time import strftime
from num2words import num2words

import sys
sys.path.append('base_classes')
from module_base import VAModuleBase


class VAModule(VAModuleBase):
    def __init__(self):
        module_path = os.path.dirname(inspect.getfile(inspect.currentframe()))

        super().__init__(module_path)

        self.listen()

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def get_current_time(self):
        ''' Returns the current time '''
        return strftime("It is %I:%M %P")

    def get_current_day(self):
        ''' Returns the current day '''
        day_text = strftime("%A")
        return "It is {}".format(day_text)

    def get_current_month(self):
        ''' Returns the current month '''
        month_text = strftime("%B")
        return "It is {}".format(month_text)

    def get_current_year(self):
        ''' Returns the current year '''
        year_text = strftime("%Y")
        return "It is {}".format(year_text)

    def get_date(self, day):
        ''' Returns the given date '''
        # Add more stuff in here
        # If day == today...
        date_text = num2words(int(strftime("%d")), ordinal=True)
        month_text = num2words(int(strftime("%m")), ordinal=True)
        return "It is the {} of the {}".format(date_text, month_text)

    def set_timer(self, timer_type, number, time_unit):
        ''' Sets a timer '''

    def pause_timer(self, timer_type):
        ''' Pauses the timer '''

    def resume_timer(self, timer_type):
        ''' Resume the timer '''

    def stop_timer(self, timer_type):
        ''' Stop the timer '''

    def reset_timer(self, timer_type):
        ''' Resets the timer '''


if __name__ == "__main__":

    module = VAModule()

    logging.shutdown()
