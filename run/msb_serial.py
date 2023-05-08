from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.serial.SerialReader as serial

if __name__ == "__main__":
    serial.main()
