from enum import Enum, IntFlag, IntEnum


class ICM20948SampleMode(IntFlag):
    """Sample mode options"""

    CONTINUOUS = 0x00
    CYCLED = 0x01


class ICM20948InternalSensorID(IntFlag):
    """Internal Sensor IDs, used in various functions as arguments to know who to affect"""

    ACC = 1 << 0
    GYR = 1 << 1
    MAG = 1 << 2
    TMP = 1 << 3
    MST = 1 << 4  # I2C Master Internal


class Bank(IntEnum):
    """Represents a register bank."""

    B0 = 0
    B1 = 1
    B2 = 2
    B3 = 3


class AccelerometerSensitivity(Enum):
    G_2 = "2g"
    G_4 = "4g"
    G_8 = "8g"
    G_16 = "16g"


class GyroscopeSensitivity(Enum):
    # TODO rename to Gyroscope... for consistency?
    DPS_250 = "250dps"
    DPS_500 = "500dps"
    DPS_1000 = "1000dps"
    DPS_2000 = "2000dps"


class AccelerometerFilter(Enum):
    DLPF_OFF = "dlpf_off"
    DLPF_246 = "dlpf_246"
    DLPF_111 = "dlpf_111.4"
    DLPF_50 = "dlpf_50.4"
    DLPF_23 = "dlpf_23.9"
    DLPF_11 = "dlpf_11.5"
    DLPF_5 = "dlpf_5.7"
    DLPF_473 = "dlpf_473"


class GyroscopeFilter(Enum):
    # TODO rename to Gyroscope... for consistency?
    DLPF_OFF = "dlpf_off"
    DLPF_196 = "dlpf_196.6"
    DLPF_151 = "dlpf_151.8"
    DLPF_119 = "dlpf_119.5"
    DLPF_51 = "dlpf_51.2"
    DLPF_23 = "dlpf_23.9"
    DLPF_11 = "dlpf_11.6"
    DLPF_5 = "dlpf_5.7"
    DLPF_361 = "dlpf_361.4"


class SettingValues:
    @classmethod
    def acc_sensitivity_and_scale(cls, setting: AccelerometerSensitivity):
        return cls._acc_sensitivity_dict[setting], cls._acc_scale_dict[setting]

    @classmethod
    def gyr_sensitivity_and_scale(cls, setting: GyroscopeSensitivity):
        return cls._gyr_sensitivity_dict[setting], cls._gyr_scale_dict[setting]

    @classmethod
    def acc_filter(cls, setting: AccelerometerFilter):
        return (
            None
            if setting is AccelerometerFilter.DLPF_OFF
            else cls._acc_filter_dict[setting]
        )

    @classmethod
    def gyr_filter(cls, setting: GyroscopeFilter):
        return (
            None
            if setting is GyroscopeFilter.DLPF_OFF
            else cls._gyr_filter_dict[setting]
        )

    # Gyro full scale range options [AGB2_REG_GYRO_CONFIG_1]
    _gyr_sensitivity_dict = {
        GyroscopeSensitivity.DPS_250: 0x00,
        GyroscopeSensitivity.DPS_500: 0x01,
        GyroscopeSensitivity.DPS_1000: 0x02,
        GyroscopeSensitivity.DPS_2000: 0x03,
    }

    # Gyro scaling factors
    _gyr_scale_dict = {
        GyroscopeSensitivity.DPS_250: 131.0,
        GyroscopeSensitivity.DPS_500: 65.5,
        GyroscopeSensitivity.DPS_1000: 32.8,
        GyroscopeSensitivity.DPS_2000: 16.4,
    }

    # Accelerometer full scale range options [AGB2_REG_ACCEL_CONFIG]
    _acc_sensitivity_dict = {
        AccelerometerSensitivity.G_2: 0x00,
        AccelerometerSensitivity.G_4: 0x01,
        AccelerometerSensitivity.G_8: 0x02,
        AccelerometerSensitivity.G_16: 0x03,
    }

    # Accelerometer scaling factors depending on accelerometer sensitivity
    _acc_scale_dict = {
        AccelerometerSensitivity.G_2: 16384.0,
        AccelerometerSensitivity.G_4: 8192.0,
        AccelerometerSensitivity.G_8: 4096.0,
        AccelerometerSensitivity.G_16: 2048.0,
    }

    # Accelerometer low pass filter configuration options
    # Format is dAbwB_nXbwY - A is the integer part of 3db BW, B is the fraction.
    # X is integer part of nyquist bandwidth, Y is the fraction
    _acc_filter_dict = {
        AccelerometerFilter.DLPF_246: 0x00,
        # AccelerationFilter.DLPF_246: 0x01,
        AccelerometerFilter.DLPF_111: 0x02,
        AccelerometerFilter.DLPF_50: 0x03,
        AccelerometerFilter.DLPF_23: 0x04,
        AccelerometerFilter.DLPF_11: 0x05,
        AccelerometerFilter.DLPF_5: 0x06,
        AccelerometerFilter.DLPF_473: 0x07,
    }

    # Gryo low pass filter configuration options
    # Format is dAbwB_nXbwZ - A is integer part of 3db BW, B is fraction.
    # X is integer part of nyquist bandwidth, Y is fraction
    _gyr_filter_dict = {
        GyroscopeFilter.DLPF_196: 0x00,
        GyroscopeFilter.DLPF_151: 0x01,
        GyroscopeFilter.DLPF_119: 0x02,
        GyroscopeFilter.DLPF_51: 0x03,
        GyroscopeFilter.DLPF_23: 0x04,
        GyroscopeFilter.DLPF_11: 0x05,
        GyroscopeFilter.DLPF_5: 0x06,
        GyroscopeFilter.DLPF_361: 0x07,
    }
