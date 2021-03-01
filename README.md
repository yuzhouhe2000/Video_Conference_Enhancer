# EE434 Project Updating 

Team: Michael Pozzi, Matt Baseheart, Yuzhou He

requirement.txt may not be complete, pip3 install the missing ones

Currently, denoiser live uses soundflower as the default loopback device. Need to change input/output from code.

Reference: https://github.com/facebookresearch/denoiser

****

To run the flask server:

pip3 install -r requirement.txt

download denoiser.th from drive (trained on Valentini dataset and DNS dataset on 64 hidden layers)

move denoiser.th to env/denoiser/ folder

cd env

flask run

open site in chrome


if dlib fails to install, try:

git clone https://github.com/davisking/dlib.git

cd dlib

mkdir build; cd build; cmake ..; cmake --build .

cd ..

python3 setup.py install

****

TODO: 

- [X] Template for flask app + a basic denoiser model

- [ ] Adjust sound volume (mono/bi channel) by speaker position

- [ ] Add extra denoising function using filters

- [ ] Face and mouth detection

- [ ] Voice activity detection from mouth movement

- [ ] Design a method to measure denoiser performance and time lag

- [ ] Depth sensing



