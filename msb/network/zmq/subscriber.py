from __future__ import annotations
import zmq
import sys
from collections.abc import Sequence

from .config import ZMQConf
from msb.config import load_config
from msb.network.pubsub.types import Subscriber
from msb.network.packer import get_unpacker


class ZMQ_Subscriber(Subscriber):
    def __init__(self, topic: bytes | str | list[bytes] | list[str], config: ZMQConf):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.connect()
        self.subscribe(topic)

        self.unpacker = get_unpacker(config.packstyle)

    def connect(self):
        try:
            # print(f"Connecting to { self.config.consumer_connection }")
            self.socket.connect(self.config.subscriber_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def _subscribe_single_topic(self, topic: bytes | str):
        if isinstance(topic, str):
            topic = topic.encode()
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def subscribe(self, topic: bytes | str | list[bytes] | list[str]):
        # Accepts single topic or list of topics
        if isinstance(topic, Sequence):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def receive(self) -> tuple[bytes, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        (topic, message) = self.socket.recv_multipart()
        message = self.unpacker(message.decode())
        return (topic, message)

    def __del__(self):
        self.socket.close()


class ZMQRawSubscriber(ZMQ_Subscriber):

    def receive(self) -> tuple[bytes, bytes]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        (topic, message) = self.socket.recv_multipart()
        return topic, message


def get_default_subscriber(topic: bytes) -> ZMQ_Subscriber:
    import os

    if "MSB_CONFIG_DIR" in os.environ:
        print("loading zmq config")
        config = load_config(ZMQConf(), "zmq", read_commandline=False)
    else:
        print("using default zmq config")
        config = ZMQConf()
    return ZMQ_Subscriber(topic, config)
