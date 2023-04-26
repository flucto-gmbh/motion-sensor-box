# Optical Flow Tracker using Lucas-Kanade Method

import numpy as np
import cv2

# Lucas-Kanade parameters
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Feature detection parameters
feature_params = dict(maxCorners=500, qualityLevel=0.3, minDistance=7, blockSize=7)


class OpticalFlowTracker:
    def __init__(self, video_src):
        self.source = video_src
        self.track_length = 10
        self.frame_index = 0
        self.detect_interval = 5
        self._tracks = []                # shape: (n_features, track_length, 2)
        self.curr = next(self.source)   # this can fail if source is empty

    @property
    def tracks(self):
        return self._tracks

    @property
    def features(self):
        return np.float32([track[-1] for track in self._tracks]).reshape(-1, 1, 2)

    @property
    def velocities(self):
        return self._calc_velocities()

    def tracking_loop(self):
        for image in self.source:
            if self._has_features():
                self.track_features()
            if self._needs_features():
                self.detect_features()
            self._update(image)
            yield

    def detect_features(self):
        """
        Static detection of good features with the Shi-Tomasi algorithm
        """
        gray_frame = cv2.cvtColor(self.curr, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(gray_frame)
        mask[:] = 255
        feature_points = cv2.goodFeaturesToTrack(gray_frame, mask=mask, **feature_params)
        if feature_points is not None:
            for x, y in np.float32(feature_points).reshape(-1, 2):
                self._tracks.append([(x, y)])

    def track_features(self):
        """
        Tracking points in both directions in time using the Lucas Kanade algorithm
        If the backtraced points are less than 1 pixel away from the initial feature
        The feature is considered good
        """
        MAX_PX_DIFFERENCE = 1

        prev_gray = cv2.cvtColor(self.prev, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(self.curr, cv2.COLOR_BGR2GRAY)
        # tracked_points = np.float32([track[-1] for track in self.tracks]).reshape(-1, 1, 2)
        tracked_points = self.features

        # Shape of forward tracked points is
        # (number of tracked points, 1, 2) where the 2 is the x and y coordinates
        forward_tracked_points, status, error = cv2.calcOpticalFlowPyrLK(
            prev_gray, curr_gray, tracked_points, None, **lk_params
        )
        backward_tracked_points, status, error = cv2.calcOpticalFlowPyrLK(
            curr_gray, prev_gray, forward_tracked_points, None, **lk_params
        )

        # We calculate the difference of the point arrays, reshape into (number of tracked differences, 2)
        # And take the maximum of the 2 values (x and y)
        # That is we take the maximum difference in EITHER x or y, not the combined difference
        backtrace_error_px = abs(tracked_points - backward_tracked_points).reshape(-1, 2).max(-1)
        features_filter = backtrace_error_px < MAX_PX_DIFFERENCE

        # For all points that are good features, add them to the new tracks
        new_tracks = []
        for track, (x, y), good_flag in zip(self._tracks, forward_tracked_points.reshape(-1, 2), features_filter):
            if good_flag:
                track.append((x, y))

                if len(track) > self.track_length:
                    del track[0]
                new_tracks.append(track)

        self._tracks = new_tracks

    def _has_features(self):
        return len(self._tracks) > 0

    def _needs_features(self):
        return self.frame_index % self.detect_interval == 0

    def _update(self, image):
        self.prev = self.curr
        self.curr = image
        self.frame_index += 1

    def _calc_velocities(self):
        velocities = []
        for track in self._tracks:
            if len(track) > 1:
                vel = np.array(track[-2]) - np.array(track[-1])
                velocities.append(vel)
            else:
                velocities.append(np.array([np.nan, np.nan]))

        return velocities

