from flask import Flask, render_template, request, redirect,url_for, json, render_template_string, jsonify, Response
from flask_socketio import SocketIO, emit,send
import sys
import time
import sounddevice as sd
import cv2
from npsocket import SocketNumpyArray
import numpy as np
from camera_input import video_input 

# Initilize flask app and socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DRY = 0.04
COUNT = 0
LIVE = 0
VAD_RESULT = 0

outport_denoiser = 9990
inport_denoiser = 9991
CONNECTED = 0
client_denoiser_receiver = SocketNumpyArray()
client_denoiser_sender = SocketNumpyArray()
client_denoiser_sender.initialize_sender('192.168.1.205', outport_denoiser)

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

    sample_rate = 16_000
    caps = query_devices(None, "input")
    channels_in = min(caps['max_input_channels'], 2)
    stream_in = sd.InputStream(
        device=None,
        samplerate=sample_rate,
        channels=channels_in)

    stream_in.start()
    
    while (LIVE == 1):
        # TODO: NEED to pass the overflow and underflow information
        frame, overflow = stream_in.read(256)
        # print(frame.shape)
        client_denoiser_sender.send_numpy_array(frame)
    
    stream_in.stop()
    return ('', 204)

@app.route("/output_audio", methods=["POST"])
def output_audio():
    global CONNECTED
    global client_denoiser_receiver
    sample_rate = 16000
    device_out = "Soundflower (2ch)"
    caps = query_devices(device_out, "output")
    channels_out = min(caps['max_output_channels'], 2)
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
    global DRY
    if request.method == 'POST':
        volume = request.form.get('slide')
        print('volume:', volume)
        DRY = int(volume)/1000
        #return jsonify({'volume': volume})
    return ('', 204)








# --------------------------------------- video part ----------------------------------------------


CAMERA_CONTROl = 1
OLD_CAMERA_CONTROl = 1
outport_video = 5000
inport_video = 9999
first = 0

# # control camera
@app.route('/camera_control',methods=['POST'])
def camera_control():
    global first
    global CAMERA_CONTROl
    if first == 0:
        video_input()
        first= first+1
    if CAMERA_CONTROl == 0:
        CAMERA_CONTROl = 1
        
    else:
        CAMERA_CONTROl = 0
    return('', 204)



# @app.route("/output_video", methods=["POST"])
# def output_audio():
#     CONNECTED = 0
#     while True:
#         if CONNECTED == 0:
#             client_denoiser_receiver = SocketNumpyArray()

#             client_denoiser_receiver.initialize_receiver(inport_denoiser)
#             print("INITIALIZED") 
#             CONNECTED = 1  
#         else:
#             out = client_denoiser_receiver.receive_array()
#             codec = cv2.VideoWriter_fourcc(*'DIVX')  # for mac OSX, not sure if it works for windows
#             output = cv2.VideoWriter('video.avi',codec,30,(640, 480))
#             output.write(frame)
#     return ('', 204)


# # # #　feed video
@app.route('/video_feed')
def video_feed():
    return ('', 204)
#     return Response(gen(),
#                         mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app)