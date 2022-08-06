import datetime
import json
import os
import picamera
import signal
import sys
import time

timeformat = "%Y%m%dT%H%M%S%z"
split_interval = 60 # seconds

from CameraConfig import CameraConfig

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

def get_new_fhandle(ts : datetime.datetime, folder : str = 'curdir', prefix : str = "msb-video") -> str:
    if folder == 'curdir':
        output_dir = os.path.abspath(os.path.curdir)
    else:
        output_dir = folder
        if not os.path.isdir(output_dir):
            raise Exception(f"no such file or directory: {folder}")
            sys.exit()
    ts_str = get_datetime_str(timestamp=ts)
    return os.path.join(output_dir, f"{prefix}_{ts_str}.h264")

def setup_camera(camera_config : CameraConfig):
    """
    setup raspberry pi camera for recording
    """ 
    camera = picamera.PiCamera()
    camera.resolution = (camera_config.width, camera_config.height)
    camera.framerate = camera_config.fps
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = get_datetime_str()
    camera.annotate_text_size = 16
    return camera

def msb_camera(camera_config : CameraConfig):
    if camera_config.verbose:
        print("starting camera recording")
        print("msb_camera configuration:")
        print(f"{json.dumps(camera_config.__dict__, indent=4)}")
    camera = setup_camera(camera_config)
    camera.start_recording(get_new_fhandle(get_datetime(), prefix=camera_config.serialnumber))
    last_ts = get_datetime()
    if camera_config.verbose:
        print(f"entering endless loop")
    while True:
        ts = get_datetime()
        if (ts - last_ts).seconds >= split_interval:
            print(f"{ts}: {split_interval} s of recording, switching")
            camera.split_recording(get_new_fhandle(ts, prefix=camera_config.serialnumber))
            last_ts = ts
        camera.annotate_text = get_datetime_str(timestamp=ts)
        camera.wait_recording(0.05)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    camera_config = CameraConfig()
    msb_camera(camera_config)
