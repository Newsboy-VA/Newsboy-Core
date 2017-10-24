

import asyncio
import sys
import os.path
import logging
import inspect
import json
import argparse

from protocol_base import ClientProtocolBase
from action_base import ActionBase


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

        # [print(k, '|', v) for k, v in self.available_actions.items()]

        self.loop = asyncio.get_event_loop()

    def listen(self):
        ''' Start a connection with the virtual assistant '''
        coro = self.loop.create_connection(lambda: VAModuleProtocol(self),
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

    def assert_parameters(self, **kwargs):
        ''' Ensure the given parameters match their corresponding entities '''
        # action_args = sorted(self.arguments.keys())
        # TODO: This function

    def __call__(self, **kwargs):
        ''' Perform the given function '''
        self.assert_arguments(**kwargs)
        return self.function(**kwargs)


class VAModuleProtocol(ClientProtocolBase):
    async def request(self, client_name, action_dict):
        ''' Runs the given action '''
        available_actions = self.protocol_handler.available_actions
        action = available_actions[action_dict['function']]
        action(**action_dict['arguments'])
