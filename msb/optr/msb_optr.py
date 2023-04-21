from msb.zmq_base.Publisher import get_default_publisher
from .tracker import OpticalFlowTracker, OptrConfig
from .video import video_source, gui_split, add_draw_func
from .analysis import calc_velocity, optr_payload
from .filter import filter_generator, add_filter_func

import cv2
import numpy as np
import glob


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


def main():
    pub = get_default_publisher()

    # Not yet implemented in OpticalFlowTracker
    config = OptrConfig()

    # Pipeline
    source = video_source("webcam", 0)
    filter = filter_generator(source)
    tracker = OpticalFlowTracker(filter)

    # Functions
    add_filter_func(filter_roi)
    # add_filter_func(filter_sobel)
    # add_filter_func(filter_rotate_cv)

    # Currently, tracker has its own velocity calc function. 
    # This will be refactored asap
    for _ in tracker.tracking_loop():
        tracks = tracker.tracks
        payload = optr_payload(tracks)
        pub.send(payload)
