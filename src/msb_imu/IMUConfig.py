import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig
from ICM20948.ICM20948_settings import ICM20948_SETTINGS

class IMUConfig(MSBConfig):
    def __init__(self, subconf = "msb-imu"):
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
        args.add_argument(
            "--sample-rate-div",
            type=int,
            default=None,
            help="""output data rate divisor. Sensor output data rate (ODR) is
            calculated by the following formula:
            ODR = 1125 / (1 + output_divisor)
            """
        )
        args.add_argument(
            "--acc-filter",
            type=int,
            default=None,
            help="""High pass filter applied to acceleration data by the sensor.
            The command line parameter corresponds to the index in the list of 
            available filters.
            The following high pass filters are available:
            _acc_filter_list = [
                _acc_d473bw_n499bw,
                _acc_d246bw_n265bw_1,
                _acc_d111bw4_n136bw,
                _acc_d50bw4_n68bw8,
                _acc_d23bw9_n34bw4,
                _acc_d11bw5_n17bw,
                _acc_d11bw5_n17bw,
                _acc_d11bw5_n17bw,
            ]
            The filter names adhere to this pattern: acc_dAbwB_nXbwY
            where A.B is the 3 db filter bandwidth frequency
            and X.Y is the Nyquist frequency
            """
        )
        args.add_argument(
            "--gyr-filter",
            type=int,
            default=None,
            help="""High pass filter applied to acceleration data by the sensor.
            The value of the command line parameter corresponds to the index in
            the list of available filters.
            The following high pass filters are available:
            _gyr_filter_list = [
                _gyr_d361bw4_n376bw5,
                _gyr_d196bw6_n229bw8,
                _gyr_d151bw8_n187bw6,
                _gyr_d119bw5_n154bw3,
                _gyr_d51bw2_n73bw3,
                _gyr_d23bw9_n35bw9,
                _gyr_d11bw6_n17bw8,
                _gyr_d5bw7_n8bw9,
            ]
            The filter names adhere to this pattern: acc_dAbwB_nXbwY
            where A.B is the 3 db filter bandwidth frequency
            and X.Y is the Nyquist frequency.
            """
        )
        args.add_argument(
            "--acc-sensitivity",
            type=str,
            default=None,
            help="""sensitivity of the acceleration sensor.
            available settings are:
             2g
             4g
             8g
            16g
            """
        )
        args.add_argument(
            "--gyr-sensitivity",
            type=str,
            default=None,
            help="""sensitivity of the gyroscope.
            available settings are:
             250dps
             500dps
            1000dps
            2000dps
            """
        )
        args.add_argument(
            "--polling",
            action="store_true",
            help="""Alternate mode: instead of using a sensor issued interrupt
            use polling to retrieve data from the sensor"""
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

        if self._cmdline_conf['sample_rate_div']:
            if self.verbose:
                print(f"overriding output divisor with command line value {self._cmdline_conf['sample_rate_div']}")
            self.sample_rate_div = self._cmdline_conf['sample_rate_div']
        
        if self._cmdline_conf['acc_sensitivity']:
            assert cmdline_conf['acc_sensitivity'] in ICM20948_SETTINGS._acc_sensitivity_dict, f"not a valid scale selection {cmdline_conf['acc_sensitivity']}"
            if self.verbose:
                print(f"overriding acceleration sensitivity with command line value {self._cmdline_conf['acc_sensitivity']}")
            self.acc_sensitivity = self._cmdline_conf['acc_sensitivity']

        if self._cmdline_conf['gyr_sensitivity']:
            assert cmdline_conf['gyr_sensitivity'] in ICM20948_SETTINGS._gyr_sensitivity_dict, f"not a valid scale selection {cmdline_conf['gyr_sensitivity']}"
            if self.verbose:
                print(f"overriding gyroscope sensitivity with command line value {self._cmdline_conf['gyr_sensitivity']}")
            self.gyr_sensitivity = self._cmdline_conf['gyr_sensitivity']

        if self._cmdline_conf['acc_filter']:
            assert self._cmdline_conf['acc_filter'] < len(ICM20948_SETTINGS._acc_filter_list), f"not a valid filter selection {cmdline_conf['acc_filter']}"
            if self.verbose:
                print(f"overriding acceleration filter setting with command line value {self._cmdline_conf['acc_filter']}")
            self.acc_filter = self._cmdline_conf['acc_filter']

        if self._cmdline_conf['gyr_filter']:
            assert self._cmdline_conf['gyr_filter'] < len(ICM20948_SETTINGS._gyr_filter_list), f"not a valid filter selection {cmdline_conf['gyr_filter']}"
            if self.verbose:
                print(f"overriding gyroscope filter setting with command line value {self._cmdline_conf['gyr_filter']}")
            self.gyr_filter = self._cmdline_conf['gyr_filter']

        if self._cmdline_conf['polling'] and not self.polling:
            if self.verbose:
                print("overrriding polling setting with command line flag")
            self.polling = True

if __name__ == "__main__":
    config = IMUConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
