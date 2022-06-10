import os
import signal
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ICM20948.ICM20948ZMQ import ICM20948ZMQ
from IMUConfig import IMUConfig
from msb_config.zeromq import open_zmq_pub_socket

# TODO
# - add argument parser to overwrite configuration
#   - add output_div
#   - add filters
#   - 

def signal_handler(sig, frame):
    print('msb_imu.py exit')
    sys.exit(0)

def msb_imu(imu_config: IMUConfig):
    signal.signal(signal.SIGINT, signal_handler)
    imu = ICM20948ZMQ(
        zmq_pub_socket=open_zmq_pub_socket(imu_config.zmq["xsub_connect_string"]),
        verbose=False,
    )
    imu.begin()

    signal.pause()

if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
