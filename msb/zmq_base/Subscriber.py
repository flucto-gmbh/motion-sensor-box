import zmq
import json
import sys

from msb.zmq_base.Config import ZMQConf


class Subscriber:
    def __init__(self, topic: bytes, config):
        self.config = config
        # after merging with configuration branch, update of
        # configuration through configuration file should happen here

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.connect()
        self.subscribe(topic)

        # Possible to add a switch via config here
        # unpacker = pickle
        self.unpacker = json

    def connect(self):
        try:
            # print(f"Connecting to { self.config.consumer_connection }")
            self.socket.connect(self.config.consumer_connection)
            # self.socket.bind(connect_to)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def subscribe(self, topic: bytes):
        # Acceps single topic or list of topics
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def receive(self) -> tuple:
        """
        reads a message from the zmq bus and returns it

        returns:
            tuple(topic, message), where topic is a byte string identifying the
            source service of the message
        """
        (topic, message) = self.socket.recv_multipart()
        message = self.unpacker.loads(message.decode())
        return (topic, message)

    def __del__(self):
        self.socket.close()


def get_default_subscriber(topic: bytes) -> Subscriber:
    config = ZMQConf()
    return Subscriber(topic, config)
