import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

GPS_TOPIC=b"gps"

class GPSConfig(MSBConfig):
    def __init__(self, subconf = "msb-gps"):
        super().__init__()
        self._load_conf(subconf=subconf)
        self._parse_cmdline_args()
        self._cmdline_config_override()

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
    config = GPSConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
