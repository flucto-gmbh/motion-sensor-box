import signal
import sys

from msb.imu.icm20948.icm20948 import ICM20948
from msb.imu.config import IMUConf
from msb.config import load_config
from msb.zmq_base.Publisher import Publisher, get_default_publisher


# this might not be necessary if ICM20948 is used as context manager
def signal_handler(sig, frame):
    print("msb_imu.py exit")
    sys.exit(0)


class IMUService:
    def __init__(self, config: IMUConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher
        self.icm20948 = ICM20948(config)

    def run(self):
        with self.icm20948:
            # signal.pause()
            while True:
                raw_data = self.icm20948.get_data()
                data = self.process_raw(raw_data)
                self.publisher.send(self.config.topic, data)

    def process_raw(self, raw) -> dict:
        data = self.align_axes_with_msb_coordinate_system(raw)
        return data

    @staticmethod
    def align_axes_with_msb_coordinate_system(data):
        # flip x and y axis for accelerometer and gyroscope
        data["acc_x"] *= -1
        data["acc_y"] *= -1
        data["rot_x"] *= -1
        data["rot_y"] *= -1

        # flip x and z axis for magnetometer
        data["mag_x"] *= -1
        data["mag_z"] *= -1

        return data


def main():
    signal.signal(signal.SIGINT, signal_handler)
    imu_config = load_config(IMUConf(), "imu")
    publisher = get_default_publisher()
    imu = IMUService(imu_config, publisher)
    imu.run()
