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

import pyaudio
import sounddevice as sd

import torch

OBJ_CUDA = torch.cuda.is_available()

if OBJ_CUDA:
    print('CUDA has been enabled.')
else:
    print('CUDA has been disabled.')

import torch.nn as nn
from torch.nn import Linear, RNN, LSTM, GRU
import torch.nn.functional as F
from torch.nn.functional import softmax, relu
from torch.autograd import Variable
import VAD


RESULT = ""
import time
import logging


start = 0
import threading
import time


def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps


time_count = 0

class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        sample_rate = 16_000

        caps = query_devices(None, "input")
        channels_in = min(caps['max_input_channels'], 2)
        self.stream_in = sd.InputStream(
            device=None,
            samplerate=sample_rate,
            channels=channels_in)
        self.frame = np.array([0]*30)
        
        
    def run(self):
        while True:
            # timeit.timeit('test(self.stream_in,self.name)', 'from __main__ import test','from myTread import self.stream_in,self.name',number = 1000)
            print(timeit.timeit(lambda:test(self.frame,self.name), number=1))
        # timeit.timeit(lambda:test(self.frame,self.name), number=9)
        # time_taken = ((time.time()-start)/9)*1000
        # if time_taken > 30:
        #     print(alert!)
            

def test(frame,name):
    VAD_RESULT = denoiser_VAD(frame)


start = time.time()

thread= []
for i in range (0,1):
    thread.append(myThread(i, "Thread-%s"%i, i))
    thread[i].start()







