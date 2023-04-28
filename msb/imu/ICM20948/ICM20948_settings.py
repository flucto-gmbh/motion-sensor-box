from enum import Enum

class GyroSensitivity(Enum):
    DPS_250  = "250dps"
    DPS_500  = "500dps"
    DPS_1000 = "1000dps"
    DPS_2000 = "2000dps"

class AccelerationSensitivity(Enum):
    G_2  = "2g"
    G_4  = "4g"
    G_8  = "8g"
    G_16 = "16g"

class AccelerationFilter(Enum):
    DLPF_OFF = "dlpf_off"
    DLPF_246 = "dlpf_246"
    DLPF_111 = "dlpf_111.4"
    DLPF_50  = "dlpf_50.4"
    DLPF_23  = "dlpf_23.9"
    DLPF_11  = "dlpf_11.5"
    DLPF_5   = "dlpf_5.7"
    DLPF_473 = "dlpf_473"

class GyroFilter(Enum):
    DLPF_OFF = "dlpf_off"
    DLPF_196 = "dlpf_196.6"
    DLPF_151 = "dlpf_151.8"
    DLPF_119 = "dlpf_119.5"
    DLPF_51  = "dlpf_51.2"
    DLPF_23  = "dlpf_23.9"
    DLPF_11  = "dlpf_11.6"
    DLPF_5   = "dlpf_5.7"
    DLPF_361 = "dlpf_361.4"


class ICM20948_SETTINGS(object):
    
    """
    ICM20948 Settings class
        : param  blabla: asfdasg
        : return:        ICM20938 Settings object
        : rtype:         Object
    """
    
    def __init__(self):
        pass

    def parse_config_file(self, filepath):
        pass

    # Gyro full scale range options [_AGB2_REG_GYRO_CONFIG_1]
    _gyr_sensitivity_dict = {
        GyroSensitivity.DPS_250  : 0x00,
        GyroSensitivity.DPS_500  : 0x01,
        GyroSensitivity.DPS_1000 : 0x02,
        GyroSensitivity.DPS_2000 : 0x03,
    }

     # Gyro scaling factors
    _gyr_scale_dict = {
        GyroSensitivity.DPS_250  : 131.0,
        GyroSensitivity.DPS_500  :  65.5,
        GyroSensitivity.DPS_1000 :  32.8,
        GyroSensitivity.DPS_2000 :  16.4
    }
    
    # Accelerometer full scale range options [_AGB2_REG_ACCEL_CONFIG]
    _acc_sensitivity_dict = {
        AccelerationSensitivity.G_2  : 0x00,
        AccelerationSensitivity.G_4  : 0x01,
        AccelerationSensitivity.G_8  : 0x02,
        AccelerationSensitivity.G_16 : 0x03,
    }

    # Accelerometer scaling factors depending on accelerometer sensitivity
    _acc_scale_dict = {
        AccelerationSensitivity.G_2  : 16384.0,
        AccelerationSensitivity.G_4  :  8192.0,
        AccelerationSensitivity.G_8  :  4096.0,
        AccelerationSensitivity.G_16 :  2048.0,
    }

    # Accelerometer low pass filter configuration options
    # Format is dAbwB_nXbwY - A is the integer part of 3db BW, B is the fraction. 
    # X is integer part of nyquist bandwidth, Y is the fraction

    _acc_d246bw_n265bw = 0x00
    _acc_d246bw_n265bw_1 = 0x01
    _acc_d111bw4_n136bw = 0x02
    _acc_d50bw4_n68bw8 = 0x03
    _acc_d23bw9_n34bw4 = 0x04
    _acc_d11bw5_n17bw = 0x05
    _acc_d5bw7_n8bw3 = 0x06
    _acc_d473bw_n499bw = 0x07

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

    # Gryo low pass filter configuration options
    # Format is dAbwB_nXbwZ - A is integer part of 3db BW, B is fraction. X is integer part of nyquist bandwidth, Y is fraction
    _gyr_d196bw6_n229bw8 = 0x00
    _gyr_d151bw8_n187bw6 = 0x01
    _gyr_d119bw5_n154bw3 = 0x02
    _gyr_d51bw2_n73bw3 = 0x03
    _gyr_d23bw9_n35bw9 = 0x04
    _gyr_d11bw6_n17bw8 = 0x05
    _gyr_d5bw7_n8bw9 = 0x06
    _gyr_d361bw4_n376bw5 = 0x07

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
