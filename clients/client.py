#!/usr/bin/env python3

import argparse
import socket

# import user_io


def main():
    ''' The main function to communicate to the virtual assistant '''
    parser = argparse.ArgumentParser(
        description='Begin a client to talk to the virtual assistant')
    parser.add_argument('--input-type', type=str, default="")
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--port', type=int, default=55802)
    parser.add_argument('--continuous', default=False, action="store_true")

    args = parser.parse_args()

    client = VAClient(args.host, args.port, args.input_type)
    while True:
        print(client.recv(), "")
    client.close()
    #
    # while True:
    #     text = speech_io.read()
    #     print(text)
    #     speech_io.write(text)
    #     speech_io.resume_reading()
    #
    # speech_io.stop_reading()


class VAClient(object):
    ''' A client object which talks to the virtual assistant '''
    def __init__(self, host, port, input_type):
        self.host = host
        self.port = port
        self.input_type = input_type

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(1)

        self.connection = VAServerConnection(self.socket)

    def send(self, string_data):
        ''' Sends data to the assistant '''
        self.connection.send(string_data)

    def recv(self):
        ''' Gets data from the assistant '''
        return self.connection.recv()

    def close(self):
        ''' Permanently closes the connection '''
        self.connection.close()

    def is_connected(self):
        ''' Checks to see if the assistant is still there '''
        return self.connection.is_connected()


class VAServerConnection(object):
    def __init__(self, socket):
        self.socket = socket

    def send(self, string_data):
        ''' Sends data to the assistant '''
        self.socket.send(string_data.encode("utf-8"))

    def recv(self):
        ''' Gets data from the assistant '''
        try:
            return self.socket.recv(1024).decode("utf-8")
        except socket.timeout:
            return None

    def close(self):
        ''' Permanently closes the connection '''
        self.socket.close()

    def is_connected(self):
        ''' Checks to see if the assistant is still there '''
        try:
            self.send("are you still there?")
            return True
        except (ConnectionResetError, BrokenPipeError):
            return False


if __name__ == "__main__":
    main()
