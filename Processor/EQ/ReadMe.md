REQUIRED LIBRARIES
numpy, scipy, matplotlib, sounddevice, pydub

DEBUGGING WITH LOCAL SOUND DEVICES
Based on the output devices in user's setup, the index of devices used by sounddevice may need to be changed in mic_test.py.
The command sounddevice -m list will display your system's devices by index. In mic_test.py, replace the index "11" in lines 23 and 38 with the index of your input device.
In mic_test.py, replace index "12" in lines 13 and 34 with the index of your output device.

VISUALIZING CHANGES WITH EQ

STEP 1: Run mic_test.py and terminate program after a satisfactory audio clip has been written
STEP 2: Run eq.py to generate a processed audio file
STEP 3: Run spectrogram.py to generate Figure 1 (Graph of original audio file) and Figure 2 (Graph of audio file after EQ)


