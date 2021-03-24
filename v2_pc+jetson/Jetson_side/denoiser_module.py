# Library
import torch
import numpy as np
import time
import socket

from denoiser.demucs import DemucsStreamer
from denoiser.utils import deserialize_model
from denoiser.VAD import denoiser_VAD
from camera.camera import VideoCamera
from npsocket import SocketNumpyArray
from buffer import udp_buffer



# GLOBAL_VARIABLES
MODEL_PATH = "denoiser/denoiser.th"
DRY = 0.04
VAD_buffer = udp_buffer()
output_buffer = udp_buffer()
frame_num = 1
sample_rate = 16_000

# Load Model
pkg = torch.load(MODEL_PATH)
if 'model' in pkg:
    if 'best_state' in pkg:
        pkg['model']['state'] = pkg['best_state']
    model = deserialize_model(pkg['model'])
else:
    model = deserialize_model(pkg)
model.eval()
streamer = DemucsStreamer(model, dry=DRY, num_frames=frame_num)


async def connect_denoiser(audio_buffer):

    first = True
    current_time = 0
    last_log_time = 0
    last_error_time = 0
    cooldown_time = 2
    log_delta = 10
    sr_ms = sample_rate / 1000
    stride_ms = streamer.stride / sr_ms

    frame, overflow = audio_buffer.read_buffer(30)
    VAD_RESULT = denoiser_VAD(frame)


    # print(f"Ready to process audio, total lag: {streamer.total_length / sr_ms:.1f}ms.")


    # while (LIVE == 1):
    #     if current_time > last_log_time + log_delta:
    #         last_log_time = current_time
    #         tpf = streamer.time_per_frame * 1000
    #         rtf = tpf / stride_ms
    #         print(f"time per frame: {tpf:.1f}ms, ", end='')
    #         print(f"RTF: {rtf:.1f}")
    #         streamer.reset_time_per_frame()
    #     last_log_time = current_time
    #     length = streamer.total_length if first else streamer.stride
    #     first = False
    #     current_time += length / sample_rate

    #     # TODO
    #     frame, overflow = stream_in.read(length)
    #     # VAD module here?
    #     VAD_RESULT = 
    #     if VAD_RESULT == 1:
    #         frame = torch.from_numpy(frame).mean(dim=1).to("cpu")
    #         with torch.no_grad():
    #             out = streamer.feed(frame[None])[0]
    #         if not out.numel():
    #             continue
    #         # compresser
    #         # out = 0.99 * torch.tanh(out)

    #         out = out[:, None].repeat(1, channels_out)
    #         mx = out.abs().max().item()
    #         if mx > 1:
    #             print("Clipping!!")
    #         out.clamp_(-1, 1)
    #         out = out.cpu().numpy()


    #         # TODO
    #         underflow = stream_out.write(out)



    #         if overflow or underflow:
    #             if current_time >= last_error_time + cooldown_time:
    #                 last_error_time = current_time
    #                 tpf = 1000 * streamer.time_per_frame

       
    # # TODO:replace by UDP
    # stream_out.stop()
    # stream_in.stop()
    # return ('', 204)



# def control_panel():
#     global DRY
#     if request.method == 'POST':
#         volume = request.form.get('slide')
#         print('volume:', volume)
#         DRY = int(volume)/1000
#         #return jsonify({'volume': volume})
#     return ('', 204)




# @app.route('/VAD', methods=['POST'])
# def VAD():
#     global LIVE
#     global VAD_RESULT
#     caps = query_devices(None, "input")

   
#     stream_in.start()
#     while(LIVE == 1):
#         frame, overflow = stream_in.read(30)
#         VAD_RESULT = denoiser_VAD(frame)
#         print(VAD_RESULT)
#     return ('', 204)


if __name__ == '__main__':
    denoiser_live()



