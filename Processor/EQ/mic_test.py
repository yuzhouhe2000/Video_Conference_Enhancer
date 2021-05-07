import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from playsound import playsound

fs = 44100
sd.default.device = 11
sd.default.channels = 2
duration = 5

output = sd.OutputStream(device = 12)
output.start()

while(True):
    #sd.default.device = 11
	myrecording = sd.rec(int(duration * fs), samplerate = fs, channels=2)
	sd.wait()
	write('test.wav', fs, myrecording)
	sd.default.device = 12
	output.write(myrecording)
	sd.default.device = 11
    #playsound('test.wav')

