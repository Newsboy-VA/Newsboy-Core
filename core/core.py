#!/usr/bin/env python3

import asyncio
import sys
import logging
import argparse

from client_communication import VAClientHandler
from module_communication import VAModuleHandler


class VirtualAssistant(object):

    def __init__(self, port):
        self.loop = asyncio.get_event_loop()
        self.client_handler = VAClientHandler(self, port)
        self.module_handler = VAModuleHandler(self, port+1)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            # Close the servers
            self.client_handler.close()
            self.module_handler.close()
            self.loop.stop()

        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(levelname)-5s (PID %(process)d) %(message)s'
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format=FORMAT,
        )

    parser = argparse.ArgumentParser(
        description='Start the Virtual Assistant Core.')
    parser.add_argument('--port', type=int, default=55801)

    args = parser.parse_args()

    VA = VirtualAssistant(args.port)

    logging.shutdown()
