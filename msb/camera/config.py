from msb.config.MSBConfig import MSBConfig
from msb.config.MSBConfig import MSBConf

class CameraConf(MSBConf):
    topic: bytes = b"cam"
    fps: int = 10
    width: int = 1920
    height: int = 1080
    rollover_period: int = 600
    video_dir: str = "/home/msb/msb_data/cam"
    timeformat: str = "%Y%m%dT%H%M%S%z"
    serial_number: str = "msb"

