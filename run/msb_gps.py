from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.gps.msb_gps as gps

if __name__ == "__main__":
    gps.main()
