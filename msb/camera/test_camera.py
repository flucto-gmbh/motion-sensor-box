import datetime
import os
import picamera
import signal
import sys
import time

timeformat = "%Y%m%dT%H%M%S%z"
split_interval = 60 # seconds

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

signal.signal(signal.SIGINT, exit_handler)

camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 10
camera.annotate_background = picamera.Color('black')
camera.annotate_text = get_datetime_str()
camera.annotate_text_size = 16
camera.start_recording(get_new_fhandle(get_datetime()))
last_ts = get_datetime()

print(f"entering endless loop")
while True:
    ts = get_datetime()
    if (ts - last_ts).seconds >= split_interval:
        print(f"{ts}: {split_interval} s of recording, switching")
        camera.split_recording(get_new_fhandle(ts))
        last_ts = ts
    camera.annotate_text = get_datetime_str(timestamp=ts)
    camera.wait_recording(0.05)

