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
