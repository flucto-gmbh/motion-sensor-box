import argparse
import json
from os import path
import signal
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.zmq_base import get_default_subscriber


def parse_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose output",
    )
    parser.add_argument(
        "-p",
        "--pretty-print",
        action="store_true",
        help="pretty print json output",
    )
    parser.add_argument(
        "-t",
        "--topic",
        type=str,
        help="topic to subscribe to",
    )

    return parser.parse_args()


def main():
    args = parse_user_input()
    topic = args.topic.encode("utf-8")

    sub = get_default_subscriber(topic)

    try:
        while True:
            _, data = sub.receive()
            print_stdout(data, args.pretty_print)
    except KeyboardInterrupt:
        print("msbpipe.py exit")
        sys.exit(0)


def print_stdout(data, pretty_print=False):
    if pretty_print:
        print(json.dumps(data, indent=4))
    else:
        print(data)


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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
