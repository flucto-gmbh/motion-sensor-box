import picamera
from picamera.array import PiRGBArray # Generates a 3D RGB array

def setup_camera(piletrack_config : PileTrackConfig):
    """
    setup raspberry pi camera for recording
    """ 
    camera = picamera.PiCamera()
    camera.resolution = (piletrack_config.width, piletrack_config.height)
    camera.framerate = piletrack_config.fps
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = get_datetime_str()
    camera.annotate_text_size = 16

    return camera

def get_frame(camera, piletrack_config):
    raw_capture = PiRGBArray(camera, size=(piletrack_config.width, piletrack_config.height))
    for frame_id, frame in enumerate(camera.capture_continuous(raw_capture, format="bgr", use_video_port=True)):
        if piletrack_config.show_video:
            image = frame.array
            # Display the frame using OpenCV
            cv.imshow("Frame", image)
            # Wait for keyPress for 1 millisecond
            key = cv.waitKey(1) & 0xFF
        # clear stream for next frame
        raw_capture.truncate(0)
        yield (frame_id, frame)


