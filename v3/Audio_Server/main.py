# Library
import torch
import numpy as np
import time
import socket
import threading

from denoiser.demucs import DemucsStreamer
from denoiser.utils import deserialize_model
from denoiser.VAD import denoiser_VAD
from npsocket import SocketNumpyArray
from real_time_omlsa.omlsa import *
import json


inport = 9999
outport = 9998
parameter_port = 9997

server_parameter_receiver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
server_parameter_receiver.bind(("127.0.0.1",parameter_port))

# Define Server Socket (receiver)
server_denoiser_receiver = SocketNumpyArray()

server_denoiser_receiver.initialize_receiver(inport)
server_denoiser_sender = SocketNumpyArray()

# server_parameter_sender = SocketNumpyArray()

# GLOBAL_VARIABLES
MODEL_PATH = "denoiser/denoiser.th"
DRY = 0.04
frame_num = 1
sample_rate = 16000
CONNECTED = 0

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

Audio_VAD_ON = False

# Load Model
pkg = torch.load(MODEL_PATH,map_location=torch.device(device))
if 'model' in pkg:
    if 'best_state' in pkg:
        pkg['model']['state'] = pkg['best_state']
    model = deserialize_model(pkg['model'])
else:
    model = deserialize_model(pkg)
model.eval()

# Threads
audio_buffer = []
threads = []


MIX = 40
Denoiser = "DSP"
EQ_params = 0

def receive_parameter():
    global MIX,Denoiser,EQ_params
    
    while True:
        recieved = server_parameter_receiver.recvfrom(1024)
        json_obj = json.loads(recieved[0].decode('utf-8'))
        MIX = json_obj.get("MIX")
        Denoiser = json_obj.get("Denoiser")
        EQ_params = json_obj.get("EQ")
        audio_buffer = []
        print(str(MIX) + " " + str(Denoiser)  + " " + str(EQ_params))

def receive_audio():
    global audio_buffer
    while True: 
        frame = server_denoiser_receiver.receive_array()
        audio_buffer.append(frame)

def denoiser_live():
    global server_denoiser_sender
    global audio_buffer
    global CONNECTED
    print("denoiser_start")
    first = True
    current_time = 0
    last_log_time = 0
    FRAME_LENGTH = 25

    log_delta = 10
    sr_ms = sample_rate / 1000
    streamer = DemucsStreamer(model, dry=DRY, num_frames=frame_num)
    stride_ms = streamer.stride / sr_ms

    while True:
        if len(audio_buffer) > 0:
        
            start = time.time()

            if "DL" in Denoiser:
                while len(audio_buffer) > FRAME_LENGTH*5:
                    del(audio_buffer[0:FRAME_LENGTH])            
                    print("Processing speed is too slow. Switch to DSP denoiser or remove denoiser")

                if len(audio_buffer)>=FRAME_LENGTH:
                    frame = audio_buffer[0:FRAME_LENGTH]
                    del(audio_buffer[0:FRAME_LENGTH])
                    frame = np.concatenate(frame)
                    if "VAD" in Denoiser: 
                        VAD_RESULT = denoiser_VAD(frame)
                    else:
                        VAD_RESULT = 1
                    
                    if current_time > last_log_time + log_delta:
                        last_log_time = current_time
                        streamer.reset_time_per_frame()

                    last_log_time = current_time
                    length = streamer.total_length if first else streamer.stride

                    first = False
                    current_time += length / sample_rate

                    if VAD_RESULT == 1:
                        out = frame
                        frame = torch.from_numpy(frame).mean(dim=1).to(device)
                        with torch.no_grad():
                            out = streamer.feed(frame[None])[0]
                        if not out.numel():
                            continue
                    
                        mx = out.abs().max().item()
                        out.clamp_(-1, 1)
                        out = out.cpu().numpy()
                        if CONNECTED == 0:
                            print("initialized sender")
                            time.sleep(1)
                            server_denoiser_sender.initialize_sender('127.0.0.1', outport)
                            CONNECTED = 1
                        else:
                            server_denoiser_sender.send_numpy_array(out)
                            # print(time.time()-start) 


            elif "DSP" in Denoiser:
                while len(audio_buffer) > 10:
                    del(audio_buffer[0:FRAME_LENGTH])            
                    print("Processing speed is too slow. Switch to DSP denoiser or remove denoiser")
                frame = audio_buffer[0]
                del(audio_buffer[0])
                out = omlsa_streamer(frame,sample_rate, frame_length, frame_move,postprocess= "butter",high_cut=6000)
                out = out.astype(np.float32)   
                if CONNECTED == 0:
                    print("initialized sender")
                    time.sleep(1)
                    server_denoiser_sender.initialize_sender('127.0.0.1', outport)
                    CONNECTED = 1
                else:
                    server_denoiser_sender.send_numpy_array(out)
                    # print(time.time()-start) 

            else:
                while len(audio_buffer) > 10:
                    del(audio_buffer[0:FRAME_LENGTH])  
                frame = audio_buffer[0]
                del(audio_buffer[0])
                out = frame

                if CONNECTED == 0:
                    print("initialized sender")
                    time.sleep(1)
                    server_denoiser_sender.initialize_sender('127.0.0.1', outport)
                    CONNECTED = 1
                else:
                    server_denoiser_sender.send_numpy_array(out)
                    # print(time.time()-start)

threads.append(threading.Thread(target=receive_audio))
threads.append(threading.Thread(target=denoiser_live))
threads.append(threading.Thread(target=receive_parameter))
print(threads)

if __name__ == '__main__':
    for thread in threads:
        print(thread)
        thread.start()




