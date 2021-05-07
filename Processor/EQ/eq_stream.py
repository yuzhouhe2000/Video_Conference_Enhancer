import time
from queue import Queue
from threading import Thread
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from playsound import playsound
from scipy.io import wavfile
from scipy import signal
import math


def producer(out_q, check_me):
	while True:
		sd.default.device=11
		myrecording = sd.rec(int(duration * fs), samplerate = fs, channels=2)
		sd.wait()
		out_q.put(myrecording)
		while(check_me.get() != "GO AHEAD"):
			continue

def consumer(in_q, check_me):
	while True:
		sd.default.device=12
		data = in_q.get()
		output.write(data)
		check_me.put("GO AHEAD")
		while(in_q.qsize() == 0):
			continue


def main():
	os.getcwd()
	q = Queue()
	check = Queue()

	t1 = Thread(target = consumer, args = (q,check,  ))
	t2 = Thread(target = producer, args = (q,check,  ))
	t1.start()
	t2.start()

	fs = 44100
	sd.default.device = 11
	sd.default.channels = 2
	duration = 5

	output = sd.OutputStream(device = 12)
	output.start()

	while(True):
	    #sd.default.device = 11
		
	    #write('test.wav', fs, myrecording)
		sd.default.device = 12
		
		sd.default.device = 11
	    #playsound('test.wav')


if __name__ == '__main__':
	main()
	






