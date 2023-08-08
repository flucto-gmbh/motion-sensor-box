from msb.config import load_config
from msb.mqtt2.forwarder import ZMQ2MQTTForwarder
from msb.network.mqtt.config import MQTTConf
from msb.network.mqtt.publisher import MQTTRawPublisher
from msb.network.zmq.config import ZMQConf
from msb.network.zmq.subscriber import ZMQRawSubscriber


def main():
    mqtt_config = load_config(MQTTConf(), "mqtt")
    for topic in mqtt_config.topics:
        print(f"Subscribing to {topic}")
    zmq_config = load_config(ZMQConf(), "zmq")
    zmq_sub = ZMQRawSubscriber(mqtt_config.topics, zmq_config)
    mqtt_pub = MQTTRawPublisher(mqtt_config)

    forwarder = ZMQ2MQTTForwarder(mqtt_config, subscriber=zmq_sub, publisher=mqtt_pub)
    forwarder.run()
