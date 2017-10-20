

import asyncio
import collections
import os.path
import sys
import inspect
import json


class VAModuleBase(object):
    ''' A module which talks to the virtual assistant '''
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.path = os.path.dirname( inspect.getfile(inspect.currentframe()))
        self.name = os.path.split(self.path)[-1]

        self.available_actions = dict()
        self.update_available_actions()

        # [print(k, '|', v) for k, v in self.available_actions.items()]

        self.loop = asyncio.get_event_loop()

    def listen(self):
        ''' Start a connection with the virtual assistant '''
        coro = self.loop.create_connection(lambda: VAModuleClientProtocol(self),
                                           host=self.host,
                                           port=self.port)
        transport, self.protocol = self.loop.run_until_complete(coro)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def update_available_actions(self):
        ''' Register all actions from the json file '''

        actions_file = open(os.path.join(self.path, "actions.json"))
        actions_json = json.load(actions_file)['actions']
        actions_file.close()
        entities_file = open(os.path.join(self.path, "entities.json"))
        entities_json = json.load(entities_file)['entities']
        entities_file.close()

        for action in actions_json:
            function_name = action['function']
            action['function'] = self.get_function_handle(function_name)
            self.available_actions[function_name] = Action(action, entities_json)

    def get_function_handle(self, function_name):
        ''' Returns the function handle give a string of it's name '''
        return getattr(self, function_name)


class Action(object):
    ''' An object that can perform an action '''
    def __init__(self, action_dict, entities_json):
        self.name = action_dict['name']
        self.synonyms = action_dict['synonyms']
        self.callback = action_dict['function']
        self.argument_dict = self.find_arguments(
            action_dict['arguments'], entities_json)

        self.assert_entities()

    def find_arguments(self, arguments, entities_json):
        ''' Create a dictionary of each argument '''
        argument_dict = dict()

        for action_arg in arguments:
            if action_arg == 'number':
                argument_dict[action_arg] = 'number'
            for entity in entities_json:
                if entity['name'] == action_arg:
                    if isinstance(entity['parameters'], dict):
                        entity_list = entity['parameters'].keys()
                    else:
                        entity_list = entity['parameters']
                    argument_dict[action_arg] = entity_list

        return argument_dict

    def assert_entities(self):
        ''' Ensure the callback arguments match the json entities '''
        callback_args = sorted(self.argument_dict.keys())
        json_args = sorted(inspect.getargspec(self.callback)[0])

        if callback_args != json_args:
            raise AssertionError("Arguments for {} are {} instead of {}".format(
                self.name, json_args, callback_args))

    def assert_parameters(self, *args):
        ''' Ensure the given parameters match their corresponding entities '''
        # callback_args = sorted(self.arguments.keys())
        # TODO: This function

    def __call__(self, *args):
        ''' Perform the given function '''
        self.assert_arguments(*args)
        return self.callback(*args)

    def __str__(self):
        string_representation = "{}(".format(self.callback.__name__)
        for arg in self.argument_dict.keys():
            string_representation += "{}, ".format(arg)
        if len(self.argument_dict) != 0:
            string_representation = string_representation[:-2]
        string_representation += ")"
        return string_representation

    def __repr__(self):
        return self.__str__()


class VAModuleClientProtocol(asyncio.Protocol):
    def __init__(self, module_class):
        self.module = module_class
        self.loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        ''' Callback when the server connection is established '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.buffer = collections.deque(maxlen=20)
        self.transport = transport
        print('{}: Connected to {}'.format(self.module.name, self.peername))

    def connection_lost(self, exc):
        ''' Callback when the server disconnects '''
        print('{}: The server has disappeared!'.format(self.module.name))
        self.transport.close()
        self.loop.stop()

    def data_received(self, data):
        ''' Callback when the module gets data '''
        message = data.decode()
        print('{}: Received "{}"'.format(self.module.name, message))
        self.buffer.append(message)

    def data_available(self):
        ''' Returns whether the read buffer has data '''
        return len(self.buffer) != 0

    # Does this need to be async?
    @asyncio.coroutine
    async def read(self, blocking=True):
        ''' Read data from the server via a circular buffer '''
        empty_buffer = True
        while empty_buffer and self.loop.is_running():
            await asyncio.sleep(0)
            empty_buffer = not self.data_available()
            if not blocking:
                break
        if empty_buffer:
            return None

        return self.buffer.popleft()

    def write(self, message):
        ''' Write data to the server '''
        self.transport.write(message.encode("utf-8"))
