from msb.config.MSBConfig import MSBConf

from msb.imu.icm20948.settings import (
    AccelerometerFilter,
    AccelerometerSensitivity,
    GyroscopeFilter,
    GyroscopeSensitivity,
)


class IMUConf(MSBConf):
    """Configuration for the inertial measurement unit (imu) service"""

    topic: bytes = b"imu"

    i2c_bus_num: int = 1
    i2c_address: int = 104
    sample_rate_divisor: int = (
        30  # 1125/(1+sample_rate_divisor) Hz where sample_rate_divisor is 0, 1, 2,…4095
    )
    acc_filter: AccelerometerFilter = AccelerometerFilter.DLPF_OFF
    gyr_filter: GyroscopeFilter = GyroscopeFilter.DLPF_OFF
    acc_sensitivity: AccelerometerSensitivity = AccelerometerSensitivity.G_2
    gyr_sensitivity: GyroscopeSensitivity = GyroscopeSensitivity.DPS_250
    precision: int = 4
    polling: bool = True
