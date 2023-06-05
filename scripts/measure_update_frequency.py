#!/bin/python3

import argparse
import sys
from os import path

import numpy as np

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.zmq_base import get_default_subscriber


def parse_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--topic",
        type=str,
        default="",
        help="topic to subscribe to",
    )

    parser.add_argument(
        "-n", "--order", type=int, default=35, help="Order of moving average"
    )

    return parser.parse_args()


class MovingAverageBuffer:
    def __init__(self, order):
        self.order = order
        self.buffer = np.ones(order) * np.nan
        self.pointer = 0

    def _advance_pointer(self):
        self.pointer += 1
        if self.pointer >= self.order:
            self.pointer = 0

    def append(self, val: float):
        self.buffer[self.pointer] = val
        self._advance_pointer()

    def moving_average(self):
        return np.nanmean(self.buffer)


class Frequency:
    def __init__(self):
        self.last_timestamp = np.nan

    def update(self, ts):
        freq = 1 / (ts - self.last_timestamp)
        self.last_timestamp = ts
        return freq


def main():
    args = parse_user_input()
    topic = args.topic
    order = args.order

    sub = get_default_subscriber(topic)

    buffer = MovingAverageBuffer(order=order)
    frequency = Frequency()

    try:
        while True:
            topic, data = sub.receive()
            ts = data["epoch"]
            freq = frequency.update(ts)
            buffer.append(freq)
            print(
                f"topic={topic.decode('utf-8')}, last={freq:.1f} Hz, mov_avg={buffer.moving_average():.2f} Hz"
            )
    except KeyboardInterrupt:
        print("measure_update_frequency.py exit")
        sys.exit(0)


if __name__ == "__main__":
    main()
