#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import RPi.GPIO as GPIO
import logging
import serial
import time


from enum import Enum

try:
    import RPi.GPIO as GPIO
except ImportError:
    try:
        import Mock.GPIO as GPIO
    except ImportError:
        GPIO = None  # will not run but import

# https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT
#
# header  start number REG0 REG1 REG2 REG3 REG4 REG5 REG6 REG7 REG8
# 0xC2    0x00  0x09   0x01 0x02 0x03 0x62 0x00 0x12 0x03 0x00 0x00
#
# 0xC2 is command header
# 0x00 is the start register you want to set
# 0x09 is the 9 registers you want to set
#
# REG0...REG8,total 9 registers parameter,REG0 is ADDH register,REG8 is CRYPT_L register
#
# REG5 is the channel register,SX1268 is from 410MHz to 483MHz,SX1262 is from 850MHz to 930MHz
#
# the calculation is like that :
# 433MHz = 410MHz + REG5(0x17,default value)
# 470MHz = 410MHz + REG5(0x3C)
# 868MHz = 850MHz + REG5(0x12,default value)
# 915MHz = 850MHz + REG5(0x41)
#
# 433MHz
# CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x17\x03\x00\x00']
# RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x17\x03\x00\x00']
#
# 470MHz
# CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x3C\x03\x00\x00']
# RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x3C\x03\x00\x00']
#
# 868MHz
# CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']
# RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x12\x03\x00\x00']
#
# 915MHz
# CFG_REG = [b'\xC2\x00\x09\x01\x02\x03\x62\x00\x41\x03\x00\x00']
# RET_REG = [b'\xC1\x00\x09\x01\x02\x03\x62\x00\x41\x03\x00\x00']


CFG_HEADER = 0xC2  # Header to use if we want to set registers.
RET_HEADER = 0xC1  # Header of the answer after registers have been set. Use it to check if set was successful.
START_REG = 0x00  # begin with the first register
NUM_REG = 0x09  # set 9 registers


class BaudRate(Enum):
    BR_1200 = 0b000
    BR_2400 = 0b001
    BR_4800 = 0b010
    BR_9600 = 0b011
    BR_19200 = 0b100
    BR_38400 = 0b101
    BR_57600 = 0b110
    BR_115200 = 0b111


class ParityBit(Enum):
    PB_8N1 = 0b00
    PB_8O1 = 0b01
    PB_8E1 = 0b10


class AirSpeed(Enum):
    AS_0_3K = 0b000
    AS_1_2K = 0b001
    AS_2_4K = 0b010
    AS_4_8K = 0b011
    AS_9_6K = 0b100
    AS_19_2K = 0b101
    AS_38_4K = 0b110
    AS_62_5K = 0b111


class PacketLen(Enum):
    PL_240B = 0b00
    PL_128B = 0b01
    PL_64B = 0b10
    PL_32B = 0b11


class TransmitPower(Enum):
    TP_22dBm = 0b00
    TP_17dBm = 0b01
    TP_12dBm = 0b10
    TP_10dBm = 0b11


class WORMode(Enum):
    WOR_transmit = 0b0
    WOR_listen = 0b1


class WORPeriod(Enum):
    WP_500ms = 0b000
    WP_1000ms = 0b001
    WP_1500ms = 0b010
    WP_2000ms = 0b011
    WP_2500ms = 0b100
    WP_3000ms = 0b101
    WP_3500ms = 0b110
    WP_4000ms = 0b111


def serialize_config(config):
    command = [0] * 12

    # set header
    command[0] = CFG_HEADER
    command[1] = START_REG
    command[2] = NUM_REG

    # set registers
    command[3] = make_reg_00h_byte(config["module_address"])
    command[4] = make_reg_01h_byte(config["module_address"])
    command[5] = make_reg_02h_byte(config["net_id"])
    command[6] = make_reg_03h_byte(
        config["baud_rate"], config["parity_bit"], config["air_speed"]
    )
    command[7] = make_reg_04h_byte(
        config["packet_len"], config["enable_ambient_noise"], config["transmit_power"]
    )
    command[8] = make_reg_05h_byte(config["channel"])
    command[9] = make_reg_06h_byte(
        config["enable_RSSI_byte"],
        config["enable_point_to_point_mode"],
        config["enable_relay_function"],
        config["enable_LBT"],
        config["WOR_mode"],
        config["WOR_period"],
    )
    command[10] = make_reg_07h_byte(config["key"])
    command[11] = make_reg_08h_byte(config["key"])

    return bytes(command)


def make_reg_00h_byte(module_address: int) -> int:
    """
    Make the high bits of the module address.

    Note that when module address is 0xFFFF (=65535), it works as broadcasting and listening address
    and LoRa module doesn't filter address anymore.

    from node_100_main.py:
    under the same frequence,if set 65535,the node can receive
    messages from another node of address is 0 to 65534 and similarly,
    the address 0 to 65534 of node can receive messages while
    the another note of address is 65535 sends.
    otherwise two node must be same the address and frequence

    :param module_address: The address of the module.
    :return: High bits of address.
    """

    assert 0 <= module_address < 2 ** 16
    address_str = format(module_address, "016b")
    assert len(address_str) == 16
    return int(address_str[:8], 2)


def make_reg_01h_byte(module_address: int) -> int:
    """
    Make the low bits of the module address.

    Note that when module address is 0xFFFF (=65535), it works as broadcasting and listening address
    and LoRa module doesn't filter address anymore.

    from node_100_main.py:
    under the same frequence,if set 65535,the node can receive
    messages from another node of address is 0 to 65534 and similarly,
    the address 0 to 65534 of node can receive messages while
    the another note of address is 65535 sends.
    otherwise two node must be same the address and frequence

    :param module_address: The address of the module.
    :return: Low bits of address.
    """

    assert 0 <= module_address < 2 ** 16
    address_str = format(module_address, "016b")
    assert len(address_str) == 16
    return int(address_str[8:], 2)


def make_reg_02h_byte(net_id: int) -> int:
    """
    Make (check) Network ID.

    net_id is used to distinguish networks.
    If you want communication between two modules, you need to set their net_id to same ID.

    :param net_id: The network ID.
    :return: The network ID.
    """

    if 0 <= net_id <= 256 and type(net_id) == int:
        return net_id
    else:
        raise ValueError(f"net_id must be an int between 0 and 256, but was {net_id}.")


def make_reg_03h_byte(
    baud_rate: BaudRate, parity_bit: ParityBit, air_speed: AirSpeed
) -> int:
    """
    Make the byte for REG0.

    baud rate(7-5), parity bit(4-3), wireless air speed / bps (2-0)

    :param baud_rate: The baud rate for the serial connection. Must be equal on the Pi's side and on the hat's side.
    Possible values are: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
    :param parity_bit: The parity bit. Possible values are: '8N1', '8O1', '8E1'
    :param air_speed: The air speed. Higher the speed, smaller the latency and shorter the communicating distance.
    Possible values are: '0.3K', '1.2K', '2.4K', '4.8K', '9.6K', '19.2K', '38.4K', '62.5K'
    :return: The value for REG0.
    """

    baud_rate_shift = 5
    parity_bit_shift = 3

    return (
        (baud_rate.value << baud_rate_shift)
        | (parity_bit.value << parity_bit_shift)
        | air_speed.value
    )


def make_reg_04h_byte(
    packet_len: PacketLen, enable_ambient_noise: bool, transmit_power: TransmitPower
) -> int:
    """
    Make the byte for REG1.

    packet_len(7-6), enable_ambient_noise(5), transmit_power(1-0) (reserved / unused: (4-2))

    :param packet_len: The size of packages in bytes. If size is exceeded messages are split.
    Possible values are: 240, 128, 64, 32
    :param enable_ambient_noise: After enabling, you can send command 0xC0 0xC1 0xC2 0xC3 to read register
    in Transmit Mode or WOR Mode.
    :param transmit_power: The transmit power. Possible values are: '22dBm', '17dBm', '12dBm', '10dBm'
    :return: The value for REG1.
    """

    packet_len_shift = 6
    ambient_noise_shift = 5

    return (
        (packet_len.value << packet_len_shift)
        | (int(enable_ambient_noise) << ambient_noise_shift)
        | transmit_power.value
    )


def make_reg_05h_byte(channel: int) -> int:
    """
    Make the byte for REG2 (channel)

    Channel control (CH) 0-83. 84 channels in total

    18 default for SX1262, 23 default for SX1268

    850.125 + CH *1MHz. Default 868.125MHz(SX1262),
    410.125 + CH *1MHz. Default 433.125MHz(SX1268)

    :param channel: The channel.
    :return: The channel / value for REG2.
    """

    if 0 <= channel <= 83:
        return channel
    else:
        raise RuntimeError(
            f"Invalid channel, channel must be between 0-83, but was {channel}."
        )


def make_reg_06h_byte(
    enable_RSSI_byte: bool,
    enable_point_to_point_mode: bool,
    enable_relay_function: bool,
    enable_LBT: bool,
    WOR_mode: WORMode,
    WOR_period: WORPeriod,
) -> int:
    """
    Make the byte for REG3.

    enable_RSSI_byte(7), enable_point_to_point_mode(6), enable_relay_function(5), enable_LBT(4), WOR_mode(3), WOR_period (2-0)

    :param enable_RSSI_byte: After enabling, data sent to serial port is added with a RSSI byte after receiving.
    :param enable_point_to_point_mode: When point to point transmitting, module will recognize the first three byte as
    Address High + Address Low + Channel and wireless transmit it. Default: False = transparent mode
    :param enable_relay_function: If target address is not module itself, module will forward data.
    To avoid data echo, we recommend you to use this function in point to point mode,
    that is target address is different with source address.
    :param enable_LBT: Module will listen before transmit wireless data.
    This function can be used to avoid interference, however, it also clause longer latency.
    The MAX LBT time is 2s, after 2s, data is forced to transmit.
    :param WOR_mode: (Wake over Radio?). This setting only work for Mode 1.
    Receiver waits for 1000ms after receive wireless data and forward,and then enter WOR mode again.
    User can send data to serial port and forward via wireless network during this interval.
    Every serial byte will refresh this interval time (1000ms).
    You much send the first byte in 1000ms.
    0 -> WOR transmit (default) Module is enabled to receive/transmit, and wakeup code is added to transmitted data.
    1 -> WOR Sender Module is disable to send data. Module is working in WOR listen mode. Consumption is reduced
    :param WOR_period: This setting only work for Mode 1; Longer the Period time of WOR listen,
    lower the average consumption, however, longer the latency The settings of receiver and sender must be same.
    Possible values are: 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000
    :return: The value for REG3.
    """

    RSSI_byte_shift = 7
    point_to_point_mode_shift = 6
    relay_function_shift = 5
    LBT_shift = 4
    WOR_mode_shift = 3

    return (
        (int(enable_RSSI_byte) << RSSI_byte_shift)
        | (int(enable_point_to_point_mode) << point_to_point_mode_shift)
        | (int(enable_relay_function) << relay_function_shift)
        | (int(enable_LBT) << LBT_shift)
        | (WOR_mode.value << WOR_mode_shift)
        | WOR_period.value
    )


def make_reg_07h_byte(key: int) -> int:
    """
    Make high bits of key.

    This key is used to encrypting to avoid wireless data intercepted by similar modules;
    This key is work as calculation factor when module is encrypting wireless data.

    :param key: The encryption key. (0-2^16-1)
    :return: The high bits of the key.
    """
    assert 0 <= key < 2 ** 16
    key_str = format(key, "016b")
    assert len(key_str) == 16
    return int(key_str[:8], 2)


def make_reg_08h_byte(key: int) -> int:
    """
    Make low bits of key.

    This key is used to encrypting to avoid wireless data intercepted by similar modules;
    This key is work as calculation factor when module is encrypting wireless data.

    :param key: The encryption key. (0-2^16-1)
    :return: The high bits of the key.
    """
    assert 0 <= key < 2 ** 16
    key_str = format(key, "016b")
    assert len(key_str) == 16
    return int(key_str[8:], 2)


class LoRaHatDriver:

    M0 = 22
    M1 = 27

    def __init__(self, config):
        self.config = config
        self.module_address = config["module_address"]
        self.net_id = config["net_id"]
        self.baud_rate = config["baud_rate"]
        self.parity_bit = config["parity_bit"]
        self.air_speed = config["air_speed"]
        self.packet_len = config["packet_len"]
        self.enable_ambient_noise = config["enable_ambient_noise"]
        self.transmit_power = config["transmit_power"]
        self.channel = config["channel"]
        self.enable_RSSI_byte = config["enable_RSSI_byte"]
        self.enable_point_to_point_mode = config["enable_point_to_point_mode"]
        self.enable_relay_function = config["enable_relay_function"]
        self.enable_LBT = config["enable_LBT"]
        self.WOR_mode = config["WOR_mode"]
        self.WOR_period = config["WOR_period"]
        self.key = config["key"]

        try:
            self.target_address = config["target_address"]
        except KeyError:
            logging.warning(
                "target_address was not supplied in config. "
                "Will not be able to send messages in point to point mode."
            )
            self.target_address = None

        GPIO.setmode(GPIO.BCM)  # https://raspberrypi.stackexchange.com/a/12967
        GPIO.setwarnings(False)  # suppress channel already in use warning
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)

        # create serial object but do not open file yet
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyS0"
        self.ser.baudrate = 9600

    def __enter__(self):
        self.apply_config()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ser.close()
        GPIO.cleanup()
        logging.info("Successfully shut down.")

    def apply_config(self):

        command_bytes = serialize_config(self.config)
        answer_bytes = bytes([RET_HEADER]) + command_bytes[1:]

        # enter configuration mode
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(1)

        self.ser.open()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        logging.debug(f"serial settings: {self.ser.get_settings()}")
        logging.debug(f"serial rts: {self.ser.rts}")
        logging.debug(f"serial dtr: {self.ser.dtr}")

        if self.ser.is_open:
            logging.info("Serial port is open, trying to write configuration.")
            self.ser.write(command_bytes)
            wait_counter = 0
            while True:
                if self.ser.in_waiting > 0:  # there is something to read
                    time.sleep(0.1)
                    read_buffer = self.ser.read(self.ser.in_waiting)
                    if read_buffer == answer_bytes:
                        logging.info("Successfully applied configuration.")
                        # enter operation mode
                        GPIO.output(self.M1, GPIO.LOW)
                        time.sleep(0.01)
                        break
                elif wait_counter >= 100:
                    logging.error("Could not apply configuration. Aborting.")
                    break
                else:
                    time.sleep(0.1)
                    wait_counter += 1

        # afterwards set the baudrate to the just configured
        if self.baud_rate != BaudRate.BR_9600:
            self.ser.baudrate = int(self.baud_rate.name.split("_")[1])

    def send(self, message: bytes):
        # message = message + "\r\n".encode("utf-8")

        if self.enable_point_to_point_mode:
            # point to point -> requires prepended target address
            # When point to point transmitting, module will recognize the
            # first three byte as Address High + Address Low + Channel. and wireless transmit it
            if self.target_address is None:
                raise RuntimeError(
                    "When sending in point to point transmitting mode "
                    "target_address has to be set in config."
                )
            address_header = bytearray(3)
            address_header[0] = make_reg_00h_byte(self.target_address)
            address_header[1] = make_reg_01h_byte(self.target_address)
            address_header[2] = make_reg_05h_byte(self.channel)

            message = bytes(address_header) + message

        self.ser.write(message)

    def receive(self) -> bytes:
        if self.module_address != 0xFFFF and self.enable_point_to_point_mode:
            logging.warning(
                "Module address is not set to 0xFFFF (broadcast address) and point to point mode is enabled. "
                "Will only receive messages from nodes with the same module address."
            )
        while True:
            if self.ser.in_waiting > 0:  # there is something to read
                time.sleep(0.1)
                read_buffer = self.ser.read(self.ser.in_waiting)
                return read_buffer

    def read_config_from_hat(self):
        pass

    def clean_up(self):
        self.ser.close()
        GPIO.cleanup()
