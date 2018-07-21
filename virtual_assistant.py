#!/usr/bin/env python3

import argparse
import subprocess
import logging
import os
import stat
import time


DEFAULT_CLIENT_PORT = 55801
DEFAULT_MODULE_PORT = 55802
DEFAULT_CORE_INPUT = 'text'
DEFAULT_CLIENT_INPUT = 'text'
DEFAULT_LOGGING_LEVEL = 'INFO'


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
    processes = args.func(args)

    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()


def load_all(args):
    ''' Load everything '''
    processes = []
    processes.extend(load_core(args))
    time.sleep(0.1)
    processes.extend(load_modules(args))
    processes.extend(load_client(args))

    return processes


def load_core(args):
    ''' Load the virtual assistant core '''
    print("Running core")
    processes = []
    processes.append(subprocess.Popen([
        './core/core.py',
        '--port='+str(args.client_port),
        '--log-level='+args.log_level,
        ]))

    return processes


def load_client(args):
    ''' Load an interface with the core '''
    print("Running client")
    processes = []
    client_args = [
        './client/client.py',
        '--client-name='+args.client_name,
        '--host='+args.host,
        '--port='+str(args.client_port),
        '--input-type='+args.input_type,
        '--log-level='+args.log_level,
    ]
    if args.continuous:
        client_args.append('--continuous')
    processes.append(subprocess.Popen(client_args))

    return processes


def load_modules(args):
    ''' Load one or more modules by themselves '''
    processes = []

    modules_dir = 'modules'
    for listing in os.listdir(modules_dir):
        module_dir = os.path.join(modules_dir, listing)
        if os.path.isdir(module_dir):
            # print(module_dir)
            module_main = os.path.join(module_dir, "main.py")
            module_name = os.path.split(module_dir)[-1]
            if os.path.isfile(module_main):
                if not os.access(module_main, os.X_OK):
                    # The main file isn't executable
                    print("Making {} executable".format(module_main))
                    curr_mode = os.stat(module_main).st_mode
                    os.chmod(module_main, curr_mode | 0o111)  #stat.S_IEXEC)
                print("Running {} module".format(module_name))
                # print([module_main, args.host, args.module_port])
                processes.append(subprocess.Popen([
                    module_main,
                    '--host='+args.host,
                    '--port='+str(args.module_port),
                    '--log-level='+args.log_level,
                    ]))
            else:
                print("Unable to run {} module".format(module_name))

    return processes


def add_main_arguments(parser):
    ''' Launch the arguments of the main program '''
    parser.add_argument(
        '-P', '--client-port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port of the client handler",
        )
    parser.add_argument(
        '-M', '--module-port',
        type=int, default=DEFAULT_MODULE_PORT,
        help="Set the port of the module handler",
        )
    # NOTE: The following may be different if you are starting just a client.
    parser.add_argument(
        '-I', '--input-type',
        choices=['text', 'sphinx', 'google'], default=DEFAULT_CORE_INPUT,
        help="Set how you want to interact with the assistant",
        )
    parser.set_defaults(
        func=load_all,
        host='localhost',
        client_name="main",
        continuous=True,
        )


def add_core_arguments(subparsers):
    ''' If you want to start a core by itself '''
    core_parser = subparsers.add_parser(
        'core',
        description="Start the assistant core by itself",
        # help="",
        )
    core_parser.add_argument(
        '-P', '--client-port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port of the client handler",
        )
    core_parser.add_argument(
        '-M', '--module-port',
        type=int, default=DEFAULT_MODULE_PORT,
        help="Set the port of the module handler",
        )
    core_parser.add_argument(
        '--log-level',
        type=str.upper,
        choices=logging._levelToName.values(), default=DEFAULT_LOGGING_LEVEL,
        help="Set which logging level to save",
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
        '-P', '--client-port',
        type=int, default=DEFAULT_CLIENT_PORT,
        help="Set the port of the client handler",
        )
    # NOTE: The following may be different if you are also starting the core.
    client_parser.add_argument(
        '-I', '--input-type',
        choices=['text', 'sphinx', 'google'], default=DEFAULT_CLIENT_INPUT,
        help="Set how you want to interact with the assistant",
        )
    client_parser.add_argument(
        '--log-level',
        type=str.upper,
        choices=logging._levelToName.values(), default=DEFAULT_LOGGING_LEVEL,
        help="Set which logging level to save",
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
    # module_parser.add_argument(
    #     '-A', '--all_modules',
    #     default=False, action='store_true',
    #     help="Start all the modules",
    #     )
    module_parser.add_argument(
        '-H', '--host',
        type=str, default='localhost',
        help="Set the IP of the assistant",
        )
    module_parser.add_argument(
        '-M', '--module-port',
        type=int, default=DEFAULT_MODULE_PORT,
        help="Set the port of the module handler",
        )
    # module_parser.add_argument(
    #     'module',
    #     type=str, nargs='*',
    #     help="The modules you want to start",
    #     )
    module_parser.add_argument(
        '--log-level',
        type=str.upper,
        choices=logging._levelToName.values(), default=DEFAULT_LOGGING_LEVEL,
        help="Set which logging level to save",
        )
    module_parser.set_defaults(func=load_modules)


if __name__ == "__main__":
    main()
