from msb.config.MSBConfig import MSBConf

from msb.imu.ICM20948.ICM20948_settings import (
    AccelerationFilter,
    AccelerationSensitivity,
    GyroFilter,
    GyroSensitivity,
)


class IMUConf(MSBConf):
    """Configuration for the inertial measurement unit (imu) service"""

    topic: bytes = b"imu"

    i2c_address: int = 104
    sample_rate_divisor: int = (
        30  # 1125/(1+sample_rate_divisor) Hz where sample_rate_divisor is 0, 1, 2,…4095
    )
    acc_filter: AccelerationFilter = AccelerationFilter.DLPF_OFF
    gyr_filter: GyroFilter = GyroFilter.DLPF_OFF
    acc_sensitivity: AccelerationSensitivity = AccelerationSensitivity.G_2
    gyr_sensitivity: GyroSensitivity = GyroSensitivity.DPS_250
    precision: int = 3
    polling: bool = True

