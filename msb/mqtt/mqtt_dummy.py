import time
from math import sin

from msb.config import load_config
from msb.mqtt.publisher import MQTT_Publisher
from msb.mqtt.config import MQTTconf


def main():
    config = load_config(MQTTconf(), "mqtt")
    mqtt = MQTT_Publisher(config)

    start = time.time()

    while True:
        sinus_value = sin((time.time() - start))
        mqtt.send("test", {"value": sinus_value})
        time.sleep(0.5)


if __name__ == "__main__":
    main()
