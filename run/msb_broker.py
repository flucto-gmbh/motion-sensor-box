from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.broker.msb_broker as broker

if __name__ == "__main__":
    broker.main()
