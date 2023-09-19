import json
import os
import signal
import sys
from msb.config import load_config
from msb.imu.config import IMUConf
from msb.imu.icm20948.icm20948 import ICM20948
from msb.network import Publisher, get_publisher


# this might not be necessary if ICM20948 is used as context manager
def signal_handler(sig, frame):
    print("msb_imu.py exit")
    sys.exit(0)


class IMUService:
    """
    Reads data from the IMU and publishes to the provided interface.

    Parameters
    ----------
    config : IMUConf
        Configuration dataclass
    publisher : Publisher
        Publisher interface
    """

    def __init__(self, config: IMUConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher
        self.icm20948 = ICM20948(config)

        conf_dir = os.environ["MSB_CONFIG_DIR"]
        imu_calibration_subpath = "msb/calibration/imu.json"
        imu_calibration_file = os.path.join(conf_dir, imu_calibration_subpath)
        try:
            with open(imu_calibration_file) as calib_file:
                calibration = json.load(calib_file)
        except FileNotFoundError:
            calibration = {"rot_x_off": 0.0, "rot_y_off": 0.0, "rot_z_off": 0.0}
        self.calibration = calibration

    def run(self):
        with self.icm20948:
            while True:
                raw_data = self.icm20948.get_data()
                data = self._process_raw(raw_data)
                self.publisher.send(self.config.topic, data)

    def _process_raw(self, raw) -> dict:
        data = self._align_axes_with_msb_coordinate_system(raw)
        data = self._apply_calibration(data)
        return data

    @staticmethod
    def _align_axes_with_msb_coordinate_system(data):
        # flip x and y axis for accelerometer and gyroscope
        data["acc_x"] *= -1
        data["acc_y"] *= -1
        data["rot_x"] *= -1
        data["rot_y"] *= -1

        # flip x and z axis for magnetometer
        data["mag_x"] *= -1
        data["mag_z"] *= -1

        return data

    def _apply_calibration(self, data):
        data["rot_x"] -= self.calibration["rot_x_off"]
        data["rot_y"] -= self.calibration["rot_y_off"]
        data["rot_z"] -= self.calibration["rot_z_off"]
        return data


def main():
    signal.signal(signal.SIGINT, signal_handler)
    imu_config = load_config(IMUConf(), "imu")
    publisher = get_publisher("zmq")
    imu = IMUService(imu_config, publisher)
    imu.run()
