from msb.config import MSBConf


class TOFConf(MSBConf):
    topic: bytes = b"tof"
    # seconds_between_updates: float = 10.0
