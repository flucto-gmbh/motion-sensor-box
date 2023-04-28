import signal
import sys


from msb.imu.ICM20948.ICM20948ZMQ import ICM20948ZMQ
from msb.imu.config import IMUConf
from msb.config import load_config
from msb.zmq_base.Publisher import Publisher, get_default_publisher


def signal_handler(sig, frame):
    print("msb_imu.py exit")
    sys.exit(0)


def msb_imu(config: IMUConf, publisher: Publisher):
    signal.signal(signal.SIGINT, signal_handler)

    imu = ICM20948ZMQ(config=config, publisher=publisher)
    imu.begin()
    signal.pause()


def main():
    imu_config = load_config(IMUConf(), "imu")
    publisher = get_default_publisher()
    msb_imu(imu_config, publisher)
