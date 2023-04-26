import cv2
import contextlib


@contextlib.contextmanager
def video_context(*args, **kwargs):
    """
    Context manager for opencvs VideoCapture object
    """
    try:
        vid_stream = cv2.VideoCapture(*args, **kwargs)
        yield vid_stream
    finally:
        print("Video format context manager releasing video")
        vid_stream.release()


def video_format_source(video_file):
    with video_context(video_file) as video:
        while True:
            success, frame = video.read()
            if success:
                yield frame
            else:
                break
