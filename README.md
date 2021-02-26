# EE434 Project Updating 

Team: Michael Pozzi, Matt Baseheart, Yuzhou He

requirement.txt may not be complete, pip3 install the missing ones

Currently, denoiser live uses soundflower as the default loopback device. Need to change input/output from code.

Reference: https://github.com/facebookresearch/denoiser

****

To run the flask server:

pip3 install -r requirement.txt

download denoiser.th from drive

move denoiser.th to env/denoiser/ folder

cd env

flask run

open site in chrome


****

TODO: 

- [ ] Add extra denoising function using filters (especially low noises)

- [ ] Head tracking

- [ ] Depth sensing

- [ ] Receive video data from Jetson

- [ ] Improve web page;
 
- [ ] Allow user to select from available audio input/output from the web page  

- [ ] Allow user to switch between denoising input and denoising output from  the web page

- [ ] Maybe continue the training with other datasets to improve performance

- [ ] Maybe using voice activity detection to reduce denoiser computation
