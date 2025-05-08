"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    db = {
        "Patty": "+49696969",
        "Chrissy R": "+49420110",
        "Björn": "+4900000"
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                self._logger.info(f"New connection established: {str(connection)}")
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    command = data.decode('utf-8')
                    self._logger.info(f"Got command '{command}' from connection {str(connection)}")
                    
                    response = self.handle_command(command).encode('utf-8')
                    connection.sendall(response + b'\0')  # Append a null byte to signal the end of the message
                self._logger.info(f"Closing connection: {str(connection)}")
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

    def handle_command(self, command):
        if command.startswith("GET "):
            name = " ".join(command.split(" ")[1:])
            if name == "":
                return 'ERROR: Der Name darf nicht leer sein'
            else:
                return self.build_output(name)
        elif command == 'GETALL':
            return "\n".join(self.build_output(key) for key in self.db.keys())

        return "ERROR: Unbekannter Befehl"

    def build_output(self, key):
        if not key in self.db:
            return f"ERROR: Nutzer {key} in Datenbank nicht gefunden"
        number = self.db[key]
        return key + ": " + number


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        data = b""
        while True:
            chunk = self.sock.recv(1024)  # receive the response in chunks
            if b'\0' in chunk:  # Check for the null byte signaling the end of the message
                data += chunk.replace(b'\0', b'')  # Remove the null byte
                break
            data += chunk
        msg_out = data.decode('utf-8')
        self.logger.info(f"Received message from server:\n\n{msg_out}")  # print the result
        #self.sock.close()  # close the connection
        #self.logger.info("Client down.")
        return msg_out
    
    def get(self, name):
        self.call(f"GET {name}")

    def getall(self):
        self.call("GETALL")

    def close(self):
        """ Close socket """
        self.sock.close()
        self.logger.info("Socket closed")
