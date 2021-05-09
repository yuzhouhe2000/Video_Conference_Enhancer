#TESTING SOSFILT FUNCTION

from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write
import soundfile as sf

sample_rate, sig = wavfile.read('test_processed.wav')
sos = signal.ellip(4,5,40,[.009,0.45],btype='bandpass', output='sos')
filtered = signal.sosfilt(sos, sig)
write_me = filtered / max(abs(filtered))
sf.write('bp_test.flac', filtered, 44100)

