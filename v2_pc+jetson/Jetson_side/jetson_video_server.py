# Library
import torch
import numpy as np
import time
import socket

from tracker.face_mark import face_mark
from npsocket import SocketNumpyArray

inport = 9995
outport = 9996

# Define Server Socket (receiver)
server_denoiser_receiver = SocketNumpyArray()
server_denoiser_receiver.initialize_receiver(inport)
server_denoiser_sender = SocketNumpyArray()


def tracker_live():
    CONNECTED = 0
    while True:
        frame = server_denoiser_receiver.receive_array()

        out = frame

        if CONNECTED == 0:
            server_denoiser_sender.initialize_sender('localhost', outport)
            server_denoiser_sender.send_numpy_array(out)
            CONNECTED = 1
        else:
            server_denoiser_sender.send_numpy_array(out)


if __name__ == '__main__':
    
    tracker_live()



