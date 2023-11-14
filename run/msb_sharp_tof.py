import sys
from os import path

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.sharp_tof import msb_sharp_tof

if __name__ == "__main__":
    msb_sharp_tof.main()
