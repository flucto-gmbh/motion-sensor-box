import sys
from os import path

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.tof import msb_tof

if __name__ == "__main__":
    msb_tof.main()
