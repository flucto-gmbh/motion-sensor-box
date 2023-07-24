from msb.config import MSBConf


class DewConf(MSBConf):
    topic: bytes = b"dew"
    seconds_between_updates: float = 10.0
