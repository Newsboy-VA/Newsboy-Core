

import threading
import socket


class VAServer(object):
    ''' A server object which talks to all clients '''
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.client_dict = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.settimeout(1)

        self.check_connections_end = False
        self.check_connections_thread = threading.Thread(
            target=self.check_connections)
        self.check_connections_thread.start()

    def check_connections(self):
        ''' Handle the coming and going of connections '''
        while not self.check_connections_end:
            # Check for new connections
            try:
                new_conn, new_addr = self.socket.accept()
                self.add_client(new_addr, new_conn)

            except socket.timeout:
                pass

            # Check which connections are still there
            bad_addresses = []
            for client_id, client in self.client_dict.items():
                if not client.is_connected():
                    bad_addresses.append(client_id)

            # Remove addresses which have disconnected
            for client_id in bad_addresses:
                self.remove_client(client_id)

        self.close()

    def end_check_connections(self):
        ''' Gracefully ends the connections thread when it can '''
        self.check_connections_end = True

    def add_client(self, client_id, conn):
        ''' Adds a client '''
        client_connection = VAClientConnection(client_id, conn)
        self.client_dict[client_id] = VAClientHandler(client_connection)
        print(client_id, "connected")

    def remove_client(self, client_id):
        ''' Removes a client '''
        self.client_dict[client_id].end_conversation_handler()
        self.client_dict.pop(client_id)
        print(client_id, "disconnected")

    def close(self):
        ''' Permanently closes the socket '''
        self.socket.close()


class VAClientConnection(object):
    def __init__(self, client_id, conn):
        self.client_id = client_id
        self.conn = conn

    def send(self, string_data):
        ''' Sends data to the client '''
        self.conn.send(string_data.encode("utf-8"))

    def recv(self):
        ''' Gets data from the client '''
        try:
            return self.conn.recv(1024).decode("utf-8")
        except socket.timeout:
            return None

    def is_connected(self):
        ''' Checks to see if the client is still there '''
        try:
            self.send("are you still there?")
            return True
        except (ConnectionResetError, BrokenPipeError):
            return False


class VAClientHandler(object):
    def __init__(self, connection, continuous=False):
        self.connection = connection
        self.continuous = continuous

        self.conversation_handler_end = False
        self.conversation_handler_thread = threading.Thread(
            target=self.conversation_handler)
        self.conversation_handler_thread.start()

    def conversation_handler(self):
        ''' The thread that continuously talks with the client '''
        while not self.conversation_handler_end:
            # conversation = Conversation(self.client_connection)

            # Wait for module ack

            if not self.continuous:
                self.conversation_handler_end = True

    def end_conversation_handler(self):
        ''' Gracefully ends the conversation thread when it can '''
        self.conversation_handler_end = True

    def send(self, string_data):
        ''' Sends data to the client '''
        self.connection.send()

    def recv(self):
        ''' Gets data from the client '''
        return self.connection.recv()

    def is_connected(self):
        ''' Checks to see if the client is still there '''
        return self.connection.is_connected()
