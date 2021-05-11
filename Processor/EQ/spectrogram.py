import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment

#ASSUME THERE IS ALREADY A FILE IN MONO FORMAT NAMED test_mono.wav

yMax = (int)(input("Enter maximum frequency value to visualize: ")

sample_rate, samples = wavfile.read('Testing_FIles/test_mono.wav')
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
original = plt.figure(1)
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.title('Original Audio')

sample_rate, samples = wavfile.read('Testing_FIles/eq_chain_processed_mono.wav')
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
processed = plt.figure(2)
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.title('Processed Audio')
plt.ylim(top=yMax)

plt.show()
