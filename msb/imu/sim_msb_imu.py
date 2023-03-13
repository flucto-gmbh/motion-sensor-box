from datetime import datetime, timezone
from math import cos, pi, sin
import os
import pickle
import signal
import sys
import time
import uptime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from IMUConfig import IMUConfig
from msb_config.zeromq import open_zmq_pub_socket

IMU_TOPIC=b'imu'

class IMU:

    """ICM-20948

    : param address: I2C address to use for the motion sensor.
                     The sensor has two different possible addresses (0x68 and 0x69)
                     depending on wether AD0 is high (0x69) or low (0x68)
    : param i2c_bus: if an I2C bus has already been initiated somewehere else,
                     use this parameter to pass the bus object to the object.
    : return:        ICM20938 object
    : rtype:         Object
    """

    device_name = "ICM20948_SIM"
    _data_generator_process = None
    _delta_t = 0.2

    _acceleration_x_raw = _acceleration_y_raw = _acceleration_z_raw = 0
    _gyroscope_x_raw = _gyroscope_y_raw = _gyroscope_z_raw = 0
    _mag_x_raw = _mag_y_raw = _mag_z_raw = _mag_stat_1 = _mag_stat_2 = 0
    _temp_raw = 0
    _time = 0  # holds the time stamp at which the last sensor data was retrieved
    _uptime = (
        0  # holds the uptime at which the last sensor data was retrieved since boot
    )
    _verbose = False

    def __init__(self):
        pass

    def __del__(self):
        pass

    def _update_data(self):

        """
        this funciton is regularly called by the data_generator_process to
        provide updated values of the simulated sensor
        """

        # logging.debug("updating data")
        self._time = time.time()
        self._uptime = uptime.uptime()
        self._acceleration_x_raw = (
            self._acceleration_y_raw
        ) = self._acceleration_z_raw = sin(self._time * 2 * pi)
        self._gyroscope_x_raw = self._gyroscope_y_raw = self._gyroscope_z_raw = cos(
            self._time * 2 * pi
        )
        self._mag_x_raw = self._mag_y_raw = self._mag_z_raw = -1 * sin(
            self._time * 2 * pi
        )
        self._temp_raw = -1 * cos(self._time * 2 * pi * 0.0001)

    def begin(self):
        pass

    @property
    def data(self):
        self._update_data()

        return [
            datetime.fromtimestamp(self._time, tz=timezone.utc),
            self._time,
            self._uptime,
            self._acceleration_x_raw,
            self._acceleration_y_raw,
            self._acceleration_z_raw,
            self._gyroscope_x_raw,
            self._gyroscope_y_raw,
            self._gyroscope_z_raw,
            self._mag_x_raw,
            self._mag_y_raw,
            self._mag_z_raw,
            self._temp_raw,
        ]


def signal_handler(sig, frame):
    print("sim_msb_imu.py exit")
    sys.exit(0)


def msb_imu(imu_config: IMUConfig):
    signal.signal(signal.SIGINT, signal_handler)
    imu = IMU()
    zmq_pub_socket = open_zmq_pub_socket(imu_config.zmq["xsub_connect_string"])
    try:
        while True:
            zmq_pub_socket.send_multipart(
                [
                    IMU_TOPIC,  # topic
                    pickle.dumps((d := imu.data)),  # serialize the payload
                ]
            )
            if imu_config.print_stdout:
                print(d)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("msb_imu bye")
        sys.exit(0)
    except Exception as e:
        print(f"caught an unexpected Exception: {e}")
        sys.exit(-1)


if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
