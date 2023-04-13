from paho.mqtt import client as mqtt_client
from dataclasses import dataclass
import ssl
import time

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


class MQTT_Publisher:
    def __init__(self, config):
        self.config = config
        self.create_topic_mapping()
        self.subscriber = get_default_subscriber()
        self.connect_mqtt()
        self.client.loop_start()

    def wait_for_input_and_publish(self):
        """
        Main loop: data comes in through zmq subscription socket,
        passed on to mqtt publish
        At the moment, Subscriber.receive() is blocking
        """

        # At which level to place the while loop?
        while True:
            # This is blocking
            (zmq_topic, data) = self.subscriber.receive()

            self.publish(self.mapping[zmq_topic], data)

    def publish(self, zmq_topic, data):
        """
        Publish to MQTT broker. Message should look as follows
        (whitespace important!)
        measurement_name [tags] topic=value timestamp
        """
        now = int(time.time_ns())
        topic = self.create_topic_from_zmq(zmq_topic)
        msg = f"{self.config.measurement} {topic}={data} {now}"

        result = self.client.publish(topic, msg, qos=self.config.qos)

        return result

    def create_topic_mapping(self):
        self.mapping = dict()
        for zmq_topic, mqtt_topic in zip(
            self.config.zmq_topics, self.config.mqtt_topics
        ):
            self.mapping[zmq_topic] = mqtt_topic

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"MQTT node connected to {self.config.broker}:{self.config.port}")
            else:
                print("Connection failed!")

        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.config.user, self.config.passwd)
        self.client.on_connect = on_connect

        if self.config.ssl:
            # By default, on Python 2.7.9+ or 3.4+,
            # the default certification authority of the system is used.
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        self.client.connect(self.config.broker, self.config.port)

    def __del__(self):
        self.client.loop_stop()


def main():
    config = MQTTConfig()
    mqtt_publisher = MQTT_Publisher(config)
    mqtt_publisher.wait_for_input_and_publish()

