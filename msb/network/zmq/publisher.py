import zmq
import sys
import json

from .config import ZMQConf
from msb.config import load_config
from msb.network.pubsub.types import Publisher
from msb.network.packer import get_packer


class ZMQ_Publisher(Publisher):
    def __init__(self, config: ZMQConf):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.packer = get_packer(config.packstyle)
        self.connect()

    def connect(self):
        try:
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def send(self, topic: bytes, data: dict):
        data = self.packer(data)
        self.socket.send_multipart([topic, data.encode('utf-8')])

    def __del__(self):
        self.socket.close()


def get_default_publisher() -> ZMQ_Publisher:
    import os
    if "MSB_CONFIG_DIR" in os.environ:
        print("loading zmq config")
        config = load_config(ZMQConf(), "zmq", read_commandline=False)
    else:
        print("using default zmq config")
        config = ZMQConf()
    return ZMQ_Publisher(config)
