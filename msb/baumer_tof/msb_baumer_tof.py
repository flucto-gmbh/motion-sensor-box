from __future__ import annotations

import signal
import sys
import time
import warnings

import numpy as np

from msb.baumer_tof.baumer import Baumer
from msb.baumer_tof.config import BAUMER_TOFConf
from msb.config import load_config
from msb.network.zmq.publisher import Publisher, get_default_publisher


def signal_handler(sig, frame):
    print("msb_baumer.py exit")
    sys.exit(0)


class AverageBuffer:
    def __init__(self, size: int):
        self.size: int = size
        self.counter: int = 0
        self._buffer: np.array = np.full(size, np.nan, np.float64)

    def push(self, val: float) -> float | None:
        if val is None:
            self.counter += 1
        else:
            self._buffer[self.counter] = val
            self.counter += 1

        if self.counter >= self.size:
            # compute avg
            avg = float(np.nanmean(self._buffer))
            # reset buffer
            self._buffer[:] = np.nan
            self.counter = 0
            return avg
        else:
            return None


class TOFService:
    def __init__(self, config: BAUMER_TOFConf, publisher: Publisher):
        self.config = config
        self.topic = config.topic
        self.publisher = publisher
        self.baumer = Baumer()
        self._points_per_average = config.points_per_average
        self._buffer = AverageBuffer(self._points_per_average)

    def run(self):
        while True:
            raw_data = self.baumer.get_data()

            data = self._calculate_average(raw_data)

            if data is not None:
                if self.config.print_stdout:
                    print(data)
                self.publisher.send(self.topic, data)

    def _calculate_average(self, raw):
        epoch, distance = raw
        if self.config.verbose:
            print(
                {
                    "epoch": epoch,
                    "distance": float(distance),
                }
            )

        avg_or_none = self._buffer.push(distance)
        if avg_or_none is None:
            return None
        else:
            return {"epoch": epoch, "distance": round(avg_or_none, 4)}


def main():
    signal.signal(signal.SIGINT, signal_handler)
    tof_config = load_config(BAUMER_TOFConf(), "baumer_tof")
    publisher = get_default_publisher()
    tof = TOFService(tof_config, publisher)
    tof.run()
