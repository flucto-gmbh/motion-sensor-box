from msb.mqtt.mqtt_base import MQTT_Base


class ZMQ_to_MQTT_Forwarder:
    def __init__(self, config, subscriber, publisher):
        self.config = config
        self.subscriber = subscriber
        self.publisher = publisher

    def _zmq_to_mqtt(self):
        # This is blocking
        (zmq_topic, data) = self.subscriber.receive()
        mqtt_topic = self._map_topic(zmq_topic)

        self.publisher.send(mqtt_topic, data)

    def zmq_to_mqtt_loop(self):
        """
        Main loop: data comes in through zmq subscription socket,
        passed on to mqtt publish
        """
        while True:
            self._zmq_to_mqtt()

    def _map_topic(self, zmq_topic):
        return self.config.mapping + zmq_topic.decode()
