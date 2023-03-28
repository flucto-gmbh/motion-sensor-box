from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.piletrack.msb_piletrack as piletrack

if __name__ == "__main__":
    piletrack.main()
