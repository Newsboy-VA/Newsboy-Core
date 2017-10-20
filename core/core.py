#!/usr/bin/env python3

import asyncio
import sys
import argparse

from client_communication import VAClientHandler
from module_communication import VAModuleHandler


class VirtualAssistant(object):

    def __init__(self, port):
        self.loop = asyncio.get_event_loop()
        self.client_handler = VAClientHandler(port)
        self.module_handler = VAModuleHandler(port+1)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the servers
        client_handler.close()
        module_handler.close()

        if sys.version_info[1] >= 6:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Start the Virtual Assistant Core.')
    parser.add_argument('--port', type=int, default=55801)
    # parser.add_argument('-logfn', type=str, default="/dev/null")
    # parser.add_argument('--input-source-index', type=int, default=0)

    args = parser.parse_args()

    VA = VirtualAssistant(args.port)
