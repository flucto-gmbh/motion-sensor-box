from msb.network.config import MQTTConf
from msb.network.mqtt.publisher import MQTTRawPublisher
from msb.network.zmq.subscriber import ZMQRawSubscriber


class ZMQ2MQTTForwarder:
    def __init__(
        self,
        config: MQTTConf,
        subscriber: ZMQRawSubscriber,
        publisher: MQTTRawPublisher,
    ):
        self.subscriber = subscriber
        self.publisher = publisher
        self.config = config
        self.topic_prefix: bytes = self.config.mapping.encode("utf-8")

    def _map_topic(self, zmq_topic: bytes) -> bytes:
        return self.topic_prefix + zmq_topic

    def _zmq_to_mqtt(self):
        # This is blocking
        (zmq_topic, data) = self.subscriber.receive()
        mqtt_topic = self._map_topic(zmq_topic)
        self.publisher.send(mqtt_topic, data)

    def run(self):
        """
        Main loop: data comes in through zmq subscription socket,
        passed on to mqtt publish
        """
        while True:
            self._zmq_to_mqtt()
