from paho.mqtt import client as mqtt_client
from dataclasses import dataclass
import ssl
import json

from msb.zmq_base.Subscriber import get_default_subscriber
from msb.mqtt.config import MQTTconf
from msb.mqtt.mqtt_base import MQTT_Base
from msb.mqtt.packer import packer_factory
from msb.config import load_config


class MQTT_Forwarder(MQTT_Base):
    def __init__(self, config, zmq_subscriber):
        super().__init__(config)
        self.subscriber = zmq_subscriber

    def _map_topic(self, zmq_topic):
        return self.config.mapping + zmq_topic.decode()

    def _zmq_to_mqtt(self):
        # This is blocking
        (zmq_topic, data) = self.subscriber.receive()
        mqtt_topic = self._map_topic(zmq_topic)

        self.send(mqtt_topic, data)

    def zmq_to_mqtt_loop(self):
        """
        Main loop: data comes in through zmq subscription socket,
        passed on to mqtt publish
        """
        while True:
            self._zmq_to_mqtt()


class MQTT_Subscriber(MQTT_Base):
    def __init__(self, config, zmq_publisher):
        super().__init__(config)
        self.publisher = zmq_publisher
        self._subscribe_to_topics()
        self.client.on_message = self._on_message
        self.client.loop_start()

    def __del__(self):
        self.client.loop_stop()

    def _subscribe_to_topics(self):
        # if subscribing to multiple topics, use a list of tuples
        subscription_list = [(topic, self.config.qos) for topic in self.config.topics]
        self.client.subscribe(subscription_list)

    def _on_message(self, client, userdata, message):
        """
        Callback on message, processes message and sends via ZMQ
        """
        try:
            self._process_message(message)
        except Exception as e:
            print("Could not unpack message")
            print(e)

    def _process_message(self, message):
        decoded_message = message.payload.decode()
        data = json.loads(decoded_message)
        zmq_topic = self._map_topic(message.topic)
        self.publisher.send(zmq_topic, data)
        print(f"Received message '{decoded_message}' on topic '{message.topic}'")

    def _map_topic(self, mqtt_topic):
        return mqtt_topic


def main():
    config = load_config(MQTTconf(), "mqtt")
    for topic in config.topics:
        print(f"Subscribing to {topic}")
    zmq_sub = get_default_subscriber([topic.encode() for topic in config.topics])
    mqtt_publisher = MQTT_Forwarder(config, zmq_sub)
    mqtt_publisher.zmq_to_mqtt_loop()
