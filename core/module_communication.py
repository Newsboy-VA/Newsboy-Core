

import asyncio
import logging

import sys
sys.path.append('base_classes')
from protocol_base import ServerProtocolBase
from server_base import ServerBase


class VAModuleHandler(ServerBase):
    def __init__(self, core, port):
        super().__init__(core, port, VAModuleHandlerProtocol)
        logging.info("Server: Listening for modules on {}".format(self.server.sockets[0].getsockname()))

    def send_request(self, client_name, module_name, intent):
        ''' Sends a request to the given module '''
        module = self.connections.get(module_name)
        if module is None:
            logging.warning("Server: No module named \"{}\"".format(module_name))
        else:
            module.write_command('request', [client_name, intent])


class VAModuleHandlerProtocol(ServerProtocolBase):
    async def response(self, client_name, message):
        ''' Acknowledges the request has been made. More may be to come. '''
        self.protocol_handler.core.client_handler.send_to_client(
            client_name, message)

    async def send_to_client(self, client_name, message, priority):
        ''' Sends a message to the given client '''
        self.protocol_handler.core.client_handler.send_to_client(
            client_name, message, priority)
