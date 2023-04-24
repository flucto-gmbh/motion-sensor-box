import zmq
import logging
import socket
import json
import sys

try:
    from broker_config import init
except ImportError as e:
    print(f'failed to import init funtion: {e}')
    sys.exit(-1)

def main():

    config = init()

    # where all data comes in
    # subscriber = f'{config["ipc_protocol"]}:///tmp/msb:{config["subscriber_ipc_port"]}'
    # where the incoming data is routed to
    # publisher = f'{config["ipc_protocol"]}:///tmp/msb:{config["publisher_ipc_port"]}'

    # where all data comes in
    subscriber = f'{config["ipc_protocol"]}:{config["subscriber_ipc_port"]}'
    # where the incoming data is routed to
    publisher = f'{config["ipc_protocol"]}:{config["publisher_ipc_port"]}'


    logging.debug(f'subscriber: {subscriber}')
    logging.debug(f'publisher: {publisher}')

    ctx = zmq.Context()

    xpub = ctx.socket(zmq.XPUB)
    try:
        xpub.bind(publisher)
    except Exception as e:
        logging.fatal(f'failed to bind to publisher: {e}')
        sys.exit(-1)
    logging.debug(f'successully bound to publisher socket: {publisher}')
    
    xsub = ctx.socket(zmq.XSUB)
    try:
        xsub.bind(subscriber)
    except Exception as e:
        logging.fatal(f'failed to bin to subscriber: {e}')
        sys.exit(-1)
    logging.debug(f'successully bound to subscriber socket: {subscriber}')

    try:
        zmq.proxy(xpub, xsub)
    except Exception as e:
        logging.fatal(f'failed to create proxy: {e}')
        sys.exit(-1)
    logging.debug('successully created proxy between subscriber and publisher')


if __name__ == "__main__":
    main()
