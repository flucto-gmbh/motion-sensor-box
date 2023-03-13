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
        output_data_div=imu_config.sample_rate_div,
        acc_filter=imu_config.acc_filter,
        gyr_filter=imu_config.gyr_filter,
        acc_sensitivity=imu_config.acc_sensitivity,
        gyr_sensitivity=imu_config.gyr_sensitivity,
        verbose=imu_config.verbose,
        print_stdout=imu_config.print_stdout,
        polling=imu_config.polling,
    )
    imu.begin()
    signal.pause()

if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
