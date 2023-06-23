from msb.zmq_base.Subscriber import get_default_subscriber
from msb.mqtt.config import MQTTconf
from msb.config import load_config
from msb.mqtt.forwarder import ZMQ_to_MQTT_Forwarder as Forwarder
from msb.mqtt.publisher import MQTT_Publisher, get_default_publisher


def main():
    config = load_config(MQTTconf(), "mqtt")
    for topic in config.topics:
        print(f"Subscribing to {topic}")
    zmq_sub = get_default_subscriber([topic.encode() for topic in config.topics])
    mqtt_pub = get_default_publisher()

    forwarder = Forwarder(config, subscriber=zmq_sub, publisher=mqtt_pub)
    forwarder.zmq_to_mqtt_loop()
