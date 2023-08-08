from __future__ import annotations
from .mqtt_base import MQTT_Base
from msb.network.packer import get_packer
from .config import MQTTConf
from msb.config import load_config
from msb.network.pubsub.types import Publisher


class MQTT_Publisher(MQTT_Base, Publisher):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MQTTConf):
        super().__init__(config)
        self.pack = get_packer(config.packstyle)

    def send(self, topic: str | bytes, data: dict):
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        if isinstance(str, bytes):  # TODO this is always False
            topic = topic.decode()

        payload = self.pack(data)
        self.client.publish(
            topic, payload, qos=self.config.qos, retain=self.config.retain
        )


class MQTTRawPublisher(MQTT_Base, Publisher):
    def send(self, topic: bytes, data: bytes):
        """
        Takes raw bytes and sends it to the broker.

        Publishing is asynchronous
        """

        self.client.publish(
            topic, data, qos=self.config.qos, retain=self.config.retain
        )


def get_mqtt_publisher() -> MQTT_Publisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found
    """
    import os

    if "MSB_CONFIG_DIR" in os.environ:
        print("loading mqtt config")
        config = load_config(MQTTConf(), "mqtt", read_commandline=False)
    else:
        print("using default mqtt config")
        config = MQTTConf()
    return MQTT_Publisher(config)


def get_default_publisher() -> MQTT_Publisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found

    Deprecated, use get_mqtt_publisher() instead
    """
    return get_mqtt_publisher()
