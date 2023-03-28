from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.fusionlog.msb_fusionlog as fusionlog

if __name__ == "__main__":
    fusionlog.main()
