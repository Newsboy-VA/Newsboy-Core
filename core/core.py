#!/usr/bin/env python3

import asyncio
import sys
import logging
import argparse

from nlu import NLU
from client_communication import VAClientHandler
from module_communication import VAModuleHandler


class VirtualAssistant(object):
    '''  '''
    def __init__(self):
        FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(message)s'
        logging.basicConfig(
            filename='info.log',
            level=logging.INFO,
            format=FORMAT,
            )

        parser = argparse.ArgumentParser(
            description='Start the Virtual Assistant Core.')
        parser.add_argument('--port', type=int, default=55801)
        args = parser.parse_args()

        self.loop = asyncio.get_event_loop()
        
        self.nlu = NLU()
        self.client_handler = VAClientHandler(self, args.port)
        self.module_handler = VAModuleHandler(self, args.port+1)

    def __enter__(self):
        self.loop.run_forever()
        return self

    def __exit__(self, type, value, traceback):
        logging.info("Shutting down...")
        # Close the servers
        self.client_handler.close()
        self.module_handler.close()
        self.loop.stop()

        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()
        logging.shutdown()

        return isinstance(value, KeyboardInterrupt)


if __name__ == "__main__":
    with VirtualAssistant() as VA:
        pass
