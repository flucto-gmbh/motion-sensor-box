import argparse
import json
import os
import pickle
import signal
import sys

if not "MSB_SRC" in os.environ:
    raise Exception("please set the $MSB environment variable and try again")
sys.path.append(os.environ["MSB_SRC"])
from msb_config.MSBConfig import MSBConfig
from msb_config.zeromq import open_zmq_sub_socket


class MSBPipeConfig(MSBConfig):
    def __init__(self):
        super().__init__()
        setattr(self, "json", False)
        setattr(self, "verbose", False)
        setattr(self, "pretty_print", False)
        self._parse_cmdline_args()
        self._cmdline_config_override()

    def _parse_cmdline_args(self):
        args = argparse.ArgumentParser()
        args.add_argument(
            "--verbose", action="store_true", help="output debugging information"
        )
        args.add_argument(
            "--json", action="store_true", help="output zeromq traffic as json"
        )
        args.add_argument(
            "--pretty-print", action="store_true", help="pretty prints jsons"
        )
        cmdline_conf = args.parse_args().__dict__
        self._cmdline_conf = cmdline_conf

    def _cmdline_config_override(self):
        if self._cmdline_conf["verbose"]:
            self.verbose = True
        if self._cmdline_conf["json"]:
            self.json = True
        if self._cmdline_conf["pretty_print"]:
            self.pretty_print = True

def signal_handler(sig, frame):
    print("msbpipe.py exit")
    sys.exit(0)


def get_data_zmqxpub(zmq_socket):
    while True:
        try:
            (topic, data) = zmq_socket.recv_multipart()
        except Exception as e:
            print(f"failed to receive message: {e}")
            continue
        topic = topic.decode("utf-8")
        try:
            data = pickle.loads(data)
        except Exception as e:
            print(f"failed to load pickle message, skipping: {e}")
            continue
        yield (topic, data)


def print_json(topic, data):
    global config
    if not topic in config.topic_headers and config.verbose:
        print(f"not a valid topic header {topic}, skipping")
    assert len(len_topic_headers := config.topic_headers[topic]) == len(
        len_data := data
    ), f"length of topic headers {len_topic_headers} and length of data {len_data} do not match"
    dict_data = {
                topic: {
                    key: value
                    for key, value in zip(config.topic_headers[topic], map(str, data))
                }
            }
    if config.pretty_print:
        print(json.dumps(dict_data, indent=4))
    else:
        print(json.dumps(dict_data))



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    config = MSBPipeConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
    try:
        zmq_socket = open_zmq_sub_socket(config.xpub_socketstring)
    except Exception as e:
        print(f"failed to open zeromq socket {config.xpub_socketstring}: {e}")
    for topic, data in get_data_zmqxpub(zmq_socket=zmq_socket):
        if config.json:
            print_json(topic, data)
        else:
            print(f"{topic}: {data}")
