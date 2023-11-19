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
        self.frontend.set_refresh_callback(self.update)

    def update(self):
        sample = self.acc_sensor.read()
        fall_data = self.fall_detector.process(sample)
        self.frontend.update(fall_data)


App()
