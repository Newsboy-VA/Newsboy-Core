

import asyncio
import logging

import collections
import json

from datatypes import NamedObjectList


class VAModuleHandler(object):
    def __init__(self, port):
        self.available_modules = NamedObjectList()
        self.loop = asyncio.get_event_loop()

        # Each module connection will create a new protocol instance
        coro = self.loop.create_server(lambda: VAModuleProtocol(self),
                                       host='localhost',
                                       port=port)
        self.server = self.loop.run_until_complete(coro)

        logging.info("Listening for modules on {}".format(self.server.sockets[0].getsockname()))

    def add_module(self, protocol):
        ''' Adds a module to the module list '''
        self.available_modules.append(protocol)

    def remove_module(self, protocol):
        ''' Remove a module from the module list '''
        self.available_modules.remove(protocol)

    def send_request(self, module_name, client_id, intent_dict):
        ''' Sends a request to the given module '''
        for module in self.available_modules:
            if module.name == module_name:
                data = {'HEADER': 'REQ', 'MESSAGE': {
                    'ACTION': intent_dict['intent'],
                    'PARAMS': intent_dict['params']
                }}
                module.write(data)

    def close(self):
        ''' Closes the server down '''
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())


class VAModuleProtocol(asyncio.Protocol):
    def __init__(self, module_handler):
        self.module_handler = module_handler
        self.buffer = collections.deque(maxlen=20)

    def connection_made(self, transport):
        ''' Callback when the module connects '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.transport = transport
        logging.info("Connection from {}".format(self.peername))
        self.module_handler.add_module(self)

    def connection_lost(self, exc):
        ''' Callback when the module disconnects '''
        logging.info("{} disconnected".format(self.peername))
        self.transport.close()
        self.module_handler.remove_module(self)

    def data_received(self, serial_data):
        ''' Callback when the server gets data '''
        data = json.loads(serial_data.decode('utf-8'))
        logging.info("Received \"{}\"".format(data))
        # if data['HEADER'] == 'GET':
            # self.write({'HEADER': '', data['MESSAGE']: getattr(self, data['MESSAGE'])})
        if data['HEADER'] == 'SET':
            setattr(self, *data['MESSAGE'])
        else:
            self.buffer.append(data)

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

    def write(self, data):
        ''' Write data to the module '''
        serial_data = json.dumps(data).encode('utf-8')
        self.transport.write(serial_data)
