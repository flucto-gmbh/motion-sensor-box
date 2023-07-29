#!/bin/python3

import argparse
import json
from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))


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
        default="",
        help="topic to subscribe to",
    )
    parser.add_argument(
        "-b",
        "--broker",
        type=str,
        default="",
        help="mqtt broker",
    )

    return parser.parse_args()


def main():
    from msb.network.config import MQTTConf
    from msb.network.mqtt.subscriber import MQTT_Subscriber

    args = parse_user_input()

    config = MQTTConf(broker=args.broker, verbose=args.verbose)

    topics = args.topic.split(",")

    sub = MQTT_Subscriber(topics, config)

    try:
        while True:
            topic, data = sub.receive()
            print_stdout(topic.decode(), data, args.pretty_print)
    except KeyboardInterrupt:
        print("msbpipe.py exit")
        sys.exit(0)


def print_stdout(topic, data, pretty_print=False):
    print(topic)
    if pretty_print:
        print(json.dumps(data, indent=4))
    else:
        print(data)


if __name__ == "__main__":
    main()
