#!/usr/bin/env python3

import asyncio
import sys
import logging
import argparse
import curses

import collections
import json

import user_io


class VAClient(object):
    ''' A client object which talks to the virtual assistant '''
    def __init__(self, host, port, input_type):
        self.host = host
        self.port = port
        self.input_type = input_type
        if input_type == 'text':
            self.io_handle = user_io.TextIO()
        elif input_type == 'speech':
            self.io_handle = user_io.SpeechIO()

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_connection(VAClientProtocol,
                                           host=host,
                                           port=port)
        self.transport, self.protocol = self.loop.run_until_complete(coro)

        self.loop.create_task(self.user_to_assistant())
        self.loop.create_task(self.assistant_to_user())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.transport.close()
            self.loop.stop()

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
        logging.info("Connected to {}".format(self.peername))

    def connection_lost(self, exc):
        ''' Callback when the server disconnects '''
        logging.info("The server has disappeared!".format(self.sockname))
        self.transport.close()
        self.loop.stop()

    def data_received(self, serial_data):
        ''' Callback when the client gets data '''
        data = json.loads(serial_data.decode('utf-8'))
        logging.info("Received \"{}\"".format(data))
        # if ...
        # elif...
        # else:
        self.buffer.append(data)

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

    def write(self, data):
        ''' Write data to the server '''
        serial_data = json.dumps(data).encode('utf-8')
        self.transport.write(serial_data)


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(pathname)s: %(message)s'
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format=FORMAT,
        )

    parser = argparse.ArgumentParser(
        description='Start a client to connect to the Virtual Assistant.')
    parser.add_argument('--input-type', type=str, default="text")
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=55801)
    parser.add_argument('--continuous', default=False, action="store_true")

    args = parser.parse_args()
    try:
        client = VAClient(args.host, args.port, args.input_type)
    except Exception as e:
        print(e)
        # pass

    if args.input_type == "text":
        curses.echo()
        curses.endwin()

    logging.shutdown()
