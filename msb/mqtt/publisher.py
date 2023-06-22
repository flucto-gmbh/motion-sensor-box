from msb.mqtt.mqtt_base import MQTT_Base
from msb.mqtt.packer import packer_factory


class MQTT_Publisher(MQTT_Base):
    def __init__(self, config):
        super().__init__(config)
        self.pack = packer_factory(config.packstyle)

    def send(self, topic: str, data: dict):
        if isinstance(str, bytes):
            topic = topic.decode()

        payload = self.pack(data)
        self.client.publish(topic, payload, qos=self.config.qos)
