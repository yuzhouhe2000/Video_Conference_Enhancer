# # Library
# import torch
# import numpy as np
# import time
# import socket
# import cv2

# from tracker.face_mark import face_mark
# from npsocket import SocketNumpyArray

# inport = 9995
# outport = 9996

# # Define Server Socket (receiver)
# server_video_receiver = SocketNumpyArray()
# server_video_receiver.initialize_receiver(inport)
# server_video_sender = SocketNumpyArray()





# def tracker_live():
#     CONNECTED = 0
#     while True:
#         frame = server_video_receiver.receive_array()


#         ret, frame = self.video.read()
#         ret, jpeg = cv2.imencode('.jpg', frame)
#         out =  jpeg.tobytes()

#         out = frame

#         if CONNECTED == 0:
#             server_video_sender.initialize_sender('localhost', outport)
#             server_video_sender.send_numpy_array(out)
#             CONNECTED = 1
#         else:
#             server_video_sender.send_numpy_array(out)


# if __name__ == '__main__':
    
#     tracker_live()


import cv2
import socket
import pickle
import numpy as np

host = "0.0.0.0"
video_inport = 5000
video_outport = 9999

max_length = 65540

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, video_inport))

frame_info = None
buffer = None
frame = None

print("-> waiting for connection")

while True:
    data, address = sock.recvfrom(max_length)
    
    if len(data) < 100:
        frame_info = pickle.loads(data)

        if frame_info:
            nums_of_packs = frame_info["packs"]

            for i in range(nums_of_packs):
                data, address = sock.recvfrom(max_length)

                if i == 0:
                    buffer = data
                else:
                    buffer += data

            frame = np.frombuffer(buffer, dtype=np.uint8)
            frame = frame.reshape(frame.shape[0], 1)

            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            frame = cv2.flip(frame, 1)
            
            if frame is not None and type(frame) == np.ndarray:
                cv2.imshow("Stream", frame)
                if cv2.waitKey(1) == 27:
                    break
                
print("goodbye")


