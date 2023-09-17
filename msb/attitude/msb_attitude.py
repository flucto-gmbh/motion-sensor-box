import signal
import sys

from msb.config import load_config
from msb.attitude.config import AttitudeConf
from msb.attitude.filters import ComplementaryFilter
from msb.network import Subscriber, Publisher, get_subscriber, get_publisher


def signal_handler(sig, frame):
    print(f"received {sig} msb_attitude.py exit")
    sys.exit(0)


class AttitudeService:
    def __init__(
        self, config: AttitudeConf, subscriber: Subscriber, publisher: Publisher
    ):
        self.subscriber = subscriber
        self.publisher = publisher
        self.config = config
        self.filter = ComplementaryFilter(
            gain=self.config.gain, exp_gain=self.config.exp_gain
        )

    def run(self):
        while True:
            _, imu_data = self.subscriber.receive()
            rpy_data = self.filter.update(imu_data)
            self.publisher.send(self.config.topic, rpy_data)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    subscriber = get_subscriber("zmq", "imu")
    publisher = get_publisher("zmq")
    attitude_config = load_config(AttitudeConf(), "attitude")
    attitude = AttitudeService(attitude_config, subscriber, publisher)
    attitude.run()
