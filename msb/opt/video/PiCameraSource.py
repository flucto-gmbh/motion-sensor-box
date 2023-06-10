import cv2
import contextlib

try:
    from picamera2 import Picamera2
except:
    print(f"picamera2 module not available! asuming offline analysis")

@contextlib.contextmanager
def picamera3_context(config):
    """
    Context manager for picamera2's capture_array() method
    """
    try:
        cam = Picamera2()
        cam.configure(
        cam.create_video_configuration(main={"size": (config.width, config.height)}))
        cam.video_configuration.controls['FrameRate'] = config.fps
        cam.start()
        yield cam
    finally:
        print("PiCamSource releasing video")
        cam.stop()

def picamera3_source(config):
    with picamera3_context(config) as video_stream:
        while True:
            #yield cv2.cvtColor(video_stream.capture_array(), cv2.COLOR_BGR2GRAY)
            yield video_stream.capture_array()
