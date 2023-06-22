from dataclasses import dataclass

from msb.config.MSBConfig import MSBConf


@dataclass
class FugroSerialConfig:
    # example output 1685854601.000000,0.010,0.020,0.100,0.010,0.004,1.200
    format: str = "{}{}"
    baudrate: int = 9600
    databits: int = 8
    parity: int = 1
