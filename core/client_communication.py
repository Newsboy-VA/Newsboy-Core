

import asyncio
import collections

# from conversation import Conversation


class VAServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.buffer = collections.deque(maxlen=20)
        self.conversation_handler_end = False
        loop = asyncio.get_event_loop()
        loop.create_task(self.conversation_handler())

    def connection_made(self, transport):
        ''' Callback when the client connects '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.transport = transport
        print('{}: Connection from {}'.format(self.sockname, self.peername))

    def connection_lost(self, exc):
        ''' Callback when the client disconnects '''
        print('{}: {} disconnected'.format(self.sockname, self.peername))
        self.end_conversation()
        self.transport.close()

    def data_received(self, data):
        ''' Callback when the client gets data '''
        message = data.decode()
        self.buffer.append(message)
        print('{}: Received "{}"'.format(self.sockname, message))

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

    def write(self, message):
        ''' Write data to the client '''
        self.transport.write(message.encode("utf-8"))

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
            while conversation.ongoing:
                conversation.converse()


            # Wait for module ack

            # Tell client it's done

            # if not self.continuous:
            #     self.conversation_handler_end = True

    def end_conversation(self):
        ''' Closes the connection when the conversation is done '''
        self.conversation_handler_end = True
