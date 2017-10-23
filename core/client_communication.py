

import asyncio
import logging

import collections
import json

from datatypes import NamedObjectList
from conversation import Conversation


class VAClientHandler(object):
    def __init__(self, core, port):
        self.core = core
        self.available_clients = NamedObjectList()
        self.loop = asyncio.get_event_loop()

        # Each client connection will create a new protocol instance
        coro = self.loop.create_server(lambda: VAServerProtocol(self),
                                       host='localhost',
                                       port=port)
        self.server = self.loop.run_until_complete(coro)

        logging.info("Listening for clients on {}".format(self.server.sockets[0].getsockname()))

    def add_client(self, protocol):
        ''' Adds a client to the client list '''
        self.available_clients.append(protocol)

    def remove_client(self, protocol):
        ''' Remove a client from the client list '''
        self.available_clients.remove(protocol)

    def close(self):
        ''' Closes the server down '''
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())


class VAServerProtocol(asyncio.Protocol):
    def __init__(self, client_handler):
        self.client_handler = client_handler
        self.client_handler.add_client(self)

        self.buffer = collections.deque(maxlen=20)
        self.conversation_handler_end = False
        loop = asyncio.get_event_loop()
        loop.create_task(self.conversation_handler())

    def connection_made(self, transport):
        ''' Callback when the client connects '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.name = self.peername  # For referencing in the available_clients
        self.transport = transport
        logging.info("Connection from {}".format(self.peername))

    def connection_lost(self, exc):
        ''' Callback when the client disconnects '''
        logging.info("{} disconnected".format(self.peername))
        self.end_conversation()
        self.transport.close()
        self.client_handler.remove_client(self)

    def data_received(self, serial_data):
        ''' Callback when the server gets data '''
        data = json.loads(serial_data.decode('utf-8'))
        logging.info("Received \"{}\"".format(data))
        self.buffer.append(data)

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    @asyncio.coroutine
    async def read(self, blocking=True):
        ''' Read data from the client via a circular buffer '''
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

    def write(self, data):
        ''' Write data to the client '''
        serial_data = json.dumps(data).encode('utf-8')
        self.transport.write(serial_data)

    @asyncio.coroutine
    async def conversation_handler(self):
        ''' Handles the conversation between the virtual assistant and user '''
        loop = asyncio.get_event_loop()
        while not self.conversation_handler_end and loop.is_running():
            await asyncio.sleep(0)
            # if client says keyphrase:
            #     conversation = Conversation(self, "client_started")
            # elif user identified:
            #     conversation = Conversation(self, "i_start")

            conversation = Conversation(self)
            while conversation.ongoing and loop.is_running():

                # await asyncio.sleep(0)
                intent = await conversation.converse()

            self.client_handler.core.module_handler.send_request(
                self.name, 'datetime', intent)
            conversation.end()

            # Wait for module ack

            # Tell client it's done

            # if not self.continuous:
            #     self.conversation_handler_end = True

    def end_conversation(self):
        ''' Closes the connection when the conversation is done '''
        self.conversation_handler_end = True
