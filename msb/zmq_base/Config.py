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

