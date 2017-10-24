

import asyncio
import collections
import json

import logging


class ProtocolBase(asyncio.Protocol):
    def __init__(self, protocol_handler):
        self.protocol_handler = protocol_handler
        self.name = None
        self.buffer = collections.deque(maxlen=20)

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.read_command())

    def connection_made(self, transport):
        ''' Callback when the peer connects '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.transport = transport

    def connection_lost(self, exc):
        ''' Callback when the peer disconnects '''
        self.transport.close()

    def data_received(self, serial_data):
        ''' Callback when the socket gets data '''
        data = json.loads(serial_data.decode('utf-8'))
        logging.debug("Received \"{}\"".format(data))
        self.buffer.append(data)

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    async def read(self, blocking=True):
        ''' Read data from the socket via a circular buffer '''
        empty_buffer = True
        while empty_buffer and self.loop.is_running():
            await asyncio.sleep(0)
            empty_buffer = not self.data_available()
            if not blocking:
                break
        if empty_buffer:
            return None
        return self.buffer.popleft()

    async def read_command(self):
        ''' Continuously checks the buffer and deals with the data '''
        while self.loop.is_running():
            data = await self.read()
            coro = getattr(self, data[0])
            await coro(*data[1])

    def write(self, data):
        ''' Write data to the peer '''
        logging.debug("Sending \"{}\"".format(data))
        serial_data = json.dumps(data).encode('utf-8')
        self.transport.write(serial_data)

    def write_command(self, command, arg_list):
        ''' Sends a command to the peer '''
        self.write([command, arg_list])


class ClientProtocolBase(ProtocolBase):
    def __init__(self, protocol_handler):
        super().__init__(protocol_handler)
        self.name = self.protocol_handler.name

    def connection_made(self, transport):
        ''' Callback when the module connects '''
        super().connection_made(transport)
        logging.info("Connected to {}".format(self.peername))
        self.write_command('set_name', [self.name])

    def connection_lost(self, exc):
        ''' Callback when the module disconnects '''
        logging.info("The server has disappeared!")
        super().connection_lost(exc)
        self.loop.stop()


class ServerProtocolBase(ProtocolBase):
    def connection_made(self, transport):
        ''' Callback when the module connects '''
        super().connection_made(transport)
        logging.info("Connection from {}".format(self.peername))
        self.protocol_handler.add_connection(self)

    def connection_lost(self, exc):
        ''' Callback when the module disconnects '''
        logging.info("{} disconnected".format(self.peername))
        super().connection_lost(exc)
        self.protocol_handler.remove_connection(self)

    async def set_name(self, name):
        ''' Set the protocol name '''
        self.name = name
