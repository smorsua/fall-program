import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

from matplotlib import figure
from matplotlib import lines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from collections import deque
import more_itertools as mit

APP_NAME = "Accelerometer server"
REFRESH_TIMEOUT = 10  # ms
SAMPLES = 100


def random_list():
    return map(lambda x: x / 2, range(SAMPLES))


class Frontend:  # TODO: instead of having a run function, i can pass the callbacks as constructor parameters
    def __init__(self):
        self.window = None
        self.text_console = None
        self.button_start = None
        self.button_stop = None
        self.connection_status = None
        self.impact_status = None
        self.start_cb = None
        self.refresh_cb = None
        self.stop_cb = None
        self.plot = None

        self.init_window()
        self.init_widgets()
        self.init_plot()  # TODO: init_plot should be inside init_widgets

    def run(self):
        self.window.mainloop()

    def init_window(self):
        self.window = tk.Tk()
        self.window.title(APP_NAME)
        self.window.minsize(800, 600)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.protocol("WM_DELETE_WINDOW", self.stop_event)

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

        # Impact status
        self.impact_status = ttk.Label(right_frame, text="Default")
        self.impact_status.grid(column=0, row=3)

    def init_plot(self):
        data = {
            "t": deque( maxlen=SAMPLES),
            "acc_x": deque( maxlen=SAMPLES),
            "acc_y": deque( maxlen=SAMPLES),
            "acc_z": deque( maxlen=SAMPLES),
        }

        line_x = lines.Line2D(list(data["t"]), list(data["acc_x"]), color="r")
        line_y = lines.Line2D(list(data["t"]), list(data["acc_y"]), color="g")
        line_z = lines.Line2D(list(data["t"]), list(data["acc_z"]), color="b")

        # Canvas.
        fig = figure.Figure()
        plot = fig.add_subplot()
        plot.set_xlabel("Time")
        plot.set_ylabel("Acceleration")

        plot.add_line(line_x)
        plot.add_line(line_y)
        plot.add_line(line_z)
        plot.set_xlim(0, SAMPLES)
        plot.set_ylim(-15, 15)

        canvas = FigureCanvasTkAgg(fig, self.window)
        canvas.get_tk_widget().grid(
            column=0, row=1, columnspan=3, padx=5, pady=5, sticky="nswe"
        )

        self.plot = {
            "canvas": canvas,
            "component": plot,
            "line_x": line_x,
            "line_y": line_y,
            "line_z": line_z,
            "data": data,
        }

    def start_event(self):
        # Start timer.
        self.start_cb(self)
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)
        self.running = True

        # Update UI.
        self.button_start.configure(state="disabled")
        self.button_stop.configure(state="normal")

    def set_start_cb(self, fn):
        self.start_cb = fn

    def set_refresh_cb(self, fn):
        self.refresh_cb = fn

    def set_stop_cb(self, fn):
        self.stop_cb = fn

    def refresh_event(self):
        # Return if not running.
        if not self.running:
            return

        self.refresh_cb(self)

        # Restart timer.
        self.window.after(REFRESH_TIMEOUT, self.refresh_event)

    def stop_event(self):
        self.stop_cb()
        # Stop timer.
        self.running = False

        # TODO: add close_callback and close the socket and client

        # Update UI.
        self.button_start.configure(state="normal")
        self.button_stop.configure(state="disabled")

    def update(self, fall_data):
        self.update_impact_status(fall_data["is_impact"])
        self.update_console("x: {:.2f} y: {:.2f} z: {:.2f}\n".format(fall_data["sample"][0],fall_data["sample"][1],fall_data["sample"][2]))
        self.update_plot(fall_data["sample"])

    def update_impact_status(self, is_impact):
        self.impact_status.config(text="Impact: {}".format(is_impact))

    def update_console(self, text):
        self.text_console.configure(state="normal")
        self.text_console.insert(tk.END, text)
        self.text_console.configure(state="disabled")
        self.text_console.see(tk.END)

    def update_plot(self, sample):
        # Increase and check sample time.
        t = mit.last(self.plot["data"]["t"], 0) + 1
        # t = list(self.plot["data"]["t"])[-1] + 1

        # Append new sample.
        self.plot["data"]["t"].append(t)
        self.plot["data"]["acc_x"].append(sample[0])
        self.plot["data"]["acc_y"].append(sample[1])
        self.plot["data"]["acc_z"].append(sample[2])

        # Update plot.
        self.plot["line_x"].set_data(
            list(self.plot["data"]["t"]), list(self.plot["data"]["acc_x"])
        )
        self.plot["line_y"].set_data(
            list(self.plot["data"]["t"]), list(self.plot["data"]["acc_y"])
        )
        self.plot["line_z"].set_data(
            list(self.plot["data"]["t"]), list(self.plot["data"]["acc_z"])
        )
        
        self.plot["component"].set_xlim(self.plot["data"]["t"][0], self.plot["data"]["t"][0]+SAMPLES-1)

        self.plot["canvas"].draw_idle()

    def update_conn_status(self, addr):
        # self.state["connection"] = addr
        text = ""
        if addr is None:
            text = "Connection Status: Disconnected"
        else:
            text = "Connection Status: Connected\n{}:{}".format(addr[0],addr[1])
        self.connection_status.config(text=text)
