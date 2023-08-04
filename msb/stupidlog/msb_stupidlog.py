import signal
import sys

from msb.config import load_config
from msb.network import get_subscriber
from msb.stupidlog.config import StupidlogConf

def signal_handler(sig, frame):
    print("msb_fusionlog.py exit")

    sys.exit(0)


class FusionlogService:
    def __init__(self, config: FusionlogConf, subscriber: Subscriber):
        self.config = config
        self.subscriber = subscriber

    def get_data(self):
        while True:
            try:
                (topic, data) = self.subscriber.receive()
            except Exception as e:
                print(f"failed to receive message: {e}")
                continue
            topic = topic.decode("utf-8")
            yield topic, data

    def run(self):
        for topic, data in self.get_data():
            if self.config.print_stdout:
                print(f"{topic} : {data}")
            # log here


def main():
    signal.signal(signal.SIGINT, signal_handler)
    config = load_config(StupidlogConf(), "stupidlog")
    subscriber = get_subscriber('zmq', topic=config.topics)
    stupidlog_service = StupidlogService(config, subscriber)
    fusionlog_service.run()
