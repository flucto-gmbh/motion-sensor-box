import json
import os
import signal
import sys
import time
from math import atan2, sqrt, pi

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
            #current_t = 0
            #dt = 0
            #roll_g = 0
            #pitch_g = 0
            #roll_a = 0
            #pitch_a = 0
            roll_c = 0
            pitch_c = 0
            alpha = 0.9
            # signal.pause()
            while True:
                raw_data = self.icm20948.get_data()
                data = self.process_raw(raw_data)
                acc_x = data['acc_x']
                acc_y = data['acc_y']
                acc_z = data['acc_z']
                rot_x = data["rot_x"]
                rot_y = data["rot_y"]
                rot_z = data["rot_z"]
                dt = data['epoch'] - last_t
                last_t = data['epoch']
                #roll_g += (data['rot_y'] * dt)
                #pitch_g += (data['rot_x'] * dt)
                # roll 
                roll_a = atan2(acc_x, acc_z)*(180/pi)
                # pitch
                pitch_a = atan2(-1*acc_y, sqrt(acc_x**2 + acc_z**2))*(180/pi)

                pitch_c = (pitch_c + rot_x * dt) * alpha + (1-alpha) * pitch_a
                data['pitch_c'] = pitch_c
                roll_c = (roll_c + rot_y * dt) * alpha + (1-alpha) * roll_a
                data['roll_c'] = roll_c
                data['pitch_a'] = pitch_a
                #data['pitch_g'] = pitch_g
                data['roll_a'] = roll_a
                #data['roll_g'] = roll_g
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
