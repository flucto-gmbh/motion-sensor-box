import zmq
import json
import sys

from msb.zmq_base.config import PublisherSubscriberConf


class Subscriber:
    def __init__(self, topic: bytes, config: PublisherSubscriberConf):
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

    def subscribe(self, topic: bytes | list[bytes]):
        # Acceps single topic or list of topics
        if isinstance(topic, list):
            for t in topic:
                self.socket.setsockopt(zmq.SUBSCRIBE, t)
        else:
            self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def receive(self) -> tuple[bytes, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        (topic, message) = self.socket.recv_multipart()
        message = self.unpacker.loads(message.decode())
        return (topic, message)

    def __del__(self):
        self.socket.close()


def get_default_subscriber(topic: bytes) -> Subscriber:
    config = PublisherSubscriberConf()
    return Subscriber(topic, config)
