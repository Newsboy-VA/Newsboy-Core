#!/usr/bin/env python3

import asyncio
import collections
import curses
# import sys


try:
    from .base_io import BaseIO
except SystemError:
    from base_io import BaseIO


class TextIO(BaseIO):
    """docstring for TextIO."""
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.echo()

        # self.stdscr.clear()

        self.buffer = collections.deque(maxlen=20)

        loop = asyncio.get_event_loop()
        loop.create_task(self.check_for_data())

    def write(self, message):
        ''' Write data to the terminal '''
        print(message + '\r')
        self.stdscr.refresh()

    @asyncio.coroutine
    async def check_for_data(self):
        ''' Continuously check for data from the terminal '''

        loop = asyncio.get_event_loop()
        line = ''
        while loop.is_running():
            await asyncio.sleep(0)
            self.stdscr.refresh()

            char_code = self.stdscr.getch()
            if char_code != curses.ERR:
                char = chr(char_code)
                if char != '\n':
                    line += char
                else:
                    self.buffer.append(line)
                    line = ''

                    print(end='\n\r')  # TODO: Make this heppen elsewhere

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    @asyncio.coroutine
    async def read(self, blocking=True):
        ''' Read data from the user via a circular buffer '''
        loop = asyncio.get_event_loop()
        empty_buffer = True
        while empty_buffer and loop.is_running():
            await asyncio.sleep(0)
            empty_buffer = not self.data_available()
            if not blocking:
                break
        if empty_buffer:
            return None

        return self.buffer.popleft()


if __name__ == "__main__":

    text_io = TextIO()

    while True:
        text = text_io.read()
        text_io.write(text)
