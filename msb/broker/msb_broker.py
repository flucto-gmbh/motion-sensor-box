import signal
import sys
import zmq

from .BrokerConfig import BrokerConfig

def signal_handler(sig, frame):
    print('msb_broker.py exit')
    sys.exit(0)

def msb_broker(broker_config : BrokerConfig):
    if broker_config.verbose:
        print("creating zmq context object")
    ctx = zmq.Context()
    if broker_config.verbose:
        print("creating xpub socket")
    xpub = ctx.socket(zmq.XPUB)
    if broker_config.verbose:
        print("creating zsub socket")
    xsub = ctx.socket(zmq.XSUB)
    try:
        xpub.bind(broker_config.zmq["xpub_connect_string"])
    except Exception as e:
        print(f'failed to bind to publisher: {e}')
        sys.exit(-1)
    if broker_config.verbose:
        print(f'successully bound to publisher socket: {broker_config.zmq["xpub_connect_string"]}')
    try:
        xsub.bind(broker_config.zmq["xsub_connect_string"])
    except Exception as e:
        print(f'failed to bin to subscriber: {e}')
        sys.exit(-1)
    if broker_config.verbose:
        print(f'successully bound to subscriber socket: {broker_config.zmq["xsub_connect_string"]}')
    try:
        if broker_config.verbose:
            print("creating proxy")
        zmq.proxy(xpub, xsub)
    except Exception as e:
        print(f'failed to create proxy: {e}')
        sys.exit(-1)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    broker_config = BrokerConfig()
    msb_broker(broker_config)
