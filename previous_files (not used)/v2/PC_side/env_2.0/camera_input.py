import cv2
import socket
import math
import pickle
import sys


max_length = 65000
host = "0.0.0.0"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def video_input():
    from app import outport_video,CAMERA_CONTROl
    port = outport_video
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    while CAMERA_CONTROl == 1:
        if ret:
            # compress frame
            retval, buffer = cv2.imencode(".jpg", frame)

            if retval:
                # convert to byte array
                buffer = buffer.tobytes()
                # get size of the frame
                buffer_size = len(buffer)

                num_of_packs = 1

                if buffer_size > max_length:
                    num_of_packs = math.ceil(buffer_size/max_length)

                frame_info = {"packs":num_of_packs}

                # send the number of packs to be expected
                print("Number of packs:", num_of_packs)
                sock.sendto(pickle.dumps(frame_info), (host, port))
                
                left = 0
                right = max_length

                for i in range(num_of_packs):
                    print("left:", left)
                    print("right:", right)

                    # truncate data to send
                    data = buffer[left:right]
                    left = right
                    right += max_length

                    # send the frames accordingly
                    print(len(data))
                    sock.sendto(data, (host, port))
            
            ret, frame = cap.read()

    print("done")
