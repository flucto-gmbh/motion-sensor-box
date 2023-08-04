from msb.config import MSBConf

class StupidlogConf(MSBConf):
    rollover_period : int = 3600
    topics: list[str] = ["imu", "gps"]
