from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
import time
import uptime
from random import random


from msb.fusionlog.config import FusionlogConf


class TimeSeriesLogger:
    def __init__(self, topic : str, config: FusionlogConf):
        self.config = config
        self.topic: str = topic
        self.interval: int = self.config.logfile_interval
        self.lower_timelimit: float = 0.0 - self.interval
        self.upper_timelimit: float = 0
        self._filehandle = None
        self._filepath = None
        self.topic_data_dir = os.path.join(config.data_dir, topic)
        if not os.path.isdir(self.topic_data_dir):
            os.makedirs(self.topic_data_dir)
        self.data_keys = set()
        self.key_order = []

    def __del__(self):
        if self._filehandle and not self._filehandle.closed:
            self._filehandle.flush()
            self._filehandle.close()

    def write(self, data):
        if len(self.data_keys) == 0:
            self.data_keys = set(data.keys())

        if not self.data_keys == set(data.keys()):
            raise RuntimeError(
                "Keys of data to send do not match the keys of the first data sent."
            )

        data["datetime"] = self._ts2str(ts := data["epoch"], data.get("datetime_fmt"))

        if ts > self.upper_timelimit:
            self._update_filehandle(ts)

        # sort data values by key order and concatenate as str
        row = ",".join((str(data[key]) for key in self.key_order)) + "\n"
        try:
            self._filehandle.write(row)
        except Exception as e:
            print(f"failed to write data to filehandle {self._filepath}: {e}")
            sys.exit()

    def _update_filehandle(self, timestamp: float):
        if self._filehandle:
            self._filehandle.flush()
            self._filehandle.close()
        self._create_filehandle(timestamp)

    def _create_filehandle(self, timestamp: float):
        file_exists = False
        self._calc_timelimits(timestamp)
        self._filepath = os.path.join(
            self.topic_data_dir,
            "{}_{}_{}_{}.csv".format(
                self.config.serial_number.lower(),
                self.topic.lower(),
                self._ts2str(self.lower_timelimit, self.config.filename_datetime_fmt),
                self._ts2str(self.upper_timelimit, self.config.filename_datetime_fmt),
            ),
        )
        try:
            # check if we are appending to an already existing file
            if os.path.isfile(self._filepath):
                file_exists = True
            self._filehandle = open(self._filepath, "a")
        except Exception as e:  # TODO catch proper exception
            print(f"failed to open file handle {self._filepath}: {e}")
            sys.exit()
        else:
            # if we are appending to an already existing file,
            # do not write out the headers
            if not file_exists:
                self._write_header()

    def _calc_timelimits(self, timestamp: float):
        while timestamp > self.upper_timelimit:
            self.lower_timelimit = self.upper_timelimit
            self.upper_timelimit += self.interval

    def _default_key_order(self):
        time_keys = ["datetime", "epoch", "uptime"]
        sorted_keys = sorted(set(self.data_keys).difference(time_keys))
        return time_keys + sorted_keys

    def _write_header(self):
        if not self.key_order:
            try:
                self.key_order = self.config.key_order[self.topic]
            except KeyError:
                print(
                    f"warning: {self.topic} has no matching key order defined in config, using default key order."
                )
                self.key_order = self._default_key_order()

        self._filehandle.write(f"{','.join(self.key_order)}\n")

    @staticmethod
    def _ts2str(timestamp: float, datetime_fmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return (
            datetime.strftime(dt, datetime_fmt)
            if datetime_fmt is not None
            else dt.isoformat()
        )


if __name__ == "__main__":
    config = FusionlogConf()
    config.data_dir = f"/home/{os.getlogin()}/msb_data"
    # set the log interval to a small number to test overflowing of the interval
    config.logfile_interval = 60
    logger = TimeSeriesLogger("imu", config)
    while True:
        data = {
            "epoch": datetime.today().timestamp(),
            "uptime": uptime.uptime(),
        }
        data |= {
            key: random()
            for key in [
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
            ]
        }
        logger.write(data)
        time.sleep(0.1)
