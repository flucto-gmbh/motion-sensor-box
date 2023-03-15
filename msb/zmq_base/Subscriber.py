import zmq
import pickle
import sys
import time


class Subscriber:
    def __init__(self, topic = "", protocol="tcp", ip="localhost", port="5555", connect_to = None):
        self.topic = topic.encode() if type(topic) != bytes else topic


        if not connect_to:
            connect_to = f"{protocol}://{ip}:{port}"
            print(f"connecting to : {connect_to}")

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(connect_to)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        print(f"Subscribed to {self.topic.decode()}")
    

    def __del__(self):
        self.socket.close()


    def receive(self):
        (topic, message) = self.socket.recv_multipart()
        print(f"Received data {message.decode()}")
        return (topic, message)


