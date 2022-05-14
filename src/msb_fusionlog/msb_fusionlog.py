import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

class FusionlogConfig(MSBConfig):
    def __init__(self, subconf = "msb-fusionlog"):
        super().__init__()
        self._load_conf(subconf=subconf)
        

def msb_fusionlog():
    config = FusionlogConfig()
    print(config)

if __name__ == "__main__":
    msb_fusionlog()
