#!/usr/bin/env python3

import collections
import curses

try:
    from .base_io import BaseIO
except SystemError:
    from base_io import BaseIO


class TextIO(BaseIO):
    ''' An interface with the user via a terminal '''
    def __init__(self):
        super().__init__()
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.echo()
        # self.stdscr.clear()
        self.line = ''

    def check_for_data(self):
        ''' Check once for data from the terminal '''
        self.stdscr.refresh()

        char_code = self.stdscr.getch()
        if char_code != curses.ERR:
            char = chr(char_code)
            if char != '\n':
                self.line += char
            else:
                self.buffer.append(self.line)
                self.line = ''
                print(end="\n\r")  # TODO: Make this happen elsewhere

    def write(self, message):
        ''' Write data to the terminal '''
        print(message + '\r')
        self.stdscr.refresh()


if __name__ == "__main__":

    text_io = TextIO()

    while True:
        text = text_io.read()
        text_io.write(text)
