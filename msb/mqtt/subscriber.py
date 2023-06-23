from time import sleep

from msb.config import load_config
from msb.mqtt.mqtt_base import MQTT_Base
from msb.mqtt.config import MQTTconf
from msb.mqtt.packer import unpacker_factory


class MessageStack:
    def __init__(self):
        self._container = list()

    def push(self, message):
        self._container.append(message)

    def pop(self):
        return self._container.pop()

    def __len__(self):
        return len(self._container)


class MQTT_Subscriber(MQTT_Base):
    def __init__(self, topics, config: MQTTconf):
        super().__init__(config)
        self._message_stack = MessageStack()
        self.subscribe(topics)
        self.client.on_message = self._on_message
        self.unpacker = unpacker_factory(config.packstyle)

    def _subscribe_single_topic(self, topic: bytes | str):
        if isinstance(topic, bytes):
            topic = topic.decode()
        if self.config.verbose:
            print(f"Subscribed to: {topic}")
        self.client.subscribe(topic, self.config.qos)

    def _subscribe_multiple_topics(self, topics: list[bytes] | list[str]):
        topics = [topic.decode() if isinstance(topic, bytes) else topic for topic in topics]
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
        reads a message from mqtt and returns it

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        # retries = 0

        while len(self._message_stack) == 0:
            sleep(0.01)

            # Is this a good idea?
            # retries += 1
            # if retries > 1000:
            #     raise TimeoutError("No message received")

        mqtt_message = self._message_stack.pop()

        topic = mqtt_message.topic.encode("utf-8")
        message_returned = self.unpacker(mqtt_message.payload.decode())
        return (topic, message_returned)

    def _on_message(self, client, userdata, message):
        """
        Callback on message, processes message and sends via ZMQ
        """
        self._message_stack.push(message)

        if self.config.verbose:
            print(f"Topic: {message.topic}")
            print(f"MQTT message: {message.payload.decode()}")


def get_default_subscriber(topic: bytes | str) -> MQTT_Subscriber:
    import os
    if "MSB_CONFIG_DIR" in os.environ:
        print("loading zmq config")
        config = load_config(MQTTconf(), "mqtt", read_commandline=False)
    else:
        print("using default zmq config")
        config = MQTTconf()
    return MQTT_Subscriber(topic, config)
