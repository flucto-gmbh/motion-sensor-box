from paho.mqtt import client as mqtt_client
from dataclasses import dataclass
import ssl
import json

from msb.zmq_base.Subscriber import get_default_subscriber
from msb.mqtt.config import MQTTconf
from msb.mqtt.packer import packer_factory
from msb.config import load_config


class MQTT_Base:
    def __init__(self, config):
        self.config = config
        self.connect()
        self.select_packer()

    def connect(self):
        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.config.user, self.config.password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if self.config.ssl:
            # By default, on Python 2.7.9+ or 3.4+,
            # the default certification authority of the system is used.
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        self.client.connect(self.config.broker, self.config.port)

    def send(self, topic: str, data: dict):
        payload = self.pack(data)
        self.client.publish(topic, payload, qos=self.config.qos)

    def select_packer(self):
        self._packer = packer_factory(self.config.packstyle)

    def pack(self, data):
        return self._packer(data)

    # MQTT callbacks
    def _on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print(f"MQTT node connected to {self.config.broker}:{self.config.port}")
        else:
            print("Connection failed!")

    def _on_disconnect(self, client, userdata, return_code):
        print(f"Disconnected from broker with return code {return_code}")


class MQTT_Publisher(MQTT_Base):
    def __init__(self, config, zmq_subscriber):
        super().__init__(config)
        self.subscriber = zmq_subscriber
        self.client.on_publish = self._on_publish

    def _map_topic(zmq_topic):
        return zmq_topic

    def _on_publish(self, client, userdata, message_id):
        print(f"Published message with id {message_id}")

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
    zmq_sub = get_default_subscriber()
    mqtt_publisher = MQTT_Publisher(config, zmq_sub)
    mqtt_publisher.zmq_to_mqtt_loop()
