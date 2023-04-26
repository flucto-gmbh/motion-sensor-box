from msb.config import MSBConf


class GPSConf(MSBConf):
    topic: bytes = b"gps"
