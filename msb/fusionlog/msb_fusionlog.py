import signal
import sys


from msb.config import load_config
from msb.zmq_base.Subscriber import Subscriber, get_default_subscriber
from msb.fusionlog.config import FusionlogConf
from msb.fusionlog.TimeSeriesLogger import TimeSeriesLogger


def signal_handler(sig, frame):
    print("msb_fusionlog.py exit")
    sys.exit(0)


class FusionlogService:
    def __init__(self, config: FusionlogConf, subscriber: Subscriber):
        self.config = config
        self.subscriber = subscriber
        self.loggers = {}
        if self.config.verbose:
            print(self.config)

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
        if self.config.verbose:
            print(f"{self.config}")

        for topic, data in self.get_data():
            if self.config.print_stdout:
                print(f"{topic} : {data}")
            if topic not in self.loggers:
                if self.config.verbose:
                    print(f"not a logger yet: {topic}, creating")
                self.loggers[topic] = TimeSeriesLogger(topic, self.config)
            #self.loggers[topic].write(data)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    fusionlog_config = load_config(FusionlogConf(), "fusionlog")
    print(fusionlog_config)
    subscriber = get_default_subscriber(topic=b"")
    fusionlog_service = FusionlogService(fusionlog_config, subscriber)
    fusionlog_service.run()
