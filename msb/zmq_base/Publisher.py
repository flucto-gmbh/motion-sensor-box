import zmq
import sys
import json

from msb.zmq_base.config import PublisherSubscriberConf


class Publisher:
    def __init__(self, config: PublisherSubscriberConf):
        self.config = config
        # after merging with configuration branch, update of
        # configuration through configuration file should happen here

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        # Possible to add a switch via config here
        # self.packer = pickle
        self.packer = json
        self.connect()

    def connect(self):
        try:
            # print(f"Connecting to { self.config.producer_connection }")
            self.socket.connect(self.config.producer_connection)
            # self.socket.bind(connect_to)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def send(self, topic: bytes, data: dict):
        # data = self.packer.dumps(data)
        data = json.dumps(data)
        self.socket.send_multipart([topic, data.encode()])

    def __del__(self):
        self.socket.close()


def get_default_publisher() -> Publisher:
    default_config = PublisherSubscriberConf()
    return Publisher(default_config)
