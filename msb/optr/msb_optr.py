import cv2
import numpy as np
import signal
import sys
import time
import uptime

from msb.zmq_base.Publisher import get_default_publisher, Publisher
from msb.config import load_config
from msb.optr.tracker import OpticalFlowTracker
from msb.optr.video import video_source, gui_split, add_draw_func
from msb.optr.filter import filter_generator, add_filter_func
from msb.optr.config import OptrConf




def filter_sobel(img: np.ndarray):
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    img = np.sqrt(grad_x**2 + grad_y**2).astype(np.uint8)
    return img


def filter_roi(img):
    height, width = img.shape[:2]
    return img[0:height, 250:800]
    # return img[0:height, int(width / 3) : int(width * 2 / 3)]


def filter_rotate_cv(img):
    center = None
    scale = 1.0
    angle = -15
    (h, w) = img.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(img, M, (w, h))

    return rotated


def optr_payload(velocity):
    return {
        "epoch" : time.time(),
        "uptime" : uptime.uptime(),
        "name": "optical flow",
        "velocity": float(velocity),
    }
def signal_handler(sig, frame):
    print("msb_imu.py exit")
    sys.exit(0)




def msb_optr(config: OptrConf, publisher: Publisher):
    signal.signal(signal.SIGINT, signal_handler)   

    # Pipeline
    source = video_source("picamera3", 0)
    filter = filter_generator(source)
    tracker = OpticalFlowTracker(filter)

    # Functions
    # add_filter_func(filter_roi)
    # add_filter_func(filter_sobel)
    # add_filter_func(filter_rotate_cv)

    # Currently, tracker has its own velocity calc function.
    # This will be refactored asap
    for i, _ in enumerate(tracker.tracking_loop()):
        print(f'processing frame {i}')
        tracks = tracker.tracks
        velocities = np.array(tracker.velocities)
        if len(velocities):
            velocities = velocities[np.isfinite(velocities[:, 0])]
            velocity_mean = np.median(velocities)
            print(velocity_mean)
            if velocity_mean:
                payload = optr_payload(velocity_mean)
                pub.send(b"optr", payload)

def main():
    optr_conf = load_config(OptrConf(), "optr")
    publisher = get_default_publisher()
    msb_optr(optr_conf, publisher)
