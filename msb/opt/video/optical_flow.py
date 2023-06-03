import cv2
import numpy as np

shi_tomasi_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

lucas_kanade_params = dict(
    winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
)


def good_features_to_track(image, params):
    return cv2.goodFeaturesToTrack(prev, mask=None, **shi_tomasi_params)


def optical_flow(prev, curr):
    """
    Sparse optical flow estimation using the Lucas-Kanade method.
    Uses features tracked by the Shi-Tomasi method.
    """
    features_prev = good_features_to_track(prev, shi_tomasi_params)

    mask = np.zeros_like(curr)

    features_curr, status, error = cv2.calcOpticalFlowPyrLK(prev, curr, features_prev, None, **lucas_kanade_params)

    good_features_prev = features_prev[status == 1]
    good_features_curr = features_curr[status == 1]

    for i, (new, old) in enumerate(zip(good_features_curr, good_features_prev)):
        new_point = new.ravel()
        old_point = old.ravel()
        a, b = new_point
        c, d = old_point
        print(i)
        print(f"new: {new_point}")
        print(f"old: {old_point}")
        mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), [0, 255, 0], 2)
        # curr = cv2.circle(curr, (a, b), 5, color[i].tolist(), -1)

    img = cv2.add(curr, mask)

    cv2.imshow("frame", img)
    cv2.waitKey(0)

    return (0, 50)


