from math import sqrt

from scipy.signal import butter, filtfilt

# import numpy as np

# from scipy import signal #import butter, filtfilt

SAMPLES = 1000

MUESTREO = 0.01


class App:
    def __init__(self):
        self.running = False
        self.client = None
        self.socket = None
        self.data_t = None
        self.data_x = None
        self.data_y = None
        self.data_z = None

        self.filter_x = [0]
        self.filter_y = [0]
        self.filter_z = [0]

        self.data_t = [0]
        self.data_x = [0]
        self.data_y = [0]
        self.data_z = [0]

        self.data_SV = [0]
        self.data_SVd = [0]

        self.data_Z2 = [0]

    def Calculo(self, x, y, z):
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_z.append(z)

        Sv = sqrt((x ^ 2) + (y ^ 2) + (z ^ 2))
        self.data_SV.append(Sv)

        self.filter_x = self.Filtro(self.data_x)
        self.filter_y = self.Filtro(self.data_y)
        self.filter_z = self.Filtro(self.data_z)

        Z2 = (Sv ^ 2 - SVd ^ 2 - 1) / 2
        self.data.Z2.append(Z2)

        for i in range(0, SAMPLES):
            SVd = sqrt((self.filter_x ^ 2) + (self.filter_y ^ 2) + (self.filter_z ^ 2))
            self.data_SVd.append(SVd)

    def butter_highpass(cutoff, fs, order=2):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype="high", analog=False)
        return b, a

    def butter_highpass_filter(self, data, cutoff, fs, order=2):
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def Filtro(self, signal):
        # signal = self.data
        # signal2 = self.data_y
        # signal3 = self.data_z

        fs = 100

        cutoff = 0.25
        order = 2

        filter_data = self.butter_highpass_filter(signal, cutoff, fs, order)
        # self.filter_y = self.butter_highpass_filter(signal2, cutoff, fs, order)
        # self.filter_z = self.butter_highpass_filter(signal3, cutoff, fs, order)

        return filter_data


App()
