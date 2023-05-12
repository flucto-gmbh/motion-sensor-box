import datetime
import json
import os
import picamera
import signal
import sys
import time

<<<<<<< HEAD
timeformat = "%Y%m%dT%H%M%S%z"
split_interval = 60 # seconds
=======
from msb.camera.config import CameraConf
from msb.config import load_config

timeformat = "%Y-%m-%d %X"
color = (0, 255, 0)
origin = (0, 30)
font_name = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2
>>>>>>> f726958 (fixed requested changes)

from msb.camera.CameraConfig import CameraConfig

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
    return os.path.join(config.video_dir, f"{ts_str}_{config.serial_number.lower()}.h264")


def apply_timestamp(request):
    global timeformat
    timestamp = time.strftime(timeformat)
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font_name, scale, color, thickness)

>>>>>>> f726958 (fixed requested changes)

def setup_camera(camera_config : CameraConfig):
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

def msb_camera(camera_config : CameraConfig):
    if camera_config.verbose:
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
        if (ts - last_ts).seconds >= split_interval:
            print(f"{ts}: {split_interval} s of recording, switching")
            camera.split_recording(get_new_fhandle(ts, prefix=camera_config.serialnumber))
            last_ts = ts
        camera.annotate_text = get_datetime_str(timestamp=ts)
        camera.wait_recording(0.05)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    camera_config = CameraConfig()
    msb_camera(camera_config)
