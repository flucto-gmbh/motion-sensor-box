from __future__ import annotations

from queue import SimpleQueue

from msb.config import load_config
from msb.network.packer import get_unpacker
from msb.network.pubsub.types import Subscriber

from .config import MQTTConf
from .mqtt_base import MQTT_Base


class MQTT_Subscriber(MQTT_Base, Subscriber):
    """
    MQTT subscriber, wraps around ecplipse's paho mqtt client.
    Network message loop is handled in a separated thread.

    Incoming messages are saved as a stack when not processed via the receive() function.
    """

    def __init__(self, topics, config: MQTTConf):
        super().__init__(config)
        self._message_queue = SimpleQueue()
        self.subscribe(topics)
        self.client.on_message = self._on_message
        self.unpacker = get_unpacker(config.packstyle)

    def _subscribe_single_topic(self, topic: bytes | str):
        if isinstance(topic, bytes):
            topic = topic.decode()
        if self.config.verbose:
            print(f"Subscribed to: {topic}")
        self.client.subscribe(topic, self.config.qos)

    def _subscribe_multiple_topics(self, topics: list[bytes] | list[str]):
        topics = [
            topic.decode() if isinstance(topic, bytes) else topic for topic in topics
        ]
        subscription_list = [(topic, self.config.qos) for topic in topics]
        if self.config.verbose:
            print(f"Subscribed to: {topics}")
        self.client.subscribe(subscription_list)

    def subscribe(self, topics):
        """
        Subscribe to one or multiple topics
        """
        # if subscribing to multiple topics, use a list of tuples
        if isinstance(topics, list):
            self._subscribe_multiple_topics(topics)
        else:
            self.client.subscribe(topics, self.config.qos)

    def receive(self) -> tuple[bytes, dict]:
        """
        Reads a message from mqtt and returns it

        Messages are saved in a stack, if no message is available, this function blocks.

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        self._raise_if_thread_died()
        mqtt_message = self._message_queue.get(
            block=True, timeout=self.config.timeout_s
        )

        topic = mqtt_message.topic.encode("utf-8")
        message_returned = self.unpacker(mqtt_message.payload.decode())
        return (topic, message_returned)

    # callback to add incoming messages onto stack
    def _on_message(self, client, userdata, message):
        self._message_queue.put(message)

        if self.config.verbose:
            print(f"Topic: {message.topic}")
            print(f"MQTT message: {message.payload.decode()}")


def get_mqtt_subscriber(topic: bytes | str) -> MQTT_Subscriber:
    """
    Generate mqtt subscriber with configuration from yaml file,
    falls back to default values if no config is found
    """
    import os

    if "MSB_CONFIG_DIR" in os.environ:
        print("loading mqtt config")
        config = load_config(MQTTConf(), "mqtt", read_commandline=False)
    else:
        print("using default mqtt config")
        config = MQTTConf()
    return MQTT_Subscriber(topic, config)


def get_default_subscriber(topic: bytes | str) -> MQTT_Subscriber:
    """
    Generate mqtt subscriber with configuration from yaml file,
    falls back to default values if no config is found

    Deprecated, use get_mqtt_subscriber(topic) instead.
    """
    return get_mqtt_subscriber(topic)
