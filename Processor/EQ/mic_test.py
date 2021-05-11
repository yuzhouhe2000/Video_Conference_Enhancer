#USE THIS FILE TO GENERATE test.wav FILE TO BE PROCESSED BY EQ

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pydub import AudioSegment

fs = 44100
sd.default.device = 11
sd.default.channels = 1
duration = 5 #Duration of recording will be 5 seconds

output = sd.OutputStream(device = 12)
output.start()

while(True):
	#RECORD AUDIO DATA
	print("Recording LIVE")
	myrecording = sd.rec(int(duration * fs), samplerate = fs, channels=1)
	sd.wait()
	print("Not Recording")
	
	#NORMALIZE and CONVERT TO MONO
	myrecording = myrecording / max(abs(myrecording))
	write('test.wav', fs, myrecording)
	toMono = AudioSegment.from_wav("test.wav")
	toMono = toMono.set_channels(1)

	#EXPORT FILE and PROMPT EXIT
	toMono.export("test_mono.wav", format="wav")
	print("Wrote to file. If satisfied with the following playback, please press ctrl + c to exit.")

	#PLAY FILE
	sd.default.device = 12
	output.write(myrecording)

	#PREPARE FOR NEXT RECORDING
	sd.default.device = 11

