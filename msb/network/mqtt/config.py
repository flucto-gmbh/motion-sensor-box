from msb.config import MSBConf
from dataclasses import dataclass


@dataclass
class MQTTConf(MSBConf):
    """
    MQTT configuration class.
    """

    broker: str = "localhost"
    user: str = ""
    password: str = ""
    port: int = 1883
    ssl: bool = False
    qos: int = 0
    retain: bool = False
    topics: list[bytes] = ([],)
    mapping: str = "/msb/"
    packstyle: str = "json"
    max_saved_messages: int = 100
    timeout_s: int = 60
