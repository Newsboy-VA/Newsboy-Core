

import asyncio
import sys
import os.path
import logging
import inspect
import argparse

import collections
import json


class VAModuleBase(object):
    ''' A module which talks to the virtual assistant '''
    def __init__(self, module_path):
        self.path = module_path
        self.name = os.path.split(self.path)[-1]

        FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(pathname)s: %(message)s'
        logging.basicConfig(
            filename='debug.log',
            level=logging.DEBUG,
            format=FORMAT,
            )

        parser = argparse.ArgumentParser(
            description='Start a module for the virtual assistant to use.')
        parser.add_argument('--host', type=str, default='localhost')
        parser.add_argument('--port', type=int, default=55802)

        args = parser.parse_args()

        self.host = args.host
        self.port = args.port

        self.available_actions = dict()
        self.update_available_actions()

        # [logging.info(k, '|', v) for k, v in self.available_actions.items()]

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
        self.function = action_dict['function']
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
        ''' Ensure the action arguments match the json entities '''
        action_args = sorted(self.argument_dict.keys())
        json_args = sorted(inspect.getargspec(self.function)[0])

        if action_args != json_args:
            raise AssertionError("Arguments for {} are {} instead of {}".format(
                self.name, json_args, action_args))

    def assert_parameters(self, *args):
        ''' Ensure the given parameters match their corresponding entities '''
        # action_args = sorted(self.arguments.keys())
        # TODO: This function

    def __call__(self, *args):
        ''' Perform the given function '''
        self.assert_arguments(*args)
        return self.function(*args)


class VAModuleClientProtocol(asyncio.Protocol):
    def __init__(self, module_class):
        self.module = module_class
        self.name = self.module.name
        self.loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        ''' Callback when the server connection is established '''
        self.sockname = transport.get_extra_info('sockname')
        self.peername = transport.get_extra_info('peername')
        self.buffer = collections.deque(maxlen=20)
        self.transport = transport
        self.write({'HEADER': 'SET', 'MESSAGE': ['name', self.name]})
        logging.info('{}: Connected to {}'.format(self.name, self.peername))

    def connection_lost(self, exc):
        ''' Callback when the server disconnects '''
        logging.info('{}: The server has disappeared!'.format(self.name))
        self.transport.close()
        self.loop.stop()

    def data_received(self, serial_data):
        ''' Callback when the module gets data '''
        data = json.loads(serial_data.decode('utf-8'))
        logging.info('{}: Received "{}"'.format(self.name, data))
        # if 'GET' in data:
            # self.write({data['GET']: getattr(self, data['GET'])})
        # else:
        if data['HEADER'] == 'REQUEST':
            # print(data)
            action = data['MESSAGE']['ACTION']
            # print(self.module[action['function']](*action['arguments']))
            # setattr(self, *data['MESSAGE'])
        else:
            self.buffer.append(data)

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

    def write(self, data):
        ''' Write data to the server '''
        serial_data = json.dumps(data).encode('utf-8')
        self.transport.write(serial_data)
