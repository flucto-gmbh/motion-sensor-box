from msb.config import MSBConf


class RawLoggerConf(MSBConf):
    data_dir: str = "/home/msb/msb_data/rawlog"

    filename_datetime_fmt: str = "%Y%m%dT%H%M%S%z"

    rollover_period: int = 3600
    """Temporal length in seconds of each logfile: 1h (3600s)"""

    excluded_topics: list[str] = ["sta", "test"]
    """The topics to be excluded from log. Excluded topics will be removed if "topic" matches element of "excluded_topics", after subscribing to topics listed in included_topics."""

    included_topics: list[str] = [""]
    """Topics to subscribe. Using "" subscribes to all topics."""
