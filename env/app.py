#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit,send
import flask_socketio
from threading import Lock
import torch
import torchaudio
from torch import nn
import os
import itertools
import glob
import math
import sys
import numpy as npx
import numpy as np
from pydub import AudioSegment as am
import time
from torch.nn import functional as F

from denoiser.demucs import DemucsStreamer
from denoiser import distrib
from denoiser.audio import Audioset, find_audio_files
from denoiser.utils import deserialize_model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
MODEL_PATH = "denoiser/denoiser.th"


DRY = 0.04
COUNT = 0


def save_wavs(estimates, noisy_sigs, filenames, out_dir, sr=16_000):
    # Write result
    for estimate, noisy, filename in zip(estimates, noisy_sigs, filenames):
        filename = os.path.join(out_dir, os.path.basename(filename).rsplit(".", 1)[0])
        write(noisy, filename + "_noisy.wav", sr=sr)
        write(estimate, filename + "_enhanced.wav", sr=sr)


def write(wav, filename, sr=16_000):
    # Normalize audio if it prevents clipping
    wav = wav / max(wav.abs().max().item(), 1)
    torchaudio.save(filename, wav, sr)


app.config['UPLOAD_FOLDER'] = 'sound'

from flask import send_from_directory

@app.route('/sound/<filename>')
def uploaded_file(filename):
    response =  send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    return response


@app.route("/", methods=['POST', 'GET'])
def index():
    
    if request.method == "POST":
        try:
    
            global COUNT   
            f = request.files['audio_data']
            with open('sound/audio.wav', 'wb') as audio:
                f.save(audio)
            sound = am.from_wav('sound/audio.wav')
            sound = sound.set_frame_rate(16000)
            sound.export('sound/audio_16.wav', format='wav')
            
            pkg = torch.load(MODEL_PATH)
            if 'model' in pkg:
                if 'best_state' in pkg:
                    pkg['model']['state'] = pkg['best_state']
                model = deserialize_model(pkg['model'])
            else:
                model = deserialize_model(pkg)

            model.eval()
            file = 'sound/audio_16.wav'
            siginfo, _ = torchaudio.info(file)
            length = siginfo.length
            
            num_frames = length
            
            out, sr = torchaudio.load(str(file), offset=0,num_frames=num_frames)
            out = F.pad(out, (0, num_frames - out.shape[-1]))

            torch.set_num_threads(1)

            with torch.no_grad():
                start_time = time.time()
                estimate = model(out)
                estimate = (1 - DRY) * estimate + DRY * out
                end_time = time.time()
            
            name = "sound/enhanced"+ str(COUNT) + ".wav"
            write(estimate[0],name,sr)
            
            RESULT = "The enhancement is successful, takes %.4f seconds"%(end_time - start_time)
        except:
            RESULT = "The enhancement failed"
            
        socketio.emit('my_response',{'data': RESULT})
        socketio.emit('count',{'data': str(COUNT)})
        COUNT = COUNT + 1
        return ('', 204)
    else:
        return render_template("index.html")


if __name__ == '__main__':
    socketio.run(app)