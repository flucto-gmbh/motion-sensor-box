from datetime import datetime, timedelta, timezone
import os
import pickle
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig
from msb_config.zeromq import open_zmq_sub_socket

from FusionlogConfig import FusionlogConfig
from TimeSeriesLogger import TimeSeriesLogger

# TODO
# - quit gracefully
# - finding the initial intervals takes an aweful long time if the logging interval is short
# - currently, an existing file is overwritten!

       
def get_data(zmq_socket):
    while True:
        try:
            (topic, data) = zmq_socket.recv_multipart()
        except Exception as e:
            print(f'failed to receive message: {e}')
            continue
        topic = topic.decode('utf-8')
        try:
            data = pickle.loads(data)
        except Exception as e:
            print(f'failed to load pickle message, skipping: {e}')
            continue
        yield (topic, data)

def msb_fusionlog():
    print(f"parsing fusionlog config")
    config = FusionlogConfig()
    print(f"{config}")
    print(f"opening zermoq socket and subscribing to {config.zmq['xpub_connect_string']}")
    zmq_sub_socket = open_zmq_sub_socket(config.zmq['xpub_connect_string'])
    loggers = dict()
    for topic, data in get_data(zmq_sub_socket):
        if config.print:
            print(f"{topic} : {data}")
        if not topic in loggers:
            if config.verbose:
                print(f"not a logger yet: {topic}, creating")
            loggers[topic] = TimeSeriesLogger(topic, config)
        loggers[topic].write(data)

if __name__ == "__main__":
    msb_fusionlog()
