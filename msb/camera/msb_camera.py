import datetime
import json
import os
import picamera2
import signal
import sys
import time

timeformat = "%Y%m%dT%H%M%S%z"

from msb.camera.config import CameraConf
from msb.config import load_config

def signal_handler(sig, frame):
    print("msb_piletrack.py exit")
    sys.exit(0)

def get_datetime() -> datetime.datetime:
    return datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)

def get_datetime_str(timeformat : str = "%Y%m%dT%H%M%S.%f%z", timestamp=None) -> str:
    if timestamp:
        return timestamp.strftime(timeformat)
    else:
        return get_datetime().strftime(timeformat)

def exit_handler(sig, frame):
    global camera
    camera.stop_recording()
    print(f"test_camera.py received signal {sig}, exiting")
    sys.exit()

def get_new_fhandle(ts : datetime.datetime, folder : str = 'curdir', prefix : str = "msb-camera") -> str:
    if folder == 'curdir':
        output_dir = os.path.abspath(os.path.curdir)
    else:
        output_dir = folder
        if not os.path.isdir(output_dir):
            raise Exception(f"no such file or directory: {folder}")
    ts_str = get_datetime_str(timestamp=ts)
    return os.path.join(output_dir, f"{prefix}_{ts_str}.h264")

def setup_camera(config : CameraConf):
    """
    setup raspberry pi camera for recording
    """ 
    camera = picamera2.Picamera2()
    camera.resolution = (config.width, config.height)
    camera.framerate = config.fps
    # camera.annotate_background = picamera2.Color('black')
    camera.annotate_text = get_datetime_str()
    camera.annotate_text_size = 16
    return camera

def msb_camera(config : CameraConf):
    if config.verbose:
        print("starting camera recording")
        print("msb_camera configuration:")
        print(f"{json.dumps(config.__dict__, indent=4)}")
    camera = setup_camera(config)
    camera.start_recording(get_new_fhandle(get_datetime(), prefix=config.serial_number))
    last_ts = get_datetime()
    if config.verbose:
        print(f"entering endless loop")
    while True:
        ts = get_datetime()
        if (ts - last_ts).seconds >= config.rollover_period:
            print(f"{ts}: {split_interval} s of recording, switching")
            camera.split_recording(get_new_fhandle(ts, prefix=config.serial_number))
            last_ts = ts
        camera.annotate_text = get_datetime_str(timestamp=ts)
        camera.wait_recording(config.fps/2.0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    camera_config = load_config(CameraConf(), "camera")
    msb_camera(camera_config)
