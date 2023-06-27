from dataclasses import dataclass
from msb.config.MSBConfig import MSBConf


@dataclass
class CameraConf(MSBConf):
    topic: bytes = b"cam"
    fps: int = 10
    width: int = 1920
    height: int = 1080
    rollover_period: int = 600
    video_dir: str = "/home/msb/msb_data/camera"
    timeformat: str = "%Y%m%dT%H%M%S%z"
    font: dict = {"color": [0, 255, 0], "origin": [0, 30], "scale": 1, "thickness": 2}
