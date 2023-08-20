from msb.config import MSBConf

class RawLoggerConf(MSBConf):

    data_dir: str = "/home/msb/msb_data/rawlog"

    filename_datetime_fmt: str = "%Y%m%dT%H%M%S%z"

    rollover_period: int = 3600
    """Temporal length in seconds of each logfile: 1h (3600s)"""

    excluded_topics: list[str] = ["sta"]
    """The topics to be excluded from log"""

    topics: list[str] = [""]
    """The topics to log."""