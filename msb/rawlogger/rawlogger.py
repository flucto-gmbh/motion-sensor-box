from __future__ import annotations

import os
import time

from datetime import datetime, timezone

from msb.rawlogger.config import RawLoggerConf


class RawLogger:

    def __init__(self, config: RawLoggerConf):
        self.config = config
        self.rollover: int = config.rollover_period
        self.lower_timelimit: float = 0.0 - self.rollover
        self.upper_timelimit: float = 0
        self._filehandle = None
        self._filepath = None
        self.data_dir = config.data_dir
        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

    def __del__(self):
        if self._filehandle and not self._filehandle.closed:
            self._filehandle.flush()
            self._filehandle.close()

    def _calc_timelimits(self, timestamp: float):
        while timestamp > self.upper_timelimit:
            self.lower_timelimit = self.upper_timelimit
            self.upper_timelimit += self.rollover

    @staticmethod
    def _ts2str(timestamp: float, datetime_fmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return (
            datetime.strftime(dt, datetime_fmt)
            if datetime_fmt is not None
            else dt.isoformat()
        )

    def _create_filehandle(self, timestamp: float):
        self._calc_timelimits(timestamp)
        self._filepath = os.path.join(
            self.data_dir,
            "{}_{}_{}.txt".format(
                self.config.serial_number.lower(),
                self._ts2str(self.lower_timelimit, self.config.filename_datetime_fmt),
                self._ts2str(self.upper_timelimit, self.config.filename_datetime_fmt),
            ),
        )
        try:
            self._filehandle = open(self._filepath, "ba")
        except Exception as e:  # TODO catch specific exception
            print(f"failed to open file handle {self._filepath}: {e}")
            raise e

    def _update_filehandle(self, timestamp: float):
        if self._filehandle:
            self._filehandle.flush()
            self._filehandle.close()
        self._create_filehandle(timestamp)

    def write(self, data: bytes):

        # This will not use the timestamp of the data to write, but the current time instead.
        # The alternative would be to search for the epoch in data.
        ts = time.time()

        if ts > self.upper_timelimit:
            self._update_filehandle(ts)

        try:
            self._filehandle.write(data)
        except Exception as e:
            print(f"failed to write data to filehandle {self._filepath}: {e}")
            raise e
