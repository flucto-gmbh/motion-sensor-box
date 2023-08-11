import json
import os
import signal
import sys

from msb.config import load_config
from msb.network.zmq.publisher import Publisher, get_default_publisher
from msb.tof.config import TOFConf
from msb.tof.tf02pro import TF02Pro


def signal_handler(sig, frame):
    print("msb_tof.py exit")
    sys.exit(0)


# TODO warn when over 60°C, not with 100Hz!


class TOFService:
    def __init__(self, config: TOFConf, publisher: Publisher):
        self.config = config
        self.topic = config.topic
        self.publisher = publisher
        self.tf02pro = TF02Pro()

    def run(self):
        while True:
            raw_data = self.tf02pro.get_data()
            data = self.process_raw(raw_data)
            if data:
                self.publisher.send(self.topic, data)

    def process_raw(self, raw) -> dict:
        data = {key: val for key, val in zip(["epoch", "distance"], raw[:2])}
        # TODO check and filter data
        return data


def main():
    signal.signal(signal.SIGINT, signal_handler)
    tof_config = load_config(TOFConf(), "tof")
    publisher = get_default_publisher()
    tof = TOFService(tof_config, publisher)
    tof.run()
