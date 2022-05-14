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
        
def get_data_dir(config : FusionlogConfig) -> str:
    if not os.path.isdir(config.data_dir):
        raise Exception("no such file or directory: {config.data_dir}")
    data_dir = os.path.join(config.data_dir, config.msb_sn)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_data() -> tuple:
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
        break
    return (topic, data)

def write_data(topic : str, data : str):
    global fhandles

def log_data(config : FusionlogConfig, zmq_sub_socket):
    fhandles = dict()
    while True:
        write_data(*get_data(zmq_sub_socket))

def msb_fusionlog():
    print(f"parsing fusionlog config")
    config = FusionlogConfig()
    print(f"{config}")
    print(f"opening zermoq socket and subscribing to {config.zmq['xpub_connect_string']}")
    zmq_sub_socket = open_zmq_sub_socket(config.zmq['xpub_connect_string'])
    data_dir = get_data_dir(config)
    log_data(config, zmq_sub_socket)

if __name__ == "__main__":
    msb_fusionlog()
