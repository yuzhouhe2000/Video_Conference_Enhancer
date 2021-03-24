import os

class udp_buffer():
    def __init__(self):
        self.length = 0
        self.data = []

    def read(self):
        if self.length > 0:
            value = self.data[0]
            self.data = self.data[1:-1]
            length =length - 1
        return value

    def write(self,frame):
        self.data.append(frame)