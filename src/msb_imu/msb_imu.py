import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from ICM20948 import ICM20948 as IMU
from IMUConfig import IMUConfig

def msb_imu(imu_config : IMUConfig):
    # 1. validate received config
    # 2. instanciate an object of type IMU
    # 3. bring up sensor
    # 4. subscribe to zmq
    # 5. enter endless loop and consume data from sensor
    pass

if __name__ == "__main__":
    imu_config = IMUConfig()
    msb_imu(imu_config)
