#!/usr/bin/env python3

import logging
import argparse

from time import strftime
from num2words import num2words

from module_classes import VAModuleBase


class VAModule(VAModuleBase):
    def __init__(self, host, port):
        super().__init__(host, port)

        self.listen()

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def get_current_time():
        ''' Returns the current time '''
        return strftime("It is %I:%M %P")

    def get_current_day():
        ''' Returns the current day '''
        day_text = strftime("%A")
        return "It is {}".format(day_text)

    def get_current_month():
        ''' Returns the current month '''
        month_text = strftime("%B")
        return "It is {}".format(month_text)

    def get_current_year():
        ''' Returns the current year '''
        year_text = strftime("%Y")
        return "It is {}".format(year_text)

    def get_date(day):
        ''' Returns the given date '''
        # Add more stuff in here
        # If day == today...
        date_text = num2words(int(strftime("%d")), ordinal=True)
        month_text = num2words(int(strftime("%m")), ordinal=True)
        return "It is the {} of the {}".format(date_dext, month_text)

    def set_timer(timer_type, number, time_unit):
        ''' Sets a timer '''

    def pause_timer(timer_type):
        ''' Pauses the timer '''

    def resume_timer(timer_type):
        ''' Resume the timer '''

    def stop_timer(timer_type):
        ''' Stop the timer '''

    def reset_timer(timer_type):
        ''' Resets the timer '''


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(pathname)s: %(message)s'
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format=FORMAT,
        )

    parser = argparse.ArgumentParser(
        description='Start a module for the virtual assistant to use.')
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=55802)

    args = parser.parse_args()

    module = VAModule(args.host, args.port)

    logging.shutdown()
