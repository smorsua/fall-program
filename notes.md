```python
class App:
    self.acc_sensor = None
    self.fall_detector = None
    self.frontend = None

    def __init__(self):
        self.acc_sensor = AccelerometerSensor()
        self.fall_detector = FallDetector()
        self.frontend = Frontend()
        self.frontend.set_refresh_callback(self.update)

    def update(self):
        sample = self.acc_sensor.read()
        fall_data = self.fall_detector.process(sample)
        self.frontend.update(fall_data)

class Frontend:
    self.window = None
    self.text_console = None
    self.button_start = None
    self.button_stop = None
    self.connection_status = None
    self.impact_status = None
    self.refresh_callback = None

    def __init__(self):
        self.init_window()
        self.init_widgets()

    def init_window(self):
    def init_widgets(self):

    def update(self, fall_data):
        self.update_impact_status(fall_data["is_impact"])
        self.update_console(text?)
        self.update_plot(sample?)
        self.update_conn_status(addr?)

    def update_impact_status(self, is_impact):
    def update_console(self, text):
    def update_plot(self, sample):
    def update_conn_status(self, addr):

class AccelerometerSensor:
    self.socket = None

    def read():

    def parse():

class FallDetector:
    self.hpf = None
    self.sv_buf = None # Ventana 0.1s, deque?

    def __init__(self, samples_per_second, window_length):
        self.hpf = ...
        self.sv_buf = deque(maxlen=samples_per_second*window_length)

    def process(self, sample):
        sv = FallDetector.sv(sample)
        sv_buf.push(sv)
        sv_d = self.sv_d(sample)
        sv_maxmin = self.sv_maxmin()
        is_impact = self.detect_m1(sv, sv_d, sv_maxmin)

        return {
            "sv": sv,
            "sv_d": sv_d,
            "sv_maxmin": sv_maxmin,
            "is_impact": is_impact
        }

    @staticmethod
    def sv(sample):

    def sv_d(self, sample):
        return self.hpf.filter(sample)

    def sv_maxmin(self):
        min = float('inf')
        max = float('-inf')
        for x in self.sv_buf:
            ...

    def detect_m1(self, sv, sv_d, sv_maxmin):
        SV_THRESHOLD =
        SV_D_THRESHOLD =
        SV_MAXMIN_THRESHOLD =

        return sv > SV_THRESHOLD and sv_d > SV_D_THRESHOLD and sv_maxmin > SV_MAXMIN_THRESHOLD

```
