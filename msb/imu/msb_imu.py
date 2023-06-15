import json
import os
import signal
import sys
import time
from math import atan2, sqrt, pi, sin, cos
import numpy as np

from msb.config import load_config
from msb.imu.config import IMUConf
from msb.imu.icm20948.icm20948 import ICM20948
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
            last_t = time.time()
            roll_c = 0
            pitch_c = 0
            alpha = 0.9
            # signal.pause()
            while True:
                raw_data = self.icm20948.get_data()
                data = self.process_raw(raw_data)
                dt = data['epoch'] - last_t
                last_t = data['epoch']
                # roll angle from acceleration
                roll_a = atan2(-data['acc_x'], sqrt(data['acc_y']**2 + data['acc_z']**2))*(180/pi)
                # pitch angle from acceleration
                pitch_a = atan2(data['acc_y'], sqrt(data['acc_x']**2 + data['acc_z']**2))*(180/pi)
                # combined pitch angle
                pitch_c = (pitch_c + data['rot_x'] * dt) * alpha + (1-alpha) * pitch_a
                data['pitch'] = pitch_c
                roll_c = (roll_c + data['rot_y'] * dt) * alpha + (1-alpha) * roll_a
                data['roll'] = roll_c
                # this is probably not correct
                mag_mag = sqrt(data['mag_x'] ** 2 + data['mag_y'] ** 2 + data['mag_z'])
                data['mag_x'] = data['mag_x'] / mag_mag
                data['mag_y'] = data['mag_y'] / mag_mag
                data['mag_z'] = data['mag_z'] / mag_mag
                by = data['mag_y']*cos(roll_a*(pi/180)) + data['mag_z']*sin(roll_a*(pi/180))
                bx = data['mag_x']*cos(pitch_a*(pi/180)) + sin(pitch_a*(pi/180))*sin(roll_a*(pi/180))+data['mag_z']*cos(roll_a*(pi/180))
                yaw = atan2(-by, bx)
                data['yaw'] = yaw*(180/pi)

                self.publisher.send(self.config.topic, data)

    def process_raw(self, raw) -> dict:
        data = self.align_axes_with_msb_coordinate_system(raw)
        data = self.apply_calibration(data)
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

    def apply_calibration(self, data):
        data["rot_x"] -= self.calibration["rot_x_off"]
        data["rot_y"] -= self.calibration["rot_y_off"]
        data["rot_z"] -= self.calibration["rot_z_off"]
        return data


def main():
    signal.signal(signal.SIGINT, signal_handler)
    imu_config = load_config(IMUConf(), "imu")
    publisher = get_default_publisher()
    imu = IMUService(imu_config, publisher)
    imu.run()
