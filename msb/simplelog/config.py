from msb.config import MSBConf

class SimplelogConf(MSBConf):
    data_dir: str = "/home/msb/msb_data/simplelog"
    filename_datetime_fmt: str = "%Y%m%dT%H%M%S%z"
    rollover_period : int = 3600
    topics: list[str] = ["imu", "gps"]
    packstyle: str = "raw"
