#TEST CODE, ATTEMPT AT RECORDING AND PLAYING AUDIO USING MULTITHREADING
#IN THE END, THOUGH THIS PROCESS WORKS BETTER THAN NON-MULTITHREADING APPROACH, IT IS NOT AT ALL NEAR REAL TIME
#FOR FUTURE WORK, LOOKING INTO STREAMS IS PROBABLY MORE USEFUL
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
		myrecording = sd.rec(int(3 * fs), samplerate = fs, channels=1)
		sd.wait()
		out_q.put(myrecording)
		while(check_me.get() != "GO AHEAD"):
			continue

#IF THIS CODE WERE TO IMPLEMENT THE EQ PROCESS AS WELL, IT MAY BE A GOOD IDEA TO ADD A THIRD THREAD
#THE THIRD THREAD COULD ACCEPT SOUND FILES FROM PRODUCER, PROCESS THEM, THEN HAND THEM TO THE CONSUMER
#IT WOULD BE IDEAL TO HAVE THIS ON A THIRD THREAD SO PLAYBACK AND RECORDING ARE NEVER INTERRUPTED


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
	fs = 44100
	sd.default.device = 11
	sd.default.channels = 1

	t1 = Thread(target = consumer, args = (q,check,  ))
	t2 = Thread(target = producer, args = (q,check,  ))
	t1.start()
	t2.start()

	output = sd.OutputStream(device = 12)
	output.start()


if __name__ == '__main__':
	main()
	






