import socket
import struct

SERVER_PORT = 7000
SERVER_TIMEOUT = 5  # s


class AccelerometerSensor:
    def __init__(self):
        self.socket = None
        self.client = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(SERVER_TIMEOUT)
        self.socket.bind(("", SERVER_PORT))

    def init():
        self.socket.listen(1)
        try:
            self.client, addr = self.socket.accept()
            self.update_conn_status(addr)
            self.update_console(f"Cliente conectado ({addr[0]})\n")
        except socket.error:
            print("error creating socket")
            # messagebox.showerror(
            #     APP_NAME,
            #     "No se ha conectado ningún cliente al puerto " + str(SERVER_PORT),
            # )
            return

    def read():
        # Try to receive data from TCP client connection.
        try:
            data = self.client.recv(1024)
        except socket.error:
            data = []

        return self.parse(data)

    def parse(data):
        # Find start mark in data.
        try:
            i = data.index(0x80)
        except ValueError:
            i = -1

        # Get acceleration samples from data.
        if 0 <= i < (len(data) - 12):
            return struct.unpack("!fff", bytearray(data[i + 1 : i + 1 + 12]))
