from __future__ import annotations
from msb.mqtt.mqtt_base import MQTT_Base
from msb.mqtt.packer import packer_factory
from msb.mqtt.config import MQTTconf
from msb.config import load_config


class MQTT_Publisher(MQTT_Base):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MQTTconf):
        super().__init__(config)
        self.pack = packer_factory(config.packstyle)

    def send(self, topic: str | bytes, data: dict):
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        if isinstance(str, bytes):
            topic = topic.decode()

        payload = self.pack(data)
        self.client.publish(
            topic, payload, qos=self.config.qos, retain=self.config.retain
        )


def get_mqtt_publisher() -> MQTT_Publisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found
    """
    import os

    if "MSB_CONFIG_DIR" in os.environ:
        print("loading mqtt config")
        config = load_config(MQTTconf(), "mqtt", read_commandline=False)
    else:
        print("using default mqtt config")
        config = MQTTconf()
    return MQTT_Publisher(config)


def get_default_publisher() -> MQTT_Publisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found

    Deprecated, use get_mqtt_publisher() instead
    """
    return get_mqtt_publisher()
