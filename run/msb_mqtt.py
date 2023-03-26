from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.mqtt.msb_mqtt as mqtt

if __name__ == "__main__":
    mqtt.main()
