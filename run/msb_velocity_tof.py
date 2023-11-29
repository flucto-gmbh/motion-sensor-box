import sys
from os import path

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.baumer_tof import velocity

if __name__ == "__main__":
    velocity.main()
