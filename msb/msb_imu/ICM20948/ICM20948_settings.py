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
        '250dps'  : 0x00,
        '500dps'  : 0x01,
        '1000dps' : 0x02,
        '2000dps' : 0x03,
    }

     # Gyro scaling factors
    _gyr_scale_dict = {
        '250dps'  : 131.0,
        '500dps'  :  65.5,
        '1000dps' :  32.8,
        '2000dps' :  16.4
    }
    
    # Accelerometer full scale range options [_AGB2_REG_ACCEL_CONFIG]
    _acc_sensitivity_dict = {
         '2g' : 0x00,
         '4g' : 0x01,
         '8g' : 0x02,
        '16g' : 0x03,
    }

    # Accelerometer scaling factors depending on accelerometer sensitivity
    _acc_scale_dict = {
         '2g' : 16384.0,
         '4g' :  8192.0,
         '8g' :  4096.0,
        '16g' :  2048.0,
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
