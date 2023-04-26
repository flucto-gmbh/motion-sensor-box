import cv2
import numpy as np
import glob
import time

from msb.optr.tracker import OpticalFlowTracker
from msb.optr.video import video_source, gui_split, add_draw_func
from msb.optr.filter import filter_generator, add_filter_func


def draw_random_dots(img):
    for _ in range(10):
        cv2.circle(img, (np.random.randint(0, img.shape[0]), np.random.randint(img.shape[1])), 5, (128, 0, 70), -1)


def filter_sobel(img: np.ndarray):
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    img = np.sqrt(grad_x**2 + grad_y**2).astype(np.uint8)
    return img


def filter_roi(img):
    height, width = img.shape[:2]
    return img[100:200, 100:200]
    # return img[0:height, int(width / 3) : int(width * 2 / 3)]


def calc_velocity(tracks):
    velocities = []
    if not len(tracks):
        return []

    for track in tracks:
        if not len(track) > 1:
            continue
        old = track[-2]
        new = track[-1]
        dy = old[1] - new[1]
        dx = old[0] - new[0]
        velocities.append(np.array([dx, dy]))

    if not len(velocities):
        return []
    return np.median(velocities, axis=0)
    # return np.mean(velocities, axis=0)


def display_track_shape(tracks):
    try:
        if len(tracks):
            a = len(tracks)
            b = len(tracks[0])
            c = len(tracks[0][0])
            return (a, b, c)
        else:
            return tracks
    except Exception:
        return 0


def test_video_generator():
    # video = video_source("video", "./data/footage_2023/DJI_0175.mp4")
    # sequence = video_source("file", sorted(glob.glob("./data/footage_2021/aft_body/*[1-2].png")))

    # Pipeline
    webcam = video_source("webcam", 0)
    gui = gui_split(webcam)
    filter = filter_generator(gui)
    tracker = OpticalFlowTracker(filter)

    # Functions
    tracks = []

    def draw_tracks(img):
        cv2.polylines(img, [np.int32(tr) for tr in tracks], False, (0, 255, 0))

    # Modification
    add_draw_func(draw_tracks)
    # add_filter_func(filter_roi)
    add_filter_func(filter_sobel)
    # add_filter_func(filter_roi)

    with open("tracks.txt", "w") as f:
        for _ in tracker.tracking_loop():
            # time.sleep(0.03)
            # f.write(str(calc_velocity(tracks)))
            # f.write("\n")
            tracks = tracker.tracks
            velocities = np.array(tracker.velocities)
            if len(velocities):
                velocities = velocities[np.isfinite(velocities[:, 0])]
                print(np.mean(velocities, axis=0))
            c = cv2.waitKey(1)
            if c == 27:
                break


if __name__ == "__main__":
    test_video_generator()
