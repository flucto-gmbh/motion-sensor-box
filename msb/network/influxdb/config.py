from dataclasses import dataclass
from msb.config import MSBConf


@dataclass
class InfluxDBConf(MSBConf):
    host: str = "localhost"
    port: int = "8086"
    bucket: str = "test"
    org: str = "test"
    read_token: str = ""
    write_token: str = ""
    all_access_token: str = ""
