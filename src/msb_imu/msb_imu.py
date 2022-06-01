import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ICM20948.ICM20948ZMQ import ICM20948ZMQ
from IMUConfig import IMUConfig
from msb_config.zeromq import open_zmq_pub_socket


def msb_imu(imu_config: IMUConfig):
    # 1. validate received config
    # 2. instanciate an object of type IMU
    # 3. bring up sensor
    # 4. subscribe to zmq
    # 5. enter endless loop and consume data from sensor
    imu = ICM20948ZMQ(
        zmq_pub_socket=open_zmq_pub_socket(imu_config.zmq["xsub_connect_string"]),
        verbose=True,
    )
    imu.begin()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
