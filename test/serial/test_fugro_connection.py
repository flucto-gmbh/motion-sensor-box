import pytest

from msb.serial.publisher import SerialPublisher


def test_serial_packer():
    from msb.serial.publisher import serial_packer

    input_dict = {
        "timestamp": 1687411107.76184,
        "abs_pile_velocity": 0.010,
        "rel_pile_velocity": 0.020,
        "vessel_roll": 0.1,
        "vessel_pitch": 0.01,
        "vessel_yaw": 0.004,
        "pile_distance_travelled": 1.2,
    }
    expected_output = "1687411107.761840,0.010,0.020,0.100,0.010,0.004,1.200"

    output = serial_packer(input_dict)

    assert output == expected_output
