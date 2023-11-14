from __future__ import annotations

import signal
import sys
import time
import warnings

import numpy as np
from msb.config import load_config
from msb.network.zmq.publisher import Publisher, get_default_publisher
from msb.sharp_tof.config import TOFConf
from msb.sharp_tof.settings import TOFServiceOperationMode
from msb.sharp_tof.sharp_GP2D12 import GP2D12


def signal_handler(sig, frame):
    print("msb_tof.py exit")
    sys.exit(0)


# TODO warn when over 60°C, not with 100Hz!


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
    def __init__(self, config: TOFConf, publisher: Publisher):
        self.config = config
        self.topic = config.topic
        self.publisher = publisher
        self.gp2d12 = GP2D12()
        self._operation_mode: TOFServiceOperationMode = config.operation_mode
        if self._operation_mode is TOFServiceOperationMode.AVERAGING:
            self._points_per_average = config.points_per_average
            self._buffer = AverageBuffer(self._points_per_average)
            self._minimum_signal_strength = config.minimum_signal_strength
            self._last_temperature_warning_time: float = 0.0
        else:
            self._points_per_average = None
            self._buffer = None
            self._minimum_signal_strength = None

    def run(self):
        while True:
            raw_data = self.gp2d12.get_data()
            if self._operation_mode is TOFServiceOperationMode.AVERAGING:
                data = self._calculate_average(raw_data)
                print("AVERAGING")
            else:
                data = self._unpack_raw(raw_data)

            if data is not None:
                if self.config.print_stdout:
                    print(data)
                self.publisher.send(self.topic, data)

    @staticmethod
    def _unpack_raw(raw) -> dict:
        return {
            "epoch": raw[0],
            "distance": raw[1],
        }

    def _calculate_average(self, raw):
        distance = raw
        if self.config.verbose:
            print(
                {
                    "distance": distance,
                    }
            )

        avg_or_none = self._buffer.push(distance)
        if avg_or_none is None:
            return None
        else:
            return {"epoch": epoch, "distance": round(avg_or_none, 4)}


def main():
    signal.signal(signal.SIGINT, signal_handler)
    tof_config = load_config(TOFConf(), "tof")
    publisher = get_default_publisher()
    tof = TOFService(tof_config, publisher)
    tof.run()
