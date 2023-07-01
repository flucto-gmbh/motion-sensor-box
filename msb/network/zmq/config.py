from dataclasses import dataclass
from msb.config.MSBConfig import MSBConf


@dataclass
class ZMQConf(MSBConf):
    protocol: str = "tcp"
    interface: str = "127.0.0.1"
    publisher_port: int = 5555
    subscriber_port: int = 5556

    @property
    def publisher_address(self):
        return f"{self.protocol}://{self.interface}:{self.publisher_port}"

    @property
    def subscriber_address(self):
        return f"{self.protocol}://{self.interface}:{self.subscriber_port}"
