from sys import argv
import time

from msb.mqtt.mqtt_base import MQTT_Base
from msb.config import load_config
from msb.mqtt.config import MQTTconf



class MQTT_Publisher(MQTT_Base):
    def __init__(self, config):
        super().__init__(config)
        self.client.on_publish = self._on_publish

    def _on_publish(self, client, userdata, message_id):
        print(f"Published message with id {message_id}")


def get_default_mqtt_publisher(confname="mqtt"):
    config = load_config(MQTTconf(), confname, read_commandline=False)
    return MQTT_Publisher(config)


if __name__ == "__main__":
    confname = argv[1] if len(argv) > 1 else "mqtt"
    pub = get_default_mqtt_publisher(confname)

    data = {"name": "turbine1",
            "epoch": time.time_ns(),
            "pwr": 700,
            "gen": 1600,
            "rtr": 2.3,
            "wnd": 8.5,
            "pit": 1.9,
            }
    while True:
        try: 
            pub.send("mqtttest", data)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting")
            break
