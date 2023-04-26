from datetime import datetime, timezone
import gps
import logging

import sys
import time
import uptime

from msb.config import load_config
from msb.gps.config import GPSConf
from msb.zmq_base.Publisher import Publisher, get_default_publisher


zero_timestamp = datetime.fromtimestamp(0, tz=timezone.utc)


class GPSService:
    def __init__(self, config: GPSConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher
        self.gpsd_socket = self.open_gpsd_socket()

    def open_gpsd_socket(self):
        if self.config.verbose:
            print(f"connecting to gpsd socket")
        try:
            gpsd_socket = gps.gps(mode=gps.WATCH_ENABLE)
        except Exception:  # TODO limit exception
            print("failed to connect to gpsd")
            sys.exit(-1)
        if self.config.verbose:
            print(f"connected to gpsd socket")

        return gpsd_socket

    @staticmethod
    def prepare_data(report):
        data = {
            "datetime": datetime.fromtimestamp(
                ts := time.time(), tz=timezone.utc
            ).isoformat(),
            "epoch": ts,
            "uptime": uptime.uptime(),
        }
        report_keys = [
            "mode",
            "time",
            "lat",
            "lon",
            "altHAE",
            "altMSL",
            "track",
            "magtrack",
            "magvar",
            "speed",
        ]
        for key in report_keys:
            data[key] = report[key] if key in report else None

        return data

    def consume_send_gps_data(self):
        try:
            while True:
                report = self.gpsd_socket.next().__dict__
                if report["class"] == "TPV":
                    if self.config.verbose:
                        print(f"received TPV report {report}")
                    if report["mode"] == 0 and self.config.verbose:
                        print("no gps fix available")
                    self.publisher.send(
                        self.config.topic, data := self.prepare_data(report)
                    )
                    if self.config.print_stdout:
                        print(f",".join(map(str, data)))
        except StopIteration:
            logging.fatal("GPSD has terminated")
        except KeyboardInterrupt:
            logging.info("goodbye")
            sys.exit(0)

    def run(self):
        self.consume_send_gps_data()


def main():
    gps_config = load_config(GPSConf(), "gps")
    publisher = get_default_publisher()
    gps_service = GPSService(gps_config, publisher)
    gps_service.run()
