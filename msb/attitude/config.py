from msb.config import MSBConf
from dataclasses import dataclass

@dataclass
class AttitudeConf(MSBConf):

    """
    Attitude config class
    """
    gain: float = 0.9
    exp_gain: float = 0.25
    topic: bytes = b'rpy'
