import os

from .types import Publisher, Subscriber
from msb.network.mqtt import MQTT_Publisher, MQTT_Subscriber, MQTTConf
from msb.network.zmq import ZMQ_Publisher, ZMQ_Subscriber, ZMQConf
from msb.config import load_config

_registered_publishers = {}
_registered_subscribers = {}


def get_publisher(name: str):
    if name not in _registered_publishers:
        raise KeyError(f"{name} is not a registered Publisher.")

    pub_cls, conf_cls = _registered_publishers[name]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return pub_cls(config)
    # return general_factory(_registered_publishers, pub_name)


def get_subscriber(name: str, topic):
    if name not in _registered_publishers:
        raise KeyError(f"{name} is not a registered Subscriber.")

    sub_cls, conf_cls = _registered_subscribers[name]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return sub_cls(topic, config)


def register_publisher(name, publisher_class: Publisher, config):
    _registered_publishers[name] = (publisher_class, config)


def register_subscriber(name, subscriber_class: Subscriber, config):
    _registered_subscribers[name] = (subscriber_class, config)


register_publisher("zmq", ZMQ_Publisher, ZMQConf)
register_publisher("mqtt", MQTT_Publisher, MQTTConf)

register_subscriber("zmq", ZMQ_Subscriber, ZMQConf)
register_subscriber("mqtt", MQTT_Subscriber, MQTTConf)
# TODO: Add tuples as names, i.e. register_publisher(("interpolated", "mqtt"))

# register_publisher("udp", UDP_Publisher)
# register_publisher("serial", Serial_Publisher)
# register_publisher("flux", Flux_Publisher)
# register_publisher("interpolated", Interpolated_Publisher)
