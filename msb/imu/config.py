import argparse
from dataclasses import dataclass
from enum import Enum, auto
import json

from numpy import format_float_scientific

from msb.config.MSBConfig import MSBConfig, MSBConf
from msb.imu.ICM20948.ICM20948_settings import ICM20948_SETTINGS
class IMUConf(MSBConf):
    """

    configuration class for the inertial measurement unit (imu) service

    """
    verbose : bool = False
    print_stdout : bool = False
    i2c_address : int = 104 
    sample_rate_divisor : int = 30 # 1125/(1+sample_rate_divisor) Hz where sample_rate_divisor is 0, 1, 2,…4095
    acc_filter : AccelerationFilter = AccelerationFilter.DLPF_OFF
    gyr_filter : GyroFilter = GyroFilter.DLPF_OFF
    acc_sensitivity : AccelerationSensitivity = AccelerationSensitivity.G_2
    gyr_sensitivity : GyroSensitivity = GyroSensitivity.DPS_250

if __name__ == "__main__":
    config = IMUConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
