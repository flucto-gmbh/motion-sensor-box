from __future__ import annotations

import signal
import sys
import time
import warnings

import numpy as np
from msb.config import load_config
from msb.network.zmq.publisher import Publisher, get_default_publisher
from msb.tof.config import TOFConf
from msb.tof.settings import TOFServiceOperationMode
from msb.tof.tf02pro import TF02Pro


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
        self.tf02pro = TF02Pro()
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
            raw_data = self.tf02pro.get_data()

            if self._operation_mode is TOFServiceOperationMode.AVERAGING:
                data = self._calculate_average(raw_data)
            else:
                data = self._unpack_raw(raw_data)

            if data is not None:
                if self.config.print_stdout:
                    print(data)
                self.publisher.send(self.topic, data)

    @staticmethod
    def _unpack_raw(raw: tuple[float, float, float, float]) -> dict:
        return {
            "epoch": raw[0],
            "distance": raw[1],
            "strength": raw[2],
            "temperature": raw[3],
        }

    def _warn_if_temperature_too_high(self, temp: float):
        # sensor is only reliable for temp below 60°C
        if temp > 60.0:
            # warn at most once per minute
            if time.time() - self._last_temperature_warning_time > 60:
                warnings.warn(f"Temperature temp={temp}°C is above 60°C.")

    def _calculate_average(self, raw: tuple[float, float, float, float]) -> dict | None:
        epoch, distance, strength, temperature = raw
        if self.config.verbose:
            print(
                {
                    "epoch": epoch,
                    "distance": distance,
                    "strength": strength,
                    "temperature": temperature,
                }
            )
        self._warn_if_temperature_too_high(temperature)
        if strength < self._minimum_signal_strength:
            distance = None
        avg_or_none = self._buffer.push(distance)
        if avg_or_none is None:
            return None
        else:
            return {"epoch": epoch, "distance": avg_or_none}


def main():
    signal.signal(signal.SIGINT, signal_handler)
    tof_config = load_config(TOFConf(), "tof")
    publisher = get_default_publisher()
    tof = TOFService(tof_config, publisher)
    tof.run()
