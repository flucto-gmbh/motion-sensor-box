import signal
import sys

from msb.imu.icm20948.icm20948 import ICM20948
from msb.imu.icm20948.registers import Register
from msb.imu.icm20948.settings import Settings
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
        self.icm20948 = ICM20948(config, Register(), Settings())

    def run(self):
        with self.icm20948:
            # signal.pause()
            while True:
                raw_data = self.icm20948.get_data()
                data = self.process_raw(raw_data)
                self.publisher.send(self.config.topic, data)


    def process_raw(self, raw) -> dict:
        # TODO or should this happen in the ICM20948
        # OR should we create a class IMU that encapsulates the ICM20948 and which is then used as the only Interface by the IMUService
        # process data
        # e.g. align axes with msb axes
        return raw


def main():
    signal.signal(signal.SIGINT, signal_handler)
    imu_config = load_config(IMUConf(), "imu")
    publisher = get_default_publisher()
    imu = IMUService(imu_config, publisher)
    imu.run()
