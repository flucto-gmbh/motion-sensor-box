import argparse
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
        self._parse_cmdline_args()
        self._cmdline_config_override()

    def _create_data_dir(self):
        if not os.path.isdir(self.data_dir):
            print(f"no such file or directory: {self.data_dir}, creating")
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            print(f"failed to create data directory {self.data_dir} : {e}")
            print(f"falling back to $HOME/msb_data")
            self.data_dir = path.join(os.environ["HOME"], "msb_data")
            self._create_data_dir()

    def _parse_cmdline_args(self):
        args = argparse.ArgumentParser()
        args.add_argument(
            "--verbose",
            action="store_true",
            help="output debugging information"
        )
        args.add_argument(
            "--print-stdout",
            action="store_true",
            help="print raw data to stdout",
        )
        cmdline_conf = args.parse_args().__dict__
        self._cmdline_conf = cmdline_conf

    def _cmdline_config_override(self):
        if self._cmdline_conf['verbose'] and not self.verbose:
            print(f"overriding verbose flag with command line flag")
            self.verbose = True

        if self._cmdline_conf['print_stdout'] and not self.print_stdout:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding print flag with command line flag")
            self.print_stdout = True



if __name__ == "__main__":
    pass
