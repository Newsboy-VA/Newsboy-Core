#!/usr/bin/env python3

import asyncio
# import sys
import logging
import argparse
import curses

import collections
import json

import user_io
import sys
sys.path.append('base_classes')
from protocol_base import ClientProtocolBase


class VAClient(object):
    ''' A client object which talks to the virtual assistant '''
    def __init__(self):
        FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(message)s'
        logging.basicConfig(
            filename='info.log',
            level=logging.INFO,
            format=FORMAT,
            )

        parser = argparse.ArgumentParser(
            description='Start a client to connect to the Virtual Assistant.')
        parser.add_argument('--client-name', type=str, default="")
        parser.add_argument('--host', type=str, default='localhost')
        parser.add_argument('--port', type=int, default=55801)
        parser.add_argument('--input-type', type=str, default='text')
        parser.add_argument('--continuous', default=False, action='store_true')

        args = parser.parse_args()

        self.name = args.client_name
        self.input_type = args.input_type
        if self.input_type == 'text':
            self.io_handle = user_io.TextIO()
        elif self.input_type == 'google':
            self.io_handle = user_io.SpeechIO()

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_connection(lambda: VAClientProtocol(self),
                                           host=args.host,
                                           port=args.port)
        self.transport, self.protocol = self.loop.run_until_complete(coro)

        self.loop.create_task(self.user_to_assistant())

    def __enter__(self):
        self.loop.run_forever()
        return self

    def __exit__(self, type, value, traceback):
        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()
        if self.input_type == 'text':
            curses.echo()
            curses.endwin()

        logging.shutdown()

        if isinstance(value, KeyboardInterrupt):
            return True
        elif isinstance(value, ConnectionRefusedError):  # Doesn't seem to work
            print("No virtual assistant found")
            return True

    async def user_to_assistant(self):
        ''' Forwards data from the user to the VA '''
        while self.loop.is_running():
            await asyncio.sleep(0)
            message = await self.io_handle.read()
            if message is not None:
                self.protocol.write_command('converse', [message])


class VAClientProtocol(ClientProtocolBase):
    def connection_made(self, transport):
        # By default, the client name is a list of it's connection. That way
        # it always has a unique identifier, and a list so it can be encoded.
        if self.name == "":
            self.name = list(transport.get_extra_info('sockname'))
        super().connection_made(transport)

    async def display(self, message, force_method=None):
        ''' Display text to the user using the preferred method '''
        #TODO: Make force_method actually do something
        if message is not None:
            self.protocol_handler.io_handle.write(message)


if __name__ == "__main__":
    with VAClient() as client:
        pass
