import zmq
import sys
import json

from .config import ZMQConf
from msb.config import load_config


class ZMQ_Publisher:
    def __init__(self, config: ZMQConf):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.packer = json
        self.connect()

    def connect(self):
        try:
            # print(f"Connecting to { self.config.producer_connection }")
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def send(self, topic: bytes, data: dict):
        data = self.packer.dumps(data)
        self.socket.send_multipart([topic, data.encode('utf-8')])

    def __del__(self):
        self.socket.close()


def get_default_publisher() -> ZMQ_Publisher:
    import os
    if "MSB_CONFIG_DIR" in os.environ:
        print("loading zmq config")
        config = load_config(PublisherSubscriberConf(), "zmq", read_commandline=False)
    else:
        print("using default zmq config")
        config = PublisherSubscriberConf()
    return ZMQ_Publisher(config)
