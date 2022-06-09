import os
import signal
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ICM20948.ICM20948ZMQ import ICM20948ZMQ
from IMUConfig import IMUConfig
from msb_config.zeromq import open_zmq_pub_socket

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def msb_imu(imu_config: IMUConfig):
    signal.signal(signal.SIGINT, signal_handler)
    imu = ICM20948ZMQ(
        zmq_pub_socket=open_zmq_pub_socket(imu_config.zmq["xsub_connect_string"]),
        verbose=True,
    )
    imu.begin()

    signal.pause()

if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
