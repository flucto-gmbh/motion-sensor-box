import os

from msb.network import MQTT_Publisher, MQTTConf
from msb.network import ZMQ_Publisher, ZMQConf
from msb.config import load_config

_registered_publishers = {}


def publisher_factory(pub_name: str, conf=None):
    if pub_name not in _registered_publishers:
        raise KeyError(f"{pub_name} is not a registered Publisher.")

    pub_cls, conf_cls = _registered_publishers["name"]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {pub_name} config")
        config = load_config(conf_cls(), pub_name, read_commandline=False)
    else:
        print(f"using default {pub_name} config")
        config = conf_cls()

    return pub_cls(config)


def register_publisher(name, publisher_class, config):
    _registered_publishers[name] = (publisher_class, config)


register_publisher("zmq", ZMQ_Publisher, ZMQConf)
register_publisher("mqtt", MQTT_Publisher, MQTTConf)

# TODO: Add tuples as names, i.e. register_publisher(("interpolated", "mqtt"))

# register_publisher("udp", UDP_Publisher)
# register_publisher("serial", Serial_Publisher)
# register_publisher("flux", Flux_Publisher)
# register_publisher("interpolated", Interpolated_Publisher)
