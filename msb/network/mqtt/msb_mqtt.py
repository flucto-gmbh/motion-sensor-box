from msb.network import get_subscriber, get_publisher
from msb.config import load_config
from .config import MQTTconf
from .forwarder import ZMQ_to_MQTT_Forwarder


def main():
    config = load_config(MQTTconf(), "mqtt")
    for topic in config.topics:
        print(f"Subscribing to {topic}")

    zmq_sub = get_subscriber("zmq", [topic for topic in config.topics])
    mqtt_pub = get_publisher("mqtt")
    forwarder = ZMQ_to_MQTT_Forwarder(config, subscriber=zmq_sub, publisher=mqtt_pub)

    # Wait for zmq messages, publish as mqtt message
    forwarder.zmq_to_mqtt_loop()
