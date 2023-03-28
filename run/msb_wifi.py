from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.wifi.msb_wifi as wifi

if __name__ == "__main__":
    wifi.main()
