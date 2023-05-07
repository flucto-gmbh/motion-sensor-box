from msb.optr.tracker import OpticalFlowTracker, OptrConfig
from msb.optr.video import video_source, gui_split, add_draw_func
from msb.optr.filter import filter_generator, add_filter_func
from msb.optr.video import gui_split, add_draw_func

import cv2
import numpy as np
import glob
import argparse
import os


def filter_sobel(img: np.ndarray):
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    img = np.sqrt(grad_x**2 + grad_y**2).astype(np.uint8)
    return img


def filter_roi(cornerpoints):
    x1, x2, y1, y2 = cornerpoints

    def roi(img):
        return img[x1:x2, y1:y2]

    return roi


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--roi", type=int, nargs=4, required=False)
    parser.add_argument("--angle", type=float, required=False)

    return parser.parse_args()


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
    tracker = OpticalFlowTracker(gui)

    # points = get_graphical_roi(source)

    # if args.roi and not len(points):
    #     add_filter_func(filter_roi(args.roi))
    # if len(points):
    #     rect = cv2.boundingRect(np.array(points))
    #     x, y, w, h = rect
    #     add_filter_func(filter_roi([y, y + h, x, x + w]))

    # Functions
    tracks = []

    def draw_tracks(img):
        cv2.polylines(img, [np.int32(tr) for tr in tracks], False, (50, 255, 0), 2)

    if args.angle:
        add_filter_func(filter_rotate(args.angle))

    # add_draw_func(draw_roi)

    def my_detection_func(cornerpoints, slices):
        x1, x2, y1, y2 = cornerpoints

        def detection_closure(img):
            feature_points = []
            # h, w = img.shape[:2]
            # slices = 10
            # X = np.linspace(0, w, 10)
            # Y = np.linspace(0, h, 10)
            X = np.linspace(x1, x2, 10)
            Y = np.linspace(y1, y2, 10)
            for x in X:
                for y in Y:
                    feature_points.append(np.array(([int(x), int(y)])))
            return feature_points

        return detection_closure

    mycorners = [200, 1500, 0, 300]

    # tracker.detection_func = my_detection_func(mycorners, 20)
    # add_draw_func(draw_rect(mycorners))
    tracker.detect_interval = 5
    tracker.track_length = 50

    add_draw_func(draw_tracks)
    # add_filter_func(filter_sobel)

    for _ in tracker.tracking_loop():
        tracks = tracker._tracks
        velocities = np.array(tracker.velocities)
        if len(velocities):
            velocities = velocities[np.isfinite(velocities[:, 0])]
            velocity_mean = np.median(velocities)
            if velocity_mean:
                print(velocity_mean)

        c = cv2.waitKey(1)
        if c == 27:
            break


if __name__ == "__main__":
    main()
