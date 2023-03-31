import zmq
import pickle
import sys
import json

class Publisher:
    def __init__(self, config):

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.config = config

        # Possible to add a switch via config here
        # self.packer = pickle
        self.packer = json


    def connect(self):
        try:
            self.socket.connect(self.config.connect_to)
            # self.socket.bind(connect_to)
        except Exception as e:
            print(f'failed to bind to zeromq socket: {e}')
            sys.exit(-1)



    def send(self, topic, data):
        data = self.packer.dumps(data)
        self.socket.send_multipart([topic, data.encode()])

    
    def __del__(self):
        self.socket.close()
    #     self.context.term()
