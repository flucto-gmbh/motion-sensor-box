from msb.imu.icm20948.comm import ICM20948Communicator
from msb.imu.icm20948.registers import Registers
from msb.imu.icm20948.settings import Bank


class TXNFailedError(Exception):
    "Raised if txn failed in _i2c_master_slv4_txn"


class AK09916:
    def __init__(self, comm: ICM20948Communicator, registers: Registers):
        """The AK09916 magnetometer built into the ICM20948."""
        self.comm = comm
        self.registers = registers

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
        try:
            who_am_i_1 = self._read_mag(self.registers.AK09916_REG_WIA1)
            who_am_i_2 = self._read_mag(self.registers.AK09916_REG_WIA2)
        except TXNFailedError:
            return False

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
            raise TXNFailedError()

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

    def setup(self):
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
