from paho.mqtt import client as mqtt_client
import sys, os
import ssl
import time

from msb.zmq_base.Subscriber import Subscriber
from msb.mqtt.MQTTConfig import MQTTConfig

class MQTTnode:
    def __init__(self, config_override={}):
        self.config = MQTTConfig(override=config_override)
        self.subscriber = Subscriber(connect_to=self.config.xpub_socketstring)
        self.connect_mqtt()
        self.client.loop_start()

    '''
    Main loop: data comes in through zmq subscription socket, passed on to mqtt publish
    At the moment, Subscriber.receive() is blocking
    '''
    def wait_for_input_and_publish(self):
        # At which level to place the while loop?
        while True:
            # This is blocking
            (zmq_topic, data) = self.subscriber.receive()

            self.publish(zmq_topic, data)


    '''
    Publish to MQTT broker. Message should look as follows (whitespace important!)
    measurement_name [tags] topic=value timestamp
    with 
    '''
    def publish(self, zmq_topic, data):
        now = int(time.time_ns())
        topic= self.create_topic_from_zmq(zmq_topic)
        msg = f"{self.config.measurement} {topic}={data} {now}"

        print(f"publishing to {topic} with msg : {msg}")
        result = self.client.publish(topic, msg, qos=self.config.qos)

        return result

    
    '''
    From a 3 character zmq topic create a hierarchical topic suitable for mqtt
    i.e. "imu" --> turbine1/blade2/flap4/imu
    '''
    def create_topic_from_zmq(self, zmq_topic):
        return f"turbine/{zmq_topic}"


    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f'MQTT node connected to {self.config.mqtt_broker}:{self.config.mqtt_port}')
            else:
                print('Connection failed!')

        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.config.user, self.config.passwd)
        self.client.on_connect = on_connect

        if self.config.ssl: 
            # By default, on Python 2.7.9+ or 3.4+, the default certification authority of the system is used.
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT) 

        self.client.connect(self.config.mqtt_broker, self.config.mqtt_port)


    def __del__(self):
        self.client.loop_stop()


def main():
    mqtt_tester = MQTTnode()
    print(mqtt_tester.config.user)
