# Reference: https://github.com/facebookresearch/denoiser
# Real Time Speech Enhancement in the Waveform Domain (Interspeech 2020)

from flask import Flask, render_template, request, redirect,url_for, json, render_template_string, jsonify, Response
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
import time
from torch.nn import functional as F
import sounddevice as sd
from flask import send_from_directory
import cv2

# User library
from denoiser.demucs import DemucsStreamer
from denoiser.utils import deserialize_model
from camera.camera import VideoCamera
from denoiser.VAD import denoiser_VAD

# Initilize flask app and socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize global variables
MODEL_PATH = "denoiser/denoiser.th"
DRY = 0.04
COUNT = 0
LIVE = 1
CAMERA_CONTROl = 1
OLD_CAMERA_CONTROl = 1
VAD_RESULT = 0

# main page
@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

# sound_device
def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps

# denoiser_live
@app.route("/live", methods=['POST'])
def denoiser_live():
    global VAD_RESULT
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
    frame_num = 1
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
        if current_time > last_log_time + log_delta:
            last_log_time = current_time
            tpf = streamer.time_per_frame * 1000
            rtf = tpf / stride_ms
            print(f"time per frame: {tpf:.1f}ms, ", end='')
            print(f"RTF: {rtf:.1f}")
            streamer.reset_time_per_frame()
        last_log_time = current_time
        length = streamer.total_length if first else streamer.stride
        first = False
        current_time += length / sample_rate
        frame, overflow = stream_in.read(length)
  
        if VAD_RESULT == 1:
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
                    print(f"time per frame is {tpf:.1f}ms, need to be below {stride_ms:.1f}ms for acceptable quality")
                    # print (f"Denoiser is running! time per frame is {tpf:.1f}ms, need to be below {stride_ms:.1f}ms")
                

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

# Voice activity detection unit
@app.route('/VAD', methods=['POST'])
def VAD():
    global LIVE
    global VAD_RESULT
    caps = query_devices(None, "input")
    channels_in = min(caps['max_input_channels'], 2)
    stream_in = sd.InputStream(
        device=None,
        samplerate=16_000,
        channels=channels_in)    
    stream_in.start()
    while(LIVE == 1):
        frame, overflow = stream_in.read(30)
        VAD_RESULT = denoiser_VAD(frame)
        print(VAD_RESULT)
    return ('', 204)

# generate frames
def gen(camera):
    global CAMERA_CONTROl
    global OLD_CAMERA_CONTROl
    while(1):
        if CAMERA_CONTROl == 1:
            camera = VideoCamera()
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if OLD_CAMERA_CONTROl == 1 and CAMERA_CONTROl == 0:
            camera.close()
        if OLD_CAMERA_CONTROl == 0 and CAMERA_CONTROl == 0:
            time.sleep(0.4)
        OLD_CAMERA_CONTROl = CAMERA_CONTROl
        
            
#　feed video
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

# control camera
@app.route('/camera_control',methods=['POST'])
def camera_control():
    global CAMERA_CONTROl
    if CAMERA_CONTROl == 0:
        CAMERA_CONTROl = 1
        
    else:
        CAMERA_CONTROl = 0
    return ('', 204)

if __name__ == '__main__':
    socketio.run(app)

