import cv2
import contextlib


@contextlib.contextmanager
def webcam_context(*args, **kwargs):
    """
    Context manager for opencvs VideoCapture object
    """
    try:
        vid_stream = cv2.VideoCapture(*args, **kwargs)
        yield vid_stream
    finally:
        print("WebCamSource releasing video")
        vid_stream.release()


def webcam_source(cam_id):
    with webcam_context(cam_id) as video_stream:
        while True:
            success, frame = video_stream.read()
            if success:
                yield frame
            else:
                break
