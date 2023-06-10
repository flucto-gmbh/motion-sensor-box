#!/usr/bin/env python3

from msb.opt.tracker import OpticalFlowTracker
from msb.opt.video import video_source, gui_split, add_draw_func
from msb.opt.filter import filter_generator, add_filter_func
from msb.opt.video import gui_split, add_draw_func
from msb.opt.msb_opt import filter_roi

import cv2
import numpy as np
import glob
import argparse
import os

import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

def filter_rotate(angle, center=None):
    # outer scope: angle and center

    def rotation_closure(img):
        local_center = center
        h, w = img.shape[:2]
        # actual function that rotates stuff
        if local_center is None:
            local_center = (w / 2, h / 2)

        scale = 1.0
        (h, w) = img.shape[:2]

        # Perform the rotation
        M = cv2.getRotationMatrix2D(local_center, angle, scale)
        img = cv2.warpAffine(img, M, (w, h))
        return img

    return rotation_closure


def draw_roi(img):
    """
    -->  x rightwards
    | X  y downwards
    vY
    """
    rel_pos = 0.01
    (h, w) = img.shape[:2]
    bot, top = int(rel_pos * h), int((1 - rel_pos) * h)
    left, right = int(rel_pos * w), int((1 - rel_pos) * w)

    cv2.rectangle(
        img,
        (left, top),
        (right, bot),
        (0, 255, 0),
        3,
    )

    return img


def draw_rect(cornerpoints):
    x1, x2, y1, y2 = cornerpoints

    def rect_closure(img):
        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3,
        )

        return img

    return rect_closure


def get_cmdline():
    def string_to_dict(arg):
        d = {}
        for kv in arg.split():
            k, v = kv.split("=")
            d[k] = v
        return d

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--track-file", type=str, required=True)
    parser.add_argument("--track-length", type=int, required=False, default=10, help="number of frames a track persists")
    parser.add_argument("--detect-interval", type=int, required=False, default=5, help="interval with which the algorithm looks for new tracks")
    parser.add_argument("--verbose", action="store_true", required=False)
    parser.add_argument("--roi", type=int, nargs=4, required=False, default=[0,1920,0,1080])
    parser.add_argument("--angle", type=float, required=False)
    parser.add_argument("-s", "--select-roi", action="store_true", required=False)
    parser.add_argument("--fps", type=int, required=False, default=10)
    parser.add_argument("--max-tracks", type=int, required=False, default=100)
    parser.add_argument("--px-to-m", type=float, required=True)
    #parser.add_argument(
    #    "--roi", type=string_to_dict, default="xmin=100 xmax=1820 ymin=100 ymax=980"
    #)
    args = parser.parse_args()
    # make argsparse onject compatible with config object
    args.roi = {"xmin" : args.roi[0],"xmax" : args.roi[1],"ymin" : args.roi[2],"ymax" : args.roi[3]}
    return args


def get_source(fname):
    if os.path.isdir(fname):
        return video_source("file", sorted(glob.glob(f"{fname}/*.png")))
    else:
        return video_source("video", fname)


def get_graphical_roi(source):
    img = next(source)

    points = []
    lastlen = 0

    # create function to draw circle on mouse click
    def draw_circle(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # check if mouse event is click
            points.append([x, y])

    # create cv2 window and bind callback
    cv2.imshow("image", img)
    cv2.setMouseCallback("image", draw_circle)

    while True:
        if len(points) != lastlen:
            print("update!")
            pts = np.array(points).reshape(-1, 1, 2)
            img2 = img.copy()
            img2 = cv2.polylines(img2, [pts], True, (255, 0, 0), 10)
            cv2.imshow("image", img2)
            lastlen = len(points)
        if cv2.waitKey(20) & 0xFF == 27:
            break

    return points


def main():
    args = get_cmdline()
    # source = video_source(
    #     "file", sorted(glob.glob("./data/footage_2021/aft_body/*[0-2].png"))
    # )
    source = get_source(args.file)
    # Pipeline
    filter = filter_generator(source)
    gui = gui_split(filter)
    tracker = OpticalFlowTracker(gui, args)

    if args.select_roi:
        points = get_graphical_roi(source)
        rect = cv2.boundingRect(np.array(points))
        x, y, w, h = rect
        add_filter_func(filter_roi([y, y + h, x, x + w]))

    if args.roi and not args.select_roi:
        add_filter_func(filter_roi(args))

    # Functions
    tracks = []

    def draw_tracks(img):
        cv2.polylines(img, [np.int32(tr) for tr in tracks], False, (50, 255, 0), 2)

    if args.angle:
        add_filter_func(filter_rotate(args.angle))

    tracker.detect_interval = 10
    # tracker.track_length = 50

    add_draw_func(draw_tracks)
    # add_filter_func(filter_sobel)

    velocity_timeseries = []

    with open(args.track_file, "w") as f:
        for _ in tracker.tracking_loop():
            velocities = np.array(tracker.velocities)
            if len(velocities):
                velocities = velocities[np.isfinite(velocities[:, 0])]
                velocity_mean = np.mean(velocities, axis=0)
                velocity_timeseries.append(velocity_mean)
                if len(velocity_timeseries) > 3:
                    vx = velocity_timeseries[-2:][0].mean()
                    vy = velocity_timeseries[-2:][1].mean()
                    f.write(f"{tracker.frame_index},{vx},{vy}\n")
                    # f.write(f"{velocity_mean[0]},{velocity_mean[1]}\n")

            c = cv2.waitKey(1)
            if c == 27:
                break


if __name__ == "__main__":
    main()
