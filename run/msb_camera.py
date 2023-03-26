from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

import msb.camera.msb_camera as camera

if __name__ == "__main__":
    camera.main()
