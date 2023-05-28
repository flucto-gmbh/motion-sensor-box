from msb.config.MSBConfig import MSBConf

class OptrConf(MSBConf):
    """Configuration for the optical pile tracking service"""
    topic: bytes = b"opt"
    width: int = 1920
    height: int = 1080
    fps: int = 10
    max_tracks: int = 10
    show_video: bool = False
    video_source: str = "picamera3"

