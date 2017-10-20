

import asyncio
import collections
import json


class VAModuleHandler(object):
    def __init__(self, port):
        self.module_list = []
        self.loop = asyncio.get_event_loop()

        # Each module connection will create a new protocol instance
        coro = self.loop.create_server(lambda: VAModuleProtocol(self),
                                  host='localhost',
                                  port=port)
        self.server = self.loop.run_until_complete(coro)

        print("Listening for modules on {}".format(self.server.sockets[0].getsockname()))

    def add_module(self, protocol):
        ''' Adds a module to the module list '''
        self.module_list.append(protocol)

    def remove_module(self, protocol):
        ''' Remove a module from the module list '''
        self.module_list.remove(protocol)

    def close(self):
        ''' Closes the server down '''
        self.server.close()
        self.loop.run_until_complete(server.wait_closed())


class VAModuleProtocol(asyncio.Protocol):
    def __init__(self, module_handler):
        self.module_handler = module_handler
        self.module_handler.add_module(self)

        self.buffer = collections.deque(maxlen=20)

    def connection_made(self, transport):
        ''' Callback when the module connects '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.transport = transport
        print("Module Handler: Connection from {}".format(self.peername))

    def connection_lost(self, exc):
        ''' Callback when the module disconnects '''
        print("Module Handler: {} disconnected".format(self.peername))
        self.transport.close()
        self.module_handler.remove_module(self)

    def data_received(self, data):
        ''' Callback when the server gets data '''
        message = data.decode()
        self.buffer.append(message)
        print("Module Handler: Received \"{}\"".format(message))

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    @asyncio.coroutine
    async def read(self, blocking=True):
        ''' Read data from the module via a circular buffer '''
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

    def write(self, message):
        ''' Write data to the module '''
        self.transport.write(message.encode("utf-8"))
