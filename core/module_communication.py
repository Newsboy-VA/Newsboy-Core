

import asyncio
import logging

import sys
sys.path.append('base_classes')
from protocol_base import ServerProtocolBase
from server_base import ServerBase


class VAModuleHandler(ServerBase):
    def __init__(self, core, port):
        super().__init__(core, port, VAModuleHandlerProtocol)
        self.nlu = self.core.nlu

    def update_available_actions(self):
        ''' Update the available_actions_dict '''
        module_actions_dict = dict()
        for module in self.connections:
            module_actions_dict[module.name] = module.available_actions_list
        self.nlu.set_available_intents(module_actions_dict)

    def add_connection(self, protocol):
        ''' Adds a connection to the connection list '''
        super().add_connection(protocol)

    def remove_connection(self, protocol):
        ''' Remove a connection from the connection list '''
        super().remove_connection(protocol)
        self.update_available_actions()

    def send_request(self, client_name, module_name, intent):
        ''' Sends a request to the given module '''
        module = self.connections.get(module_name)
        if module is None:
            logging.error("Server: No module named \"{}\"".format(module_name))
        else:
            module.write_command('request', [client_name, intent])


class VAModuleHandlerProtocol(ServerProtocolBase):
    def __init__(self, protocol_handler):
        super().__init__(protocol_handler)
        self.available_actions_list = []

    async def set_actions(self, available_actions):
        ''' Sets the actions this module can perform '''
        self.available_actions_list = available_actions
        self.protocol_handler.update_available_actions()
        # logging.warning(1, self.available_actions_list)

    async def response(self, client_name, message):
        ''' Acknowledges the request has been made. More may be to come. '''
        self.protocol_handler.core.client_handler.send_to_client(
            client_name, message)

    async def send_to_client(self, client_name, message, priority):
        ''' Sends a message to the given client '''
        self.protocol_handler.core.client_handler.send_to_client(
            client_name, message, priority)
