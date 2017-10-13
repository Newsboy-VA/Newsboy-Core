#!/usr/bin/env python3

import socket

import user_io

import argparse


class VAClient(object):
    ''' A client object which talks to the virtual assistant '''
    def __init__(self, host, port, io_method):
        self.host = host
        self.port = port
        self.io_method = io_method
        if io_method == "text":
            self.io_handle = user_io.TextIO()
        elif io_method == "speech":
            self.io_handle = user_io.SpeechIO()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(1)

        self.connection = VAServerConnection(self.socket)

        while True:
            # self.server_write(self.user_read())
            self.user_write(self.server_read())
        self.close()

    def user_write(self, string_data):
        ''' Sends data to the user '''
        self.io_handle.write(string_data)

    def user_read(self):
        ''' Gets data from the user '''
        return self.io_handle.read()

    def server_write(self, string_data):
        ''' Sends data to the assistant '''
        self.connection.send(string_data)

    def server_read(self):
        ''' Gets data from the assistant '''
        return self.connection.recv()

    def server_close(self):
        ''' Permanently closes the connection '''
        self.connection.close()

    def server_is_connected(self):
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
    parser = argparse.ArgumentParser(
        description='Start a client to connect to the Virtual Assistant.')
    parser.add_argument('--io-method', type=str, default="text")
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--port', type=int, default=55801)
    parser.add_argument('--continuous', default=False, action="store_true")

    args = parser.parse_args()

    client = VAClient(args.host, args.port, args.io_method)
