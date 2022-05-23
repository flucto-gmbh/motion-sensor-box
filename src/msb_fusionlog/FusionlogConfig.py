import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

class FusionlogConfig(MSBConfig):
    def __init__(self, subconf = "msb-fusionlog"):
        super().__init__()
        self._load_conf(subconf=subconf)
        self._create_data_dir()

    def _create_data_dir(self):
        if not os.path.isdir(self.data_dir):
            raise Exception("no such file or directory: {config.data_dir}")
        os.makedirs(self.data_dir, exist_ok=True)

if __name__ == "__main__":
    pass
