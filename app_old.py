#
# Accelerometer server.
#
# SensorStreamer [Jan Mrázek]
#     https://play.google.com/store/apps/details?id=cz.honzamrazek.sensorstreamer
#     https://github.com/yaqwsx/SensorStreamer
#
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

import socket
import struct

from matplotlib import figure
from matplotlib import lines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from math import sqrt

from collections import deque

# Constants.
APP_NAME = "Accelerometer server"
REFRESH_TIMEOUT = 10  # ms
SERVER_PORT = 7000
SERVER_TIMEOUT = 5  # s
SAMPLES = 1000


def random_list():
    return map(lambda x: x / 2, range(SAMPLES))


def hpf(sv):
    return 0


def sv_maxmin():
    return 0


#
# Application.
#
class App:
    def __init__(self):
        self.init_window()

        self.state = {
            "parameters": {
                "sv": 0,
                "sv_d": 0,
                "sv_maxmin": 0,
            },
            "plot": {
                "t": deque(random_list(), maxlen=SAMPLES),
                "acc_x": deque(random_list(), maxlen=SAMPLES),
                "acc_y": deque(random_list(), maxlen=SAMPLES),
                "acc_z": deque(random_list(), maxlen=SAMPLES),
                "fall_interval": None,
            },
            "connection": None,
        }

        self.init_widgets()
        self.init_plot()

        # Initialize variables.
        self.running = False
        self.client = None
        self.socket = None

        # Run main loop.
        self.window.mainloop()

    def init_window(self):
        self.window = tk.Tk()
        self.window.title(APP_NAME)
        self.window.minsize(800, 600)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.protocol("WM_DELETE_WINDOW", self.close_event)

    def init_widgets(self):
        # Right frame.
        left_frame = ttk.Frame(self.window)
        left_frame.grid(column=0, row=0, padx=5, pady=5, sticky="nswe")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Text console.
        label1 = ttk.Label(left_frame, text="Salida")
        label1.grid(column=0, row=0, sticky="w")

        self.text_console = scrolledtext.ScrolledText(left_frame, state="disabled")
        self.text_console.grid(column=0, row=1, sticky="nswe")

        # Separator.
        separator1 = ttk.Separator(self.window, orient="vertical")
        separator1.grid(column=1, row=0, pady=5, sticky="ns")

        # Right frame.
        right_frame = ttk.Frame(self.window)
        right_frame.grid(column=2, row=0, padx=5, pady=5, sticky="ns")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(4, weight=1)

        # Controls.
        self.button_start = ttk.Button(
            right_frame, text="Inicia", command=self.start_event
        )
        self.button_start.grid(column=0, row=0, pady=5, sticky="we")

        self.button_stop = ttk.Button(
            right_frame, text="Para", command=self.stop_event, state="disabled"
        )
        self.button_stop.grid(column=0, row=1, pady=5, sticky="we")

        # Connection status
        self.connection_status = ttk.Label(right_frame, text="Default")
        self.connection_status.grid(column=0, row=2)

        self.update_conn_status(None)

        # Impact status
        self.impact_status = ttk.Label(right_frame, text="Default")
        self.impact_status.grid(column=0, row=3)

    def init_plot(self):
        self.line_x = lines.Line2D(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_x"]), color="r"
        )
        self.line_y = lines.Line2D(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_y"]), color="g"
        )
        self.line_z = lines.Line2D(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_z"]), color="b"
        )

        # Canvas.
        fig = figure.Figure()

        self.plot = fig.add_subplot()
        self.plot.set_xlabel("Time")
        self.plot.set_ylabel("Acceleration")

        self.plot.add_line(self.line_x)
        self.plot.add_line(self.line_y)
        self.plot.add_line(self.line_z)
        self.plot.set_xlim(0, SAMPLES)
        self.plot.set_ylim(-15, 15)

        self.canvas = FigureCanvasTkAgg(fig, self.window)
        self.canvas.get_tk_widget().grid(
            column=0, row=1, columnspan=3, padx=5, pady=5, sticky="nswe"
        )

    def close_event(self):
        # If already running.
        if self.running:
            # Stop timer.
            self.running = False
            # Close TCP client connection.
            self.client.close()
            # Close TCP socket.
            self.socket.close()

        # Accept close event.
        self.window.withdraw()

    def refresh_event(self):
        # Return if not running.
        if not self.running:
            return

        # Try to receive data from TCP client connection.
        # try:
        #     # data = self.client.recv(1024)
        # except socket.error:
        #     data = []

        # x, y, z = self.parse_data(data)
        x, y, z = 0, 0, 0
        self.update_parameters(x, y, z)

        self.impact = self.detect_impact()

        self.update_impact_status()
        self.update_plot(x, y, z)
        self.update_console(f"{x:.2f} {y:.2f} {z:.2f}\n")

        # Restart timer.
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)

    def parse_data(self, data):
        # Find start mark in data.
        try:
            i = data.index(0x80)
        except ValueError:
            i = -1

        # Get acceleration samples from data.
        if 0 <= i < (len(data) - 12):
            return struct.unpack("!fff", bytearray(data[i + 1 : i + 1 + 12]))

    def update_parameters(self, x, y, z):
        sv = sqrt(x**2 + y**2 + z**2)
        self.state["parameters"]["sv"] = sv
        self.state["parameters"]["sv_d"] = hpf(sv)
        self.state["parameters"]["sv_maxmin"] = sv_maxmin()

    def detect_impact(self):
        return True

    def update_impact_status(self):
        self.impact_status.config(text="Impact: {}".format(self.impact))

    def update_console(self, text):
        self.text_console.configure(state="normal")
        self.text_console.insert(tk.END, text)
        self.text_console.configure(state="disabled")
        self.text_console.see(tk.END)

    def update_plot(self, x, y, z):
        # Increase and check sample time.
        t = list(self.state["plot"]["t"])[-1] + 1

        # Append new sample.
        self.state["plot"]["t"].append(t)
        self.state["plot"]["acc_x"].append(x)
        self.state["plot"]["acc_y"].append(y)
        self.state["plot"]["acc_z"].append(z)

        # Update plot.
        self.line_x.set_data(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_x"])
        )
        self.line_y.set_data(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_y"])
        )
        self.line_z.set_data(
            list(self.state["plot"]["t"]), list(self.state["plot"]["acc_z"])
        )

        self.canvas.draw_idle()

    def update_conn_status(self, addr):
        self.state["connection"] = addr
        text = ""
        if addr is None:
            text = "Connection Status: Disconnected"
        else:
            text = "Connection Status: Connected\n{}:{}".format(addr[0], addr[1])
        self.connection_status.config(text=text)

    def start_event(self):
        # self.init_socket()

        # Start timer.
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)
        self.running = True

        # Update UI.
        self.button_start.configure(state="disabled")
        self.button_stop.configure(state="normal")

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(SERVER_TIMEOUT)
        self.socket.bind(("", SERVER_PORT))
        self.socket.listen(1)
        try:
            self.client, addr = self.socket.accept()
            self.update_conn_status(addr)
            self.update_console(f"Cliente conectado ({addr[0]})\n")
        except socket.error:
            messagebox.showerror(
                APP_NAME,
                "No se ha conectado ningún cliente al puerto " + str(SERVER_PORT),
            )
            return

    def stop_event(self):
        # Stop timer.
        self.running = False

        # Close TCP client connection.
        self.client.close()

        # Close TCP socket.
        self.socket.close()

        # Update UI.
        self.button_start.configure(state="normal")
        self.button_stop.configure(state="disabled")


#
# Main.
#
App()
