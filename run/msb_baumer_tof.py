import sys
from os import path

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.baumer_tof import msb_baumer_tof

if __name__ == "__main__":
    msb_baumer_tof.main()
