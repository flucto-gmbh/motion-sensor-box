from __future__ import annotations

import smbus
import warnings

# https://github.com/pimoroni/icm20948-python/blob/master/library/icm20948/__init__.py
# https://github.com/flucto-gmbh/motion-sensor-box/blob/main/msb/imu/ICM20948/ICM20948ZMQ.py
# https://github.com/ilanschnell/bitarray


class I2C:
    def __init__(self, i2c_bus_num: int, i2c_addr: int):
        """Allows to interact with an I2C device.

        Parameters
        ----------
        i2c_bus_num: int
            The number of the i2c bus.
        i2c_addr: int
            The address of the device to interact with.
        """
        self.bus_num = i2c_bus_num
        self.address = i2c_addr
        self._bus = smbus.SMBus()
        self._bus_is_open = False

    def __enter__(self):
        self._bus.open(self.bus_num)
        self._bus_is_open = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bus.close()
        self._bus_is_open = False

    def read(self, register: int, size: int = 1):
        """Read from I2C device.

        Parameters
        ----------
        register: int
            The register to read from.
        size: int, optional
            The number of bytes to read. Defaults to 1.

        Returns
        -------
        bytes:
            The read bytes.
        """
        try:
            if size == 1:
                return self._bus.read_byte_data(self.address, register)
            else:
                return self._bus.read_i2c_block_data(self.address, register, size)
        except OSError as e:
            if self._bus_is_open:
                raise e
            else:
                warnings.warn("Trying to read from closed bus.")

    def write(self, register: int, value: int | bytes):
        """Write to I2C device.

        Parameters
        ----------
        register: int
            The register to write to.
        value: int
            The byte to write.
        """
        try:
            self._bus.write_byte_data(self.address, register, value)
        except OSError as e:
            if self._bus_is_open:
                raise e
            else:
                warnings.warn("Trying to write to closed bus.")
