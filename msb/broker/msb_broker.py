import signal
import sys
import zmq

from msb.broker.config import BrokerConf
from msb.config import load_config

def signal_handler(sig, frame):
    print('msb_broker.py exit')
    sys.exit(0)


def msb_broker(config : BrokerConf):
    # xsub binds to publisher address/port
    xsub_address = config.publisher_address
    # xpub binds to subscriber address/port
    xpub_address = config.subscriber_address
    if config.verbose:
        print("creating zmq context object")
    ctx = zmq.Context()
    if config.verbose:
        print("creating xpub socket")
    xpub = ctx.socket(zmq.XPUB)
    if config.verbose:
        print("creating zsub socket")
    xsub = ctx.socket(zmq.XSUB)
    try:
        xpub.bind(xpub_address)
    except Exception as e: # TODO limit exceptions
        print(f'failed to bind to publisher: {e}')
        sys.exit(-1) # TODO why use -1?
    if config.verbose:
        print(f'successfully bound to publisher socket: {xpub_address}')
    try:
        xsub.bind(xsub_address)
    except Exception as e:
        print(f'failed to bin to subscriber: {e}')
        sys.exit(-1)
    if config.verbose:
        print(f'successully bound to subscriber socket: {xsub_address}')
    try:
        if config.verbose:
            print("creating proxy")
        zmq.proxy(xpub, xsub)
    except Exception as e:
        print(f'failed to create proxy: {e}')
        sys.exit(-1)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    broker_config = load_config(BrokerConf(), "zmq")
    msb_broker(broker_config)
