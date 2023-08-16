#!/bin/python3
import sys
import time
from os import path

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

from msb.network.zmq import get_default_publisher

if __name__ == "__main__":
    topic = input("Choose topic to publish to [test]: ")
    if not topic:
        topic = "test"
    publisher = get_default_publisher()
    print("Choose input mode:")
    print("1 - interactive mode")
    print("2 - repeat mode")
    mode = int(input("[1] : "))
    if not mode:
        mode = 1
    if mode == 1:
        while True:
            msg = input("Enter message: ")
            publisher.send(topic, msg)
            print(f"Sent {topic} : {msg}")
    elif mode == 2:
        msg = input("Enter message: ")
        while True:
            publisher.send(topic, msg)
            print(f"Sent {topic} : {msg}")
            time.sleep(1.0)

    else:
        print(f"Unknown mode {mode}. Exiting.")
