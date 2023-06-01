import json
import os
import subprocess
import sys
import time

import numpy as np
from tqdm import tqdm

sys.path.append("..")
from msb.zmq_base.Subscriber import Subscriber, get_default_subscriber


def get_gyro_measurement_data(subscriber: Subscriber, n_meas=100):
    measurements = np.empty((n_meas, 3))
    for i in tqdm(range(n_meas)):
        _, data = subscriber.receive()
        measurements[i] = [data["rot_x"], data["rot_y"], data["rot_z"]]
    return measurements


def calculate_gyro_offsets(measurements: np.array):
    means = np.round(measurements.mean(axis=0), decimals=1)
    return {"x": means[0], "y": means[1], "z": means[2]}


def save_calibration(gyro_offsets: dict):
    conf_dir = os.environ["MSB_CONFIG_DIR"]
    imu_calibration_subpath = "msb/calibration/imu.json"
    imu_calibration_file = os.path.join(conf_dir, imu_calibration_subpath)
    try:
        with open(imu_calibration_file, "rt") as cal_file:
            calibration = json.load(cal_file)
    except FileNotFoundError:
        calibration = {}

    calibration["rot_x_off"] = gyro_offsets["x"]
    calibration["rot_y_off"] = gyro_offsets["y"]
    calibration["rot_z_off"] = gyro_offsets["z"]

    os.makedirs(os.path.dirname(imu_calibration_file), exist_ok=True)

    with open(imu_calibration_file, "wt") as cal_file:
        json.dump(calibration, cal_file)

    return imu_calibration_file


def main(subscriber: Subscriber):
    print("Welcome to gyroscope calibration.")
    # imu_topic = input("Enter the imu topic [imu]: ")
    # imu_topic = imu_topic if imu_topic else "imu"
    # print(f"imu topic: {imu_topic}")
    print(
        "Please place the msb with z axis upwards and do not move it while calibrating."
    )
    _ = input("Press Enter to continue.")
    time.sleep(0.5)
    print("Measuring...")
    gyro_measurements = get_gyro_measurement_data(subscriber)
    print("Calibrating...")
    gyro_offsets = calculate_gyro_offsets(gyro_measurements)
    print("The estimated offsets are:")
    print(
        f"x={gyro_offsets['x']:.4}, y={gyro_offsets['y']:.4}, z={gyro_offsets['z']:.4}"
    )
    yes_no_save = input("Do you want to save estimated offsets? [y/N]: ")
    save_gyro_offsets = True if yes_no_save.lower() in ["y", "j", "yes"] else False
    if save_gyro_offsets:
        calibration_file = save_calibration(gyro_offsets)
        print(f"Calibration saved to {calibration_file}.")
    else:
        print("Calibration not saved.")
    yes_no_restart = input(
        "Calibration finished. Do you want to restart the imu service? [y/N]: "
    )
    restart_imu_service = True if yes_no_restart.lower() in ["y", "j", "yes"] else False
    if restart_imu_service:
        compl_proc = subprocess.run(["sudo", "systemctl", "restart", "msb-imu.service"])
        if compl_proc.returncode == 0:
            print("Successfully restarted imu service.")
        else:
            print("Could not restart imu service.")
    print("Done.")


if __name__ == "__main__":
    subscriber = get_default_subscriber("imu")
    main(subscriber)
