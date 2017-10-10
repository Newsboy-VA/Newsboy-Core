

import socket


class VAServer(object):
    ''' A server object which talks to all clients '''
    def __init__(self, host='', port=55801):
        self.host = host
        self.port = port

        self.client_dict = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.settimeout(1)

    def check_connections(self):
        ''' Handle the coming and going of connections '''
        # Check for new connections
        try:
            new_conn, new_addr = self.socket.accept()
            self.add_client(new_addr, new_conn)

        except socket.timeout:
            pass

        # Check which connections are still there
        bad_addresses = []
        for client in self.client_dict.values():
            try:
                client.send("are you still there?")
            except (ConnectionResetError, BrokenPipeError):
                bad_addresses.append(client.client_id)

        # Remove addresses which have disconnected
        for client_id in bad_addresses:
            self.remove_client(client_id)

    def add_client(self, client_id, conn):
        ''' Adds a client '''
        self.client_dict[client_id] = VAClientHandler(client_id, conn)
        print(client_id, "connected")

    def remove_client(self, client_id):
        ''' Removes a client '''
        self.client_dict.pop(client_id)
        print(client_id, "disconnected")

    def close(self):
        ''' Permanently closes the socket '''
        self.socket.close()


class VAClientHandler(object):
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
            return ""
