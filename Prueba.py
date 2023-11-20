import numpy as np

from scipy import signal
from iir_filter import IIRFilter
import math

import matplotlib.pyplot as plt



class Prueba: 

    def __init__(self):

        fs=1000
        t = np.arange(0, 1, 1/fs) 
        f0=100
        data=5*np.cos(2*np.pi*f0*t)

        sos = signal.butter(
            btype="highpass", N=2, fs=100, Wn=2 * math.pi * 5, output="sos"
        )

        hpf = IIRFilter(sos, 6)

        signal_f = [hpf.filter(x) for x in data]
            

        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(t, data, label='Señal de entrada')
        plt.plot(t, signal_f, label='Señal filtrada')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.legend()

        w, h = signal.sosfreqz(sos, worN=8000)
        plt.subplot(2, 1, 2)
        plt.plot(0.5 * fs * w / np.pi, np.abs(h), 'b')
        plt.title('Respuesta en Frecuencia del Filtro')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud')

        plt.tight_layout()
        plt.show()

Prueba()
