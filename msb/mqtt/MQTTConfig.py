import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from config.MSBConfig import MSBConfig

class MQTTConfig(MSBConfig):
    def __init__(self, subconf = "msb-mqtt", override=dict()):
        super().__init__()
        self.set_default_attributes()

        if override:
            self.load_override(override)
        else:
            self._load_conf(subconf=subconf)

        self._parse_cmdline_args()
        self._cmdline_config_override()

    def set_default_attributes(self):
        self.user = ""
        self.passwd = ""
        self.mqtt_broker = "localhost"
        self.mqtt_port = "1883"
        self.topics = []
        self.measurement = "test"
        self.qos = 2
        self.ssl = True


    def load_override(self, override):
        for att_name, att_value in override.items():
            setattr(self, att_name, att_value)


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
