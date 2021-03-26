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

inport = 9991
outport = 9992

# Define Server Socket (receiver)
server_denoiser_receiver = SocketNumpyArray()
server_denoiser_receiver.initialize_receiver(inport)
server_denoiser_sender = SocketNumpyArray()

# GLOBAL_VARIABLES
MODEL_PATH = "denoiser/denoiser.th"
DRY = 0.04
frame_num = 1
sample_rate = 16_000
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
    last_error_time = 0
    cooldown_time = 2
    log_delta = 10
    sr_ms = sample_rate / 1000
    streamer = DemucsStreamer(model, dry=DRY, num_frames=frame_num)
    stride_ms = streamer.stride / sr_ms
    
    print(f"Ready to process audio, total lag: {streamer.total_length / sr_ms:.1f}ms.")

    while True:
        
        if len(audio_buffer) > 0:
            while len(audio_buffer) > 10:
                del(audio_buffer[0])
            frame = audio_buffer[0]
            del(audio_buffer[0])
            print(len(audio_buffer))

            
            VAD_RESULT = denoiser_VAD(frame)
            # VAD_RESULT = 1

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

            if VAD_RESULT == 1:
                start = time.time()
                out = frame
                frame = torch.from_numpy(frame).mean(dim=1).to(device)
                with torch.no_grad():
                    out = streamer.feed(frame[None])[0]

                if not out.numel():
                    continue
                # compresser
                # out = 0.99 * torch.tanh(out)

                # TODO: repeat is 2
                out = out[:, None].repeat(1,2)
                mx = out.abs().max().item()
                if mx > 1:
                    print("Clipping!!")
                out.clamp_(-1, 1)
                out = out.cpu().numpy()
                

                if CONNECTED == 0:
                    server_denoiser_sender.initialize_sender('127.0.0.1', outport)
                    CONNECTED = 1
                else:
                    server_denoiser_sender.send_numpy_array(out)
                    print(time.time()-start)



threads.append(threading.Thread(target=receive_audio))
threads.append(threading.Thread(target=denoiser_live))
print(threads)

if __name__ == '__main__':
    for thread in threads:
        print(thread)
        thread.start()




