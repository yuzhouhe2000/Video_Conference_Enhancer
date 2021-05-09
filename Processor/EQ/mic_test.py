import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from playsound import playsound
from pydub import AudioSegment

fs = 44100
sd.default.device = 11
sd.default.channels = 1
duration = 5

output = sd.OutputStream(device = 12)
output.start()

while(True):
    #sd.default.device = 11
	print("Start Recording")
	myrecording = sd.rec(int(duration * fs), samplerate = fs, channels=1)
	sd.wait()
	print("Finished Recording")
	myrecording = myrecording / max(abs(myrecording))
	write('test.wav', fs, myrecording)
	toMono = AudioSegment.from_wav("test.wav")
	toMono = toMono.set_channels(1)
	print("Wrote to file")
	toMono.export("test_mono.wav", format="wav")
	sd.default.device = 12
	output.write(myrecording)
	sd.default.device = 11
    #playsound('test.wav')

