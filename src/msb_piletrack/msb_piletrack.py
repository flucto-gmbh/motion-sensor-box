import cv2 as cv
from dataclasses import dataclass
import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import Rectangle
import numpy as np
import os
import pandas as pd
import picamera
from picamera.array import PiRGBArray  # Generates a 3D RGB array
from scipy.optimize import curve_fit
import signal
import sys
import time
from tkinter import E
import video

from pile_vision import find_meter_digits, get_meter_templates

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from PileTrackConfig import PileTrackConfig
from msb_config.zeromq import open_zmq_pub_socket

# TODO
# - open camera stream an show it
# - implement simple tracking
# - implement calculations

lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03),
)

feature_params = dict(maxCorners=20, qualityLevel=0.3, minDistance=7, blockSize=7)


def print_verbose(message: str):
    global piletrack_config
    if piletrack_config.verbose:
        print(message)


def signal_handler(sig, frame):
    print("msb_piletrack.py exit")
    sys.exit(0)


def get_datetime() -> datetime.datetime:
    return datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)


def get_datetime_str(timeformat: str = "%Y%m%dT%H%M%S.%f%z", timestamp=None) -> str:
    if timestamp:
        return timestamp.strftime(timeformat)
    else:
        return get_datetime().strftime(timeformat)


def setup_camera(piletrack_config: PileTrackConfig):
    """
    setup_camera(piletrack_config) -> PiCamera

    Sets up the raspberry pi camera for recording.
    Configuration parameters, such as framerate (fps)
    video width- and height and annotation are taken from
    the piletrack_config configuration object.

    Arguments:
        piletrack_config: PileTrackConfig object

    Returns:
        Instance of type PiCamera
    """
    print_verbose("setting up camera")
    camera = picamera.PiCamera()
    camera.resolution = (piletrack_config.width, piletrack_config.height)
    camera.framerate = piletrack_config.fps
    # camera.annotate_background = picamera.Color("black")
    # camera.annotate_text = get_datetime_str()
    # camera.annotate_text_size = 16

    return camera


def get_frame(camera, piletrack_config):
    """
    get_frame(camera, piletrack_config) -> (frame_id, frame)

    Extracts a frame from the raspberry pi camera and returns
    a tuple containing a frame ID (monotonically increasing frame count)
    and the frame itself

    Arguments:
        camera: PiCamera object
        piletrack_config: PileTrackConfig configuration object

    Returns:
        (frame_id : int, frame : numpy.array): frame ID (frame number) and the frame itself
    """

    raw_capture = PiRGBArray(
        camera, size=(piletrack_config.width, piletrack_config.height)
    )
    for frame_id, frame in enumerate(
        camera.capture_continuous(raw_capture, format="bgr", use_video_port=True)
    ):
        if not frame:
            print_verbose("frame ({frame_id}) is none, skipping")
            continue
        # insert datetime into frame
        camera.annotate_background = picamera.Color("black")
        camera.annotate_text = get_datetime_str()
        camera.annotate_text_size = 16
        frame = frame.array
        if piletrack_config.rotate:
            frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
        # clear stream for next frame
        raw_capture.truncate(0)
        yield (frame_id, frame)

def draw_tracks(frame, tracks, color=[0, 255, 0]):
    cv.polylines(frame, [np.int32(tr) for tr in tracks], False, (0, 255, 0))

def show_video(frame, piletrack_config):
    cv.imshow("Frame", frame)
    key = cv.waitKey(1) & 0xFF

def setup_recorder(frame, piletrack_config):
    # Thanks to: https://stackoverflow.com/questions/29317262/opencv-video-saving-in-python
    # Define the codec and create VideoWriter object
    # fourcc = cv.CV_FOURCC(*'DIVX')
    # out = cv.VideoWriter('output.avi',fourcc, 20.0, (640,480))
    # out = cv.VideoWriter('output.avi', -1, 20.0, (640,480))
    fheight = frame.shape[0]
    fwidth = frame.shape[1]
    fourcc = cv.VideoWriter_fourcc(*"XVID")
    output_folder = "."
    out = cv.VideoWriter(
        # is this fps?
        f"tracking_{get_datetime_str()}.mp4",
        fourcc,
        piletrack_config.fps,
        (fwidth, fheight),
    )
    return out
    # out = cv.VideoWriter("output.avi", cv.VideoWriter_fourcc(*"MJPG"), 30,(640,480))

def get_mask(frame, piletrack_config):
    # pile_mask = np.zeros(frame.shape[:2], dtype="uint8")
    pile_mask = np.zeros(
        # [piletrack_config.width, piletrack_config.height], dtype="uint8"
        # opencv expects frames to be in the height, width order
        # [piletrack_config.height, piletrack_config.width],
        [frame.shape[0], frame.shape[1]],
        dtype="uint8",
    )
    cv.rectangle(
        pile_mask,
        (
            piletrack_config.region_of_interest["x1"],
            piletrack_config.region_of_interest["y1"],
        ),
        (
            piletrack_config.region_of_interest["x2"],
            piletrack_config.region_of_interest["y2"],
        ),
        255,
        -1,
    )
    return pile_mask

def draw_roi(frame, piletrack_config):
    cv.rectangle(
        frame,
        (
            piletrack_config.region_of_interest["x1"],
            piletrack_config.region_of_interest["y1"],
        ),
        (
            piletrack_config.region_of_interest["x2"],
            piletrack_config.region_of_interest["y2"],
        ),
        (0, 255, 0),
        1,
    )

def update_features(
    frame_id: int,
    current_frame_gray: np.array,
    pile_mask: np.array,
    feature_tracks: list,
    piletrack_config: PileTrackConfig,
):
    if (
        frame_id % piletrack_config.pile_speed_update_interval == 0
        and len(feature_tracks) < feature_params["maxCorners"]
        # and len(tracks) < piletrack_config.max_number_of_features
    ):
        print_verbose(f"tracking features in {frame_id}")
        for x, y in [np.int32(tr[-1]) for tr in feature_tracks]:
            cv.circle(pile_mask, (x, y), 5, 0, -1)
        p = cv.goodFeaturesToTrack(current_frame_gray, mask=pile_mask, **feature_params)
        if p is not None:
            print_verbose(f"found {len(p)} features")
        if p is not None:
            for x, y in np.float32(p).reshape(-1, 2):
                feature_tracks.append([(x, y)])
    return feature_tracks

def filter_features(p0, p0r, p1, ylim, diff_limit=1):
    # calculate deviations between forwards optical flow and backwards optical flow
    tracking_diff = abs(p0 - p0r).reshape(-1, 2).max(-1)
    print_verbose(f"difference between forward and backward tracking: {tracking_diff}")
    features_to_keep = tracking_diff < diff_limit
    # Monopile limit
    features_in_roi = np.array([item[0][1] for item in p1]) < ylim
    return features_to_keep & features_in_roi

def calculate_velocity(feature_tracks, p1, features_to_keep):
    new_feature_tracks = []
    feature_track_velocities = []
    all_x = []

    for track, (new_x, new_y), keep_feature in zip(
        feature_tracks, p1.reshape(-1, 2), features_to_keep
    ):
        if not keep_feature:
            continue
        last_track = track[-1]
        velocity = new_y - last_track[1]
        feature_track_velocities.append(velocity)
        track.append((new_x, new_y))
        if len(track) > piletrack_config.max_track_length:
            del track[0]
        new_feature_tracks.append(track)
        # cv.circle(vis, (int(x), int(y)), 2, (0, 255, 0), -1)
        all_x.append(new_x)  # For pixel-to-m conversion

    return (new_feature_tracks, feature_track_velocities, all_x)

def track_features(
    frame_id: int,
    previous_frame_gray: np.array,
    current_frame_gray: np.array,
    feature_tracks: list,
    piletrack_config: PileTrackConfig,
) -> (list, list, list):
    if len(feature_tracks) == 0:
        print_verbose(f"no features available")
        return feature_tracks

    p1 = list()
    features_to_keep = list()

    # convert feature_tracks into a format accepted by opencv
    p0 = np.float32([tr[-1] for tr in feature_tracks]).reshape(-1, 1, 2)
    print_verbose(f"coverted {len(p0)} features into opencv format")

    print_verbose("calculating forward optical flow")
    # apply optical flow
    p1, _st, _err = cv.calcOpticalFlowPyrLK(
        previous_frame_gray, current_frame_gray, p0, None, **lk_params
    )
    print_verbose("calculating backwards optical flow")
    p0r, _st, _err = cv.calcOpticalFlowPyrLK(
        current_frame_gray, previous_frame_gray, p1, None, **lk_params
    )
    features_to_keep = filter_features(
        p0, p0r, p1, ylim=piletrack_config.region_of_interest["y2"]
    )
    return calculate_velocity(feature_tracks, p1, features_to_keep)


def msb_piletrack(piletrack_config: PileTrackConfig):
    """
    msb_piletrack(piletrack_config : PileTrackConfig)

    Main logic of msb_piletrack.py is contained in this function.

    Arguments:
        piletrack_config: PileTrackConfig instance
    """

    signal.signal(signal.SIGINT, signal_handler)
    try:
        zmq_pub_socket = (
            open_zmq_pub_socket(piletrack_config.zmq["xsub_connect_string"]),
        )
    except Exception as e:
        print("failed to connect to zeromq xsub socket")
        sys.exit(-1)
    camera = setup_camera(piletrack_config)
    previous_frame_gray = None
    pile_mask = None
    recorder = None
    feature_tracks = []
    feature_track_velocities = []
    all_x = []

    for frame_id, frame in get_frame(camera, piletrack_config):
        print_verbose(f"frame ID {frame_id}")
        current_frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        if frame_id == 0:
            pile_mask = get_mask(current_frame_gray, piletrack_config)
            if piletrack_config.record_video:
                recorder = setup_recorder(current_frame_gray, piletrack_config)
        feature_tracks = update_features(
            frame_id=frame_id,
            current_frame_gray=current_frame_gray,
            pile_mask=pile_mask,
            feature_tracks=feature_tracks,
            piletrack_config=piletrack_config,
        )
        if previous_frame_gray is not None:
            feature_tracks, feature_track_velocities, all_x = track_features(
                frame_id=frame_id,
                previous_frame_gray=previous_frame_gray,
                current_frame_gray=current_frame_gray,
                feature_tracks=feature_tracks,
                piletrack_config=piletrack_config,
            )

        feature_track_velocities_mps = (
            piletrack_config.px_to_m * feature_track_velocities * piletrack_config.fps
        )
        try:
            feature_tracks_median_velocity_mps = np.median(feature_track_velocities_mps)
        except:
            feature_tracks_median_velocity_mps = 0
        if piletrack_config.print_stdout:
            print(f"median velocity: {feature_tracks_median_velocity_mps}")
        if piletrack_config.show_video or piletrack_config.record_video:
            draw_roi(frame, piletrack_config)
            draw_tracks(frame, feature_tracks, piletrack_config)
        if piletrack_config.show_video:
            show_video(frame, piletrack_config)
        if piletrack_config.record_video:
            recorder.write(frame)
        previous_frame_gray = current_frame_gray.copy()

if __name__ == "__main__":
    piletrack_config = PileTrackConfig()
    print_verbose(
        f"msb_piletrack.py\nconfiguration:\n{json.dumps(piletrack_config.__dict__, indent=4)}"
    )
    msb_piletrack(piletrack_config)
