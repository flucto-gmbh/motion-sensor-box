from dataclasses import dataclass

from msb.config.MSBConfig import MSBConf


@dataclass
class SerialConf(MSBConf):
    port: str = "/dev/serial0"
    baudrate: int = 9600
    bytesize: int = 8
    encoding: str = "ascii"
