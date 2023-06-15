from msb.config import MSBConf

class AttitudeConf(MSBConf):

    """
    Attitude config class
    """
    gain: float = 0.9
    exp_gain: float = 0.25
    topic: bytes = b'rpy'
