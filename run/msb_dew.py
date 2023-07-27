from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.dew import msb_dew

if __name__ == "__main__":
    msb_dew.main()
