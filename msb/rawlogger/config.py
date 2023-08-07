from msb.config import MSBConf

class RawLoggerConf(MSBConf):
    data_dir: str = "/home/msb/msb_data/rawlog"

    filename_datetime_fmt: str = "%Y%m%dT%H%M%S%z"

    rollover_period : int = 3600
    """Temporal length in seconds of each logfile: 1h (3600s)"""

    topics: list[str] = ["imu", "gps"]
    """The topics to log."""

