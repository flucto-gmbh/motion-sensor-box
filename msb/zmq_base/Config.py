from dataclasses import dataclass
import json

@dataclass
class PublisherConfig:
    protocol: str = "tcp"
    address: str = "127.0.0.1"
    port = "5555"

    @property
    def connect_to(self): 
        return f"{self.protocol}://{self.address}:{self.port}"

@dataclass
class SubscriberConfig:
    topic: bytes = b"testtopic"
    protocol: str = "tcp"
    address: str = "127.0.0.1"
    port = "5556"

    @property
    def connect_to(self): 
        return f"{self.protocol}://{self.address}:{self.port}"

@dataclass
class ZMQConf:
    protocol : str = "tcp"
    address : str = "127.0.0.1"
    publisher_port : int = 5555
    subscriber_port : int = 5556
    packer : str = "json"

    @property
    def connect_to_publisher(self):
        return f"{self.protocol}://{self.address}:{self.publisher_port}"

    @property
    def connect_to_subscriber(self):
        return f"{self.protocol}://{self.address}:{self.subscriber_port}"
