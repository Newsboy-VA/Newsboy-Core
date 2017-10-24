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
    def __init__(self, client_name, host, port, input_type):
        self.name = client_name
        self.host = host
        self.port = port
        self.input_type = input_type
        if input_type == 'text':
            self.io_handle = user_io.TextIO()
        elif input_type == 'speech':
            self.io_handle = user_io.SpeechIO()

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_connection(lambda: VAClientProtocol(self),
                                           host=host,
                                           port=port)
        self.transport, self.protocol = self.loop.run_until_complete(coro)

        self.loop.create_task(self.user_to_assistant())
        # self.loop.create_task(self.assistant_to_user())
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
                self.protocol.write_command('converse', [message])

    # @asyncio.coroutine
    # async def assistant_to_user(self):
    #     ''' Forwards data from the VA to the user '''
    #     while self.loop.is_running():
    #         await asyncio.sleep(0)
    #         message = await self.protocol.read()
    #         if message is not None:
    #             self.io_handle.write(message)


class VAClientProtocol(ClientProtocolBase):
    def connection_made(self, transport):
        self.name = transport.get_extra_info('sockname')
        super().connection_made(transport)

    async def display(self, message, force_method=None):
        ''' Display text to the user using the preferred method '''
        #TODO: Make force_method actually do something
        self.protocol_handler.io_handle.write(message)


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(message)s'
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
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
    try:
        client = VAClient(args.client_name, args.host, args.port, args.input_type)
    except Exception as e:
        print(e)

    if args.input_type == 'text':
        curses.echo()
        curses.endwin()

    logging.shutdown()
