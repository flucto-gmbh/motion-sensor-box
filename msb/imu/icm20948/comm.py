from msb.imu.icm20948.i2c import I2C
from msb.imu.icm20948.settings import Bank


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
