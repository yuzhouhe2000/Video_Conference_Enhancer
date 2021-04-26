from flask import Flask, render_template, request, redirect,url_for, json, render_template_string, jsonify, Response
from flask_socketio import SocketIO, emit,send
import sys
import time
import sounddevice as sd
import cv2
from npsocket import SocketNumpyArray
import numpy as np
from camera_input import video_input 
import socket


# Initilize flask app and socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

MIX = 40
COUNT = 0
LIVE = 0
VAD_RESULT = 0
Denoiser = "DSP"
outport_denoiser = 9990
inport_denoiser = 9991
outport_parameter = 9992
CONNECTED = 0
client_denoiser_receiver = SocketNumpyArray()
client_denoiser_sender = SocketNumpyArray()
client_denoiser_sender.initialize_sender('127.0.0.1', outport_denoiser)
client_parameter_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/param', methods=['POST'])
def parameter():
    EQ_params = request.form.get("EQ")
    Denoiser = request.form.get("Denoiser")
    parameters = {"EQ": EQ_params, "Denoiser": Denoiser, "MIX": MIX}
    parameters_json = json.dumps(parameters).encode('utf-8')
    client_parameter_sender.sendto(parameters_json, ("127.0.0.1", outport_parameter))
    print(parameters_json)
    return ('', 204)

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
    global Denoiser
    
    LIVE = 1
    print("live request")

    sample_rate = 44100
    caps = query_devices(None, "input")
    channels_in = min(caps['max_input_channels'], 1)
    stream_in = sd.InputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_in)
    stream_in.start()
    while (LIVE == 1):
        if Denoiser == "DL":
            frame, overflow = stream_in.read(2608)
            client_denoiser_sender.send_numpy_array(frame)
        elif Denoiser == "DSP":
            frame, overflow = stream_in.read(128)
            client_denoiser_sender.send_numpy_array(frame)
    stream_in.stop()
    return ('', 204)

@app.route("/output_audio", methods=["POST"])
def output_audio():
    global CONNECTED
    global client_denoiser_receiver
    sample_rate = 44100
    device_out = "Soundflower (2ch)"
    caps = query_devices(device_out, "output")
    channels_out = min(caps['max_output_channels'], 1)
    stream_out = sd.OutputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_out)
    stream_out.start()

    while True:
        if CONNECTED == 0:
            client_denoiser_receiver.initialize_receiver(inport_denoiser)
            print("INITIALIZED") 
            CONNECTED = 1  
        else:
            out = client_denoiser_receiver.receive_array()
            # print(out)
            stream_out.write(out)
    stream_out.stop()
    return ('', 204)


@app.route("/endlive", methods=['POST'])
def end_live():
    global LIVE
    LIVE = 0
    socketio.emit('my_response',{'data': ""})
    return ('', 204)


@app.route('/slide', methods=['GET', 'POST'])
def control_panel():
    global MIX
    if request.method == 'POST':
        MIX = request.form.get('slide')
        print('MIX changed to:', MIX)
    return ('', 204)


if __name__ == '__main__':
    socketio.run(app)