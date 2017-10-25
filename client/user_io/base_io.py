

import asyncio
import collections


class BaseIO(object):
    """docstring for BaseIO."""
    def __init__(self):
        self.buffer = collections.deque(maxlen=20)

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.check_for_data_loop())

    async def check_for_data_loop(self):
        ''' Continuously check for data from the user '''
        while self.loop.is_running():
            await asyncio.sleep(0)
            self.check_for_data()

    def check_for_data(self):
        ''' Check once for data from the user '''
        raise NotImplementedError

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    async def read(self, blocking=True):
        ''' Read data from the user via a circular buffer '''
        empty_buffer = True
        while empty_buffer and self.loop.is_running():
            await asyncio.sleep(0)
            empty_buffer = not self.data_available()
            if not blocking:
                break
        if empty_buffer:
            return None

        return self.buffer.popleft()

    def write(self, text):
        ''' Write data to the user '''
        raise NotImplementedError
