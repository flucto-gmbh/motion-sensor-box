import math
import time

import numpy as np


class ExponentialFilter:

    """
    Implements a simple exponential filter of first order to denoise a signal
    """

    def __init__(self, gain: float = 0.5):
        self.gain = gain
        self.state = 0
        self._first = True

    def update(self, data):
        if self._first:
            self.state = data
            self._first = False
        else:
            self.state = self.gain * data + (1 - self.gain) * self.state
        return self.state


class ComplementaryFilter:

    """
    Implements a Complementary filter to estimate roll, pitch and yaw
    based on IMU data
    """

    def __init__(
        self,
        gain: float = 0.99,
        exp_gain: float = 0.1,
        rel_acceleration_limit: float = 0.1,
    ):
        self.last_timestamp = time.time()
        self.alpha = gain
        self.exp_gain = exp_gain
        self.rel_acceleration_limit = rel_acceleration_limit
        self.state = np.zeros(3, dtype=np.float64)
        self.acc_x_exp_filter = ExponentialFilter(gain=self.exp_gain)
        self.acc_y_exp_filter = ExponentialFilter(gain=self.exp_gain)
        self.acc_z_exp_filter = ExponentialFilter(gain=self.exp_gain)

    def update(self, data):
        epoch = data["epoch"]
        dt = epoch - self.last_timestamp
        self.last_timestamp = epoch

        acc_x, acc_y, acc_z = (
           self.acc_x_exp_filter.update(data["acc_x"]),
           self.acc_y_exp_filter.update(data["acc_y"]),
           self.acc_z_exp_filter.update(data["acc_z"]),
        )
        #acc_x, acc_y, acc_z = data["acc_x"], data["acc_y"], data["acc_z"]
        rot_x, rot_y, rot_z = data["rot_x"], data["rot_y"], data["rot_z"]
        mag_x, mag_y, mag_z = data["mag_x"], data["mag_y"], data["mag_z"]
        mag_acc = math.sqrt(
            acc_x**2 + acc_y**2 + acc_z**2
        )

        if (
            (1 - self.rel_acceleration_limit)
            < mag_acc
            < (1 + self.rel_acceleration_limit)
        ):
            # roll angle from acceleration
            roll_acc = math.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2))
            # pitch angle from acceleration
            pitch_acc = math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2))
        else:
            print(f"acceleration correction not available, magnitude acceleration: {mag_acc}")
            roll_acc = 0
            pitch_acc = 0

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
        yaw_mag = np.arctan2(-by, bx)

        # use gyro to update
        # roll
        self.state[0] = (self.state[0] + math.radians(rot_y * dt)) * self.alpha + (
            1 - self.alpha
        ) * roll_acc
        # pitch
        self.state[1] = (self.state[1] + math.radians(rot_x * dt)) * self.alpha + (
            1 - self.alpha
        ) * pitch_acc
        # yaw
        self.state[2] = (self.state[2] + math.radians(rot_z * dt)) * self.alpha + (
            1 - self.alpha
        ) * yaw_mag

        return {
            "epoch": epoch,
            "uptime": data["uptime"],
            "acc_x_f": acc_x,
            "acc_y_f": acc_y,
            "acc_z_f": acc_z,
            "roll": math.degrees(self.state[0]),
            "pitch": math.degrees(self.state[1]),
            "yaw": math.degrees(self.state[2]),
        }
