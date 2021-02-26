# Reference: https://github.com/facebookresearch/denoiser
# Real Time Speech Enhancement in the Waveform Domain (Interspeech 2020)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python library
from flask import Flask, render_template, request, redirect,url_for, json, render_template_string, jsonify
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
import sounddevice as sd
from flask import send_from_directory


# User library
from denoiser.demucs import DemucsStreamer
from denoiser.utils import deserialize_model

# Initilize flask app and socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
MODEL_PATH = "denoiser/denoiser.th"

# Initialize global variables
DRY = 0.04
COUNT = 0
LIVE = 1

# Save wav files for recording
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

# set up sound resource folder
app.config['UPLOAD_FOLDER'] = 'sound'




@app.route('/sound/<filename>')
def uploaded_file(filename):
    response =  send_from_directory(app.config['UPLOAD_FOLDER'],filename)
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


def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps

@app.route("/live", methods=['POST'])
def denoiser_live():
    global LIVE
    LIVE = 1
    print("live request")
    pkg = torch.load(MODEL_PATH)
    if 'model' in pkg:
        if 'best_state' in pkg:
            pkg['model']['state'] = pkg['best_state']
        model = deserialize_model(pkg['model'])
    else:
        model = deserialize_model(pkg)

    model.eval()
    frame_num = 2
    streamer = DemucsStreamer(model, dry=DRY, num_frames=frame_num)
    sample_rate = 16_000

    caps = query_devices(None, "input")
    channels_in = min(caps['max_input_channels'], 2)
    stream_in = sd.InputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_in)

    device_out = "Soundflower (2ch)"
    caps = query_devices(device_out, "output")
    channels_out = min(caps['max_output_channels'], 2)
    stream_out = sd.OutputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_out)
    
    stream_in.start()
    stream_out.start()
    first = True
    current_time = 0
    last_log_time = 0
    last_error_time = 0
    cooldown_time = 2
    log_delta = 10
    sr_ms = sample_rate / 1000
    stride_ms = streamer.stride / sr_ms
    print(f"Ready to process audio, total lag: {streamer.total_length / sr_ms:.1f}ms.")


    while (LIVE == 1):
        try:
            if current_time > last_log_time + log_delta:
                last_log_time = current_time
                tpf = streamer.time_per_frame * 1000
                rtf = tpf / stride_ms
                print(f"time per frame: {tpf:.1f}ms, ", end='')
                print(f"RTF: {rtf:.1f}")
                streamer.reset_time_per_frame()

            length = streamer.total_length if first else streamer.stride
            first = False
            current_time += length / sample_rate
            frame, overflow = stream_in.read(length)
            frame = torch.from_numpy(frame).mean(dim=1).to("cpu")
            with torch.no_grad():
                out = streamer.feed(frame[None])[0]
            if not out.numel():
                continue
            # compresser
            # out = 0.99 * torch.tanh(out)

            out = out[:, None].repeat(1, channels_out)
            mx = out.abs().max().item()
            if mx > 1:
                print("Clipping!!")
            out.clamp_(-1, 1)
            out = out.cpu().numpy()
            underflow = stream_out.write(out)
            if overflow or underflow:
                if current_time >= last_error_time + cooldown_time:
                    last_error_time = current_time
                    tpf = 1000 * streamer.time_per_frame
                    RESULT =  f"time per frame is {tpf:.1f}ms, need to be below {stride_ms:.1f}ms for acceptable quality"
                    socketio.emit('my_response',{'data': RESULT})
                    # print (f"Denoiser is running! time per frame is {tpf:.1f}ms, need to be below {stride_ms:.1f}ms")

        except KeyboardInterrupt:
            print("Stopping")
            break

    stream_out.stop()
    stream_in.stop()
    return ('', 204)

@app.route("/endlive", methods=['POST'])
def end_live():
    global LIVE
    LIVE = 0
    socketio.emit('my_response',{'data': ""})
    return ('', 204)


@app.route('/slide', methods=['GET', 'POST'])
def control_panel():
    global DRY
    if request.method == 'POST':
        volume = request.form.get('slide')
        print('volume:', volume)
        DRY = int(volume)/1000
        #return jsonify({'volume': volume})
    return ('', 204)


if __name__ == '__main__':
    socketio.run(app)

