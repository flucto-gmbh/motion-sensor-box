import os
import pickle
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig
from msb_config.zeromq import open_zmq_sub_socket

class FusionlogConfig(MSBConfig):
    def __init__(self, subconf = "msb-fusionlog"):
        super().__init__()
        self._load_conf(subconf=subconf)

class TemporalLogger():
    def __init__(self, topic, config):
        pass

    def write(data):
        pass
        
def get_data_dir(config : FusionlogConfig) -> str:
    if not os.path.isdir(config.data_dir):
        raise Exception("no such file or directory: {config.data_dir}")
    data_dir = os.path.join(config.data_dir, config.msb_sn)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

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
    data_dir = get_data_dir(config)
    loggers = dict()
    for topic, data in get_data(zmq_sub_socket):
        if config.print:
            print(f"{topic} : {data}")
        if not topic in fhandles:
            if config.verbose:
                print(f"not a logger yet: {topic}, creating")
            loggers[topic] = TemporalLogger(topic, config)
        loggers[topic].write()
        

if __name__ == "__main__":
    msb_fusionlog()
