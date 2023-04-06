import zmq
import pickle
import json

from msb.zmq_base.Config import ZMQConf

class Subscriber:
    def __init__(self, topic_or_topics):

        self.config = ZMQConf()
        # after merging with configuration branch, update of
        # configuration through configuration file should happen here

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.config.connect_to_subscriber)
        self.subscribe(topic_or_topics)

        # Possible to add a switch via config here
        # unpacker = pickle
        if self.config.packer == "json":
            self.unpacker = json
        elif self.config.packer == "pickle":
            self.unpacker = pickle
        else:
            raise Exception(f'{self.config.packer} is not a valid packer/unpacker. Please proide a valid serializer')
    
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
        """
        reads a message from the zmq bus and returns it

        returns:
            tuple(topic, message), where topic is a byte string identifyin the 
            source service of the message
        """
        (topic, message) = self.socket.recv_multipart()
        message = self.unpacker.loads(message.decode())
        return (topic, message)

