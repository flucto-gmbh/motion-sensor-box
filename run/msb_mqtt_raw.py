from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.mqtt2 import msb_mqtt

if __name__ == "__main__":
    msb_mqtt.main()
