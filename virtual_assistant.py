#!/usr/bin/env python3

import asyncio
import sys
import os
import argparse


DEFAULT_CLIENT_PORT = 55801
DEFAULT_MODULE_PORT = 55802
DEFAULT_CORE_INPUT = 'text'
DEFAULT_CLIENT_INPUT = 'text'


def main():
    parser = argparse.ArgumentParser(
        description="Virtual Assistant Launcher",
        conflict_handler='resolve')
    subparsers = parser.add_subparsers()

    add_main_arguments(parser)
    add_core_arguments(subparsers)
    add_client_arguments(subparsers)
    add_modules_arguments(subparsers)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    # Load the modules into asyncio tasks
    args.func(args)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()

    if sys.version_info[1] >= 6:
        loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


def load_all(args):
    ''' Load everything '''
    load_core(args)
    load_client(args)
    load_modules(args)


def load_core(args):
    ''' Load the virtual assistant core '''
    print("Running core")
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.create_subprocess_exec(
        './core/core.py',
        '--port='+str(args.port)
        ))


def load_client(args):
    ''' Load an interface with the core '''
    print("Running client")
    loop = asyncio.get_event_loop()
    client_args = [
        './client/client.py',
        '--client-name='+args.client_name,
        '--host='+args.host,
        '--port='+str(args.port),
        '--input-type='+args.input_type,
    ]
    if args.continuous:
        client_args.append('--continuous')
    loop.create_task(asyncio.create_subprocess_exec(*client_args))


def load_modules(args):
    ''' Load one or more modules by themselves '''
    loop = asyncio.get_event_loop()
    modules_dir = 'modules'
    for listing in os.listdir(modules_dir):
        module_dir = os.path.join(modules_dir, listing)
        if os.path.isdir(module_dir):
            # print(module_dir)
            module_main = os.path.join(module_dir, "main.py")
            module_name = os.path.split(module_dir)[-1]
            if os.path.isfile(module_main):
                print("Running {} module".format(module_name))
                # print([module_main, args.host, args.port])
                loop.create_task(asyncio.create_subprocess_exec(
                    module_main,
                    '--host='+args.host,
                    '--port='+str(args.port)
                    ))
            else:
                print("Unable to run {} module".format(module_name))


def add_main_arguments(parser):
    ''' Launch the arguments of the main program '''
    parser.add_argument(
        '-P', '--port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port of the client handler",
        )
    # NOTE: The following may be different if you are starting just a client.
    parser.add_argument(
        '-I', '--input_type',
        choices=['text', 'sphinx', 'google'], default=DEFAULT_CORE_INPUT,
        help="Set how you want to interact with the assistant",
        )
    parser.set_defaults(
        func=load_all,
        host='localhost',
        client_name="main",
        continuous=True,
        all_modules=True,
        )


def add_core_arguments(subparsers):
    ''' If you want to start a core by itself '''
    core_parser = subparsers.add_parser(
        'core',
        description="Start the assistant core by itself",
        # help="",
        )
    core_parser.add_argument(
        '-P', '--port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port",
        )
    core_parser.set_defaults(func=load_core)


def add_client_arguments(subparsers):
    ''' If you want to start a client by itself '''
    client_parser = subparsers.add_parser(
        'client',
        description="Start a client by itself",
        # help="",
        )
    client_parser.add_argument(
        '--client-name',
        type=str, default='',
        help="Set the name of the client",
        )
    client_parser.add_argument(
        '-H', '--host',
        type=str, default='localhost',
        help="Set the IP of the assistant",
        )
    client_parser.add_argument(
        '-P', '--port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port of the client handler",
        )
        # NOTE: The following may be different if you are also starting the core.
    client_parser.add_argument(
        '-I', '--input_type',
        choices=['text', 'sphinx', 'google'], default=DEFAULT_CLIENT_INPUT,
        help="Set how you want to interact with the assistant",
        )
    # NOTE: The following default is 'True' as opposed to the client.py default
    #       which is 'False'.
    client_parser.add_argument(
        '-C', '--continuous',
        default=False, action='store_true',
        help="Whether or not to run more than one command",
        )
    client_parser.add_argument(
        'input_text',
        type=str, nargs='*',
        help="A command to give the assistant",
        )

    client_parser.set_defaults(func=load_client)


def add_modules_arguments(subparsers):
    ''' If you want to start one or more modules by themselves '''
    module_parser = subparsers.add_parser(
        'modules',
        description="Start one or more modules by themselves",
        # help="",
        )
    module_parser.add_argument(
        '-A', '--all_modules',
        default=False, action='store_true',
        help="Start all the modules",
        )
    module_parser.add_argument(
        '-H', '--host',
        type=str, default='localhost',
        help="Set the IP of the assistant",
        )
    module_parser.add_argument(
        '-P', '--port',
        type=int, default=DEFAULT_MODULE_PORT,
        help="Set the port of the module handler",
        )
    module_parser.add_argument(
        'module',
        type=str, nargs='*',
        help="The modules you want to start",
        )
    module_parser.set_defaults(func=load_modules)


if __name__ == "__main__":
    main()
