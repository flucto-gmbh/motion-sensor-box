from paho.mqtt import client as mqtt_client
from dataclasses import dataclass
import ssl
import time
import json

from msb.zmq_base.Subscriber import get_default_subscriber


@dataclass
class MQTTConfig:
    broker: str = "localhost"
    user: str = "mqttuser"
    password: str = "mqttpass"
    port: int = 1883
    ssl: bool = False
    zmq_topics: list = []
    mqtt_topics: list = []
    timesource: str = "default"


class MQTT_Base:
    def __init__(self, config):
        self.config = config
        self.create_topic_mapping()
        self.connect()

    # MQTT callbacks
    def on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print(f"MQTT node connected to {self.config.broker}:{self.config.port}")
        else:
            print("Connection failed!")

    def _on_disconnect(self, client, userdata, return_code):
        print(f"Disconnected from broker with return code {return_code}")

    def connect(self):
        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.config.user, self.config.passwd)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if self.config.ssl:
            # By default, on Python 2.7.9+ or 3.4+,
            # the default certification authority of the system is used.
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        self.client.connect(self.config.broker, self.config.port)

    def send(self, topic: str, data: dict):
        payload = json.dumps(data)
        self.client.publish(topic, payload, qos=self.config.qos)


class MQTT_Publisher(MQTT_Base):
    def __init__(self, config, zmq_subscriber):
        super().__init__(config)
        self.subscriber = zmq_subscriber
        self.client.on_publish = self._on_publish

    def map_topic(zmq_topic):
        return zmq_topic

    def _on_publish(self, client, userdata, message_id):
        print(f"Published message with id {message_id}")

    def zmq_to_mqtt_loop(self):
        """
        Main loop: data comes in through zmq subscription socket,
        passed on to mqtt publish
        """
        while True:
            # This is blocking
            (zmq_topic, data) = self.subscriber.receive()
            mqtt_topic = self.map_topic(zmq_topic)

            self.send(mqtt_topic, data)


class MQTT_Subscriber(MQTT_Base):
    def __init__(self, config, zmq_publisher):
        super().__init__(config)
        self.publisher = zmq_publisher
        self.client.on_message = self._on_message
        self.client.loop_start()

    def __del__(self):
        self.client.loop_stop()

    def _on_message(self, client, userdata, message):
        """
        Callback for when a message is received
        """
        try:
            decoded_message = message.payload.decode()
            data = json.loads(decoded_message)
            print(f"Received message '{decoded_message}' on topic '{message.topic}'")
        except Exception as e:
            print("Could not unpack message")
            print(e)


def main():
    config = MQTTConfig()
    zmq_sub = get_default_subscriber()
    mqtt_publisher = MQTT_Publisher(config, zmq_sub)
    mqtt_publisher.zmq_to_mqtt_loop()
