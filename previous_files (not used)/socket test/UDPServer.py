import socket

UDP_IP = "192.168.5.138"
# Your PC address
UDP_PORT = 5454

ServerSocket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
ServerSocket.bind((UDP_IP, UDP_PORT))

while 1:
    print ("Received: "+str(ServerSocket.recv(30))) # buffer size is 30 bytes
    
