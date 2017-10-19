#!/usr/bin/env python3

import asyncio
import argparse

from client_communication import VAServerProtocol


class VirtualAssistant(object):

    def __init__(self, port):
        loop = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        coro = loop.create_server(VAServerProtocol,
                                  host='localhost',
                                  port=port)
        server = loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Start the Virtual Assistant Core.')
    parser.add_argument('--port', type=int, default=55801)
    # parser.add_argument('-logfn', type=str, default="/dev/null")
    # parser.add_argument('--input-source-index', type=int, default=0)

    args = parser.parse_args()

    VA = VirtualAssistant(args.port)
