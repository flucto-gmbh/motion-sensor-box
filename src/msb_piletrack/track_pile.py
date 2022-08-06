"""
Pile tracking based on Lucas-Kanada optical flow.

This module was developed based on: https://github.com/opencv/opencv/blob/b0dc474160e389b9c9045da5db49d03ae17c6a6b/samples/python/lk_track.py
"""

from tkinter import E
import numpy as np
import cv2 as cv
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import Rectangle
from scipy.optimize import curve_fit
import video
import os
from dataclasses import dataclass

from pile_vision import find_meter_digits, get_meter_templates

do_export_video = True
do_search_m_marking_numbers = True
meter_digit_threshold = 0.4
track_max_len = 10
detect_speed_interval = 5
detect_markers_interval = 10

# Pile run
# Problem: Markers are lost when features travel too many pixels / frame
#fname = "pile-run.mp4"
#fname = "pile-run-brief.mp4"
#fname = "pile-run-small-res.mp4"
fname = "../../../pile-tracker/vids/pile-run-small-res-brief.mp4"
#fname="Aft Body Camera_urn-uuid-00306F00-0030-6F4A-1555-00306F4A1555_2022-07-09_09-24-08(1).mp4" # no m-markers, dirt spots on white surface 

# No pile run

# Almost no movemements, overall pile going up (in video)
#fname = "Aft Door Camera_urn-uuid-00306F00-0030-6F4A-155B-00306F4A155B_2022-07-09_05-36-56(4).mp4"

# Small movements up and down caused by vessel (?!), overall pile going up (in video)
#fname = "Aft Door Camera_urn-uuid-00306F00-0030-6F4A-155B-00306F4A155B_2022-07-09_05-36-56(3).mp4"

# Rusty part of the monopile with m-markings
#fname = "Aft Door Camera_urn-uuid-00306F00-0030-6F4A-155B-00306F4A155B_2022-07-09_05-36-56(1).mp4"

# Rusty part transitions to white part, no m-markings
#fname = "Fwd Door Camera_urn-uuid-00306F00-0030-6F4A-15AB-00306F4A15AB_2022-07-09_05-15-04(2).mp4"

# Piling: first rusty, then white part, moves big distance (before pile run)
#fname = "Aft Door Camera_urn-uuid-00306F00-0030-6F4A-155B-00306F4A155B_2022-07-09_05-36-56(2).mp4" #start_frame_idx = 38000
#fname = "aft_door_camera_calibration.mp4" # 1 min of "xxxx56(2).mp4"

# Action cam videos
#fname="2022-07-28_DJI_0069.MP4" # start_frame_idx 17400
#fname="2022-07-28_DJI_0070.MP4"
#fname="2022-07-28_DJI_0082.MP4" # start_frame_idx 5000
#fname="2022-07-28_DJI_0084.MP4" # start_frame_idx 0 
#fname="2022-07-28_DJI_0086.MP4" # start_frame_idx 10800

start_frame_idx = 0 # 0 for starting at beginning of video

cam ="osbit_aft_door"
if "Fwd Door" in fname:
    cam = "osbit_fwd_door"
elif "DJI" in fname:
    cam = "action_cam_bridge_deck"

video_folder = "vids"
# fpath = os.path.join(video_folder, fname)
fpath = fname

def calibration_function(x: np.array, a=None, b=None, c=None, cam="osbit_aft_door") -> np.array:
    """Function for converting a y-pixel distance into a meter distance given a x-pixel value. N pixel = 1 meter.


    Args:
        x (np.array): x-pixel position(s)
        a (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        b (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        c (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        cam (str, optional): Camera name (different cameras has different presaved calibration functions). 
            Defaults to "osbit_aft_door".

    Returns:
        np.array: meter distance(s)
    """
    x = np.array(x)

    if a is None and b is None and c is None:
        if cam == "osbit_aft_door":
            a = 1.69453802e-02
            b = 6.47904637e+02
            c = 2.75114714e+02
        elif cam == "action_cam_bridge_deck":
            a = 0
            b = 0
            c = 10.5
        else:
            raise NotImplementedError

    return -1 * (a * (x - b)) ** 2 + c


def px_to_m_conversion_factor(x, fname="x", do_calibration_fit=False, do_plot_calibration_curve=False):
    """
    Caclulates the conversion factor between y-pixel- distance and m-pixel distance given a x-pixel value.
    """

    dist_51m_to_special_marking = 1.48 # See 'calibration2.jpg' and '19A502-JBO-DWSMDD-EN-4019-06_Monopile - Paint  Markings.pdf'

    # Left image section (with special marking; from image 'calibration2.jpg')
    x_pos = [115, 193, 294]
    n_pixel_is_1m = (np.asarray([275, 328, 361]) / dist_51m_to_special_marking).tolist()

    # Middle image section (with meter markings; from image 'calibration1.jpg')
    x_pos.extend([848, 938, 1018])
    n_pixel_is_1m.extend([258, 248, 239])


    # Right image section (with special marking; from image 'calibration2.jpg'')
    x_pos.extend([1178, 1231])
    n_pixel_is_1m.extend((np.asarray([298, 256]) / dist_51m_to_special_marking).tolist())

    if do_calibration_fit:
        popt, _ = curve_fit(calibration_function, x_pos, n_pixel_is_1m)     
        a, b, c = popt # Unpack optima parameters for the objective function.
        print("popt: " + str(popt))
    else: 
        # y = np.interp(x, x_pos, n_pixel_is_1m) # Alternative to calibration function: just linearly interpolate
        #a = 1.69453802e-02
        #b = 6.47904637e+02
        #c = 2.75114714e+02
        y = calibration_function(x, cam=cam)
        #print("cam: " + str(cam))
        #print("calibration y: " + str(y))



    if do_plot_calibration_curve:
        x_new = np.arange(80, 1260, 10)
        y_new = calibration_function(x_new) # Use optimal parameters to calculate new values

        fig, ax = plt.subplots()
        ax.plot(x_pos, n_pixel_is_1m, '.b')
        ax.plot(x_pos, n_pixel_is_1m, '-b')
        ax.plot(x_new, y_new, '-r')
        x_text = 80
        ax.text(x_text, 270, 'Calibration curve', color='r')
        formula = f"-1 * ({a:.3f} * (x - {b:.0f})) ** 2 + {c:.0f}"
        ax.text(x_text, 265, formula, color='r', fontsize=6)
        ax.add_patch(Rectangle((848, 175), 1018-848, 105, facecolor='k', edgecolor='none', fill=True, alpha=0.3))
        ax.text(848, 175, "Meter markings", color='k', fontsize=6)
        #ax.plot(x, y, 'xr')
        plt.xlabel('x-Position (pixel)')
        plt.ylabel('y-pixel distance that equals 1 m')
        plt.show()

    # For videos with reduced resolution the px-to-m is different.
    if "small-res" in fname:
        y *= 478 / 1080
        
    one_pixel_is_x_m = 1 / y

    return one_pixel_is_x_m

fps = 30


@dataclass
class RegionOfInterest:
    """
    Region of interest within the image. Is used for specifying the pile area for speed estimation
    and the meter marker number area for pentration depth estimation.
    """
    roi_left_lim: float = 0
    roi_right_lim: float = 300
    roi_up_lim: float = 0 # pixel coordinates, 0 = very top of image
    roi_down_lim: float = 300
    roi_type: str = "pile" # Type of ROI, can be "pile" or "marking_number". Defaults to "pile".
    cam: str = "osbit_aft_door" #Name of camera. Defaults to "osbit_aft_door".
    width: int = 1920
    height: int = 1080


    def __post_init__(self):
        cam_options = ["osbit_aft_door", "osbit_fwd_door", "action_cam_bridge_deck"]
        if cam not in cam_options:
            raise ValueError(f"cam was {cam} but must be one of {cam_options}.")
        if self.roi_type == "pile":
            if self.cam == "osbit_aft_door":
                self.roi_left_lim = int(0.176 * self.width)
                self.roi_right_lim = int(0.587 * self.width)
                self.roi_up_lim = int(0.021 * self.height) # pixel coordinates, 0 = very top of image
                self.roi_down_lim = int(0.52 * self.height)
            elif cam == "osbit_fwd_door":
                self.roi_left_lim = int(0.35 * self.width)
                self.roi_right_lim = int(0.75 * self.width)
                self.roi_up_lim = int(0.01 * self.height)
                self.roi_down_lim = int(0.5 * self.height)
            elif cam == "action_cam_bridge_deck":
                self.roi_left_lim = int(0.53 * self.width)
                self.roi_right_lim = int(0.565 * self.width) # When small crane obstructs UET 0.53, otherwise 0.55 is fine
                self.roi_up_lim = int(0.25 * self.height) # Could be as low as 0.01, in video 0082 set to 0.15, in video 0084 to 0.10, in video 0086 0.2
                self.roi_down_lim = int(0.32 * self.height)

            self.stop_track_down_lim = int(0.52 * self.height)

        elif self.roi_type == "marking_numbers":
            if cam == "osbit_aft_door":
                self.roi_left_lim = int(1050 / 1920 * self.width)
                self.roi_right_lim = int(1250 / 1920 * self.width)
                self.roi_up_lim = 0
                self.roi_down_lim = int(700 / 1080 * self.height)

        allowed_types = ["pile", "marking_numbers"]
        if self.roi_type not in allowed_types:
            raise ValueError(f"Type was '{self.roi_type}', but must be {allowed_types}")
        
@dataclass
class CameraInfo:
    name: str = "osbit_aft_door"
    roi_pile: RegionOfInterest = RegionOfInterest()
    roi_meter_marking_numbers: RegionOfInterest = RegionOfInterest()
    resolution: tuple = (1920, 1080) # widtth, height
    pile_centerline: int = 960
    roller_y_at_p_center: int = 750
    roller_y_at_m_marking_numbers: int = 655
    roller_line: np.array = np.array([[140,635],[580,800], [1100,710], [1237,540]], np.int32)


@dataclass
class Site:
    name: str = "YUN56"
    gripper_keel_dist = 27.132 # for DLS 4200 during Yunlin installation, symbol g_v in drawing
    water_depth: float = 27.0
    draft: float = 8.356

    def gripper_seabed_dist(self) -> float:
        return self.gripper_keel_dist - self.draft + self.water_depth
    

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 20,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

def draw_str(dst, target, s):
    x, y = target
    cv.putText(dst, s, (x+1, y+1), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv.LINE_AA)
    cv.putText(dst, s, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv.LINE_AA)
                       

def track_video(fpath, cam_info:CameraInfo, do_export_video=False, track_max_len=10, detect_speed_interval=5, detect_markers_interval=10):
    roi_pile = cam_info.roi_pile
    roi_numbers = cam_info.roi_meter_marking_numbers
    tracks = []
    cap = video.create_capture(fpath)
    frame_idx = start_frame_idx
    cap.set(cv.CAP_PROP_POS_FRAMES, frame_idx)
    
    # A mask is the same size as our image, but has only two pixel
    # values, 0 and 255 -- pixels with a value of 0 (background) are
    # ignored in the original image while mask pixels with a value of
    # 255 (foreground) are allowed to be kept
    _, frame = cap.read()
    print(f"type(frame): {type(frame)}")
    if frame is None:
        raise ValueError(f"frame is None. Possibly the start_frame_idx of {start_frame_idx} is too high (higher than the total frame count).")
    pile_mask = np.zeros(frame.shape[:2], dtype="uint8")
    cv.rectangle(pile_mask, (roi_pile.roi_left_lim, roi_pile.roi_up_lim), 
        (roi_pile.roi_right_lim, roi_pile.roi_down_lim), 255, -1)
    numbers_mask = np.zeros(frame.shape[:2], dtype="uint8")
    cv.rectangle(numbers_mask, (roi_numbers.roi_left_lim, roi_numbers.roi_up_lim), 
        (roi_numbers.roi_right_lim, roi_numbers.roi_down_lim), 255, -1)

    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    frame_ids = np.arange(0, total_frames)
    median_vel = np.empty((total_frames))
    median_vel[:] = np.nan
    median_vel_mps = np.empty(total_frames)
    median_vel_mps[:] = np.nan
    alltracks_vel = []
    travelled_distance = np.empty(total_frames)
    travelled_distance[:] = np.nan
    travelled_distance[start_frame_idx-1:start_frame_idx+10] = 0
    penetration_depth_array = np.empty(total_frames)
    penetration_depth_array[:] = np.nan

    # Variables for m-marking estimation
    found_m_number = None
    number_xy = (None, None)
    number_wh = (None, None)
    goodness = None
    m_marker_color_bgr = (0, 0, 255)
    roller_color_bgr = (0, 180, 255)
    travelled_since_last_detection = None
    travelled_at_last_detection = None
    marker_at_gripper_height = np.nan
    number_templates = get_meter_templates()
    is_stable_number = False
    found_numbers = []
    expected_meter_digit = None
    expected_ypos = [None, None]

    if do_export_video:
        # Thanks to: https://stackoverflow.com/questions/29317262/opencv-video-saving-in-python
        # Define the codec and create VideoWriter object
        #fourcc = cv.CV_FOURCC(*'DIVX')
        #out = cv.VideoWriter('output.avi',fourcc, 20.0, (640,480))
        #out = cv.VideoWriter('output.avi', -1, 20.0, (640,480))

        fshape = frame.shape
        fheight = fshape[0]
        fwidth = fshape[1]
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        output_folder = "output-vids/"
        out = cv.VideoWriter(output_folder + "tracking_" + fname, fourcc, 20.0, (fwidth,fheight))
        #out = cv.VideoWriter("output.avi", cv.VideoWriter_fourcc(*"MJPG"), 30,(640,480))

    while True:
        _ret, frame = cap.read()
        if frame is None:
            break
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        vis = frame.copy()
        vels = [np.NaN]

        # Draw region of interest for tracking speed features
        cv.rectangle(vis, (roi_pile.roi_left_lim, roi_pile.roi_up_lim), 
            (roi_pile.roi_right_lim, roi_pile.roi_down_lim), (0,255,0), 1)

        # Draw region of interest for meter numbers
        if do_search_m_marking_numbers:
            cv.rectangle(vis, (roi_numbers.roi_left_lim, roi_numbers.roi_up_lim), 
                (roi_numbers.roi_right_lim, roi_numbers.roi_down_lim), m_marker_color_bgr, 1)
        print(f"len(tracks is: {len(tracks)}")
        if len(tracks) > 0:
            img0, img1 = prev_gray, frame_gray
            print(f"tracks: {tracks}")
            print(f"tracks: {[tr[-1] for tr in tracks]}")
            print(f"tracks: {np.float32([tr[-1] for tr in tracks]).reshape(-1, 1, 2)}")
            p0 = np.float32([tr[-1] for tr in tracks]).reshape(-1, 1, 2)
            print(f"p0: {p0}")
            p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
            p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)

            # Features are only kept if a backwards-check succeeds and if they are within the monopile limit.
            # Backward-check
            d = abs(p0-p0r).reshape(-1, 2).max(-1) 
            print(f"d = {d}")
            good = d < 1

            # Monopile limit
            p1_y = [item[0][1] for item in p1]
            is_on_monopile = np.array(p1_y) < (roi_pile.stop_track_down_lim)
            good = good * is_on_monopile

            new_tracks = []
            vels = []
            all_x = []
            for tr, (x, y), good_flag in zip(tracks, p1.reshape(-1, 2), good):
                if not good_flag:
                    continue
                last_xy = tr[-1]
                vel = y - last_xy[1]
                vels.append(vel)
                tr.append((x, y))
                if len(tr) > track_max_len:
                    del tr[0]
                new_tracks.append(tr)
                cv.circle(vis, (int(x), int(y)), 2, (0, 255, 0), -1)

                all_x.append(x) # For pixel-to-m conversion
            tracks = new_tracks
            cv.polylines(vis, [np.int32(tr) for tr in tracks], False, (0, 255, 0))
            print('id:' + str(frame_idx))
            
            median_vel[frame_idx] = np.median(vels)
            px_to_m = px_to_m_conversion_factor(all_x, fname=fname, do_plot_calibration_curve=False) 
            #print("px_to_m: " + str(px_to_m))
            vels_mps = px_to_m * vels * fps
            median_vel_mps[frame_idx] = np.median(vels_mps)
            travelled_distance[frame_idx] = travelled_distance[frame_idx - 1] + median_vel_mps[frame_idx] / fps

            vert_distance = 20
            drawing_line = 1
            draw_str(vis, (20, drawing_line * vert_distance), "frame id: " + str(frame_idx))
            drawing_line += 1
            draw_str(vis, (20, drawing_line * vert_distance), "track count: %d" % len(tracks))
            drawing_line += 1
            vel_last_1s = np.mean(median_vel[frame_idx - fps:frame_idx])
            draw_str(vis, (20, drawing_line * vert_distance), "mean velocity last 1s (px/frame): {:.2f}".format(vel_last_1s))
            drawing_line += 1
            vel_last_1s_mmpermin = np.mean(median_vel_mps[frame_idx - fps:frame_idx]) * 1000 * 60
            draw_str(vis, (20, drawing_line * vert_distance), "mean velocity last 1 s (mm/min): {:.0f}".format(vel_last_1s_mmpermin))
            drawing_line += 1
            t_average = 5 # 5 seconds
            vel_last_5s = np.mean(median_vel_mps[frame_idx - t_average * fps : frame_idx])
            vel_last_5s = vel_last_5s * 1000 * 60
            draw_str(vis, (20, drawing_line * vert_distance), "mean velocity last 5 s (mm/min): {:.0f}".format(vel_last_5s))
            drawing_line += 1
            t_average = 30 
            vel_last_long_s = np.mean(median_vel_mps[frame_idx - t_average * fps : frame_idx])
            vel_last_long_s = vel_last_long_s * 1000 * 60
            draw_str(vis, (20, drawing_line * vert_distance), "mean velocity last " + str(t_average) + " s (mm/min): {:.0f}".format(vel_last_long_s))
            drawing_line += 1
            #draw_str(vis, (20, drawing_line * vert_distance), "travelled distance (m): {:.3f}".format(travelled_distance[frame_idx]))
            #drawing_line += 1
            penetration_depth = marker_at_gripper_height - site.gripper_seabed_dist()
            penetration_depth_array[frame_idx] = penetration_depth
            draw_str(vis, (20, drawing_line * vert_distance), "penetration depth (m): {:.3f}".format(penetration_depth))
            drawing_line += 1


            draw_str(vis, (20, int(0.95 * frame.shape[0])), "'d' to delete features | 'ESC' to stop program")
        alltracks_vel.append(vels)

        # Every x frames we look for new speed features (and if we have less than we would like to have).
        if frame_idx % detect_speed_interval == 0 and len(tracks) < feature_params["maxCorners"]:
            mask = pile_mask
            for x, y in [np.int32(tr[-1]) for tr in tracks]:
                cv.circle(mask, (x, y), 5, 0, -1)
            p = cv.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
            if p is not None:
                for x, y in np.float32(p).reshape(-1, 2):
                    tracks.append([(x, y)])

        if frame_idx % detect_markers_interval == 0:
            r = roi_marking_numbers
            frame_roi_numbers = frame_gray[r.roi_up_lim : r.roi_down_lim, r.roi_left_lim : r.roi_right_lim]
            if do_search_m_marking_numbers:
                d = find_meter_digits(frame_roi_numbers, number_templates, threshold=meter_digit_threshold, 
                    expected_meter_digit=expected_meter_digit, expected_ypos=expected_ypos, do_write_as_png=True)
                print(d)
                if d is not None:
                    found_m_number= d["found_m_number"]
                    found_numbers.append(found_m_number)
                    number_xy = d["number_xy"]
                    number_xy = (number_xy[0] + r.roi_left_lim, number_xy[1] + r.roi_up_lim)
                    number_wh = d["number_wh"]
                    goodness = d["goodness"]
                    number_xy_at_last_detection = number_xy
                    travelled_at_last_detection = travelled_distance[frame_idx]

                    # Check if last numbers are the same, thanks to: https://stackoverflow.com/questions/62670387/how-to-check-how-many-of-the-last-elements-in-a-list-are-equal-in-python
                    n = 3
                    if len(found_numbers) >= n and len(set(found_numbers[-n:])) == 1 and np.isnan(found_numbers[-1]) == False:
                        is_stable_number = True
                        expected_meter_digit = found_m_number
                        temp = d["number_xy"][1]
                        y_last_number = float(temp) / frame_roi_numbers.shape[0]
                        expected_ypos = [y_last_number - 0.1, y_last_number + 0.1]
                        if expected_ypos[0] < 0: expected_ypos[0] = 0
                        if expected_ypos[1] > 1: expected_ypos[1] = 1
                    else:
                        is_stable_number = False
                        expected_meter_digit = None
                        expected_ypos = [None, None]
                else:
                    goodness = None
                    expected_meter_digit = None
                    expected_ypos = [None, None]
                    found_numbers.append(np.nan)

        # Draw estimated m-marking positions
        m_marker_line_length = 30
        p_center = cam_info.pile_centerline
        if found_m_number is not None:
            n_px_is_1m_at_center = int(1  / px_to_m_conversion_factor(p_center, fname=fname, do_plot_calibration_curve=False))
            n_px_is_1m_at_m_numbers = int(1 / px_to_m_conversion_factor(number_xy[0], fname=fname, do_plot_calibration_curve=False))
            travelled_since_last_detection = travelled_distance[frame_idx] - travelled_at_last_detection
            if np.isnan(travelled_since_last_detection):
                travelled_since_last_detection = 0
            number_xy = number_xy_at_last_detection
            new_number_xy = (number_xy[0], number_xy[1] + int(travelled_since_last_detection * n_px_is_1m_at_m_numbers))
            number_xy = new_number_xy
            pt2 = (number_xy[0] + number_wh[0], number_xy[1] + number_wh[1])
            cv.rectangle(vis, number_xy, pt2, m_marker_color_bgr, 2)
            text_xy = (number_xy[0] + number_wh[0] + 1, number_xy[1] + int(0.5 * number_wh[1]))
            cv.putText(vis, str(found_m_number), text_xy, cv.FONT_HERSHEY_PLAIN, 
                2.0, m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)
            if goodness is None:
                text = "Conf < threshold"
            else:
                text = "Conf: {:.2f}".format(goodness)
            cv.putText(vis, text, (text_xy[0], text_xy[1]+10), cv.FONT_HERSHEY_PLAIN, 
                0.8, m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)
            line_pt1 = (number_xy[0], number_xy[1] + int(0.5 * number_wh[1]))
            line_pt2 = (p_center, number_xy[1] + int(0.5 * number_wh[1]))
            cv.line(vis, line_pt1, line_pt2, m_marker_color_bgr, 1)
            cv.putText(vis, str(found_m_number), (p_center - 10, text_xy[1]), fontFace=cv.FONT_HERSHEY_PLAIN, 
                fontScale=1.0, color=m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)

            # Estimate monopile height at gripper position
            px_dist_to_found_number = cam_info.roller_y_at_m_marking_numbers - number_xy[1] 
            m_dist = px_dist_to_found_number * px_to_m_conversion_factor(p_center, fname=fname, do_plot_calibration_curve=False)
            marker_at_gripper_height = found_m_number - m_dist
            offset = -50
            pt1 = (p_center + offset, cam_info.roller_y_at_p_center)
            pt2 = (p_center + m_marker_line_length + offset, cam_info.roller_y_at_p_center)
            cv.line(vis, pt1, pt2, m_marker_color_bgr, 1)
            cv.putText(vis, f"{marker_at_gripper_height:.3f}", (pt1[0] - 10, pt1[1]), fontFace=cv.FONT_HERSHEY_PLAIN, 
                fontScale=1.0, color=m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)

            # From known position, go up in image for drawing 1-m markers
            current_number = found_m_number
            current_y_pos = text_xy[1]
            is_pixel_in_image = True 
            while is_pixel_in_image:
                current_number = current_number + 1
                current_y_pos = current_y_pos - n_px_is_1m_at_center
                if current_y_pos < 1:
                    is_pixel_in_image = False
                else:
                    pt1 = (p_center, current_y_pos)
                    pt2 = (p_center + m_marker_line_length, current_y_pos)
                    cv.line(vis, pt1, pt2, m_marker_color_bgr, 1)
                    cv.putText(vis, str(current_number), (pt1[0] - 10, pt1[1]), fontFace=cv.FONT_HERSHEY_PLAIN, 
                        fontScale=1.0, color=m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)

            # From known position, down up in image for drawing 1-m markers
            current_number = found_m_number
            current_y_pos = text_xy[1]
            is_pixel_in_image = True
            while is_pixel_in_image:
                current_number = current_number - 1
                current_y_pos = current_y_pos + n_px_is_1m_at_center
                if current_y_pos > cam_info.resolution[1]:
                    is_pixel_in_image = False
                else:
                    pt1 = (p_center, current_y_pos)
                    pt2 = (p_center + m_marker_line_length, current_y_pos)
                    cv.line(vis, pt1, pt2, m_marker_color_bgr, 1)
                    cv.putText(vis, str(current_number), (pt1[0] - 10, pt1[1]), fontFace=cv.FONT_HERSHEY_PLAIN, 
                        fontScale=1.0, color=m_marker_color_bgr, thickness=1, lineType=cv.LINE_AA)

        # Draw roller line
        if do_search_m_marking_numbers:
            roller_line = cam_info.roller_line
            roller_line = roller_line.reshape((-1,1,2))
            cv.polylines(vis, [roller_line], False, roller_color_bgr, 1)
            roller_y_at_p_center = cam_info.roller_y_at_p_center
            pt1 = (p_center, roller_y_at_p_center)
            pt2 = (p_center + m_marker_line_length, roller_y_at_p_center)
            cv.line(vis, pt1, pt2, roller_color_bgr, 2)        
            text = f"{site.gripper_seabed_dist():0.3f} m to seabed"
            cv.putText(vis, text, (pt2[0] + 10, pt2[1]), fontFace=cv.FONT_HERSHEY_PLAIN, 
                fontScale=1.0, color=roller_color_bgr, thickness=1, lineType=cv.LINE_AA)

        frame_idx += 1
        prev_gray = frame_gray
        cv.imshow('lk_track', vis)

        if do_export_video:
            out.write(vis)

        ch = cv.waitKey(1) # wait x ms, at least 1
        if ch == 27: # ESC
            break
        elif ch == ord('d'):
            #print("Deleting current features")
            tracks = []


    if do_export_video:
        out.release()
    cap.release()

    return (frame_ids, median_vel, alltracks_vel, median_vel_mps, penetration_depth_array)

site = Site()

# Get resolution 
cap = video.create_capture(fpath)
_, frame = cap.read()
resolution = frame.shape[0:-1]
print(f"resolution: {resolution}")

roi_pile = RegionOfInterest(roi_type="pile", cam=cam, width=resolution[1], height=resolution[0]) # Default ROI for aft cam
roi_marking_numbers = RegionOfInterest(roi_type="marking_numbers", cam=cam,  width=resolution[1], height=resolution[0])
print(f"roi_marking_numbers: {roi_marking_numbers}")
cam_info = CameraInfo(name=cam, roi_pile=roi_pile, roi_meter_marking_numbers=roi_marking_numbers, 
    resolution=(resolution[1], resolution[0]), pile_centerline=835)


(frame_ids, median_vel, alltracks_vel, median_vel_mps, penetration_depth_array) = track_video(fpath=fpath, 
    cam_info=cam_info, do_export_video=do_export_video, track_max_len=10, detect_speed_interval=5, detect_markers_interval=10)

cv.destroyAllWindows()


def moving_average(x, n=31) :
    """
    Calculates a moving average, symmetric around each index such that the output has no "delay".
    x = series of which moving average should be calculated.
    n = size of window including the point for which the moving average shall be calculated.
        Should be an odd number such that the avering window is symmetric around the point.
        If it is an even number, it is increased +1
    """
    if n % 2 == 0:
        n += 1
    csum = np.nancumsum(x, dtype=float)
    add_each_side = int((n - 1)/2)
    mov_average = np.empty(csum.shape)
    mov_average[:] = np.nan
    mov_average[add_each_side + 1 : -add_each_side] = csum[n:] - csum[:-n]
    mov_average[np.isnan(x).flatten()] = np.nan
    return mov_average / n

tracking_bad_start_id = None
#if fname == "pile-run-small-res-brief.mp4":
#    tracking_bad_start_id = 200 # 200 for video "pile-run-small-res-brief.mp4"

# In px/frame
fig1, ax = plt.subplots()
ax.plot(frame_ids, median_vel)
mov_average = moving_average(median_vel)
ax.plot(frame_ids, mov_average)
ax.axhline(0, color='black')
if tracking_bad_start_id is not None:
    width = max(frame_ids) -  tracking_bad_start_id
    height = np.nanmax(median_vel) - np.nanmin(median_vel)
    ax.add_patch(Rectangle((tracking_bad_start_id, np.nanmin(median_vel)), width, height, facecolor='r', edgecolor='none', fill=True, alpha=0.3))
    ax.text(tracking_bad_start_id, np.nanmax(median_vel), 'Algorithm bad from here', fontsize=6, color='r', verticalalignment='bottom')
ax.set_xlabel('Frame id (-)')
ax.set_ylabel('Vertical velocity (pixel/frame)') 
if len(alltracks_vel) < 500:
    for i, vels in enumerate(alltracks_vel):
        x = np.zeros(len(vels)) + i + start_frame_idx
        if len(vels) > 1:
            ax.scatter(x, vels)
ax.set_title("File: " + str(fname))
fig_folder = "figs/"
fig1.savefig(fig_folder + "plot_" + fname[:-4] + "pixelperframe.png", dpi=300, format="png")

# In m/s
fig2, axs = plt.subplots(2, 1, figsize=(10, 5.5))
pandas_freq = int(1/fps*1000)
start_date = "2022-07-28" # This is a placeholder. TODO: Get this from video?
abs_times = pd.date_range(start_date, periods=len(frame_ids), freq=str(pandas_freq) + "ms")
median_vel_mmpermin = median_vel_mps * 1000 * 60
mov_average_1s = moving_average(median_vel_mmpermin, n=31)
n_seconds_average = 5 # 5? 15? 30?
mov_average_long = moving_average(median_vel_mmpermin, n=fps*n_seconds_average)
ax = axs[0]
ax.plot(abs_times, median_vel_mmpermin, label="Raw")
ax.plot(abs_times, mov_average_1s, "-g", label="1 s average",)
ax.plot(abs_times, mov_average_long, "-r", label=str(n_seconds_average) + " s average")


ax.axhline(0, color='black')
ax.set_xlabel('Time')
ax.set_ylabel('Vertical velocity (mm/min)') 
ax.legend()
ax = axs[1]
ax.plot(abs_times, mov_average_long, "-r", label=str(n_seconds_average) + " s average")
ax.axhline(0, color='black')
ax.set_xlabel('Time (hours:minutes:seconds)')
ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M:%S'))
ax.set_ylabel('Vertical velocity (mm/min)') 
ax.legend()
plt.suptitle("File: " + str(fname))
fig2.savefig(fig_folder + "plot_" + fname[:-4] + "_physicalunits.png", dpi=300, format="png")

fig3, ax = plt.subplots()
ax.plot(abs_times, penetration_depth_array)
ax.set_xlabel('Time')
ax.set_ylabel('Penetration depth (m)') 

plt.show()
