from accelerometer_sensor import AccelerometerSensor
from fall_detector import FallDetector
from frontend import Frontend

SAMPLES_PER_SECOND = 100
WINDOW_LENGTH = 0.1


class App:
    def __init__(self):
        self.acc_sensor = AccelerometerSensor()
        self.fall_detector = FallDetector(SAMPLES_PER_SECOND, WINDOW_LENGTH)
        self.frontend = Frontend()
        self.frontend.set_start_cb(self.start_cb)
        self.frontend.set_refresh_cb(self.update)
        self.frontend.set_stop_cb(self.acc_sensor.close)
        self.frontend.run()

    def start_cb(self, frontend):
        self.acc_sensor.init()
        frontend.update_conn_status(self.acc_sensor.addr)

    def update(self, frontend):
        sample = self.acc_sensor.read()
        fall_data = self.fall_detector.process(sample)
        frontend.update(fall_data)


App()
