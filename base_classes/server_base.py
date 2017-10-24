

import asyncio
import logging

from datatypes import NamedObjectList


class ServerBase(object):
    def __init__(self, core, port, protocol):
        self.core = core
        self.connections = NamedObjectList()
        self.loop = asyncio.get_event_loop()

        # Each client connection will create a new protocol instance
        coro = self.loop.create_server(lambda: protocol(self),
                                       host='localhost',
                                       port=port)
        self.server = self.loop.run_until_complete(coro)

    def add_connection(self, protocol):
        ''' Adds a connection to the connection list '''
        self.connections.append(protocol)

    def remove_connection(self, protocol):
        ''' Remove a connection from the connection list '''
        self.connections.remove(protocol)

    def close(self):
        ''' Closes the server down '''
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
