import time
from math import sin

from msb.config import load_config
from msb.mqtt.msb_mqtt import MQTT_Base
from msb.mqtt.config import MQTTconf


def main():
    config = load_config(MQTTconf(), "mqtt")
    mqtt = MQTT_Base(config)

    start = time.time()

    while True:
        sinus_value = sin((time.time() - start))
        mqtt.send("test", {"value": sinus_value})
        time.sleep(0.5)


if __name__ == "__main__":
    main()