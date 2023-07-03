import os

from msb.network.pubsub import Publisher, Subscriber
from msb.network.mqtt import MQTT_Publisher, MQTTConf
from msb.network.zmq import ZMQ_Publisher
from msb.network.zmq.config import ZMQConf
from msb.config import load_config

_registered_publishers = {}
_registered_subscribers = {}


def general_factory(registry: dict, name: str, conf=None):
    if name not in _registered_publishers:
        raise KeyError(f"{name} is not a registered Publisher.")

    pub_cls, conf_cls = registry[name]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return pub_cls(config)


def publisher_factory(pub_name: str, conf=None):
    return general_factory(_registered_publishers, pub_name, conf)


def subscriber_factory(sub_name: str, conf=None):
    return general_factory(_registered_subscribers, sub_name, conf)


def register_publisher(name, publisher_class: Publisher, config):
    _registered_publishers[name] = (publisher_class, config)


def register_subscriber(name, subscriber_class: Subscriber, config):
    _registered_subscribers[name] = (subscriber_class, config)


register_publisher("zmq", ZMQ_Publisher, ZMQConf)
register_publisher("mqtt", MQTT_Publisher, MQTTConf)

# TODO: Add tuples as names, i.e. register_publisher(("interpolated", "mqtt"))

# register_publisher("udp", UDP_Publisher)
# register_publisher("serial", Serial_Publisher)
# register_publisher("flux", Flux_Publisher)
# register_publisher("interpolated", Interpolated_Publisher)
