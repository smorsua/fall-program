from accelerometer_sensor import AccelerometerSensor
from fall_detector import FallDetector
from frontend import Frontend
from enum import Enum

SAMPLES_PER_SECOND = 100
WINDOW_LENGTH = 0.1

class AppState(Enum):
    IDLE = 0
    RUNNING = 1
class App:
    def __init__(self):
        self.state = AppState.IDLE
        self.acc_sensor = AccelerometerSensor()
        self.fall_detector = FallDetector(SAMPLES_PER_SECOND, WINDOW_LENGTH)
        self.frontend = Frontend()
        self.frontend.set_start_cb(self.start_cb)
        self.frontend.set_refresh_cb(self.update)
        self.frontend.set_stop_cb(self.close_cb)
        self.frontend.run()
        self.output = None

    def start_cb(self):
        try:
            self.acc_sensor.init()
            self.next_state(AppState.RUNNING)
        except:
            print("error initializing acc_sensor")

    def update(self, frontend):
        if self.state is AppState.RUNNING:           
            try:
                sample = self.acc_sensor.read()
                fall_data = self.fall_detector.process(sample)
                frontend.update(fall_data)
                self.output.write("{}\n".format(fall_data))
            except:
                self.next_state(AppState.IDLE)
            
    def next_state(self, next_state):
        if self.state is AppState.IDLE and next_state is AppState.RUNNING:
            self.idle_to_running()
        elif self.state is AppState.RUNNING and next_state is AppState.IDLE:
            self.running_to_idle()
        self.state = next_state

    def idle_to_running(self):
        self.output = open("output.txt", "w")
        
        # Update UI.
        self.frontend.button_start.configure(state="disabled")
        self.frontend.button_stop.configure(state="normal")
        self.frontend.update_conn_status(self.acc_sensor.addr)
        
    def running_to_idle(self):
        self.output.close()
        self.acc_sensor.close()
        
        # Update UI.
        self.frontend.button_start.configure(state="normal")
        self.frontend.button_stop.configure(state="disabled")
        self.frontend.update_conn_status(None)
        
    def close_cb(self):
        self.next_state(AppState.IDLE)

App()
