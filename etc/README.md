# EE434 Project Updating 

A software that receive audio & video input and enhance them in real time. Possible application: meeting (using feedback loop in apps like Zoom) and speech/lecture recording/streaming. The software will denoise the received audio and enhance the audio performance based on video infomation. Also, a pan tilt system will be used to let the camera focus on the speaker all the time.

Team: Michael Pozzi, Matt Baseheart, Yuzhou He

requirements.txt may not be complete, pip3 install the missing ones

Currently, denoiser live uses soundflower as the default loopback device. You can configure it with your own devices. 


Reference: https://github.com/facebookresearch/denoiser


****

TODO: 

- [X] Template for flask app + a basic denoiser model

- [x] Face and mouth detection

- [x] Voice Activity Detection using voice

- [X] Server, Client, and UDP

- [ ] Adjust sound volume by speaker position

- [ ] Add extra denoising function using filters

- [ ] Depth sensing using eye separation

- [ ] Add configure.py to control all setups easily

- [ ] Track face and eyes using Camshift

****

To run the flask server (linux/mac):

download "denoiser.th" and "shape_predictor_68_face_landmarks.dat" from drive

move "[denoiser.th](https://drive.google.com/file/d/17WuFlrUMJZdYiYEqvBfq4hmAd3x_NwDm/view?usp=sharing)" to env/denoiser/

move "[shape_predictor_68_face_landmarks.dat](https://drive.google.com/file/d/1skzv2u-eo2ySiN9yJ0jTLcZwwJWxg-d1/view?usp=sharing)" to env/camera/

    1. pip3 install -r requirements.txt

    2. on Jetson or on any device for server:

        cd v3/Jetson_side

        python3 jetson_denoiser_server.py

    3. on PC or any device for client (needs to have sounddevice):
    
        cd v3/PC_side/env_2.0

        flask run

    4. open site in chrome

Checkpoints:

    v1: run on pc with a flask app. env(v1.1) has a recording feature, while it is removed in env(v1.2). The recording uses javascript recorder, and streaming uses sounddevice. v1.2 is used to develop v2, with socket communications.
    
    v2: run client (pc_side) on pc and server (jetson_side) on jetson. needs to set up the socket. Communication is through UDP socket. video function is not developed in v2.
    
    v3: becaue our Jetson nano is not that fast, we moved denoiser_server to the CPU on PC and want to save jetsoon GPU resources for CV application. You can also change the socket configuration and run it on jetson / other cloud computing devices. CV application is still under development.

    


if dlib fails to install, try to install from source (for cv):

    git clone https://github.com/davisking/dlib.git

    cd dlib

    mkdir build; cd build; cmake ..; cmake --build .

    cd ..

    python3 setup.py install

    (if assert error happens, delete the lines with the assert(false) statement in the error files)
    

if OSX has limited the maximum UDP-package to be 9216:

    sudo sysctl -w net.inet.udp.maxdgram=65535





