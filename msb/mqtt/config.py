from msb.config import MSBConf


class MQTTconf(MSBConf):
    """
    MQTT configuration class.
    """
    broker: str = "localhost"
    user: str = ""
    password: str = ""
    port: int = 1883
    ssl: bool = False
    qos: int = 0
    topics: list[bytes] = ([],)
    mapping: str = "/msb/"
    packstyle: str = "json"
