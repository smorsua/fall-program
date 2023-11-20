from scipy import signal
from iir_filter import IIRFilter
import math
from collections import deque


class FallDetector:
    def __init__(self, samples_per_second, window_length):
        sos = signal.butter(
            btype="highpass", N=2, fs=100, Wn=2 * math.pi * 5, output="sos"
        )
        self.hpf = IIRFilter(sos, 10)
        self.sv_buf = deque(maxlen=math.ceil(samples_per_second * window_length))

    def process(self, sample):
        sv = FallDetector.sv(sample)
        self.sv_buf.append(sv)
        sv_d = self.sv_d(sv)
        sv_maxmin = self.sv_maxmin()
        is_impact = self.detect_m1(sv, sv_d, sv_maxmin)

        return {
            "sample": sample,
            "sv": sv,
            "sv_d": sv_d,
            "sv_maxmin": sv_maxmin,
            "is_impact": is_impact,
        }

    @staticmethod
    def sv(sample):
        return math.sqrt(sample[0] ** 2 + sample[1] ** 2 + sample[2] ** 2)

    def sv_d(self, sample):
        return self.hpf.filter(sample)

    def sv_maxmin(self):
        min = float("inf")
        max = float("-inf")
        for x in self.sv_buf:
            if x < min:
                min = x
            if x > max:
                max = x
        return max - min

    def detect_m1(self, sv, sv_d, sv_maxmin):
        SV_THRESHOLD = 0
        SV_D_THRESHOLD = 0
        SV_MAXMIN_THRESHOLD = 0

        return (
            sv > SV_THRESHOLD
            and sv_d > SV_D_THRESHOLD
            and sv_maxmin > SV_MAXMIN_THRESHOLD
        )
