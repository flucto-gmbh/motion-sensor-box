from contextlib import contextmanager
from enum import IntEnum, IntFlag
import sys
import time
import uptime

import RPi.GPIO as gpio


from msb.imu.icm20948.registers import Registers
from msb.imu.icm20948.settings import (
    Settings,
    AccelerationFilter,
    AccelerationSensitivity,
    GyroFilter,
    GyroSensitivity,
)
from msb.imu.config import IMUConf
from msb.imu.icm20948.i2c import I2C

from msb.zmq_base.Publisher import Publisher


class Bank(IntEnum):
    """Represents a register bank."""

    B0 = 0
    B1 = 1
    B2 = 2
    B3 = 3


class ICM_20948_Internal(IntFlag):
    """Internal Sensor IDs, used in various functions as arguments to know who to affect"""

    # TODO rename?
    ACC = 1 << 0
    GYR = 1 << 1
    MAG = 1 << 2
    TMP = 1 << 3
    MST = 1 << 4  # I2C Master Internal


class ICM_20948_Sample_Mode(IntFlag):
    """Sample mode options"""

    # TODO rename
    CONTINOUS = 0x00
    CYCLED = 0x01


class ICM20948Communicator:
    _current_bank: Bank = None

    def __init__(self, bank_register: bytes, i2c_bus_num: int, i2c_address: int):
        self.bank_register = bank_register
        self._i2c = I2C(i2c_bus_num, i2c_address)

        self._bank_is_set = False

    def __enter__(self):
        self._i2c.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._i2c.__exit__(exc_type, exc_val, exc_tb)

    def _set_bank(self, bank: Bank):
        bank_bits = (int(bank) << 4) & 0x30  # bits 5:4 of REG_BANK_SEL
        self._i2c.write(self.bank_register, bank_bits)
        self._current_bank = bank

    def read(self, bank: Bank, register: bytes, size: int = 1) -> bytes:
        if bank != self._current_bank:
            self._set_bank(bank)
        return self._i2c.read(register, size)

    def write(self, bank: Bank, register: bytes, value: bytes) -> None:
        if bank != self._current_bank:
            self._set_bank(bank)
        self._i2c.write(register, value)


class ICM20948:
    _update_numbytes = 23  # Read Accel, gyro, temp, and 9 bytes of mag
    _precision = 6  # TODO what exactly is this?
    _interrupt_pin = 6

    def __init__(
        self,
        config: IMUConf,
        registers: Registers,
        settings: Settings,
        publisher: Publisher,
    ):
        self.config = config
        self.registers = registers
        self.settings = settings
        self.publisher = publisher
        i2c_bus_num = self.config.i2c_bus_num
        i2c_address = self.config.i2c_address
        self.comm = ICM20948Communicator(
            self.registers.REG_BANK_SEL, i2c_bus_num, i2c_address
        )

        # TODO move to config or settings
        self._valid_chip_ids = [0xEA, 0xFF, 0x1F]

        self._delta_t = 1 / (1125 / (self.config.sample_rate_divisor + 1))
        if self.config.verbose:
            print(f"delta t is: {self._delta_t}")

        self._data = {
            key: None
            for key in [
                "epoch" "uptime",
                "acc_x",
                "acc_y",
                "acc_z",
                "rot_x",
                "rot_y",
                "rot_z",
                "mag_x",
                "mag_y",
                "mag_z",
                "temp",
            ]
        }

    def __enter__(self):
        self.comm.__enter__()
        self._setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.comm.__exit__(exc_type, exc_val, exc_tb)

    def _software_reset(self):
        """Performs a software reset on the ICM20948 module"""

        # Read the power management register
        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1)

        # Set the device reset bit [7]
        register |= 1 << 7

        self.comm.write(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1, register)

    def _set_sleep_mode(self, on: bool):
        """Sets the ICM20948 module in or out of sleep mode"""

        # Read the power management register
        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1)

        # Set/clear the sleep bit [6] as needed
        if on:
            register |= 1 << 6  # set bit
        else:
            register &= ~(1 << 6)  # clear bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1, register)

    def _set_low_power_mode(self, on: bool):
        """Sets the ICM20948 module in or out of low power mode"""

        # Read the power management register
        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1)

        # Set/clear the low power mode bit [5] as needed
        if on:
            register |= 1 << 5  # set bit
        else:
            register &= ~(1 << 5)  # clear bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_PWR_MGMT_1, register)

    def _set_sample_mode(
        self, sensors: ICM_20948_Internal, mode: ICM_20948_Sample_Mode
    ):
        """
        Sets the sample mode of the ICM90248 module
        :param sensors: byte representing the selected sensors (accelerometer, gyroscope, magnetometer)
        :param mode:    the mode in which the sensors are to be sampled. Two modes are available: continuos or cycled
        :return:        Returns true if the sample mode setting write was successful, otherwise False.
        :rtype:         bool

        """
        # TODO update docstring
        # check for valid sensor ID from user of this function
        if not (
            sensors
            & (ICM_20948_Internal.ACC | ICM_20948_Internal.GYR | ICM_20948_Internal.MST)
        ):
            raise RuntimeError("Invalid Sensor ID")

        # Read the LP CONFIG Register
        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_LP_CONFIG)

        if sensors & ICM_20948_Internal.ACC:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == ICM_20948_Sample_Mode.CYCLED:
                register |= 1 << 5  # set bit
            elif mode == ICM_20948_Sample_Mode.CONTINOUS:
                register &= ~(1 << 5)  # clear bit

        if sensors & ICM_20948_Internal.GYR:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == ICM_20948_Sample_Mode.CYCLED:
                register |= 1 << 4  # set bit
            elif mode == ICM_20948_Sample_Mode.CONTINOUS:
                register &= ~(1 << 4)  # clear bit

        if sensors & ICM_20948_Internal.MST:
            # Set/clear the sensor specific sample mode bit as needed
            if mode == ICM_20948_Sample_Mode.CYCLED:
                register |= 1 << 6  # set bit
            elif mode == ICM_20948_Sample_Mode.CYCLED:
                register &= ~(1 << 6)  # clear bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_LP_CONFIG, register)

    def _set_acc_sensitivity(self, acc_sensitivity):
        """Sets the full scale range for the accel in the ICM20948 module"""
        # TODO update docstring
        # Read the Accel Config Register
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1)

        register &= ~(0b00000110)  # clear bits 2:1 (0b0000.0XX0)

        register |= (
            acc_sensitivity << 1
        )  # place mode select into bits 2:1 of AGB2_REG_ACCEL_CONFIG

        self.comm.write(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1, register)

    def _set_gyr_sensitivity(self, gyr_sensitivity):
        """Sets the full scale range for the gyro in the ICM20948 module"""
        # TODO update docstring
        # Read the Gyro Config Register
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1)

        register &= ~(0b00000110)  # clear bits 2:1 (0b0000.0XX0)

        register |= (
            gyr_sensitivity << 1
        )  # place mode select into bits 2:1 of AGB2_REG_GYRO_CONFIG_1

        self.comm.write(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1, register)

    def _set_dlpf_cfg_accel(self, dlpcfg: int):
        """Sets the digital low pass filter for the accel in the ICM20948 module"""
        # TODO update docstring
        # Read the Accel Config Register
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1)

        if self.config.verbose:
            print(f"current low pass filer for gyroscope is: {register}")

        register &= ~(0b00111000)  # clear bits 5:3 (0b00XX.X000)

        register |= (
            dlpcfg << 3
        )  # place dlpcfg select into bits 5:3 of AGB2_REG_ACCEL_CONFIG_1

        self.comm.write(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1, register)

        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1)
        if self.config.verbose:
            print(f"low pass filer for acceleration is: {register >> 3}")

    def _set_dlpf_cfg_gyro(self, dlpcfg: int):
        """Sets the digital low pass filter for the gyro in the ICM20948 module"""
        # TODO update docstring
        # Read the gyro Config Register
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1)

        if self.config.verbose:
            print(f"current low pass filer for gyroscope is: {register}")

        register &= ~(0b00111000)  # clear bits 5:3 (0b00XX.X000)

        register |= (
            dlpcfg << 3
        )  # place dlpcfg select into bits 5:3 of _AGB2_REG_GYRO_CONFIG_1

        self.comm.write(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1, register)
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1)
        if self.config.verbose:
            print(f"low pass filter for gyroscope is: {register >> 3}")

    def _enable_dlpf_accel(self, on: bool):
        """Enables or disables the accelerometer DLPF of the ICM90248 module"""
        # TODO update docstring
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1)

        # Set/clear the ACCEL_FCHOICE bit [0] as needed
        if on:
            register |= 1 << 0  # set bit
        else:
            register &= ~(1 << 0)  # clear bit

        self.comm.write(Bank.B2, self.registers.AGB2_REG_ACCEL_CONFIG_1, register)

    def _enable_dlpf_gyro(self, on: bool):
        """Enables or disables the Gyro DLPF of the ICM90248 module"""
        # TODO update docstring

        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1)

        # Set/clear the GYRO_FCHOICE bit [0] as needed
        if on:
            register |= 1 << 0  # set bit
        else:
            register &= ~(1 << 0)  # clear bit

        return self.comm.write(Bank.B2, self.registers.AGB2_REG_GYRO_CONFIG_1, register)

    def set_sample_rate_divisor_gyro(self, rate):
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_SMPLRT_DIV)

        # clear register # TODO why read then?
        register &= ~(0b11111111)
        register |= rate << 0

        self.comm.write(Bank.B2, self.registers.AGB2_REG_GYRO_SMPLRT_DIV, register)

    ###
    # Begin Magnetometer setup methods
    ###
    def _i2c_master_passthrough(self, enable: bool):
        """Enables or disables I2C Master Passthrough"""

        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_INT_PIN_CONFIG)

        # Set/clear the BYPASS_EN bit [1] as needed
        if enable:
            register |= 1 << 1  # set bit
        else:
            register &= ~(1 << 1)  # clear bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_INT_PIN_CONFIG, register)

    def _enable_i2c_master(self, enable: bool):
        """Enables or disables I2C Master"""

        self._i2c_master_passthrough(False)  # Disable BYPASS_EN

        # Setup Master Clock speed as 345.6 kHz, and NSP (aka next slave read) to "stop between reads"

        register = self.comm.read(Bank.B3, self.registers.AGB3_REG_I2C_MST_CTRL)

        register &= ~(0x0F)  # clear bits for master clock [3:0]
        register |= 0x07  # set bits for master clock [3:0], 0x07 corresponds to 345.6 kHz, good for up to 400 kHz
        register |= (
            1 << 4
        )  # set bit [4] for NSR (next slave read). 0 = restart between reads. 1 = stop between reads.

        self.comm.write(Bank.B3, self.registers.AGB3_REG_I2C_MST_CTRL, register)

        # enable/disable Master I2C

        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_USER_CTRL)

        # Set/clear the I2C_MST_EN bit [5] as needed
        if enable:
            register |= 1 << 5  # set bit
        else:
            register &= ~(1 << 5)  # clear bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_USER_CTRL, register)

    def _check_mag_id(self):
        """Checks to see that the Magnetometer returns the correct ID value

        :return: Returns true if the check was successful, otherwise False.
        :rtype: bool
        """

        who_am_i_1 = self._read_mag(self.registers.AK09916_REG_WIA1)
        who_am_i_2 = self._read_mag(self.registers.AK09916_REG_WIA2)

        if (who_am_i_1 == (self.registers.MAG_AK09916_WHO_A_M_I >> 8)) and (
            who_am_i_2 == (self.registers.MAG_AK09916_WHO_A_M_I & 0xFF)
        ):
            return True
        else:
            return False

    def _read_mag(self, reg):
        data = self._i2c_master_single_read(self.registers.MAG_AK09916_I2C_ADDR, reg)
        return data

    def _i2c_master_single_read(self, addr: int, reg: int):
        data = self._i2c_master_slv4_txn(addr, reg, 0, True, True)
        return data

    def _write_mag(self, reg, data):
        data = self._i2c_master_single_write(
            self.registers.MAG_AK09916_I2C_ADDR, reg, data
        )
        return data

    def _i2c_master_single_write(self, addr: int, reg: int, data):
        data1 = self._i2c_master_slv4_txn(addr, reg, data, False, True)
        return data1

    def _i2c_master_slv4_txn(
        self, addr: int, reg: int, data: int, do_read: bool, send_reg_addr: bool
    ):
        # Used to configure a device before it is set up into a normal 0-3 slave slot
        # Transact directly with an I2C device, one byte at a time
        # Thanks MikeFair! // https://github.com/kriswiner/MPU9250/issues/86

        # not do_read -> do_write

        if do_read:
            addr |= 0x80

        self.comm.write(Bank.B3, self.registers.AGB3_REG_I2C_SLV4_ADDR, addr)

        self.comm.write(Bank.B3, self.registers.AGB3_REG_I2C_SLV4_REG, reg)

        ctrl_register_slv4 = 0x00
        ctrl_register_slv4 |= 1 << 7  # EN bit [7] (set)
        ctrl_register_slv4 &= ~(1 << 6)  # INT_EN bit [6] (cleared)
        ctrl_register_slv4 &= ~(0x0F)  # DLY bits [4:0] (cleared = 0)

        if send_reg_addr:
            ctrl_register_slv4 &= ~(1 << 5)  # REG_DIS bit [5] (cleared)
        else:
            ctrl_register_slv4 |= 1 << 5  # REG_DIS bit [5] (set)

        txn_failed = False

        if not do_read:
            self.comm.write(Bank.B3, self.registers.AGB3_REG_I2C_SLV4_DO, data)

        # Kick off txn
        self.comm.write(
            Bank.B3, self.registers.AGB3_REG_I2C_SLV4_CTRL, ctrl_register_slv4
        )

        max_cycles = 1000
        count = 0
        slave_4_done = False
        while not slave_4_done:
            i2c_mst_status = self.comm.read(
                Bank.B0, self.registers.AGB0_REG_I2C_MST_STATUS
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
            raise RuntimeError("txn failed.")

        if do_read:
            return self.comm.read(Bank.B3, self.registers.AGB3_REG_I2C_SLV4_DI)

        # if we get here, then it was a successful write

    def _i2c_master_reset(self):
        """Resets I2C Master Module"""

        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_USER_CTRL)

        # Set the I2C_MST_RST bit [1]
        register |= 1 << 1  # set bit

        self.comm.write(Bank.B0, self.registers.AGB0_REG_USER_CTRL, register)

    def _i2c_master_slave_cfg(
        self, slave, addr, reg, length, rw, enable, data_only, grp, swap
    ):
        """Configures Master/slave settings for the ICM20948 as master, and slave in slots 0-3"""

        # Adjust slave address, reg (aka sub-address), and control as needed for each slave slot (0-3)
        slv_addr_reg = 0x00
        slv_reg_reg = 0x00
        slv_ctrl_reg = 0x00
        if slave == 0:
            slv_addr_reg = self.registers.AGB3_REG_I2C_SLV0_ADDR
            slv_reg_reg = self.registers.AGB3_REG_I2C_SLV0_REG
            slv_ctrl_reg = self.registers.AGB3_REG_I2C_SLV0_CTRL
        elif slave == 1:
            slv_addr_reg = self.registers.AGB3_REG_I2C_SLV1_ADDR
            slv_reg_reg = self.registers.AGB3_REG_I2C_SLV1_REG
            slv_ctrl_reg = self.registers.AGB3_REG_I2C_SLV1_CTRL
        elif slave == 2:
            slv_addr_reg = self.registers.AGB3_REG_I2C_SLV2_ADDR
            slv_reg_reg = self.registers.AGB3_REG_I2C_SLV2_REG
            slv_ctrl_reg = self.registers.AGB3_REG_I2C_SLV2_CTRL
        elif slave == 3:
            slv_addr_reg = self.registers.AGB3_REG_I2C_SLV3_ADDR
            slv_reg_reg = self.registers.AGB3_REG_I2C_SLV3_REG
            slv_ctrl_reg = self.registers.AGB3_REG_I2C_SLV3_CTRL
        else:
            return False

        # Set the slave address and the rw flag
        address = addr
        if rw:
            address |= 1 << 7  # set bit# set RNW bit [7]

        self.comm.write(Bank.B3, slv_addr_reg, address)

        # Set the slave sub-address (reg)
        sub_address = reg
        self.comm.write(Bank.B3, slv_reg_reg, sub_address)

        # Set up the control info
        ctrl_reg_slvX = 0x00
        ctrl_reg_slvX |= length
        ctrl_reg_slvX |= enable << 7
        ctrl_reg_slvX |= swap << 6
        ctrl_reg_slvX |= data_only << 5
        ctrl_reg_slvX |= grp << 4

        self.comm.write(Bank.B3, slv_ctrl_reg, ctrl_reg_slvX)

    def startup_magnetometer(self):
        """Initialize the magnetometer with default values"""

        # Do not connect the SDA/SCL pins to AUX_DA/AUX_CL
        self._i2c_master_passthrough(False)
        self._enable_i2c_master(True)

        # After an ICM reset the Mag sensor may stop responding over the I2C master
        # Reset the Master I2C until it responds
        tries = 0
        max_tries = 5
        while tries < max_tries:
            # See if we can read the WhoIAm register correctly
            if self._check_mag_id():
                break  # WIA matched!
            self._i2c_master_reset()  # Otherwise, reset the master I2C and try again
            tries += 1

        if tries == max_tries:
            raise RuntimeError(f"Mag ID fail. Tries: {tries}")

        # Set up magnetometer
        mag_reg_ctrl2 = 0x00
        mag_reg_ctrl2 |= self.registers.AK09916_mode_cont_100hz
        self._write_mag(self.registers.AK09916_REG_CNTL2, mag_reg_ctrl2)

        return self._i2c_master_slave_cfg(
            0,
            self.registers.MAG_AK09916_I2C_ADDR,
            self.registers.AK09916_REG_ST1,
            9,
            True,
            True,
            False,
            False,
            False,
        )

    ###
    # End Magnetometer setup methods
    ###

    def _poll(self):
        while True:
            start_time = time.monotonic()
            try:
                self._update_data(interrupt_pin=-1)
            except KeyboardInterrupt:
                if self.config.verbose:
                    print(f"caught ctrl+x, exit")
                    sys.exit(0)
            except Exception as e:
                if self.config.verbose:
                    print(f"failed to update data: {e}, skipping")
                sys.exit(-1)

            while time.monotonic() < start_time + self._delta_t:
                if self.config.verbose:
                    print("sleeping 1 ms")
                time.sleep(0.001)

    def _update_data(self, interrupt_pin: int):
        """Reads and updates raw values from accel, gyro, mag and temp of the ICM90248 module"""
        # TODO rename function, it reads and sends data
        if self.config.verbose:
            if self.config.polling:
                print(f"{time.time()}: polling sensor")
            else:
                print(
                    f"{time.time()}: updating data via triggered interrupt pin {interrupt_pin}"
                )
        buff = self.comm.read(
            Bank.B0, self.registers.AGB0_REG_ACCEL_XOUT_H, self._update_numbytes
        )
        self._data["epoch"] = time.time()
        self._data["uptime"] = uptime.uptime()
        # acceleration
        self._data["acc_x"] = round(
            self._to_signed_int(((buff[0] << 8) | (buff[1] & 0xFF))) / self.acc_scale,
            self._precision,
        )
        self._data["acc_y"] = round(
            self._to_signed_int(((buff[2] << 8) | (buff[3] & 0xFF))) / self.acc_scale,
            self._precision,
        )
        self._data["acc_z"] = round(
            self._to_signed_int(((buff[4] << 8) | (buff[5] & 0xFF))) / self.acc_scale,
            self._precision,
        )
        # angular velocity
        self._data["rot_x"] = round(
            self._to_signed_int(((buff[6] << 8) | (buff[7] & 0xFF))) / self.gyr_scale,
            self._precision,
        )
        self._data["rot_y"] = round(
            self._to_signed_int(((buff[8] << 8) | (buff[9] & 0xFF))) / self.gyr_scale,
            self._precision,
        )
        self._data["rot_z"] = round(
            self._to_signed_int(((buff[10] << 8) | (buff[11] & 0xFF))) / self.gyr_scale,
            self._precision,
        )
        # TODO use _to_signed_int for magnetic as well?
        # TODO what about scaling factor for mag?
        # magnetic field
        # careful: magnetic data is read little endian
        self._data["mag_x"] = round(
            (buff[16] << 8) | (buff[15] & 0xFF), self._precision
        )
        self._data["mag_y"] = round(
            (buff[18] << 8) | (buff[17] & 0xFF), self._precision
        )
        self._data["mag_z"] = round(
            (buff[20] << 8) | (buff[19] & 0xFF), self._precision
        )
        self._data["temp"] = round((buff[12] << 8) | (buff[13] & 0xFF), self._precision)

        # TODO: move topic from send method to constructor of publisher
        self.publisher.send(self.config.topic, self._data)
        if self.config.verbose:
            print(f"data: {self._data}")
        if self.config.print_stdout:
            print(",".join(map(str, self._data)))

    def _configure_interrupt(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self._interrupt_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(
            self._interrupt_pin, gpio.RISING, callback=self._update_data
        )

        # currently only raw data ready mode is supported.
        # first check the current mode
        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_INT_ENABLE_1)

        if self.config.verbose:
            print(f"_AGB0_REG_INT_ENABLE_1: {register}")

        register = 1 << 0

        self.comm.write(Bank.B0, self.registers.AGB0_REG_INT_ENABLE_1, register)

        register = self.comm.read(Bank.B0, self.registers.AGB0_REG_INT_ENABLE_1)

        if self.config.verbose:
            print(f"AGB0_REG_INT_ENABLE_1: {register}")
        if not register == 1:
            raise RuntimeError("failed to activate interrupt")

    @staticmethod
    def _to_signed_int(data):
        """
        Takes an input data of 16 bits, and returns the signed 32 bit int version of this data
        this is necessary, because python does not overflow

        :return: Signed 32 bit integer
        :rtype: int

        """
        if data > 32767:
            data -= 65536
        return data

    def _setup(self):
        # are we who we need to be?
        chip_id = self.comm.read(Bank.B0, self.registers.AGB0_REG_WHO_A_M_I)
        if chip_id not in self._valid_chip_ids:
            print("Invalid Chip ID: 0x%.2X" % chip_id)
            sys.exit(1)
        else:
            if self.config.verbose:
                print(f"sensor {chip_id} is online")

        self._software_reset()
        time.sleep(0.05)
        self._set_sleep_mode(False)
        self._set_low_power_mode(False)

        # set sample mode to continuous for both accel and gyro
        self._set_sample_mode(
            (ICM_20948_Internal.ACC | ICM_20948_Internal.GYR),
            ICM_20948_Sample_Mode.CONTINOUS,
        )

        # set full scale range for both accel and gyro (separate functions)
        # TODO this does not seem "nice" yet
        acc_sensitivity = self.settings.acc_sensitivity_dict[
            self.config.acc_sensitivity
        ]
        self.acc_scale = self.settings.acc_scale_dict[self.config.acc_sensitivity]
        self._set_acc_sensitivity(acc_sensitivity)

        gyr_sensitivity = self.settings.gyr_sensitivity_dict[
            self.config.gyr_sensitivity
        ]
        self.gyr_scale = self.settings.gyr_scale_dict[self.config.gyr_sensitivity]
        self._set_gyr_sensitivity(gyr_sensitivity)

        # set low pass filter for accel
        acc_filter_enum = self.config.acc_filter
        if acc_filter_enum is AccelerationFilter.DLPF_OFF:
            self._enable_dlpf_accel(False)
        else:
            acc_filter_value = self.settings.acc_filter_dict[acc_filter_enum]
            self._set_dlpf_cfg_accel(acc_filter_value)
            self._enable_dlpf_accel(True)

        # set low pass filter for gyro
        gyr_filter_enum = self.config.gyr_filter
        if gyr_filter_enum is GyroFilter.DLPF_OFF:
            self._enable_dlpf_gyro(False)
        else:
            gyr_filter_value = self.settings.gyr_filter_dict[gyr_filter_enum]
            self._set_dlpf_cfg_gyro(gyr_filter_value)
            self._enable_dlpf_gyro(True)

        # set output data rate
        self.set_sample_rate_divisor_gyro(rate=self.config.sample_rate_divisor)

        # fire up the compass
        self.startup_magnetometer()

        if self.config.polling:
            if self.config.verbose:
                print(f"starting to poll imu")
            self._poll()
        else:
            self._configure_interrupt()

