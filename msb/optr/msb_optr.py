from msb.zmq_base.Publisher import get_default_publisher
from .tracker import OpticalFlowTracker, OptrConfig
from .video import video_source, gui_split, add_draw_func
from .analysis import calc_velocity, payload_from_tracks

import cv2
import numpy as np

import time

def main():
    pub = get_default_publisher()

    config = OptrConfig()
    # source = video_source(config.source)
    source = video_source("webcam", 0)
    # gui = video_source("gui", source)
    gui = gui_split(source)

    # pipleline = []

    # Functions
    tracks = []

    def draw_tracks(img):
        cv2.polylines(img, [np.int32(tr) for tr in tracks], False, (0, 255, 0))

    # Modification
    add_draw_func(draw_tracks)

    # add_filter_func(filter_roi)
    tracker = OpticalFlowTracker(gui)

    for tracks in tracker.tracking_loop():
        payload = payload_from_tracks(tracks)
        print(payload)
        time.sleep(1)
        # pub.send(payload)
        c = cv2.waitKey(1)
        if c == 27:
            break

        # if tracker.frame_index > 5:
            # break
