#!/usr/bin/env python3

import asyncio
import collections
import sys
import curses
import argparse

import user_io


class VAClient(object):
    ''' A client object which talks to the virtual assistant '''
    def __init__(self, host, port, io_method):
        self.host = host
        self.port = port
        self.io_method = io_method
        if io_method == "text":
            self.io_handle = user_io.TextIO()
        elif io_method == "speech":
            self.io_handle = user_io.SpeechIO()

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_connection(VAClientProtocol,
                                           host=host,
                                           port=port)
        transport, self.protocol = self.loop.run_until_complete(coro)

        self.loop.create_task(self.user_to_assistant())
        self.loop.create_task(self.assistant_to_user())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

    @asyncio.coroutine
    async def user_to_assistant(self):
        ''' Forwards data from the user to the VA '''
        while self.loop.is_running():
            await asyncio.sleep(0)
            message = await self.io_handle.read()
            if message is not None:
                self.protocol.write(message)

    @asyncio.coroutine
    async def assistant_to_user(self):
        ''' Forwards data from the VA to the user '''
        while self.loop.is_running():
            await asyncio.sleep(0)
            message = await self.protocol.read()
            if message is not None:
                self.io_handle.write(message)


class VAClientProtocol(asyncio.Protocol):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        ''' Callback when the server connection is established '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.buffer = collections.deque(maxlen=20)
        self.transport = transport
        # print('{}: Connected to {}'.format(self.sockname, self.peername))

    def connection_lost(self, exc):
        ''' Callback when the server disconnects '''
        # print('{}: The server has disappeared!'.format(self.sockname))
        self.transport.close()
        self.loop.stop()

    def data_received(self, data):
        ''' Callback when the client gets data '''
        message = data.decode()
        # print('{}: Received "{}"'.format(self.sockname, message))
        # if ...
        # elif...
        # else:
        self.buffer.append(message)

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    @asyncio.coroutine
    async def read(self, blocking=True):
        ''' Read data from the server via a circular buffer '''
        empty_buffer = True
        while empty_buffer and self.loop.is_running():
            await asyncio.sleep(0)
            empty_buffer = not self.data_available()
            if not blocking:
                break
        if empty_buffer:
            return None

        return self.buffer.popleft()

    def write(self, message):
        ''' Write data to the server '''
        self.transport.write(message.encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Start a client to connect to the Virtual Assistant.')
    parser.add_argument('--io-method', type=str, default="text")
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=55801)
    parser.add_argument('--continuous', default=False, action="store_true")

    args = parser.parse_args()
    try:
        client = VAClient(args.host, args.port, args.io_method)
    except Exception as e:
        print(e)
        # pass
    print("hi")
    if args.io_method == "text":
        curses.echo()
        curses.endwin()
