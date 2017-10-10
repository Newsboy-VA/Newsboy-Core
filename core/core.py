#!/usr/bin/env python3

# import argparse

from client_communication import VAServer


def main():
    ''' This is the main function of the virtual assistant '''
    server = VAServer()
    while True:
        server.check_connections()
    server.close()


if __name__ == "__main__":
    main()
