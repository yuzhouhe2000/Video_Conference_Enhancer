#A = 10^(DBGAIN/40)
#Q = Related to BW of Filter, suggested value is .707 for "sharp" changes or 1.1 for "rounded" changes

import numpy as np
from scipy.io import wavfile
from scipy import signal
import math

def lowpass(w0, Q):
	#LPF
	#H(s) = 1/(s^2 + s/Q + 1)

	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = (1-COSW0)/2
	b1 = 1-COSW0
	b2 = b0
	a0 = 1 + alpha
	a1 = -2*COSW0
	a2 = 1 - alpha

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos

def highpass(w0, Q):
	#HPF
	#H(s) = (s^2) / ((s^2) + (s/Q) + 1)
	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = (1+COSW0)/2
	b1 = -(1+COSW0)
	b2 = b0
	a0 = 1 + alpha
	a1 = -2*COSW0
	a2 = 1 - alpha

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos


def bandpass(w0, Q):
	#BPF using peak gain Q
	#H(s) = s / (s^2 + s/q + 1)
	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = Q*alpha #= SINW0/2
	b1 = 0
	b2 = -b0
	a0 = a + alpha
	a1 = -2*COSW0
	a2 = 1 - alpha

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos


def peaking(w0, Q, A):
	#Peaking EQ
	#H(s) = (s^2 + s*A/Q + 1) / ( s^2 + s/(A*Q) + 1)
	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = 1 + (alpha*A)
	b1 = -2*COSW0
	b2 = 1 - (alpha*A)
	a0 = 1 + (alpha/A)
	a1 = -2*COSW0
	a2 = 1 - (alpha/A)

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos


def lowShelf(w0, Q, A):
	#Low Shelf
	#H(s) = A * ((s^2 + sqrt(A)*s/Q + A) / (A*(s^2) + sqrt(A)*s/Q + 1)
	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = A*((A+1)-(A-1)*COSW0 + (2*math.sqrt(A)*alpha))
	b1 = 2*A*((A-1)-((A+1)*COSW0))
	b2 = A*((A+1)-(A-1)*COSW0 - (2*math.sqrt(A)*alpha))
	a0 = (A+1) + ((A-1)*COSW0) + (2*math.sqrt(A)*alpha)
	a1 = -2 * ((A-1) + ((A+1)*COSW0))
	a2 = (A+1) + ((A-1)*COSW0) - (2*math.sqrt(A)*alpha)

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos


def highShelf(w0, Q, A):
	#High Shelf
	#H(s) = A * ((A*(s^2) + sqrt(A)*s/Q + 1) / ((s^2) + sqrt(A)*s/Q + A)
	COSW0 = math.cos(w0)
	alpha = math.sin(w0)/(2*Q)

	b0 = A*((A+1)+(A-1)*COSW0 + (2*math.sqrt(A)*alpha))
	b1 = 2*A*((A-1)+((A+1)*COSW0))
	b2 = A*((A+1)+(A-1)*COSW0 - (2*math.sqrt(A)*alpha))
	a0 = (A+1) - ((A-1)*COSW0) + (2*math.sqrt(A)*alpha)
	a1 = -2 * ((A-1) - ((A+1)*COSW0))
	a2 = (A+1) - ((A-1)*COSW0) - (2*math.sqrt(A)*alpha)

	num = [b0, b1, b2]
	den = [a0, a1, a2]
	sos = signal.tf2sos(num, den)
	return sos

def main():
	mode = (int)(input("1 for \"Real Time\" 2 to process a file: "))
	if(mode==1):
		print("Selected 1: This feature is not implemented yet")
	else:
		print("Selected 2")
		#SET
		FS = 44100
		sampleRate, inputArray = wavfile.read("test_mono.wav")

		#GET FROM USER
		print("LPF================================")
		F0 = (int)(input("Center frequency in Hz: "))
		Q = (float)(input("Q factor: "))
		W0 = 2*math.pi*(F0/FS)
		sos = lowpass(W0, Q)
		inputArray2 = signal.sosfilt(sos, inputArray)

		#print("Low Shelf================================")
		#F0 = (int)(input("Center frequency in Hz: "))
		#Q = (float)(input("Q factor: "))
		#A = (float)(input("A factor: "))
		#W0 = 2*math.pi*(F0/FS)
		#sos = lowShelf(W0, Q, A)
		#inputArray3 = signal.sosfilt(sos, inputArray2)

		print("Peaking EQ================================")
		F0 = (int)(input("Center frequency in Hz: "))
		Q = (float)(input("Q factor: "))
		A = (int)(input("A factor: "))
		W0 = 2*math.pi*(F0/FS)
		sos = peaking(W0, Q, A)
		inputArray4 = signal.sosfilt(sos, inputArray2)

		#print("High Shelf================================")
		#F0 = (int)(input("Center frequency in Hz: "))
		#Q = (float)(input("Q factor: "))
		#A = (float)(input("A factor: "))
		#W0 = 2*math.pi*(F0/FS)
		#sos = highShelf(W0, Q, A)
		#inputArray5 = signal.sosfilt(sos, inputArray4)

		print("HPF================================")
		F0 = (int)(input("Center frequency in Hz: "))
		Q = (float)(input("Q factor: "))
		W0 = 2*math.pi*(F0/FS)
		sos = highpass(W0, Q)
		outputArray = signal.sosfilt(sos, inputArray4)
		write_me = outputArray / max(abs(outputArray))

		wavfile.write("processed_mono.wav", sampleRate, write_me)

if __name__ == '__main__':
	main()


