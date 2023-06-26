import cv2
import datetime
import json
import os
from picamera2 import MappedArray, Picamera2
from picamera2.encoders import H264Encoder
import signal
import sys
import time

from msb.camera.config import CameraConf
from msb.config import load_config

timeformat = "%Y-%m-%d %X"
color = (0, 255, 0)
origin = (0, 30)
font_name = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2


def signal_handler(sig, frame):
    print("msb_camera.py exit")
    sys.exit(0)


def get_datetime() -> datetime.datetime:
    return datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)


def get_datetime_str(timestamp: datetime.datetime, config: CameraConf) -> str:
    return timestamp.strftime(config.timeformat)


def get_new_fhandle(timestamp: datetime.datetime, config: CameraConf) -> str:
    ts_str = get_datetime_str(timestamp, config)
    if not os.path.isdir(config.video_dir):
        try:
            os.makedirs(config.video_dir, exists_ok=True)
        except Exception as e:
            print(f"failed to create output directory: {config.video_dir}")
            sys.exit()
    return os.path.join(config.video_dir, f"{ts_str}_{config.serial_number.lower()}.h264")


def apply_timestamp(request):
    global timeformat
    timestamp = time.strftime(timeformat)
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font_name, scale, color, thickness)


def setup_camera(config: CameraConf):
    """
    setup raspberry pi camera for recording
    """
    camera = Picamera2()
    camera.configure(
        camera.create_video_configuration(main={"size": (config.width, config.height)})
    )
    camera.video_configuration.controls['FrameRate'] = config.fps
    camera.pre_callback = apply_timestamp
    return camera


def setup_globals(config: CameraConf):
    global color
    global origin
    global scale
    global thickness
    global timeformat

    color = tuple(config.font["color"])
    origin = tuple(config.font["origin"])
    scale = config.font["scale"]
    thickness = config.font["thickness"]
    timeformat = config.timeformat


def msb_camera(config: CameraConf):
    if config.verbose:
        print("starting camera recording")
        print("msb_camera configuration:")
        print(f"{config.to_json()}")

    camera = setup_camera(config)
    encoder = H264Encoder()
    camera.start_recording(encoder, get_new_fhandle(ts := get_datetime(), config))
    last_ts = ts
    if config.verbose:
        print(f"entering endless loop")
    while True:
        ts = get_datetime()
        if (ts - last_ts).seconds >= config.rollover_period:
            if config.verbose:
                print(
                    f"{ts}: {config.rollover_period} s of recording, rolling over in new file"
                )
            camera.stop_recording()
            camera.start_recording(encoder, get_new_fhandle(get_datetime(), config))
            last_ts = ts


def main():
    signal.signal(signal.SIGINT, signal_handler)
    config = load_config(CameraConf(), "camera")
    setup_globals(config)
    msb_camera(config)
