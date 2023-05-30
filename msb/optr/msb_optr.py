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


# TODO
# - add live video option
# - implement roi
# - implement maximum number of tracks

def signal_handler(sig, frame):
    print("msb_imu.py exit")
    sys.exit(0)

def filter_sobel(config):
    """apply a sobel filter to a given image"""
    def inner(img):
        grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
        grad_y = cv2.Sobel(img, cv2.CV_64F, 1, 0)
        return np.sqrt(grad_x**2 + grad_y**2).astype(np.uint8)
    return inner


def filter_roi(config):
    """crop an image to a given region of interest"""
    #height, width = img.shape[:2]
    def inner(img):
        return img[config.roi['xmin']:config.roi['xmax'], config.roi['ymin']:config.roi['ymax']]
    return inner
    # return img[0:height, int(width / 3) : int(width * 2 / 3)]

def filter_rotate_cv(config):
    """rotate and scale an image"""
    (h, w) = img.shape[:2]
    # Perform the rotation
    def inner(img):
        M = cv2.getRotationMatrix2D(config.rotate.center, config.rotate.angle, config.rotate.scale)
        return cv2.warpAffine(img, M, (w, h))
    return inner


def optr_payload(velocity):
    return {
        "epoch" : time.time(),
        "uptime" : uptime.uptime(),
        "name": "optical flow",
        "velocity": float(velocity),
    }

def msb_optr(config: OptrConf, publisher: Publisher):
    signal.signal(signal.SIGINT, signal_handler)   

    # Pipeline
    source = video_source("picamera3", config)
    if config.show_video:
        if config.verbose:
            print('creating gui')
        gui = gui_split(source)
        filter = filter_generator(gui)
    else:
        filter = filter_generator(source)
    tracker = OpticalFlowTracker(filter)

    # Functions
    add_filter_func(filter_roi(config))
    # add_filter_func(filter_sobel)
    # add_filter_func(filter_rotate_cv)

    tracks = []
    def draw_tracks(img):
        cv2.polylines(img, [np.int32(tr) for tr in tracks], False, (0, 255, 0))
    add_draw_func(draw_tracks)

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
                publisher.send(config.topic, payload)
        # if config.show_video:
        #    cv2.imshow("PiCamera3", 

def main():
    optr_conf = load_config(OptrConf(), "optr")
    publisher = get_default_publisher()
    msb_optr(optr_conf, publisher)
