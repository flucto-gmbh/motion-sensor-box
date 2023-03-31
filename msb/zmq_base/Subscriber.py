import zmq
import pickle
import json


class Subscriber:
    def __init__(self, topic_or_topics, config):

        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(config.connect_to)
        self.subscribe(topic_or_topics)

        # Possible to add a switch via config here
        # unpacker = pickle
        self.unpacker = json
    
    def subscribe(self, topics):
        # Acceps single topic or list of topics
        if type(topics) is not list:
            self.socket.setsockopt(zmq.SUBSCRIBE, topics)
        else:
            for topic in topics:
                self.socket.setsockopt(zmq.SUBSCRIBE, topic)


    def __del__(self):
        self.socket.close()


    def receive(self):
        (topic, message) = self.socket.recv_multipart()
        message = self.unpacker.loads(message.decode())
        return (topic, message)


