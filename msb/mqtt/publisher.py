from msb.mqtt.mqtt_base import MQTT_Base
from msb.mqtt.packer import packer_factory
from msb.mqtt.config import MQTTconf
from msb.config import load_config


class MQTT_Publisher(MQTT_Base):
    def __init__(self, config):
        super().__init__(config)
        self.pack = packer_factory(config.packstyle)

    def send(self, topic: str, data: dict):
        if isinstance(str, bytes):
            topic = topic.decode()

        payload = self.pack(data)
        self.client.publish(topic, payload, qos=self.config.qos)


def get_default_publisher() -> MQTT_Publisher:
    import os
    if "MSB_CONFIG_DIR" in os.environ:
        print("loading zmq config")
        config = load_config(MQTTconf(), "mqtt", read_commandline=False)
    else:
        print("using default mqtt config")
        config = MQTTconf()
    return MQTT_Publisher(config)
