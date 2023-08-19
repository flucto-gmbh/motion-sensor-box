import signal
import sys

from msb.config import load_config
from msb.network.zmq.config import ZMQConf
from msb.network.zmq.subscriber import ZMQRawSubscriber
from msb.rawlogger.config import RawLoggerConf 
from msb.rawlogger.rawlogger import RawLogger


def signal_handler(sig, frame):
    print("msb_rawlogger.py exit")

    sys.exit(0)


class RawLoggerService:
    def __init__(self, config: RawLoggerConf, subscriber: ZMQRawSubscriber, excluded_topics):
        self.excluded_topics = excluded_topics
        self.config = config
        self.subscriber = subscriber
        self.logger = RawLogger(config)
        print(self.logger,"self.logger")
        if self.config.verbose:
            print(self.config)

    def get_data(self,excluded_topics) -> tuple[bytes, bytes]:
        while True:
            try:
                (topic, data) = self.subscriber.receive()
            except Exception as e:  # TODO specify exception subclass
                print(f"failed to receive message: {e}")
                continue
            yield topic, data


    def run(self,excluded_topics):
        for topic, data_raw in self.get_data(excluded_topics):
            if topic.decode('utf-8') in excluded_topics:
                pass
            elif self.config.print_stdout:
                print(f"{topic.decode('utf-8')} : {data_raw.decode('utf-8')}")
            else:
                data = b'{"' + topic + b'":' + data_raw + b"}\n"
                self.logger.write(data)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    raw_logger_config = load_config(RawLoggerConf(), "rawlogger")
    zmq_config = load_config(ZMQConf(), "zmq")
    excluded_topics = raw_logger_config.excluded_topics
    subscriber = ZMQRawSubscriber(raw_logger_config.topics, zmq_config)
    raw_logger_service = RawLoggerService(raw_logger_config, subscriber,excluded_topics)
    raw_logger_service.run(excluded_topics)


