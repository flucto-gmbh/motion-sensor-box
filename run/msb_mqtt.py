from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))


if __name__ == "__main__":
    import msb.network.mqtt.forwarder as mqtt_forwarder
    mqtt_forwarder.main()
