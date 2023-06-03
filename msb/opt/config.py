from msb.config.MSBConfig import MSBConf

class OptConf(MSBConf):
    """Configuration for the optical pile tracking service"""
    topic: bytes = b"opt"
    width: int = 1920
    height: int = 1080
    fps: int = 10
    max_tracks: int = 100
    show_video: bool = False
    show_roi: bool = False
    video_source: str = "picamera3"
    rotate: dict = {"center": (960,540), "angle": 0, "scale": 1.0}
    roi: dict = {"xmin": 100, "xmax" : 1820, "ymin": 100, "ymax": 980}


