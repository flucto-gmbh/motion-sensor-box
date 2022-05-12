class ICM20938_REGISTERS(object):


    """
    ICM20948_Registers
    """

    # Internal Sensor IDs, used in various functions as arguments to know who to affect
    _ICM_20948_Internal_Acc = (1 << 0)
    _ICM_20948_Internal_Gyr = (1 << 1)
    _ICM_20948_Internal_Mag = (1 << 2)
    _ICM_20948_Internal_Tmp = (1 << 3)
    _ICM_20948_Internal_Mst = (1 << 4) # I2C Master Internal

    # Sample mode options
    _ICM_20948_Sample_Mode_Continuous = 0x00
    _ICM_20948_Sample_Mode_Cycled = 0x01

    # the following code section lists relevant Registers on the ICM 20948
    # Note, that I2C addresses have a maximum of 255 values (0x00 to 0xFF). 
    # Therefore, on the ICM-20948 four register banks are available [0-3]

    # Gyroscope and Accelerometer
    # User Bank 0
    _AGB0_REG_WHO_A_M_I = 				0x00 # return the ID for the Motion sensor

    # This Register enables the DMP, the FIFO as well as the additional I2C interface
    # on the chip
    # _AGB0_REG_USER CTRL = b10000000 enables the DMP
    # _AGB0_REG_USER CTRL = b01000000 enables the FIFO
    # _AGB0_REG_USER CTRL = b00100000 enables the I2C Master
    # _AGB0_REG_USER CTRL = b00010000 diables I2C and activates SPI mode only
    # _AGB0_REG_USER CTRL = b00001000 resets the DMP
    # _AGB0_REG_USER CTRL = b00000100 resets the internal SRAM
    # _AGB0_REG_USER CTRL = b00000100 resets the internal SRAM
    # _AGB0_REG_USER CTRL = b00000010 resets the I2C master module (if active)
    # _AGB0_REG_USER CTRL = b00000001  undefinded 
    _AGB0_REG_USER_CTRL = 				0x03  

    # Controls the output data rate
    # _AGB0_REG_LP_CONFIG = b01000000 operates the I2C master in duty cycle mode. 
    #                                ODR is then determined by I2C_MST_ODR_CONFIG
    # _AGB0_REG_LP_CONFIG = b00100000 Operates the accelerometer in duty cycle mode.
    #                                ODR is then defined by ACCEL_SMPLRT_DIV
    # _AGB0_REG_LP_CONFIG = b00010000 Operates the Gyroscope in duty cycle mode.
    #                                ODR is then defined by GYRO_SMPLRT_DIV
    _AGB0_REG_LP_CONFIG = 				0x05 

    # controls power modes - handle with care
    _AGB0_REG_PWR_MGMT_1 = 				0x06
    _AGB0_REG_PWR_MGMT_2 = 				0x07

    # configure the interrupt pin
    # _AGB0_REG_INT_PIN_CONFIG = b10000000 sets the interrupt pin logic level to low
    # _AGB0_REG_INT_PIN_CONFIG = b01000000 sets the interrupt pin as open drain
    # _AGB0_REG_INT_PIN_CONFIG = b00100000 holds the interrupt pin level until status is cleared
    # For further options, please refer to the manual
    _AGB0_REG_INT_PIN_CONFIG = 			0x0F 

    # enables interrupt pin 1
    # _AGB0_REG_INT_ENABLE = b10000000 enable wake on FSYNC
    # _AGB0_REG_INT_ENABLE = b00001000 enable wake on motion
    # _AGB0_REG_INT_ENABLE = b00000100 PLL ready interrupt
    # _AGB0_REG_INT_ENABLE = b10000010 DMP interrupt enabled 
    # _AGB0_REG_INT_ENABLE = b10000001 I2C master interrupt
    _AGB0_REG_INT_ENABLE = 				0x10

    # configures interrupt pin 1
    # _AGB0_REG_INT_ENABLE_1 = b00000001 Raw data ready interrupt
    _AGB0_REG_INT_ENABLE_1 = 			0x11

    # configures interrupt pin 1
    # _AGB0_REG_INT_ENABLE_2 = b00001111 FIFO overflow interrupt
    _AGB0_REG_INT_ENABLE_2 = 			0x12
    
    # configures interrupt pin 1
    # _AGB0_REG_INT_ENABLE_3 = b00001111 enables FIFO watermark interrupt
    _AGB0_REG_INT_ENABLE_3 = 			0x13

    # see documentation
    _AGB0_REG_I2C_MST_STATUS = 			0x17 

    # check what kind of interrupt occured
    # if b00001000 wake on motion interrupt occured
    # if b00000100 PLL has been enabled and is ready
    # if b00000010 A DMP interrupt has occured
    # if b00000001 I2C Master interrupt has occured
    _AGB0_REG_INT_STATUS = 				0x19 

    # check what kind of interrupt occured
    # if b00000001 raw data is ready (useful for polling raw data)
    _AGB0_REG_INT_STATUS_1 = 			0x1A
    
    # check what kind of interrupt occured
    # if b00001111 FIFO overflow interrupt occured
    _AGB0_REG_INT_STATUS_2 = 			0x1B
    
    # check what kind of interrupt occured
    # if b00001111 FIFO watermark overflow occured
    _AGB0_REG_INT_STATUS_3 = 			0x1C

    # if FZYNC is used, the data in the following two registers 
    # represents the delay time in microseconds
    # to calculate the delay time, do: ((DELAY_TIMEH << 8) & DELAY_TIMEL) * 0.9645
    _AGB0_REG_DELAY_TIMEH = 				0x28 
    _AGB0_REG_DELAY_TIMEL = 				0x29

    # raw acceleration data
    # to convert data to real units, use the following operation:
    # ((_AGB0_REG_sensor_iOUT_H << 8) & _AGB0_REG_ACCEL_iOUT_L) / sensor_SENSIBILITY
    # where i = X, Y, Z and sensor = ACCEL, GYRO, TEMP
    _AGB0_REG_ACCEL_XOUT_H = 			0x2D 
    _AGB0_REG_ACCEL_XOUT_L = 			0x2E
    _AGB0_REG_ACCEL_YOUT_H = 			0x2F
    _AGB0_REG_ACCEL_YOUT_L = 			0x30
    _AGB0_REG_ACCEL_ZOUT_H = 			0x31
    _AGB0_REG_ACCEL_ZOUT_L = 			0x32
    _AGB0_REG_GYRO_XOUT_H = 			0x33
    _AGB0_REG_GYRO_XOUT_L = 			0x34
    _AGB0_REG_GYRO_YOUT_H = 			0x35
    _AGB0_REG_GYRO_YOUT_L = 			0x36
    _AGB0_REG_GYRO_ZOUT_H = 			0x37
    _AGB0_REG_GYRO_ZOUT_L = 			0x38
    _AGB0_REG_TEMP_OUT_H  = 			0x39
    _AGB0_REG_TEMP_OUT_L = 				0x3A
    
    # registers for external I2C sensors
    # for further information, refere to the manual
    _AGB0_REG_EXT_SLV_SENS_DATA_00 =	0x3B
    _AGB0_REG_EXT_SLV_SENS_DATA_01 = 	0x3C
    _AGB0_REG_EXT_SLV_SENS_DATA_02 = 	0x3D
    _AGB0_REG_EXT_SLV_SENS_DATA_03 = 	0x3E
    _AGB0_REG_EXT_SLV_SENS_DATA_04 = 	0x3F
    _AGB0_REG_EXT_SLV_SENS_DATA_05 = 	0x40
    _AGB0_REG_EXT_SLV_SENS_DATA_06 = 	0x41
    _AGB0_REG_EXT_SLV_SENS_DATA_07 = 	0x42
    _AGB0_REG_EXT_SLV_SENS_DATA_08 = 	0x43
    _AGB0_REG_EXT_SLV_SENS_DATA_09 = 	0x44
    _AGB0_REG_EXT_SLV_SENS_DATA_10 = 	0x45
    _AGB0_REG_EXT_SLV_SENS_DATA_11 = 	0x46
    _AGB0_REG_EXT_SLV_SENS_DATA_12 = 	0x47
    _AGB0_REG_EXT_SLV_SENS_DATA_13 = 	0x48
    _AGB0_REG_EXT_SLV_SENS_DATA_14 = 	0x49
    _AGB0_REG_EXT_SLV_SENS_DATA_15 = 	0x4A
    _AGB0_REG_EXT_SLV_SENS_DATA_16 = 	0x4B
    _AGB0_REG_EXT_SLV_SENS_DATA_17 = 	0x4C
    _AGB0_REG_EXT_SLV_SENS_DATA_18 = 	0x4D
    _AGB0_REG_EXT_SLV_SENS_DATA_19 = 	0x4E
    _AGB0_REG_EXT_SLV_SENS_DATA_20 = 	0x4F
    _AGB0_REG_EXT_SLV_SENS_DATA_21 = 	0x50
    _AGB0_REG_EXT_SLV_SENS_DATA_22 = 	0x51
    _AGB0_REG_EXT_SLV_SENS_DATA_23 = 	0x52

    # TODO continue here
    _AGB0_REG_FIFO_EN_1 = 				0x66 
    _AGB0_REG_FIFO_EN_2 = 				0x67
    _AGB0_REG_FIFO_MODE = 				0x69
    _AGB0_REG_FIFO_COUNT_H = 			0x70 
    _AGB0_REG_FIFO_COUNT_L = 			0x71
    _AGB0_REG_FIFO_R_W = 				0x72
    _AGB0_REG_DATA_RDY_STATUS = 		0x74 
    _AGB0_REG_FIFO_CFG = 				0x76 
    _AGB0_REG_ME_M_START_ADDR = 		0x7C # Hmm  Invensense thought they were sneaky not listing these locations on the datasheet...
    _AGB0_REG_ME_M_R_W = 				0x7D # These three locations seem to be able to access some memory within the device
    _AGB0_REG_ME_M_BANK_SEL = 			0x7E # And that location is also where the DMP image gets loaded
    _AGB0_REG_REG_BANK_SEL = 			0x7F 
    # Bank 1
    _AGB1_REG_SELF_TEST_X_GYRO = 		0x02 
    _AGB1_REG_SELF_TEST_Y_GYRO = 		0x03
    _AGB1_REG_SELF_TEST_Z_GYRO = 		0x04
    _AGB1_REG_SELF_TEST_X_ACCEL = 		0x0E 
    _AGB1_REG_SELF_TEST_Y_ACCEL = 		0x0F
    _AGB1_REG_SELF_TEST_Z_ACCEL = 		0x10
    _AGB1_REG_XA_OFFS_H = 				0x14 
    _AGB1_REG_XA_OFFS_L = 				0x15
    _AGB1_REG_YA_OFFS_H = 				0x17 
    _AGB1_REG_YA_OFFS_L = 				0x18
    _AGB1_REG_ZA_OFFS_H = 				0x1A 
    _AGB1_REG_ZA_OFFS_L = 				0x1B
    _AGB1_REG_TIMEBASE_CORRECTION_PLL = 0x28 
    _AGB1_REG_REG_BANK_SEL = 			0x7F 
    # Bank 2
    _AGB2_REG_GYRO_SMPLRT_DIV = 		0x00 
    _AGB2_REG_GYRO_CONFIG_1 = 			0x01
    _AGB2_REG_GYRO_CONFIG_2 = 			0x02
    _AGB2_REG_XG_OFFS_USRH = 			0x03
    _AGB2_REG_XG_OFFS_USRL = 			0x04
    _AGB2_REG_YG_OFFS_USRH = 			0x05
    _AGB2_REG_YG_OFFS_USRL = 			0x06
    _AGB2_REG_ZG_OFFS_USRH = 			0x07
    _AGB2_REG_ZG_OFFS_USRL = 			0x08
    _AGB2_REG_ODR_ALIGN_EN = 			0x09
    _AGB2_REG_ACCEL_SMPLRT_DIV_1 = 		0x10 
    _AGB2_REG_ACCEL_SMPLRT_DIV_2 = 		0x11
    _AGB2_REG_ACCEL_INTEL_CTRL = 		0x12
    _AGB2_REG_ACCEL_WO_M_THR = 			0x13
    _AGB2_REG_ACCEL_CONFIG_1 = 			0x14
    _AGB2_REG_ACCEL_CONFIG_2 = 			0x15
    _AGB2_REG_FSYNC_CONFIG = 			0x52 
    _AGB2_REG_TEMP_CONFIG = 			0x53
    _AGB2_REG_MOD_CTRL_USR = 			0x54
    _AGB2_REG_REG_BANK_SEL = 			0x7F 
    # Bank 3
    _AGB3_REG_I2C_MST_ODR_CONFIG = 		0x00 
    _AGB3_REG_I2C_MST_CTRL = 			0x01
    _AGB3_REG_I2C_MST_DELAY_CTRL = 		0x02
    _AGB3_REG_I2C_SLV0_ADDR = 			0x03
    _AGB3_REG_I2C_SLV0_REG = 			0x04
    _AGB3_REG_I2C_SLV0_CTRL = 			0x05
    _AGB3_REG_I2C_SLV0_DO = 			0x06
    _AGB3_REG_I2C_SLV1_ADDR = 			0x07
    _AGB3_REG_I2C_SLV1_REG = 			0x08
    _AGB3_REG_I2C_SLV1_CTRL = 			0x09
    _AGB3_REG_I2C_SLV1_DO = 			0x0A
    _AGB3_REG_I2C_SLV2_ADDR = 			0x0B
    _AGB3_REG_I2C_SLV2_REG = 			0x0C
    _AGB3_REG_I2C_SLV2_CTRL = 			0x0D
    _AGB3_REG_I2C_SLV2_DO = 			0x0E
    _AGB3_REG_I2C_SLV3_ADDR = 			0x0F
    _AGB3_REG_I2C_SLV3_REG = 			0x10
    _AGB3_REG_I2C_SLV3_CTRL = 			0x11
    _AGB3_REG_I2C_SLV3_DO = 			0x12
    _AGB3_REG_I2C_SLV4_ADDR = 			0x13
    _AGB3_REG_I2C_SLV4_REG = 			0x14
    _AGB3_REG_I2C_SLV4_CTRL = 			0x15
    _AGB3_REG_I2C_SLV4_DO = 			0x16
    _AGB3_REG_I2C_SLV4_DI = 			0x17
    _AGB3_REG_REG_BANK_SEL = 			0x7F 
    
    # Magnetometer
    _M_REG_WIA2 = 						0x01 
    _M_REG_ST1 = 						0x10 
    _M_REG_HXL = 						0x11
    _M_REG_HXH = 						0x12
    _M_REG_HYL = 						0x13
    _M_REG_HYH = 						0x14
    _M_REG_HZL = 						0x15
    _M_REG_HZH = 						0x16
    _M_REG_ST2 = 						0x18
    _M_REG_CNTL2 = 						0x31 
    _M_REG_CNTL3 = 						0x32
    _M_REG_TS1 = 						0x33
    _M_REG_TS2 = 						0x34


    # Magnetometer specific stuff
    _MAG_AK09916_I2C_ADDR = 0x0C
    _MAG_AK09916_WHO_A_M_I = 0x4809
    _MAG_REG_WHO_A_M_I = 0x00
    _AK09916_mode_power_down = 0x00
    _AK09916_mode_single 	= (0x01 << 0)
    _AK09916_mode_cont_10hz 	= (0x01 << 1)
    _AK09916_mode_cont_20hz 	= (0x02 << 1)
    _AK09916_mode_cont_50hz 	= (0x03 << 1)
    _AK09916_mode_cont_100hz = (0x04 << 1)
    _AK09916_mode_self_test 	= (0x01 << 4)

    #Magnetometer Registers (aka sub-addresses when reading as I2C Master)
    _AK09916_REG_WIA1 = 0x00
    _AK09916_REG_WIA2 = 0x01
    _AK09916_REG_ST1 = 0x10
    _AK09916_REG_HXL = 0x11
    _AK09916_REG_HXH = 0x12
    _AK09916_REG_HYL = 0x13
    _AK09916_REG_HYH = 0x14
    _AK09916_REG_HZL = 0x15
    _AK09916_REG_HZH = 0x16
    _AK09916_REG_ST2 = 0x18
    _AK09916_REG_CNTL2 = 0x31
    _AK09916_REG_CNTL3 = 0x32


