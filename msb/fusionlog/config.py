from msb.config import MSBConf

_default_key_order = {
    "att": [
        "datetime",
        "epoch",
        "uptime",
        "roll",
        "roll_corr",
        "pitch",
        "pitch_corr",
    ],
    "imu": [
        "datetime",
        "epoch",
        "uptime",
        "acc_x",
        "acc_y",
        "acc_z",
        "rot_x",
        "rot_y",
        "rot_z",
        "mag_x",
        "mag_y",
        "mag_z",
        "temp",
    ],
    "gps": [
        "datetime",
        "epoch",
        "uptime",
        "gps_mode",
        "gps_timestamp",
        "latitude",
        "longitude",
        "altitude",
        "altitude_msl",
        "track",
        "mag_track",
        "mag_var",
        "speed",
    ],
    "pwr": [
        "datetime",
        "epoch",
        "uptime",
        "load-1",
        "load-5",
        "load-15",
        "mem-available",
        "swap-cached",
    ],
}

class FusionlogConf(MSBConf):
    data_dir: str = "/home/msb/msb_data"
    filename_datetime_fmt: str = "%Y%m%dT%H%M%S%z"
    logfile_interval: int = 3600
    """temporal length in seconds of each logfile: 1h (3600s)"""
    # logfile_interval : 10
    # """for testing purposes"""
    max_logfiles: int = 100
    """maximum number of logfiles before oldest logfiles get overwritten"""
    key_order: dict[str, list[str]] = _default_key_order
    topics: list[str] = ["imu", "gps"]
    """The topics to log."""
