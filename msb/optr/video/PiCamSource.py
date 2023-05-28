import cv2
import contextlib
from picamera2 import Picamera2

@contextlib.contextmanager
def picamera3_context(cam_config):
    """
    Context manager for picamera2's capture_array() method
    """
    try:
        cam = Picamera2()
        cam.start()
        
        # implement configuration here
        #vid_stream = cv2.VideoCapture(*args, **kwargs)
        yield cam
    finally:
        print("PiCamSource releasing video")
        cam.stop()

def picamera3_source(cam_config):
    with picamera3_context(cam_config) as video_stream:
        while True:
            #yield cv2.cvtColor(video_stream.capture_array(), cv2.COLOR_BGR2GRAY)
            yield video_stream.capture_array()
