

import asyncio
import sys
import os.path
import logging
import inspect
import json
import argparse
import traceback

from protocol_base import ClientProtocolBase
from action_base import ActionBase


class VAModuleBase(object):
    ''' A module which talks to the virtual assistant '''
    def __init__(self):
        self.path = os.path.dirname(inspect.getmodule(self).__file__)
        self.name = os.path.split(self.path)[-1]

        FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(message)s'
        logging.basicConfig(
            filename='info.log',
            level=logging.INFO,
            format=FORMAT,
            )

        parser = argparse.ArgumentParser(
            description='Start a module for the virtual assistant to use.')
        parser.add_argument('--host', type=str, default='localhost')
        parser.add_argument('--port', type=int, default=55802)

        args = parser.parse_args()

        self.available_actions = dict()
        self.update_available_actions()

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_connection(lambda: VAModuleProtocol(self),
                                           host=args.host,
                                           port=args.port)
        transport, self.protocol = self.loop.run_until_complete(coro)

    def __enter__(self):
        ''' Start a connection with the virtual assistant '''
        self.loop.run_forever()
        return self

    def __exit__(self, type, value, traceback):
        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

        logging.shutdown()

        if isinstance(value, KeyboardInterrupt):
            return True
        elif isinstance(value, ConnectionRefusedError):  # Doesn't seem to work
            print("No virtual assistant found")
            return True

    def background_tasks(self):
        ''' Perform all the background tasks that need to be done '''
        pass

    def send_to_client(self, client_name, message, priority=2):
        ''' Sends a message to the given client '''
        self.protocol.write_command(
            'send_to_client', [client_name, message, priority])

    def update_available_actions(self):
        ''' Register all actions from the json file '''

        actions_file = open(os.path.join(self.path, "actions.json"))
        self.actions_json = json.load(actions_file)['actions']
        actions_file.close()
        entities_file = open(os.path.join(self.path, "entities.json"))
        self.entities_json = json.load(entities_file)['entities']
        entities_file.close()

        for action_dict in self.actions_json:
            function_name = action_dict['function']
            function_handle = self.get_function_handle(function_name)

            action = Action(action_dict)
            action.set_function_handle(function_handle)
            action.find_argument_parameters(self.entities_json)
            self.available_actions[function_name] = action

    def get_function_handle(self, function_name):
        ''' Returns the function handle give a string of it's name '''
        return getattr(self, function_name)


class Action(ActionBase):
    ''' A class that can perform an action '''
    def assert_items(self):
        super().assert_items()
        assert(isinstance(self['name'], str))
        if 'synonyms' not in self:
            self['synonyms'] = []
        assert(isinstance(self['synonyms'], list))

    def set_function_handle(self, function_handle):
        ''' Sets the function handle '''
        self.function_handle = function_handle
        self.assert_entities()

    def find_argument_parameters(self, entities_json):
        ''' Create a dictionary of each argument with the parameters '''
        argument_dict = dict()

        for action_arg in self['arguments']:
            if action_arg == 'number':
                argument_dict[action_arg] = 'number'
            for entity in entities_json:
                if entity['name'] == action_arg:
                    # if isinstance(entity['parameters'], dict):
                    #     entity_list = entity['parameters'].keys()
                    # else:
                    #     entity_list = entity['parameters']
                    # argument_dict[action_arg] = entity_list
                    argument_dict[action_arg] = entity['parameters']

        self['arguments'] = argument_dict

    def assert_entities(self):
        ''' Ensure the action arguments match the json entities '''
        json_args = sorted(self['arguments'].keys())
        action_args = sorted(inspect.getargspec(self.function_handle)[0])
        action_args.remove('self')

        if action_args != json_args:
            raise AssertionError("Arguments for {} are {} instead of {}".format(
                self.name, action_args, json_args))

    def __call__(self, **kwargs):
        ''' Perform the given function '''
        try:
            self.assert_arguments(**kwargs)
            return self.function_handle(**kwargs)
        except:
            logging.exception("Unable to run command")


    def assert_arguments(self, **kwargs):
        ''' Ensure the given parameters match their corresponding entities '''
        # action_args = sorted(self.arguments.keys())
        # TODO: This function


class VAModuleProtocol(ClientProtocolBase):
    def connection_made(self, transport):
        ''' Callback when the module connects '''
        super().connection_made(transport)
        serializable_actions = []
        for action in self.protocol_handler.available_actions.values():
            action_dict = dict(action.items())
            serializable_actions.append(dict(action))
        self.write_command('set_actions', [serializable_actions])

    async def request(self, client_name, action_dict):
        ''' Runs the given action '''
        available_actions = self.protocol_handler.available_actions
        if action_dict['function'] not in available_actions:
            logging.error("{}: Module does not contain \"{}\"".format(
                self.name, action_dict['function']))
        else:
            action = available_actions[action_dict['function']]
            response = action(**action_dict['arguments'])
            self.write_command('response', [client_name, response])
