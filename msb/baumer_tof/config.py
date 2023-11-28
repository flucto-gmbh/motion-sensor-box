from msb.config import MSBConf
from msb.tof.settings import TOFServiceOperationMode


class BAUMER_TOFConf(MSBConf):
    topic: bytes = b"baumer_tof"
    operation_mode: TOFServiceOperationMode = TOFServiceOperationMode.AVERAGING
    """Possible values are averaging or raw"""

    points_per_average: int = 100
    """The number of points to use for averaging (only used in mode TOFServiceOperationMode.AVERAGING).
    The raw data is sampled at about 100 Hz, so that 100 points_per_average result in roughly 1 average per second."""
