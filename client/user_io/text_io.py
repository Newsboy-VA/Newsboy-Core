#!/usr/bin/env python3

import collections
import curses
import logging

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
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.noecho()
        # self.stdscr.clear()

        self.shape = self.stdscr.getmaxyx()
        # print(self.shape)

        self.line = ''

    def reset_size(self):
        ''' Reset the size of the text on the terminal '''

    def check_for_data(self):
        ''' Check once for data from the terminal '''

        self.stdscr.refresh()

        # import time
        # t0 = time.time()
        try:
            char = self.stdscr.getkey()
        except:
            return
        # t1 = time.time()
        # print(t1-t0)

        if char != curses.ERR:
            # print(char)
            if char.startswith('KEY_'):
                func = getattr(self, char.lower(), None)
                if func is not None:
                    func()
            elif char == '\n':
                self.buffer.append(self.line)
                # logging.info(self.line)
                self.line = ''
                print(end="\n\r")  # TODO: Make this happen elsewhere
            else:
                self.line += char

            print('\r' + self.line, end='')

        # self.stdscr.refresh()

    def write(self, message):
        ''' Write data to the terminal '''
        print(message + '\r')
        self.stdscr.refresh()

    def key_resize(self):
        self.reset_size()
        self.shape = self.stdscr.getmaxyx()

    def key_backspace(self):
        if len(self.line) > 0:
            self.line = self.line[:-1]

    # def key_undo(self):
    #     self.key_backspace()


if __name__ == "__main__":

    text_io = TextIO()

    while True:
        text = text_io.read()
        text_io.write(text)
