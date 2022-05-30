import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

class IMUConfig(MSBConfig):
    def __init__(self, subconf = "msb-imu"):
        super().__init__()
        self._load_conf(subconf=subconf)

if __name__ == "__main__":
    config = IMUConfig()
    print(json.dumps(config.__dict__, indent=4))
