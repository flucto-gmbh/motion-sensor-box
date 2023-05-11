import sys
import time
import uptime

import RPi.GPIO as gpio

from queue import SimpleQueue

from msb.imu.icm20948.comm import ICM20948Communicator
from msb.imu.icm20948.registers import Registers
from msb.imu.icm20948.settings import (
    Settings,
    AccelerationFilter,
    GyroFilter,
    ICM_20948_Sample_Mode,
    ICM_20948_Internal,
    Bank,
)
from msb.imu.config import IMUConf
from msb.imu.icm20948.ak09916 import AK09916

from msb.zmq_base.Publisher import Publisher


class ICM20948:
    _update_numbytes = 23  # Read Accel, gyro, temp, and 9 bytes of mag
    _precision = 6  # TODO what exactly is this?
    _interrupt_pin = 6

    def __init__(
        self,
        config: IMUConf,
        registers: Registers,
        settings: Settings,
    ):
        self.config = config
        self.registers = registers
        self.settings = settings
        self._data_q = SimpleQueue()
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
        self.magnetometer = AK09916(self.comm, self.registers)

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

    def _set_sample_rate_divisor_gyro(self, rate):
        register = self.comm.read(Bank.B2, self.registers.AGB2_REG_GYRO_SMPLRT_DIV)

        # clear register # TODO why read then?
        register &= ~(0b11111111)
        register |= rate << 0

        self.comm.write(Bank.B2, self.registers.AGB2_REG_GYRO_SMPLRT_DIV, register)

    def _setup_polling(self):
        raise NotImplementedError("Polling is not yet implemented.")
        # TODO polling needs to happen in another thread which fills self._data_q
        # also dont forget to cancel that task in __exit__
        # while True:
        #     start_time = time.monotonic()
        #     try:
        #         self._read_new_data(interrupt_pin=-1)
        #     except KeyboardInterrupt:
        #         if self.config.verbose:
        #             print(f"caught ctrl+x, exit")
        #             sys.exit(0)
        #     except Exception as e:
        #         if self.config.verbose:
        #             print(f"failed to update data: {e}, skipping")
        #         sys.exit(-1)
        #
        #     while time.monotonic() < start_time + self._delta_t:
        #         if self.config.verbose:
        #             print("sleeping 1 ms")
        #         time.sleep(0.001)

    def _setup_interrupt(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self._interrupt_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(
            self._interrupt_pin, gpio.RISING, callback=self._read_new_data
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

    def _parse_acc(self, raw: int) -> float:
        return round(
            self._to_signed_int(raw) / self._acc_scale,
            self._precision,
        )

    def _parse_gyr(self, raw: int) -> float:
        return round(
            self._to_signed_int(raw) / self._gyr_scale,
            self._precision,
        )

    def _parse_mag(self, raw: int) -> float:
        return round(raw, self._precision)

    def _parse_temp(self, raw: int) -> float:
        return round(raw, self._precision)

    def _read_new_data(self, interrupt_pin: int):
        """Reads and queues raw values from accel, gyro, mag and temp of the ICM90248 module"""
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
        data = {
            "epoch": time.time(),
            "uptime": uptime.uptime(),
            # acceleration
            "acc_x": self._parse_acc((buff[0] << 8) | (buff[1] & 0xFF)),
            "acc_y": self._parse_acc((buff[2] << 8) | (buff[3] & 0xFF)),
            "acc_z": self._parse_acc((buff[4] << 8) | (buff[5] & 0xFF)),
            # angular velocity
            "rot_x": self._parse_gyr((buff[6] << 8) | (buff[7] & 0xFF)),
            "rot_y": self._parse_gyr((buff[8] << 8) | (buff[9] & 0xFF)),
            "rot_z": self._parse_gyr((buff[10] << 8) | (buff[11] & 0xFF)),
            # TODO use _to_signed_int for magnetic as well?
            # TODO what about scaling factor for mag?
            # magnetic field
            # careful: magnetic data is read little endian
            "mag_x": self._parse_mag((buff[16] << 8) | (buff[15] & 0xFF)),
            "mag_y": self._parse_mag((buff[18] << 8) | (buff[17] & 0xFF)),
            "mag_z": self._parse_mag((buff[20] << 8) | (buff[19] & 0xFF)),
            "temp": self._parse_temp((buff[12] << 8) | (buff[13] & 0xFF)),
        }

        self._data_q.put(data)
        if self.config.verbose:
            print(f"data: {data}")
        if self.config.print_stdout:
            print(",".join(map(str, data)))

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
        self._acc_scale = self.settings.acc_scale_dict[self.config.acc_sensitivity]
        self._set_acc_sensitivity(acc_sensitivity)

        gyr_sensitivity = self.settings.gyr_sensitivity_dict[
            self.config.gyr_sensitivity
        ]
        self._gyr_scale = self.settings.gyr_scale_dict[self.config.gyr_sensitivity]
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
        self._set_sample_rate_divisor_gyro(rate=self.config.sample_rate_divisor)

        # fire up the compass
        self.magnetometer.setup()

        if self.config.polling:
            self._setup_polling()
        else:
            self._setup_interrupt()

    def get_data(self) -> dict:
        return self._data_q.get()
