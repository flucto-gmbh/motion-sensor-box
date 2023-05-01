import json
import os
import signal
import sys
import time

# from ICM20948.ICM20948ZMQ import ICM20948ZMQ
from msb.imu.ICM20948.ICM20948ZMQ import ICM20948ZMQ
from msb.imu.config import IMUConfig
from msb.config.zeromq import open_zmq_pub_socket

# TODO
# - add polling option
# - add 

def signal_handler(sig, frame):
    print('imu_standalone.py exit')
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
    if not imu_config.polling:
        signal.pause()

if __name__ == "__main__":
    imu_config = IMUConfig()
    if imu_config.verbose:
        print(f"{json.dumps(imu_config.__dict__, indent=4)}")
    msb_imu(imu_config)
