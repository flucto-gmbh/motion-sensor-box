from dataclasses import dataclass


@dataclass
class ZMQConf:
    protocol: str = "tcp"
    address: str = "127.0.0.1"
    producer_port: int = 5555
    consumer_port: int = 5556
    packer: str = "json"

    @property
    def producer_connection(self):
        return f"{self.protocol}://{self.address}:{self.producer_port}"

    @property
    def consumer_connection(self):
        return f"{self.protocol}://{self.address}:{self.consumer_port}"
