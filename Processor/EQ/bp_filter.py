#TESTING SOSFILT FUNCTION

from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write

sample_rate, sig = wavfile.read('Testing_Files/test_mono.wav')
sos = signal.ellip(4,5,40,[.009,0.45],btype='bandpass', output='sos')
filtered = signal.sosfilt(sos, sig)
write_me = filtered / max(abs(filtered))
wavfile.write('Testing_Files/SOS_bpf_test_mono.wav', filtered, 44100)

