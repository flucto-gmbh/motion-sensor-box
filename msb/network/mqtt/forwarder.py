from .config import MQTTConf
from msb.config import load_config
from msb.network import get_publisher, get_subscriber


def map_topic(zmq_topic, mapping):
    return mapping + zmq_topic.decode()


def main():
    config: MQTTConf = load_config(MQTTConf(), "mqtt")
    sub = get_subscriber("zmq", config.topics)
    pub = get_publisher("mqtt")

    sub.unpacker = pub.packer = lambda x: x

    while True:
        (zmq_topic, data) = sub.receive()
        mqtt_topic = map_topic(zmq_topic, config.mapping)

        pub.send(mqtt_topic, data)
