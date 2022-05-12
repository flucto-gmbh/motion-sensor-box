from collections.abc import Sequence

from driver import (
    BaudRate,
    ParityBit,
    AirSpeed,
    PacketLen,
    TransmitPower,
    WORMode,
    WORPeriod,
)


def parse_command_byte(byte_val: int) -> str:
    """Command byte"""
    if byte_val == 0xC2:
        return "Configure temporary registers"
    elif byte_val == 0xC1:
        return "Answer / Read registers"
    elif byte_val == 0xC0:
        return "Configure registers"
    else:
        raise ValueError(f"Unknown register value {byte_val}")


def parse_start_byte(byte_val: int) -> int:
    """Start register"""
    assert 0 <= byte_val < 8
    return byte_val


def parse_data_length_byte(byte_val: int) -> int:
    """Length of data"""
    assert 0 <= byte_val <= 9
    return byte_val


def parse_reg_00h_and_01h_bytes(byte_val_3: int, byte_val_4: int) -> int:
    """Module address"""
    assert 0 <= byte_val_3 < 256
    assert 0 <= byte_val_4 < 256
    # module address has 16 bit = 2 byte
    # byte_val_3 are high bits of module address
    # byte_val_4 are low bits of module address
    # shifting byte_val_3 8 bits to the left makes them the high bits of a 16 bit number
    # these high bits can then be logically or'ed with the lower bits
    return byte_val_3 << 8 | byte_val_4


def parse_reg_02h_byte(byte_val: int) -> int:
    """Net ID"""
    assert 0 <= byte_val < 256
    return byte_val


def parse_reg_03h_byte(byte_val: int) -> dict:
    """baud rate(7-5), parity bit(4-3), wireless air speed / bps (2-0)"""
    assert 0 <= byte_val < 256

    baud_rate_mask = 0b11100000
    baud_rate_shift = 5
    parity_bit_mask = 0b00011000
    parity_bit_shift = 3
    air_speed_mask = 0b00000111
    air_speed_shift = 0

    baud_rate_val = (byte_val & baud_rate_mask) >> baud_rate_shift
    parity_bit_val = (byte_val & parity_bit_mask) >> parity_bit_shift
    air_speed_val = (byte_val & air_speed_mask) >> air_speed_shift

    baud_rate = BaudRate(baud_rate_val)

    parity_bit = ParityBit(parity_bit_val)

    air_speed = AirSpeed(air_speed_val)

    return {"baud_rate": baud_rate, "parity_bit": parity_bit, "air_speed": air_speed}


def parse_reg_04h_byte(byte_val: int) -> dict:
    """
    packet_len(7-6), enable_ambient_noise(5), transmit_power(1-0)

    (reserved / unused: (4-2))
    """
    packet_len_mask = 0b11000000
    packet_len_shift = 6
    ambient_noise_mask = 0b00100000
    ambient_noise_shift = 5
    reserved_mask = 0b00011100
    reserved_shift = 2
    transmit_power_mask = 0b00000011
    transmit_power_shift = 0

    packet_len_val = (byte_val & packet_len_mask) >> packet_len_shift
    ambient_noise_val = (byte_val & ambient_noise_mask) >> ambient_noise_shift
    reserved_val = (byte_val & reserved_mask) >> reserved_shift
    transmit_power_val = (byte_val & transmit_power_mask) >> transmit_power_shift

    assert reserved_val == 0
    del reserved_val

    packet_len = PacketLen(packet_len_val)
    enable_ambient_noise = bool(ambient_noise_val)
    transmit_power = TransmitPower(transmit_power_val)

    return {
        "packet_len": packet_len,
        "enable_ambient_noise": enable_ambient_noise,
        "transmit_power": transmit_power,
    }


def parse_reg_05h_byte(byte_val: int) -> int:
    """
    Channel control (CH) 0-83. 84 channels in total

    850.125 + CH *1MHz. Default 868.125MHz(SX1262),
    410.125 + CH *1MHz. Default 433.125MHz(SX1268)
    """
    assert 0 <= byte_val <= 83
    return byte_val


def parse_reg_06h_byte(byte_val: int) -> dict:
    """
    enable_RSSI_byte(7), enable_point_to_point_mode(6), enable_relay_function(5), enable_LBT(4), WOR_mode(3), WOR_period (2-0)
    """
    RSSI_byte_mask = 0b10000000
    RSSI_byte_shift = 7
    point_to_point_mode_mask = 0b01000000
    point_to_point_mode_shift = 6
    relay_function_mask = 0b00100000
    relay_function_shift = 5
    LBT_mask = 0b00010000
    LBT_shift = 4
    WOR_mode_mask = 0b00001000
    WOR_mode_shift = 3
    WOR_period_mask = 0b00000111
    WOR_period_shift = 0

    RSSI_byte_value = (byte_val & RSSI_byte_mask) >> RSSI_byte_shift
    point_to_point_mode_value = (
        byte_val & point_to_point_mode_mask
    ) >> point_to_point_mode_shift
    relay_function_value = (byte_val & relay_function_mask) >> relay_function_shift
    LBT_value = (byte_val & LBT_mask) >> LBT_shift
    WOR_mode_value = (byte_val & WOR_mode_mask) >> WOR_mode_shift
    WOR_period_value = (byte_val & WOR_period_mask) >> WOR_period_shift

    enable_RSSI_byte = bool(RSSI_byte_value)
    enable_point_to_point_mode = bool(point_to_point_mode_value)
    enable_relay_function = bool(relay_function_value)
    enable_LBT = bool(LBT_value)
    WOR_mode = WORMode(WOR_mode_value)
    WOR_period = WORPeriod(WOR_period_value)

    return {
        "enable_RSSI_byte": enable_RSSI_byte,
        "enable_point_to_point_mode": enable_point_to_point_mode,
        "enable_relay_function": enable_relay_function,
        "enable_LBT": enable_LBT,
        "WOR_mode": WOR_mode,
        "WOR_period": WOR_period,
    }


def parse_07h_and_08h_bytes(byte_val_10: int, byte_val_11: int) -> int:
    """Key"""
    assert 0 <= byte_val_10 < 256
    assert 0 <= byte_val_11 < 256
    # key has 16 bit = 2 byte
    # byte_val_10 are high bits of module address
    # byte_val_11 are low bits of module address
    # shifting byte_val_10 8 bits to the left makes them the high bits of a 16 bit number
    # these high bits can then be logically or'ed with the lower bits
    return byte_val_10 << 8 | byte_val_11


def command_to_dict(command_bytes: Sequence[int]) -> dict:
    assert len(command_bytes) == 12

    command_dict = {}
    command_dict["command"] = parse_command_byte(command_bytes[0])
    command_dict["start_register"] = parse_start_byte(command_bytes[1])
    command_dict["data_length"] = parse_data_length_byte(command_bytes[2])
    command_dict["module_address"] = parse_reg_00h_and_01h_bytes(
        command_bytes[3], command_bytes[4]
    )
    command_dict["net_id"] = parse_reg_02h_byte(command_bytes[5])
    command_dict.update(parse_reg_03h_byte(command_bytes[6]))
    command_dict.update(parse_reg_04h_byte(command_bytes[7]))
    command_dict["channel"] = parse_reg_05h_byte(command_bytes[8])
    command_dict.update(parse_reg_06h_byte(command_bytes[9]))
    command_dict["key"] = parse_07h_and_08h_bytes(command_bytes[10], command_bytes[11])

    return command_dict


if __name__ == "__main__":

    reg_array = bytes(
        [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x17, 0x00, 0x00, 0x00]
    )

    command_dict = command_to_dict(reg_array)

    pass
# f"{194:b}"
#'11000010'
# f"{194:x}"
#'c2'
# f"{194:#x}"
#'0xc2'
