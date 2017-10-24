

import asyncio
import logging

import sys
sys.path.append('base_classes')
from protocol_base import ServerProtocolBase
from server_base import ServerBase

from conversation import Conversation


class VAClientHandler(ServerBase):
    def __init__(self, core, port):
        super().__init__(core, port, VAClientHandlerProtocol)

        logging.info("Listening for clients on {}".format(self.server.sockets[0].getsockname()))

    def send_to_client(self, client_name, message):
        ''' Sends a message to the given client '''
        client = self.connections.get(client_name)
        if client is None:
            logging.warning("No client named \"{}\"".format(client_name))
        else:
            client.write_command('display', [message])


class VAClientHandlerProtocol(ServerProtocolBase):
    def __init__(self, protocol_handler):
        super().__init__(protocol_handler)
        self.conversation = Conversation(self)
        self.loop.create_task(self.conversation_handler())

    async def converse(self, phrase):
        ''' Adds a phrase to the conversation '''
        self.conversation.client_speech.append(phrase)

    async def conversation_handler(self):
        ''' Handles the conversation between the virtual assistant and user '''
        end_conversation = False
        while not end_conversation and self.loop.is_running():
            await asyncio.sleep(0)
            # if client says keyphrase:
            #     conversation = Conversation(self, "client_started")
            # elif user identified:
            #     conversation = Conversation(self, "i_start")

            while self.conversation.ongoing and self.loop.is_running():
                intent = await self.conversation.converse()

            self.protocol_handler.core.module_handler.send_request(
                self.name, 'datetime', intent)
            # end_conversation = True

            self.conversation = Conversation(self)
            # Wait for module ack

            # Tell client it's done

            # if not self.continuous:
            #     self.conversation_handler_end = True
