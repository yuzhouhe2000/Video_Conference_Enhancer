#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect,Response
from flask_socketio import SocketIO, emit,send
import flask_socketio
from threading import Lock
import torch
from torch import nn
import os
import itertools
import glob
import math
import sys
import numpy as npx
import numpy as np
from pydub import AudioSegment as am
from VAD import denoiser_VAD
import timeit
import python_speech_features
import array
import pyaudio
import sounddevice as sd
import torch
import torch.nn as nn
from torch.nn import Linear, RNN, LSTM, GRU
import torch.nn.functional as F
from torch.nn.functional import softmax, relu
from torch.autograd import Variable
import VAD
import threading
import time
import time
import logging


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

learning_rate = 0.001


# Define Global Variable
LIVE = 1
SAMPLE_RATE = 16000
SAMPLE_CHANNELS = 1
SAMPLE_WIDTH = 2
BATCH_SIZE = 1
# Frame size to use for the labelling.
FRAME_SIZE_MS = 30
# Calculate frame size in data points.
FRAME_SIZE = int(SAMPLE_RATE * (FRAME_SIZE_MS / 1000.0))
FRAMES = 20
FEATURES = 12

RESULT = ""

OBJ_CUDA = torch.cuda.is_available()

if OBJ_CUDA:
    print('CUDA has been enabled.')
else:
    print('CUDA has been disabled.')




start = 0


def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps


time_count = 0



frame = np.array([0]*30)
mfcc_feature = python_speech_features.mfcc(frame,SAMPLE_RATE, winstep=(FRAME_SIZE_MS / 1000), 
                            winlen= 4 * (FRAME_SIZE_MS / 1000), nfft=2048)
mfcc_feature = mfcc_feature[:, 1:]
mfcc_stream = []
for i in range (0,20):
    mfcc_stream.append(mfcc_feature)
mfcc_stream_array = np.array(mfcc_stream)
mfcc_stream_array = mfcc_stream_array.transpose(1,0,2)
mfcc_stream_array = mfcc_stream_array.astype(np.float32)
test_data_tensor = torch.from_numpy(mfcc_stream_array).to(device)





def test_other():
    # 0.0025
    frame = np.array([0]*30)
    mfcc_feature = python_speech_features.mfcc(frame,SAMPLE_RATE, winstep=(FRAME_SIZE_MS / 1000), 
                                winlen= 4 * (FRAME_SIZE_MS / 1000), nfft=2048)
    mfcc_feature = mfcc_feature[:, 1:]
    mfcc_stream = []
    for i in range (0,20):
        mfcc_stream.append(mfcc_feature)

    mfcc_stream_array = np.array(mfcc_stream)  
    mfcc_stream_array = mfcc_stream_array.transpose(1,0,2)
    mfcc_stream_array = mfcc_stream_array.astype(np.float32)
    test_data_tensor = torch.from_numpy(mfcc_stream_array).to(device)

print("tensor prepare time: " + str(timeit.timeit(lambda:test_other(), number=100)/100))










class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        
        
    def run(self):
        global test_data_tensor
            # timeit.timeit('test(self.stream_in,self.name)', 'from __main__ import test','from myTread import self.stream_in,self.name',number = 1000)
        
        print(timeit.timeit(lambda:test(test_data_tensor,self.name), number=50)/50)
        
            

def test(test_data_tensor,name):
    denoiser_VAD(test_data_tensor)
    # print("Thread "+ name )



thread= []
time.sleep(2)


for i in range (0,100):
    thread.append(myThread(i, "Thread-%s"%i, i))
    thread[i].start()


