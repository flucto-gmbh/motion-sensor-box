from datetime import datetime, timezone
import numpy as np
import pickle
import RPi.GPIO as gpio
import smbus
import sys
import time
import uptime

from .ICM20948_registers import ICM20938_REGISTERS
from .ICM20948_settings import ICM20948_SETTINGS

# TODO
# - fix temperature
# - add polling option

# -----------------------------------------------------------------------------
# ICM20948.pi
#
# Python library for the TDK IncenSence ICM-20948 9-DoF Motion Sensor
#
# ------------------------------------------------------------------------
#
# Written by Aljoscha Sander, December 2020
# This library is loosely based on the Sparkfun qwiic_icm20948.py library
#
# ==================================================================================
# Copyright (c) 2020 Aljoscha Sander
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==================================================================================

"""
ICM20948
============
Python module for the [InvenSence ICM20948 9-DoF Motion Sensor](https://invensense.tdk.com/products/motion-tracking/9-axis/icm-20948/)

This library is loosely based on Sparkfuns [Qwiic ICM-20948 library](https://github.com/sparkfun/Qwiic_9DoF_IMU_ICM20948_Py)

"""

# global constants

_DEFAULT_NAME = "ICM20948"
_AVAILABLE_I2C_ADDRESS = [0x68, 0x69]  # depending wether the AD0 line is high or low,
# two different addresses are available
IMU_TOPIC = b"imu"
# define our valid chip IDs
_validChipIDs = [0xEA, 0xFF, 0x1F]


class ICM20948ZMQ(ICM20938_REGISTERS, ICM20948_SETTINGS):

    """
    ICM-20948

        : param address: I2C address to use for the motion sensor.
                         The sensor has two different possible addresses (0x68 and 0x69)
                         depending on wether AD0 is high (0x69) or low (0x68)
        : param i2c_bus: if an I2C bus has already been initiated somewehere else,
                         use this parameter to pass the bus object to the object.
        : return:        ICM20938 object
        : rtype:         Object
    """

    device_name = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS
    interrupt_pin = 6

    _acc_sensitivity = None
    _acc_scale = None
    _gyr_sensitivity = None
    _gyr_scale = None

    _precision = 6

    _update_numbytes = 23  # Read Accel, gyro, temp, and 9 bytes of mag
    # _data = np.zeros(13)
    _data = [0] * 13

    _interrupt_enabled = False
    _output_data_div = None
    _verbose = False
    _print_stdout = False

    REG_BANK_SEL = 0x7F

    # Constructor
    def __init__(
        self,
        zmq_pub_socket,
        address=None,
        i2c_driver=None,
        acc_sensitivity="2g",
        acc_filter=0,
        gyr_sensitivity="500dps",
        gyr_filter=0,
        precision=6,
        output_data_div=22,
        verbose=False,
        print_stdout=False,
        polling=False,
    ):

        self.zmq_pub_socket = zmq_pub_socket
        # if an address is provided, us this, otherwise fall back to the first of the two default
        # addresses (0x68)
        self.address = address if address != None else self.available_addresses[0]

        # load the I2C driver if one isn't provided
        if i2c_driver == None:
            self._i2c = smbus.SMBus(1)
            if self._i2c == None:
                print("Unable to load I2C driver for this platform.")
                sys.exit(-1)
        else:
            self._i2c = i2c_driver

        if acc_sensitivity in self._acc_sensitivity_dict:
            self._acc_sensitivity = self._acc_sensitivity_dict[
                acc_sensitivity
            ]
            self._acc_scale = self._acc_scale_dict[acc_sensitivity]
        else:
            print("invalid accelerometer sensitivity, defaulting to +- 2g")
            self._acc_sensitivity = self._acc_sensitivity_dict["2g"]
            self._acc_scale = self._acc_scale_dict["2g"]

        if acc_filter < len(self._acc_filter_list):
            self._acc_filter = self._acc_filter_list[acc_filter]
        else:
            print(f"invalid filter selection {acc_filter}, defaulting to filter 1")
            self._acc_filter = self._acc_filter_list[0]

        if gyr_sensitivity in self._gyr_sensitivity_dict:
            self._gyr_sensitivity = self._gyr_sensitivity_dict[gyr_sensitivity]
            self._gyr_scale = self._gyr_scale_dict[gyr_sensitivity]
        else:
            print("invalid gyroscope sensitivity, defaulting to +- 250 degree / second")
            self._gyr_sensitivity = self._gyr_sensitivity_dict["250dps"]
            self._gyr_scale = self._gyr_scale_dict["250dps"]

        if gyr_filter < len(self._gyr_filter_list):
            self._gyr_filter = self._gyr_filter_list[gyr_filter]
        else:
            print(f"invalid gyroscope filter selection {gyr_filter}, defaulting to filter 1")
            self._gyr_filter = self._gyr_filter_list[0]
        
        self._precision = precision
        self._output_data_div = output_data_div
        self._verbose = verbose
        self._print_stdout = print_stdout
        self._polling = polling
        self._delta_t = 1 / (1125 / (self._output_data_div + 1))
        if self._verbose:
            print(f"delta t is: {self._delta_t}")

    def begin(self):
        """
        Initialize the operation of the ICM20948 module

        :return: Returns true of the initializtion was successful, otherwise False.
        :rtype: bool

        """
        # are we who we need to be?
        self._set_bank(0)
        chip_ID = self._i2c.read_byte_data(self.address, self._AGB0_REG_WHO_A_M_I)
        if not chip_ID in _validChipIDs:
            print("Invalid Chip ID: 0x%.2X" % chip_ID)
            sys.exit(-1)
        else:
            if self._verbose:
                print(f"sensor {chip_ID} is online")

        # software reset
        self.sw_reset()
        time.sleep(0.05)

        # set sleep mode off
        self.sleep(False)

        # set lower power mode off
        self.low_power(False)

        # set sample mode to continuous for both accel and gyro
        self.set_sample_mode(
            (self._ICM_20948_Internal_Acc | self._ICM_20948_Internal_Gyr),
            self._ICM_20948_Sample_Mode_Continuous,
        )

        # set full scale range for both accel and gryo (separate functions)
        self.set_acc_sensitivity()
        self.set_gyr_sensitivity()

        # set low pass filter for both accel and gyro (separate functions)
        self.set_DLPF_cfg_accel(self._acc_filter)
        self.set_DLPF_cfg_gyro(self._gyr_filter)

        # enable digital low pass filters on both accel and gyro
        self.enable_DLPF_accel(True)
        self.enable_DLPF_gyro(True)

        # set output data rate
        self.set_ODR_gyro(rate=self._output_data_div)

        # fire up the compass
        self.startup_magnetometer()

        if self._polling:
            if self._verbose:
                print(f"starting to poll imu")
            self._set_bank(0)
            self._poll()
        else:
            # setup the interrupt
            self._configure_interrupt()
            # set bank to 0
            self._set_bank(0)
            return True

    @property
    def data(self):
        return self._data

    def _update_data(self, interrupt_pin: int):
        """
        Reads and updates raw values from accel, gyro, mag and temp of the ICM90248 module

        :return: Returns True if I2C readBlock was successful, otherwise False.
        :rtype: bool

        """
        if self._verbose:
            if self._polling:
                print(f"{time.time()}: polling sensor")
            else:
                print(
                    f"{time.time()}: updating data via triggered interrupt pin {interrupt_pin}"
                )
        buff = self._i2c.read_i2c_block_data(
            self.address, self._AGB0_REG_ACCEL_XOUT_H, self._update_numbytes
        )
        self._data[0] = datetime.fromtimestamp(ts := time.time(), tz=timezone.utc)
        self._data[1] = ts
        self._data[2] = uptime.uptime()
        # acceleration
        self._data[3] = round(
            self.to_signed_int(((buff[0] << 8) | (buff[1] & 0xFF))) / self._acc_scale, self._precision
        )
        self._data[4] = round(
            self.to_signed_int(((buff[2] << 8) | (buff[3] & 0xFF))) / self._acc_scale, self._precision
        )
        self._data[5] = round(
            self.to_signed_int(((buff[4] << 8) | (buff[5] & 0xFF))) / self._acc_scale, self._precision
        )
        # angular velocity
        self._data[6] = round(
            self.to_signed_int(((buff[6] << 8) | (buff[7] & 0xFF))) / self._gyr_scale, self._precision
        )
        self._data[7] = round(
            self.to_signed_int(((buff[8] << 8) | (buff[9] & 0xFF))) / self._gyr_scale, self._precision
        )
        self._data[8] = round(
            self.to_signed_int(((buff[10] << 8) | (buff[11] & 0xFF))) / self._gyr_scale, self._precision
        )
        # magnetic field
        # careful: magnetic data is read little endian
        self._data[9]  = round((buff[16] << 8) | (buff[15] & 0xFF), self._precision)
        self._data[10] = round((buff[18] << 8) | (buff[17] & 0xFF), self._precision)
        self._data[11] = round((buff[20] << 8) | (buff[19] & 0xFF), self._precision)
        self._data[12] = round((buff[12] << 8) | (buff[13] & 0xFF), self._precision)
        self.zmq_pub_socket.send_multipart(
            [IMU_TOPIC, pickle.dumps(self._data)]  # topic  # serialize the payload
        )
        if self._verbose:
            print(f"data: {self._data}")
        if self._print_stdout:
            print(','.join(map(str, self._data)))

    def _poll(self):
        while True:
            start_time = time.monotonic()
            try:
                self._update_data(interrupt_pin=-1)
            except KeyboardInterrupt:
                if self._verbose:
                    print(f"caught ctrl+x, exit")
                    sys.exit(0)
            except Exception as e:
                if self._verbose:
                    print(f"failed to update data: {e}, skipping")
                sys.exit(-1)

            while time.monotonic() < start_time + self._delta_t:
                if self._verbose:
                    print("sleeping 1 ms")
                time.sleep(0.001)


    def _configure_interrupt(self):

        gpio.setmode(gpio.BCM)
        gpio.setup(self.interrupt_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(
            self.interrupt_pin, gpio.RISING, callback=self._update_data
        )

        # currently only raw data ready mode is suported.
        # first check the current mode
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_INT_ENABLE_1)

        if self._verbose:
            print(f"_AGB0_REG_INT_ENABLE_1: {register}")

        register = 1 << 0

        # Write register
        self._set_bank(0)
        ret = self._i2c.write_byte_data(
            self.address, self._AGB0_REG_INT_ENABLE_1, register
        )
        if self._verbose:
            print(f"enabling interrupt returned {ret}")

        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_INT_ENABLE_1)

        if self._verbose:
            print(f"_AGB0_REG_INT_ENABLE_1: {register}")
        if not register == 1:
            raise Exception("failed to activate interrupt")

    def _set_bank(self, bank):
        """
        Sets the bank register of the ICM20948 module

        :return: Returns true if the bank was a valid value and it was set, otherwise False.
        :rtype: bool

        """
        if bank > 3:  # Only 4 possible banks
            print("Invalid Bank value: %d" % bank)
            return False
        bank = (bank << 4) & 0x30  # bits 5:4 of REG_BANK_SEL
        # return ICM_20948_execute_w(pdev, REG_BANK_SEL, &bank, 1)
        return self._i2c.write_byte_data(self.address, self.REG_BANK_SEL, bank)

    def sw_reset(self):
        """
        Performs a software reset on the ICM20948 module

        :return: Returns true if the software reset was successful, otherwise False.
        :rtype: bool

        """
        # Read the Power Management Register, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_PWR_MGMT_1)

        # Set the device reset bit [7]
        register |= 1 << 7

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_PWR_MGMT_1, register
        )

    def sleep(self, on):
        """
        Sets the ICM20948 module in or out of sleep mode

        :return: Returns true if the sleep setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the Power Management Register, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_PWR_MGMT_1)

        # Set/clear the sleep bit [6] as needed
        if on:
            register |= 1 << 6  # set bit
        else:
            register &= ~(1 << 6)  # clear bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_PWR_MGMT_1, register
        )

    def low_power(self, on):
        """
        Sets the ICM20948 module in or out of low power mode

        :return: Returns true if the power mode setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the Power Management Register, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_PWR_MGMT_1)

        # Set/clear the low power mode bit [5] as needed
        if on:
            register |= 1 << 5  # set bit
        else:
            register &= ~(1 << 5)  # clear bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_PWR_MGMT_1, register
        )

    def set_sample_mode(self, sensors, mode):
        """
        Sets the sample mode of the ICM90248 module
        :param sensors: byte representing the selected sensors (accelerometer, gyroscope, magnetometer)
        :param mode:    the mode in which the sensors are to be sampled. Two modes are available: continuos or cycled
        :return:        Returns true if the sample mode setting write was successful, otherwise False.
        :rtype:         bool

        """
        # check for valid sensor ID from user of this function
        if (
            sensors
            & (
                self._ICM_20948_Internal_Acc
                | self._ICM_20948_Internal_Gyr
                | self._ICM_20948_Internal_Mst
            )
        ) == False:
            print("Invalid Sensor ID")
            return False

        # Read the LP CONFIG Register, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_LP_CONFIG)

        if sensors & self._ICM_20948_Internal_Acc:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == self._ICM_20948_Sample_Mode_Cycled:
                register |= 1 << 5  # set bit
            elif mode == self._ICM_20948_Sample_Mode_Continuous:
                register &= ~(1 << 5)  # clear bit

        if sensors & self._ICM_20948_Internal_Gyr:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == self._ICM_20948_Sample_Mode_Cycled:
                register |= 1 << 4  # set bit
            elif mode == self._ICM_20948_Sample_Mode_Continuous:
                register &= ~(1 << 4)  # clear bit

        if sensors & self._ICM_20948_Internal_Mst:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == self._ICM_20948_Sample_Mode_Cycled:
                register |= 1 << 6  # set bit
            elif mode == self._ICM_20948_Sample_Mode_Continuous:
                register &= ~(1 << 6)  # clear bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_LP_CONFIG, register
        )

    def set_acc_sensitivity(self):
        """
        Sets the full scale range for the accel in the ICM20948 module

        :return: Returns true if the full scale range setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the Accel Config Register, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_ACCEL_CONFIG_1)

        register &= ~(0b00000110)  # clear bits 2:1 (0b0000.0XX0)

        register |= (
            self._acc_sensitivity << 1
        )  # place mode select into bits 2:1 of _AGB2_REG_ACCEL_CONFIG

        # Write register
        self._set_bank(2)
        return self._i2c.write_byte_data(
            self.address, self._AGB2_REG_ACCEL_CONFIG_1, register
        )

    def set_gyr_sensitivity(self):
        """
        Sets the full scale range for the gyro in the ICM20948 module

        :return: Returns true if the full scale range setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the Gyro Config Register, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_GYRO_CONFIG_1)

        register &= ~(0b00000110)  # clear bits 2:1 (0b0000.0XX0)

        register |= (
            self._gyr_sensitivity << 1
        )  # place mode select into bits 2:1 of _AGB2_REG_GYRO_CONFIG_1

        # Write register
        self._set_bank(2)
        return self._i2c.write_byte_data(
            self.address, self._AGB2_REG_GYRO_CONFIG_1, register
        )

    def get_ODR_gyro(self):
        self._set_bank(2)
        register = self._i2c.read_byte_data(
            self.address, self._AGB2_REG_GYRO_SMPLRT_DIV
        )
        return register

    def set_ODR_gyro(self, rate=4):
        self._set_bank(2)
        register = self._i2c.read_byte_data(
            self.address, self._AGB2_REG_GYRO_SMPLRT_DIV
        )

        # clear register
        register &= ~(0b11111111)
        register |= rate << 0

        ret = self._i2c.write_byte_data(
            self.address, self._AGB2_REG_GYRO_SMPLRT_DIV, register
        )

        if self._verbose:
            print(f"write function returned {ret}")
        if self._verbose:
            print(f"current output divisor {self.get_ODR_gyro()}")

    def set_DLPF_cfg_accel(self, dlpcfg):
        """
        Sets the digital low pass filter for the accel in the ICM20948 module

        :return: Returns true if the dlp setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the Accel Config Register, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_ACCEL_CONFIG_1)

        if self._verbose:
            print(f"current low pass filer for gyroscope is: {register}")

        register &= ~(0b00111000)  # clear bits 5:3 (0b00XX.X000)

        register |= (
            dlpcfg << 3
        )  # place dlpcfg select into bits 5:3 of _AGB2_REG_ACCEL_CONFIG_1

        # Write register
        self._set_bank(2)
        self._i2c.write_byte_data(
            self.address, self._AGB2_REG_ACCEL_CONFIG_1, register
        )

        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_ACCEL_CONFIG_1)
        if self._verbose:
            print(f"low pass filer for acceleration is: {register >> 3}")

    def set_DLPF_cfg_gyro(self, dlpcfg):
        """
        Sets the digital low pass filter for the gyro in the ICM20948 module

        :return: Returns true if the dlp setting write was successful, otherwise False.
        :rtype: bool

        """
        # Read the gyro Config Register, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_GYRO_CONFIG_1)

        if self._verbose:
            print(f"current low pass filer for gyroscope is: {register}")

        register &= ~(0b00111000)  # clear bits 5:3 (0b00XX.X000)

        register |= (
            dlpcfg << 3
        )  # place dlpcfg select into bits 5:3 of _AGB2_REG_GYRO_CONFIG_1

        # Write register
        self._set_bank(2)
        self._i2c.write_byte_data(
            self.address, self._AGB2_REG_GYRO_CONFIG_1, register
        )
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_GYRO_CONFIG_1)
        if self._verbose:
            print(f"low pass filter for gyroscope is: {register >> 3}")



    def enable_DLPF_accel(self, on):
        """
        Enables or disables the accelerometer DLPF of the ICM90248 module

        :return: Returns true if the DLPF mode setting write was successful, otherwise False.
        :rtype: bool

        """

        # Read the _AGB2_REG_ACCEL_CONFIG_1, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_ACCEL_CONFIG_1)

        # Set/clear the ACCEL_FCHOICE bit [0] as needed
        if on:
            register |= 1 << 0  # set bit
        else:
            register &= ~(1 << 0)  # clear bit

        # Write register
        self._set_bank(2)
        return self._i2c.write_byte_data(
            self.address, self._AGB2_REG_ACCEL_CONFIG_1, register
        )

    def enable_DLPF_gyro(self, on):
        """
        Enables or disables the Gyro DLPF of the ICM90248 module

        :return: Returns true if the DLPF mode setting write was successful, otherwise False.
        :rtype: bool

        """

        # Read the _AGB2_REG_GYRO_CONFIG_1, store in local variable "register"
        self._set_bank(2)
        register = self._i2c.read_byte_data(self.address, self._AGB2_REG_GYRO_CONFIG_1)

        # Set/clear the GYRO_FCHOICE bit [0] as needed
        if on:
            register |= 1 << 0  # set bit
        else:
            register &= ~(1 << 0)  # clear bit

        # Write register
        self._set_bank(2)
        return self._i2c.write_byte_data(
            self.address, self._AGB2_REG_GYRO_CONFIG_1, register
        )

    def data_ready(self):
        """
        Returns status of RAW_DATA_0_RDY_INT the ICM90248 module

        :return: Returns true if raw data is ready, otherwise False.
        :rtype: bool

        """

        # Read the _AGB0_REG_INT_STATUS_1, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_INT_STATUS_1)

        # check bit [0]
        if register & (1 << 0):
            return True
        else:
            return False

    def to_signed_int(self, input):
        """
        Takes an input data of 16 bits, and returns the signed 32 bit int version of this data
        this is necessary, because python does not overflow

        :return: Signed 32 bit integer
        :rtype: int

        """
        if input > 32767:
            input -= 65536
        return input

    def i2c_master_passthrough(self, passthrough):
        """
        Enables or disables I2C Master Passthrough

        :return: Returns true if the setting write was successful, otherwise False.
        :rtype: bool

        """

        # Read the _AGB0_REG_INT_PIN_CONFIG, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_INT_PIN_CONFIG)

        # Set/clear the BYPASS_EN bit [1] as needed
        if passthrough:
            register |= 1 << 1  # set bit
        else:
            register &= ~(1 << 1)  # clear bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_INT_PIN_CONFIG, register
        )

    def i2c_master_enable(self, enable):
        """
        Enables or disables I2C Master

        :return: Returns true if the setting write was successful, otherwise False.
        :rtype: bool

        """

        self.i2c_master_passthrough(False)  # Disable BYPASS_EN

        # Setup Master Clock speed as 345.6 kHz, and NSP (aka next slave read) to "stop between reads"
        # Read the _AGB3_REG_I2C_MST_CTRL, store in local variable "register"
        self._set_bank(3)
        register = self._i2c.read_byte_data(self.address, self._AGB3_REG_I2C_MST_CTRL)

        register &= ~(0x0F)  # clear bits for master clock [3:0]
        register |= 0x07  # set bits for master clock [3:0], 0x07 corresponds to 345.6 kHz, good for up to 400 kHz
        register |= (
            1 << 4
        )  # set bit [4] for NSR (next slave read). 0 = restart between reads. 1 = stop between reads.

        # Write register
        self._set_bank(3)
        self._i2c.write_byte_data(self.address, self._AGB3_REG_I2C_MST_CTRL, register)

        # enable/disable Master I2C
        # Read the _AGB0_REG_USER_CTRL, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_USER_CTRL)

        # Set/clear the I2C_MST_EN bit [5] as needed
        if enable:
            register |= 1 << 5  # set bit
        else:
            register &= ~(1 << 5)  # clear bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_USER_CTRL, register
        )

    def i2c_master_slv4_txn(self, addr, reg, data, rw, send_reg_addr):
        # Used to configure a device before it is setup into a normal 0-3 slave slot
        # Transact directly with an I2C device, one byte at a time
        # Thanks MikeFair! // https://github.com/kriswiner/MPU9250/issues/86

        if rw:
            addr |= 0x80

        self._set_bank(3)
        self._i2c.write_byte_data(self.address, self._AGB3_REG_I2C_SLV4_ADDR, addr)

        self._set_bank(3)
        self._i2c.write_byte_data(self.address, self._AGB3_REG_I2C_SLV4_REG, reg)

        ctrl_register_slv4 = 0x00
        ctrl_register_slv4 |= 1 << 7  # EN bit [7] (set)
        ctrl_register_slv4 &= ~(1 << 6)  # INT_EN bit [6] (cleared)
        ctrl_register_slv4 &= ~(0x0F)  # DLY bits [4:0] (cleared = 0)

        if send_reg_addr:
            ctrl_register_slv4 &= ~(1 << 5)  # REG_DIS bit [5] (cleared)
        else:
            ctrl_register_slv4 |= 1 << 5  # REG_DIS bit [5] (set)

        txn_failed = False

        if rw == False:
            self._set_bank(3)
            self._i2c.write_byte_data(self.address, self._AGB3_REG_I2C_SLV4_DO, data)

        # Kick off txn
        self._set_bank(3)
        self._i2c.write_byte_data(
            self.address, self._AGB3_REG_I2C_SLV4_CTRL, ctrl_register_slv4
        )

        max_cycles = 1000
        count = 0
        slave_4_done = False
        while slave_4_done == False:
            self._set_bank(0)
            i2c_mst_status = self._i2c.read_byte_data(
                self.address, self._AGB0_REG_I2C_MST_STATUS
            )
            if i2c_mst_status & (1 << 6):  # Check I2C_SLAVE_DONE bit [6]
                slave_4_done = True
            if count > max_cycles:
                slave_4_done = True
            count += 1

        if i2c_mst_status & (1 << 4):  # Check I2C_SLV4_NACK bit [4]
            txn_failed = True

        if count > max_cycles:
            txn_failed = True

        if txn_failed:
            return False

        if rw:
            self._set_bank(3)
            return self._i2c.read_byte_data(self.address, self._AGB3_REG_I2C_SLV4_DI)

        return True  # if we get here, then it was a successful write

    def i2c_master_single_write(self, addr, reg, data):
        data1 = self.i2c_master_slv4_txn(addr, reg, data, False, True)
        return data1

    def write_mag(self, reg, data):
        data = self.i2c_master_single_write(self._MAG_AK09916_I2C_ADDR, reg, data)
        return data

    def i2c_master_single_read(self, addr, reg):
        data = self.i2c_master_slv4_txn(addr, reg, 0, True, True)
        return data

    def read_mag(self, reg):
        data = self.i2c_master_single_read(self._MAG_AK09916_I2C_ADDR, reg)
        return data

    def mag_who_am_i(self):
        """
        Checks to see that the Magnatometer returns the correct ID value

        :return: Returns true if the check was successful, otherwise False.
        :rtype: bool

        """

        who_am_i_1 = self.read_mag(self._AK09916_REG_WIA1)
        who_am_i_2 = self.read_mag(self._AK09916_REG_WIA2)

        if (who_am_i_1 == (self._MAG_AK09916_WHO_A_M_I >> 8)) and (
            who_am_i_2 == (self._MAG_AK09916_WHO_A_M_I & 0xFF)
        ):
            return True
        else:
            return False

    def i2c_master_reset(self):
        """
        Resets I2C Master Module

        :return: Returns true if the i2c write was successful, otherwise False.
        :rtype: bool

        """

        # Read the _AGB0_REG_USER_CTRL, store in local variable "register"
        self._set_bank(0)
        register = self._i2c.read_byte_data(self.address, self._AGB0_REG_USER_CTRL)

        # Set the I2C_MST_RST bit [1]
        register |= 1 << 1  # set bit

        # Write register
        self._set_bank(0)
        return self._i2c.write_byte_data(
            self.address, self._AGB0_REG_USER_CTRL, register
        )

    def i2c_master_slave_cfg(
        self, slave, addr, reg, len, rw, enable, data_only, grp, swap
    ):
        """
        Configures Master/slave settings for the ICM20948 as master, and slave in slots 0-3

        :return: Returns true if the configuration was successful, otherwise False.
        :rtype: bool

        """
        # Adjust slave address, reg (aka sub-address), and control as needed for each slave slot (0-3)
        slv_addr_reg = 0x00
        slv_reg_reg = 0x00
        slv_ctrl_reg = 0x00
        if slave == 0:
            slv_addr_reg = self._AGB3_REG_I2C_SLV0_ADDR
            slv_reg_reg = self._AGB3_REG_I2C_SLV0_REG
            slv_ctrl_reg = self._AGB3_REG_I2C_SLV0_CTRL
        elif slave == 1:
            slv_addr_reg = self._AGB3_REG_I2C_SLV1_ADDR
            slv_reg_reg = self._AGB3_REG_I2C_SLV1_REG
            slv_ctrl_reg = self._AGB3_REG_I2C_SLV1_CTRL
        elif slave == 2:
            slv_addr_reg = self._AGB3_REG_I2C_SLV2_ADDR
            slv_reg_reg = self._AGB3_REG_I2C_SLV2_REG
            slv_ctrl_reg = self._AGB3_REG_I2C_SLV2_CTRL
        elif slave == 3:
            slv_addr_reg = self._AGB3_REG_I2C_SLV3_ADDR
            slv_reg_reg = self._AGB3_REG_I2C_SLV3_REG
            slv_ctrl_reg = self._AGB3_REG_I2C_SLV3_CTRL
        else:
            return False

        self._set_bank(3)

        # Set the slave address and the rw flag
        address = addr
        if rw:
            address |= 1 << 7  # set bit# set RNW bit [7]

        self._i2c.write_byte_data(self.address, slv_addr_reg, address)

        # Set the slave sub-address (reg)
        sub_address = reg
        self._i2c.write_byte_data(self.address, slv_reg_reg, sub_address)

        # Set up the control info
        ctrl_reg_slvX = 0x00
        ctrl_reg_slvX |= len
        ctrl_reg_slvX |= enable << 7
        ctrl_reg_slvX |= swap << 6
        ctrl_reg_slvX |= data_only << 5
        ctrl_reg_slvX |= grp << 4
        return self._i2c.write_byte_data(self.address, slv_ctrl_reg, ctrl_reg_slvX)

    def startup_magnetometer(self):
        """
        Initialize the magnotometer with default values

        :return: Returns true of the initializtion was successful, otherwise False.
        :rtype: bool

        """
        self.i2c_master_passthrough(
            False
        )  # Do not connect the SDA/SCL pins to AUX_DA/AUX_CL
        self.i2c_master_enable(True)

        # After a ICM reset the Mag sensor may stop responding over the I2C master
        # Reset the Master I2C until it responds
        tries = 0
        max_tries = 5
        while tries < max_tries:
            # See if we can read the WhoIAm register correctly
            if self.mag_who_am_i():
                break  # WIA matched!
            self.i2c_master_reset()  # Otherwise, reset the master I2C and try again
            tries += 1

        if tries == max_tries:
            print("Mag ID fail. Tries: %d\n", tries)
            return False

        # Set up magnetometer
        mag_reg_ctrl2 = 0x00
        mag_reg_ctrl2 |= self._AK09916_mode_cont_100hz
        self.write_mag(self._AK09916_REG_CNTL2, mag_reg_ctrl2)

        return self.i2c_master_slave_cfg(
            0,
            self._MAG_AK09916_I2C_ADDR,
            self._AK09916_REG_ST1,
            9,
            True,
            True,
            False,
            False,
            False,
        )
