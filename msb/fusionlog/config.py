from msb.config import MSBConf

class FusionlogConf(MSBConf):
    data_dir: str = "/home/msb/msb_data"
    datetime_fmt: str = "%Y%m%dT%H%M%S%z"
    """temporal length in seconds of each logfile: 1h (3600s)"""
    logfile_interval: int = 3600
    # """for testing purposes"""
    # logfile_interval : 10
    """maximum number of logfiles before oldest logfiles get overwritten"""
    max_logfiles: int = 100
