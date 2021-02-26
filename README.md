# EE434 Project Updating 

By Michael Pozzi, Matt Baseheart, Yuzhou He

requirement.txt may not be complete, pip3 install the missing ones

Currently, denoiser live uses soundflower as the default loopback device. Need to change input/output from code.

Reference: https://github.com/facebookresearch/denoiser

****

To run the flask server:

pip3 install -r requirement.txt

download denoiser.th from drive

cd env

flask run

open in site chrome


****

TODO: 

- [ ] add extra denoising function using filters (especially low noises)

- [ ] head tracking

- [ ] depth sensing

- [ ] receive video data from Jetson

- [ ] improve web page;
 
- [ ] allow user to select from available audio input/output from the web page  

- [ ] allow user to switch between denoising input and denoising output from  the web page

- [ ] Maybe continue the training with other datasets to improve performance

- [ ] Maybe using voice activity detection to reduce denoiser computation
