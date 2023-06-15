import math
import time

import numpy as np


class ComplementaryFilter:
    def __init__(self, gain: float = 0.9):
        self.last_timestamp = time.time()
        self.alpha = gain
        self.state = np.zeros(3, dtype=np.float64)

    def update(self, data):
        epoch = data["epoch"]
        dt = epoch - self.last_timestamp
        self.last_timestamp = epoch

        acc_x, acc_y, acc_z = data["acc_x"], data["acc_y"], data["acc_z"]
        rot_x, rot_y, rot_z = data["rot_x"], data["rot_y"], data["rot_z"]
        mag_x, mag_y, mag_z = data["mag_x"], data["mag_y"], data["mag_z"]

        alpha = self.alpha

        # roll angle from acceleration
        roll_acc = np.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2))

        # pitch angle from acceleration
        pitch_acc = np.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2))

        # yaw angle from mag
        # TODO this is probably not correct
        mag_mag = math.sqrt(mag_x**2 + mag_y**2 + mag_z**2)
        mag_x = mag_x / mag_mag
        mag_y = mag_y / mag_mag
        mag_z = mag_z / mag_mag
        by = mag_y * math.cos(roll_acc) + mag_z * math.sin(roll_acc)
        bx = (
            mag_x * math.cos(pitch_acc)
            + math.sin(pitch_acc) * math.sin(roll_acc)
            + mag_z * math.cos(roll_acc)
        )
        yaw_mag = np.atan2(-by, bx)

        # use gyro to update
        # roll
        self.state[0] = (self.state[0] + math.radians(rot_y * dt)) * alpha + (
            1 - alpha
        ) * roll_acc
        # pitch
        self.state[1] = (self.state[1] + math.radians(rot_x * dt)) * alpha + (
            1 - alpha
        ) * pitch_acc
        # yaw
        self.state[2] = (self.state[2] + math.radians(rot_z * dt)) * alpha + (
            1 - alpha
        ) * yaw_mag

        return {
            "epoch": epoch,
            "uptime": data["uptime"],
            "roll": math.degrees(self.state[0]),
            "pitch": math.degrees(self.state[1]),
            "yaw": math.degrees(self.state[2]),
        }
