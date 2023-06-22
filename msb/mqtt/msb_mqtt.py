from msb.zmq_base.Subscriber import get_default_subscriber
from msb.mqtt.config import MQTTconf
from msb.config import load_config
from msb.mqtt.forwarder import ZMQ_to_MQTT_Forwarder as Forwarder


def main():
    config = load_config(MQTTconf(), "mqtt")
    for topic in config.topics:
        print(f"Subscribing to {topic}")
    zmq_sub = get_default_subscriber([topic.encode() for topic in config.topics])
    forwarder = Forwarder(config, zmq_sub)
    forwarder.zmq_to_mqtt_loop()
