from datetime import datetime, timedelta, timezone
import os
import sys
import time
import uptime
from random import random

from msb.fusionlog.config import FusionlogConf


class TimeSeriesLogger:
    def __init__(self, topic, config: FusionlogConf):
        self.config = config
        # self.msb_sn = self.config.serial_number
        self.topic = str(topic)
        self.interval = timedelta(seconds=self.config.logfile_interval)
        self.lower_timelimit = (
            datetime.fromtimestamp(0, tz=timezone.utc) - self.interval
        )
        self.upper_timelimit = datetime.fromtimestamp(0, tz=timezone.utc)
        self._filehandle = None
        self._filepath = None
        self.topic_data_dir = os.path.join(config.data_dir, topic)
        if not os.path.isdir(self.topic_data_dir):
            os.makedirs(self.topic_data_dir)

    def __del__(self):
        if self._filehandle and not self._filehandle.closed:
            self._filehandle.flush()
            self._filehandle.close()

    def write(self, data):
        # TODO data[0] does not exist for new json data
        # data["datetime"] is str not datetime object
        # we would need to use e.g. datetime.fromisoformat(data["datetime"])
        # or datetime.strptime(data["datetime"], data["datetime_fmt"])

        # data is a dict now, where the data timestamp is a unix epoch
        # found at data['timestamp']
        if (timestamp := datetime.fromtimestamp(data['epoch'], tz=timezone.utc)) > self.upper_timelimit:
            self._update_filehandle(timestamp)
        try:
            #self._filehandle.writelines("{}\n".format(",".join(map(str, data))))
            self._filehandle.writelines("{}\n".format(",".join(map(str, data))))
        except Exception as e:
            print(f"failed to write data to filehandle {self._filepath}: {e}")
            sys.exit()

    def _update_filehandle(self, timestamp: datetime):
        if self._filehandle:
            self._filehandle.flush()
            self._filehandle.close()
        self._create_filehandle(timestamp)

    def _create_filehandle(self, timestamp: datetime):
        file_exists = False
        self._calc_timelimits(timestamp)
        self._filepath = os.path.join(
            self.topic_data_dir,
            "{}_{}_{}_{}.csv".format(
                self.config.serial_number.lower(),
                self.topic.lower(),
                self._ts2str(self.lower_timelimit),
                self._ts2str(self.upper_timelimit),
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

    def _calc_timelimits(self, timestamp: datetime):
        while timestamp > self.upper_timelimit:
            self.lower_timelimit = self.upper_timelimit
            self.upper_timelimit += self.interval

    def _write_header(self):
        pass
        # TODO update to new dict/json data
        # if not self.topic in self.config.topic_headers:
        #     print(
        #         f"warning: {self.topic} has no matching header defined in {self.config._conf_fpath}"
        #     )
        #     return
        # self._filehandle.write(
        #     "{}\n".format(",".join(self.config.topic_headers[self.topic]))
        # )

    def _ts2str(self, timestamp: datetime) -> str:
        try:
            return timestamp.strftime(self.config.datetime_fmt)
        except Exception as e:
            print(f"failed to convert to string: {timestamp}: {e}")
            sys.exit()


if __name__ == "__main__":
    config = FusionlogConf()
    # set the log interval to a small number to test overflowing of the interval
    config.logfile_interval = 60
    logger = TimeSeriesLogger("imu", config)
    while True:
        data = [
            datetime.fromtimestamp(ts := time.time(), tz=timezone.utc),
            ts,
            uptime.uptime(),
            *[random() for i in range(9)],
        ]
        logger.write(data)
        time.sleep(0.1)
