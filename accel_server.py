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


# Constants.
APP_NAME        = "Accelerometer server"
REFRESH_TIMEOUT = 10  # ms
SERVER_PORT     = 7000
SERVER_TIMEOUT  = 5   # s
SAMPLES         = 1000


#
# Application.
#
class App:
    def __init__(self):
        # Create window.
        self.window = tk.Tk()
        self.window.title(APP_NAME)
        self.window.minsize(800, 600)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.protocol("WM_DELETE_WINDOW", self.close_event)

        # Create widgets.
        self.create_widgets()

        # Create plot.
        self.create_plot()

        # Initialize variables.
        self.running = False
        self.client = None
        self.socket = None
        self.data_t = None
        self.data_x = None
        self.data_y = None
        self.data_z = None

        # Run main loop.
        self.window.mainloop()


    def create_widgets(self):
        # Right frame.
        frame1 = ttk.Frame(self.window)
        frame1.grid(column=0, row=0, padx=5, pady=5, sticky="nswe")
        frame1.columnconfigure(0, weight=1)
        frame1.rowconfigure(1, weight=1)

        # Text console.
        label1 = ttk.Label(frame1, text="Salida")
        label1.grid(column=0, row=0, sticky="w")

        self.text_console = scrolledtext.ScrolledText(frame1, state="disabled")
        self.text_console.grid(column=0, row=1, sticky="nswe")

        # Separator.
        separator1 = ttk.Separator(self.window, orient="vertical")
        separator1.grid(column=1, row=0, pady=5, sticky="ns")

        # Left frame.
        frame2 = ttk.Frame(self.window)
        frame2.grid(column=2, row=0, padx=5, pady=5, sticky="ns")
        frame2.columnconfigure(0, weight=1)
        frame2.rowconfigure(4, weight=1)

        # Controls.
        self.button_start = ttk.Button(frame2, text="Inicia",
                                       command=self.start_event)
        self.button_start.grid(column=0, row=0, pady=5, sticky="we")

        self.button_stop = ttk.Button(frame2, text="Para",
                                      command=self.stop_event, state="disabled")
        self.button_stop.grid(column=0, row=1, pady=5, sticky="we")


    def create_plot(self):
        # Data samples.
        self.data_t = [0]
        self.data_x = [0]
        self.data_y = [0]
        self.data_z = [0]

        # Lines.
        self.line_x = lines.Line2D(self.data_t, self.data_x, color="r")
        self.line_y = lines.Line2D(self.data_t, self.data_y, color="g")
        self.line_z = lines.Line2D(self.data_t, self.data_z, color="b")

        # Canvas.
        fig = figure.Figure()

        plot = fig.add_subplot()
        plot.add_line(self.line_x)
        plot.add_line(self.line_y)
        plot.add_line(self.line_z)
        plot.set_xlim(0, SAMPLES)
        plot.set_ylim(-15, 15)

        self.canvas = FigureCanvasTkAgg(fig, self.window)
        self.canvas.get_tk_widget().grid(column=0, row=1, columnspan=3,
                                         padx=5, pady=5, sticky="nswe")


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


    def draw_samples(self, x, y, z):
        # Increase and check sample time.
        t = self.data_t[-1] + 1
        if t >= SAMPLES:
            t = 0
            self.data_t.clear()
            self.data_x.clear()
            self.data_y.clear()
            self.data_z.clear()

        # Append new sample.
        self.data_t.append(t)
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_z.append(z)

        # Update plot.
        self.line_x.set_data(self.data_t, self.data_x)
        self.line_y.set_data(self.data_t, self.data_y)
        self.line_z.set_data(self.data_t, self.data_z)
        self.canvas.draw_idle()


    def refresh_event(self):
        # Return if not running.
        if not self.running:
            return

        # Try to receive data from TCP client connection.
        try:
            data = self.client.recv(1024)
        except socket.error:
            data = []

        # Find start mark in data.
        try:
            i = data.index(0x80)
        except ValueError:
            i = -1

        # Get acceleration samples from data.
        if 0 <= i < (len(data) - 12):
            x, y, z = struct.unpack("!fff", bytearray(data[i+1:i+1+12]))
            # Draw acceleration samples
            self.draw_samples(x, y, z)
            # Show acceleration samples at the end of text console.
            text = f"{x:.2f} {y:.2f} {z:.2f}\n"
            self.text_console.configure(state="normal")
            self.text_console.insert(tk.END, text)
            self.text_console.configure(state="disabled")
            self.text_console.see(tk.END)

        # Restart timer.
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)


    def start_event(self):
        # Try to accept connection from TCP client.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(SERVER_TIMEOUT)
        self.socket.bind(("", SERVER_PORT))
        self.socket.listen(1)
        try:
            self.client, addr = self.socket.accept()
        except socket.error:
            messagebox.showerror(APP_NAME, "No se ha conectado ningún cliente al puerto " +
                                 str(SERVER_PORT))
            return

        # Reset data samples.
        self.data_t = [0]
        self.data_x = [0]
        self.data_y = [0]
        self.data_z = [0]

        # Clear and show client connection in the text console.
        self.text_console.configure(state="normal")
        self.text_console.delete(1.0, tk.END)
        self.text_console.insert(tk.END, f"Cliente conectado ({addr[0]})\n")
        self.text_console.configure(state="disabled")

        # Start timer.
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)
        self.running = True

        # Update UI.
        self.button_start.configure(state="disabled")
        self.button_stop.configure(state="normal")


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
