from datetime import datetime, timezone
import json
import os
import signal
import sys
import time

from msb.config import load_config
from msb.network import get_subscriber
from msb.network.packer import get_unpacker
from msb.network.pubsub.types import Subscriber
from msb.simplelog.config import SimplelogConf

def signal_handler(sig, frame):
    print("msb_fusionlog.py exit")
    sys.exit(0)


class SimplelogService:
    def __init__(self, config: SimplelogConf, subscriber: Subscriber):
        self.config = config
        self.subscriber = subscriber
        self._filehandle_creation_timstamp = time.time()
        self._create_filehandle(self._filehandle_creation_timstamp)


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
            writestring = json.dumps({topic : data})
            if self.config.print_stdout:
                print(writestring)
            self._filehandle.write(f"{writestring}\n")
            if (timestamp := time.time()) > (self._filehandle_creation_timstamp + self.config.rollover_period): 
                self._update_filehandle(timestamp)
                self._filehandle_creation_timstamp = timestamp


    def _update_filehandle(self, timestamp: float):
        if self._filehandle:
            self._filehandle.flush()
            self._filehandle.close()
        self._create_filehandle(timestamp)


    def _create_filehandle(self, timestamp: float):
        self._filepath = os.path.join(self.config.data_dir, self._create_logfilename(timestamp))
        try:
            self._filehandle = open(self._filepath, "a")
        except Exception as e:  # TODO catch proper exception
            print(f"failed to open file handle {self._filepath}: {e}")
            sys.exit()


    def _create_logfilename(self, timestamp: float):
        timestamp_str = datetime.strftime(
            datetime.fromtimestamp(timestamp, tz=timezone.utc), 
            self.config.filename_datetime_fmt
        )
        return f"{timestamp_str}_{self.config.serial_number}.json"


def main():
    signal.signal(signal.SIGINT, signal_handler)
    config = load_config(SimplelogConf(), "simplelog")
    config.unpacker = 'raw'
    subscriber = get_subscriber('zmq', topic=config.topics)
    # override unpacker defined in zmq.yaml config file
    subscriber.unpacker = get_unpacker('raw')
    simplelog_service = SimplelogService(config, subscriber)
    simplelog_service.run()
