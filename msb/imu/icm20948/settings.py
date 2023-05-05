from enum import Enum
from dataclasses import dataclass


class GyroSensitivity(Enum):
    DPS_250 = "250dps"
    DPS_500 = "500dps"
    DPS_1000 = "1000dps"
    DPS_2000 = "2000dps"


class AccelerationSensitivity(Enum):
    G_2 = "2g"
    G_4 = "4g"
    G_8 = "8g"
    G_16 = "16g"


class AccelerationFilter(Enum):
    DLPF_OFF = "dlpf_off"
    DLPF_246 = "dlpf_246"
    DLPF_111 = "dlpf_111.4"
    DLPF_50 = "dlpf_50.4"
    DLPF_23 = "dlpf_23.9"
    DLPF_11 = "dlpf_11.5"
    DLPF_5 = "dlpf_5.7"
    DLPF_473 = "dlpf_473"


class GyroFilter(Enum):
    DLPF_OFF = "dlpf_off"
    DLPF_196 = "dlpf_196.6"
    DLPF_151 = "dlpf_151.8"
    DLPF_119 = "dlpf_119.5"
    DLPF_51 = "dlpf_51.2"
    DLPF_23 = "dlpf_23.9"
    DLPF_11 = "dlpf_11.6"
    DLPF_5 = "dlpf_5.7"
    DLPF_361 = "dlpf_361.4"


@dataclass
class Settings:

    """
    ICM20948 Settings class
        : param  blabla: asfdasg
        : return:        ICM20938 Settings object
        : rtype:         Object
    """

    # Gyro full scale range options [_AGB2_REG_GYRO_CONFIG_1]
    gyr_sensitivity_dict = {
        GyroSensitivity.DPS_250: 0x00,
        GyroSensitivity.DPS_500: 0x01,
        GyroSensitivity.DPS_1000: 0x02,
        GyroSensitivity.DPS_2000: 0x03,
    }

    # Gyro scaling factors
    gyr_scale_dict = {
        GyroSensitivity.DPS_250: 131.0,
        GyroSensitivity.DPS_500: 65.5,
        GyroSensitivity.DPS_1000: 32.8,
        GyroSensitivity.DPS_2000: 16.4,
    }

    # Accelerometer full scale range options [_AGB2_REG_ACCEL_CONFIG]
    acc_sensitivity_dict = {
        AccelerationSensitivity.G_2: 0x00,
        AccelerationSensitivity.G_4: 0x01,
        AccelerationSensitivity.G_8: 0x02,
        AccelerationSensitivity.G_16: 0x03,
    }

    # Accelerometer scaling factors depending on accelerometer sensitivity
    acc_scale_dict = {
        AccelerationSensitivity.G_2: 16384.0,
        AccelerationSensitivity.G_4: 8192.0,
        AccelerationSensitivity.G_8: 4096.0,
        AccelerationSensitivity.G_16: 2048.0,
    }

    # Accelerometer low pass filter configuration options
    # Format is dAbwB_nXbwY - A is the integer part of 3db BW, B is the fraction.
    # X is integer part of nyquist bandwidth, Y is the fraction
    acc_filter_dict = {
        AccelerationFilter.DLPF_246: 0x00,
        # AccelerationFilter.DLPF_246: 0x01,
        AccelerationFilter.DLPF_111: 0x02,
        AccelerationFilter.DLPF_50: 0x03,
        AccelerationFilter.DLPF_23: 0x04,
        AccelerationFilter.DLPF_11: 0x05,
        AccelerationFilter.DLPF_5: 0x06,
        AccelerationFilter.DLPF_473: 0x07,
    }
    # TODO: add AccelerationFilter.DLPF_OFF

    # Gryo low pass filter configuration options
    # Format is dAbwB_nXbwZ - A is integer part of 3db BW, B is fraction. X is integer part of nyquist bandwidth, Y is fraction
    gyr_filter_dict = {
        GyroFilter.DLPF_196: 0x00,
        GyroFilter.DLPF_151: 0x01,
        GyroFilter.DLPF_119: 0x02,
        GyroFilter.DLPF_51: 0x03,
        GyroFilter.DLPF_23: 0x04,
        GyroFilter.DLPF_11: 0x05,
        GyroFilter.DLPF_5: 0x06,
        GyroFilter.DLPF_361: 0x07,
    }
    # TODO: add GyroFilter.DLPF_OFF
