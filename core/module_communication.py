

import asyncio
import logging

import sys
sys.path.append('base_classes')
from protocol_base import ServerProtocolBase
from server_base import ServerBase


class VAModuleHandler(ServerBase):
    def __init__(self, core, port):
        super().__init__(core, port, VAModuleHandlerProtocol)

        logging.info("Listening for modules on {}".format(self.server.sockets[0].getsockname()))

    def send_request(self, client_name, module_name, intent):
        ''' Sends a request to the given module '''
        module = self.connections.get(module_name)
        if module is None:
            logging.warning("No module named \"{}\"".format(module_name))
        else:
            module.write_command('request', [client_name, intent])


class VAModuleHandlerProtocol(ServerProtocolBase):
    async def send_to_client(self, client_id, message):
        ''' Send a message to the client '''
        self.name = name
