from dataclasses import dataclass
from msb.config.MSBConfig import MSBConf


class ZMQConf(MSBConf):
    verbose: bool = True
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


class PublisherSubscriberConf(ZMQConf):
    packer: str = "json"

    @property
    def producer_connection(self): # TODO rename/use publisher_address
        return f"{self.protocol}://{self.interface}:{self.publisher_port}"

    @property
    def consumer_connection(self): # TODO rename/use subscriber_address
        return f"{self.protocol}://{self.interface}:{self.subscriber_port}"
