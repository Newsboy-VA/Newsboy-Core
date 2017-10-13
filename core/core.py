#!/usr/bin/env python3

from client_communication import VAServer

import argparse


class VirtualAssistant(object):

    def __init__(self, port):
        self.server = VAServer(host='', port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Start the Virtual Assistant Core.')
    parser.add_argument('--port', type=int, default=55801)
    # parser.add_argument('-logfn', type=str, default="/dev/null")
    # parser.add_argument('--input-source-index', type=int, default=0)

    args = parser.parse_args()

    VA = VirtualAssistant(args.port)
