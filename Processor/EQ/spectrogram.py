import matplotlib.pyplot as plt
#import matplotlib.axes.Axes as ax
import numpy as np
from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment

#ASSUME THERE IS ALREADY A FILE CALLED TEST_MONO
#convert = AudioSegment.from_wav('test.wav')
#convert = convert.set_channels(1)
#convert.export('test_mono.wav', format = 'wav')

sample_rate, samples = wavfile.read('test_mono.wav')
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
original = plt.figure(1)
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')



sample_rate, samples = wavfile.read('processed_mono.wav')
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
processed = plt.figure(2)
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')


plt.show()
