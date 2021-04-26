# EE434 Project Updating 

A software that receive audio & video input and enhance them in real time. Possible application: meeting (using feedback loop in apps like Zoom) and speech/lecture recording/streaming. The software will denoise the received audio, adjust EQ and enhance the audio performance based on video infomation.

Team: Michael Pozzi, Matt Baseheart, Yuzhou He

How it works:

    After Audio Client collects Input Frames
    
        1. If Voice Activity Detected: Client send the audio data to Server through UDP

        2. Another thread waits for server output and play the output

    When Audio Server receives Input:

        1. To Denoiser

        2. To EQ

        3. To video based enhancement 

        4. Send processed audio back to Client through UDP

To run the flask server (linux/mac):

    0. Download "denoiser.th" from drive. Move "[denoiser.th](https://drive.google.com/file/d/17WuFlrUMJZdYiYEqvBfq4hmAd3x_NwDm/view?usp=sharing)" to 434-project/Processor/Audio_Server/denoiser/denoiser.th

    1. pip3 install -r requirements.txt

    2. on Jetson or on any device for server (need to run server first to allow UDP binding):

        cd 434-project/Processor/Audio_Server

        python3 main.py

    3. on PC or any device for client (needs to have sounddevice):
    
        cd 434-project/Processor/Audio_Client

        flask run

    4. connect the video processor to the audio chain:

        cd 434-project/Processor/Video
        
        python3 eye_detect.py

    5. open flask site in chrome "http://127.0.0.1:5000/")

    [Notes: The default IP configuration allows you to run both client and server on the same device. (127.0.0.1) You need to reconfigure the ip and port if you are running them on separate devices.]
    

Notes:

if OSX limits the maximum UDP-package to be 9216, input the following command in terminal to remove the restriction:

    sudo sysctl -w net.inet.udp.maxdgram=65535





