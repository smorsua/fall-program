from collections import deque
from scipy.signal import sosfilt


class IIRFilter:
    def __init__(self, sos, buf_size):
        self.sos = sos
        self.buf = deque([0] * buf_size, maxlen=buf_size)

    def filter(self, input):
        return sosfilt(self.sos, list(self.buf))[-1]
