import json
import os
import pprint
import signal
import subprocess
import sys
import time
from contextlib import contextmanager

import numpy as np
from tqdm import tqdm

sys.path.append("..")
from msb.zmq_base.Subscriber import Subscriber, get_default_subscriber


def get_gyro_measurement_data(subscriber: Subscriber, n_meas=1142):
    # 8 * 35.7 * 4 =  1142.4 -> approx 4 periods
    measurements = np.empty((n_meas, 3))
    for i in tqdm(range(n_meas)):
        _, data = subscriber.receive()
        measurements[i] = [data["rot_x"], data["rot_y"], data["rot_z"]]
    return measurements


def calculate_gyro_offsets(measurements: np.array):
    means = np.round(measurements.mean(axis=0), decimals=1)
    return {"rot_x_off": means[0], "rot_y_off": means[1], "rot_z_off": means[2]}


def get_default_calibration():
    return {
        "rot_x_off": 0.0,
        "rot_y_off": 0.0,
        "rot_z_off": 0.0,
    }


###
# %% Calibration file handling
###


def get_calibration_file_path():
    conf_dir = os.environ["MSB_CONFIG_DIR"]
    imu_calibration_subpath = "msb/calibration/imu.json"
    imu_calibration_file = os.path.join(conf_dir, imu_calibration_subpath)
    return imu_calibration_file


def load_calibration(imu_calibration_file: str):
    try:
        with open(imu_calibration_file, "rt") as cal_file:
            calibration = json.load(cal_file)
    except FileNotFoundError:
        calibration = {}
    return calibration


def dump_calibration(calibration: dict, imu_calibration_file: str):
    imu_calibration_file = get_calibration_file_path()
    os.makedirs(os.path.dirname(imu_calibration_file), exist_ok=True)

    with open(imu_calibration_file, "wt") as cal_file:
        json.dump(calibration, cal_file)


def unset_calibration(calibration_file_path):
    current_calibration = load_calibration(calibration_file_path)
    print("Current calibration is:")
    pprint.pp(current_calibration)
    print("Unsetting calibration.")
    dump_calibration(get_default_calibration(), calibration_file_path)
    return current_calibration


###
# %% IMU service controls
###


def control_imu_service(control: str):
    return subprocess.run(["sudo", "systemctl", control, "msb-imu.service"]).returncode


def stop_imu_service():
    return_code = control_imu_service("stop")
    if return_code == 0:
        print("Successfully stopped imu service.")
    else:
        print("Could not stop imu service.")


def restart_imu_service():
    return_code = control_imu_service("restart")
    if return_code == 0:
        print("Successfully restarted imu service.")
    else:
        print("Could not restart imu service.")


###
# %% Run imu (not as a service) for calibration
###
@contextmanager
def imu_with_calibration_settings():
    # settings taken from https://github.com/wollewald/ICM20948_WE/blob/dfe12a80e48785849aa2b74161ec5d8901cbcfbe/src/ICM20948_WE.cpp#L63
    imu_parameter = {
        "acc_filter": "dlpf_5.7",
        "gyr_filter": "dlpf_5.7",
        "acc_sensitivity": "2g",
        "gyr_sensitivity": "250dps",
        "sample_rate_divisor": 31,
    }
    params = [f"{k}={v}" for k, v in imu_parameter.items()]
    imu_process = subprocess.Popen(
        ["python", "run/msb_imu.py", "--params", *params],
        cwd="/home/msb/motion-sensor-box",
    )
    time.sleep(2)
    print("IMU started.")
    try:
        yield imu_process
    finally:
        imu_process.send_signal(signal.SIGINT)
        imu_process.wait()
        print("IMU stopped.")


def main(subscriber: Subscriber):
    print("Welcome to gyroscope calibration.")
    print("The imu service will be stopped during calibration.")
    print(
        "Please place the msb with z axis upwards and do not move it while calibrating."
    )
    _ = input("Press Enter to continue.")

    calibration_file_path = get_calibration_file_path()

    stop_imu_service()
    old_calibration = unset_calibration(calibration_file_path)
    time.sleep(1)

    # Measure
    with imu_with_calibration_settings():
        print("Measuring...")
        gyro_measurements = get_gyro_measurement_data(subscriber)

    # Calibrate
    print("Calibrating...")
    calibration = calculate_gyro_offsets(gyro_measurements)
    print("The estimated offsets are:")
    pprint.pp(calibration)

    # Save new calibration values?
    yes_no_save = input("Do you want to save the newly estimated offsets? [y/N]: ")
    if yes_no_save.lower() in ["y", "j", "yes"]:
        dump_calibration(calibration, calibration_file_path)
        print(f"Calibration saved to {calibration_file_path}.")
    else:
        dump_calibration(old_calibration, calibration_file_path)
        print("Previous calibration restored.")

    # Restart imu service?
    yes_no_restart = input(
        "Calibration finished. Do you want to restart the imu service? [y/N]: "
    )
    if yes_no_restart.lower() in ["y", "j", "yes"]:
        restart_imu_service()
    print("Done.")


if __name__ == "__main__":
    subscriber = get_default_subscriber("imu")
    main(subscriber)
