import socket
import struct

SERVER_PORT = 7000
SERVER_TIMEOUT = 5  # s

class AccelerometerSensor: #TODO: add callbacks to sensor to update frontend
    def __init__(self):
        self.socket = None
        self.client = None
        self.addr = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(SERVER_TIMEOUT)
        self.socket.bind(("", SERVER_PORT))
        self.socket.listen(1)

    def init(self):
        self.client, self.addr = self.socket.accept()

    def close(self):
        self.client.close()

    def read(self):
        # Try to receive data from TCP client connection.
        try:
            data = self.client.recv(1024)
            return AccelerometerSensor.parse(data)
        except socket.error:
            raise socket.error


    @staticmethod
    def parse(data):
        # Find start mark in data.
        try:
            i = data.index(0x80)
        except ValueError:
            i = -1

        # Get acceleration samples from data.
        if 0 <= i < (len(data) - 12):
            return struct.unpack("!fff", bytearray(data[i + 1 : i + 1 + 12]))
