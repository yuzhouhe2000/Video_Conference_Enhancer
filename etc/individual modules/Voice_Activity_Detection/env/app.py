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


import python_speech_features
import array
import torch.nn as nn
from torch.nn import Linear, RNN, LSTM, GRU
import torch.nn.functional as F
from torch.nn.functional import softmax, relu
from torch.autograd import Variable
# import framework
import pyaudio
import numpy
import sounddevice as sd



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


import torch

OBJ_CUDA = torch.cuda.is_available()

if OBJ_CUDA:
    print('CUDA has been enabled.')
else:
    print('CUDA has been disabled.')

def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps

import torch.nn as nn
from torch.nn import Linear, RNN, LSTM, GRU
import torch.nn.functional as F
from torch.nn.functional import softmax, relu
from torch.autograd import Variable

class Net(nn.Module):
    def __init__(self, large = True, lstm = True):
        super(Net, self).__init__()
        self.large = large
        self.lstm = lstm
        self.relu = nn.ReLU()
        if lstm:
            self.hidden = self.init_hidden()
            self.rnn = LSTM(input_size=FEATURES, hidden_size=FRAMES, num_layers=1, batch_first=True)
        else:
            self.rnn = GRU(input_size=FEATURES, hidden_size=FRAMES, num_layers=1, batch_first=True)
        
        if large:
            self.lin1 = nn.Linear(FRAMES**2, 26)
            self.lin2 = nn.Linear(26, 2)
        else:
            self.lin = nn.Linear(FRAMES**2, 2)
            
        self.softmax = nn.Softmax(dim=1)
    
    def init_hidden(self):
        h = Variable(torch.zeros(1, BATCH_SIZE, FRAMES))
        c = Variable(torch.zeros(1, BATCH_SIZE, FRAMES))
        
        if OBJ_CUDA:
            h = h.cuda()
            c = c.cuda()
        
        return h, c
    
    def forward(self, x):
        if OBJ_CUDA:
           self.rnn.flatten_parameters()
        
        # (batch, frames, features)
        if hasattr(self, 'lstm') and self.lstm:
            x, _ = self.rnn(x, self.hidden)
        else:
            x, _ = self.rnn(x).cuda()
            
        x = x.contiguous().view(-1, FRAMES**2)
        
        # (batch, units)
        if self.large:
            x = self.relu(self.lin1(x))
            x = self.lin2(x)
        else:
            x = self.lin(x)
        
        return self.softmax(x)

model = Net()
print(model)

parameter_count = sum(p.numel() for p in model.parameters())
print(f'Model parameters: {parameter_count}')
            
RESULT = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
import time



@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/live",methods = ['POST'])
def live():
    return_message = ""
    global LIVE
    LIVE = 1
    print("live request")
    sample_rate = 16_000
    caps = query_devices(None, "input")
    channels_in = min(caps['max_input_channels'], 1)
    stream_in = sd.InputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_in)

    stream_in.start()
    mfcc_stream = []
    count = 0
    start = 0
    while (LIVE == 1):

        frame, overflow = stream_in.read(360)

        frame = frame.reshape((-1,)) 

        with torch.no_grad():
            mfcc_feature = python_speech_features.mfcc(frame,SAMPLE_RATE, winstep=(FRAME_SIZE_MS / 1000), 
                                       winlen= 4 * (FRAME_SIZE_MS / 1000), nfft=2048)
            mfcc_feature = mfcc_feature[:, 1:]
            # delta = python_speech_features.delta(mfcc_feature, 2)
            # mfcc_feature = np.hstack((mfcc_feature, delta))
            # mfcc_feature = librosa.feature.mfcc(y=frame, sr=sample_rate, n_mfcc=24)
            mfcc_stream.append(mfcc_feature)
            if len(mfcc_stream) >= (FRAMES+1):
                mfcc_stream.pop(0)
            count = count + 1
            if len(mfcc_stream) == FRAMES:
                if count >= 10:
                    mfcc_stream_array = np.array(mfcc_stream)
                    mfcc_stream_array = mfcc_stream_array.transpose(1,0,2)
                    mfcc_stream_array = mfcc_stream_array.astype(np.float32)
                    test_data_tensor = torch.from_numpy(mfcc_stream_array).to(device)
                    model.load_state_dict(torch.load("lstm.net",map_location=torch.device(device)))
                    model.eval()
                    output = model(test_data_tensor).to(device)
                    pred_y = torch.max(output, 1)[1].data.numpy()
                    result = pred_y[0]

                    end = time.time()

                    if result == 1:
                        return_message = "Is Speaking"
                        RESULT = return_message
                        
                    else:
                        return_message = "Not Speaking"
                        RESULT = return_message
                    
                    socketio.emit('my_response',{'data': RESULT})
                    count = 0
                    print("time taken: " + str(end - start) + "s, result is " + RESULT)
                    start = end

    stream_in.stop()
    return ('', 204)

@app.route("/endlive", methods=['POST'])
def denoiser_live():
    global LIVE
    LIVE = 0
    print("live is " + str(LIVE))
    return ('', 204)

if __name__ == '__main__':
    socketio.run(app)


