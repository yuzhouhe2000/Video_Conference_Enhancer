# Library
import torch
import numpy as np
import time
import socket
import threading

from denoiser.demucs import DemucsStreamer
from denoiser.utils import deserialize_model
from npsocket import SocketNumpyArray
from real_time_omlsa.omlsa import *
import json


inport = 9991
outport = 9992
parameter_port = 9993

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
Denoiser = "DSP EQ"
sos_list = ""




def receive_audio_parameter():
    global MIX,Denoiser,sos_list,audio_buffer
    
    while True:
        recieved = server_parameter_receiver.recvfrom(1024)
        json_obj = json.loads(recieved[0].decode('utf-8'))
        print(json_obj)
        MIX = json_obj.get("MIX")
        Denoiser = json_obj.get("Denoiser")
        sos_list = json_obj.get("sos")

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
    FRAME_LENGTH = 20

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
                    
                    if current_time > last_log_time + log_delta:
                        last_log_time = current_time
                        streamer.reset_time_per_frame()

                    last_log_time = current_time
                    length = streamer.total_length if first else streamer.stride

                    first = False
                    current_time += length / sample_rate

                    out = frame
                    frame = torch.from_numpy(frame).mean(dim=1).to(device)
                    with torch.no_grad():
                        out = streamer.feed(frame[None])[0]
                    if not out.numel():
                        continue
                
                    out.clamp_(-1, 1)
                    out = out.cpu().numpy()
                    if CONNECTED == 0:
                        print("initialized sender")
                        time.sleep(2)
                        server_denoiser_sender.initialize_sender('127.0.0.1', outport)
                        CONNECTED = 1
                    else:
                        server_denoiser_sender.send_numpy_array(out)
                        # print(time.time()-start) 


            elif "DSP" in Denoiser:
                while len(audio_buffer) > 20:
                    del(audio_buffer[0])            
                    print("Processing speed is too slow. Switch to DSP denoiser or remove denoiser")
                if len(audio_buffer) > 0:
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
                if len(audio_buffer) > 0: 
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
threads.append(threading.Thread(target=receive_audio_parameter))

print(threads)

if __name__ == '__main__':
    for thread in threads:
        print(thread)
        thread.start()




