import zmq
import logging
import socket
import json
import sys
import pickle

try:
    from wifi_config import init
except Exception as e:
    logging.fatal(f'failed to import init from wifi_config.py: {e}')

def main():

    config = init()

    logging.debug('msb_wifi.py starting up')

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port_subx"]}'

    logging.debug(f'trying to bind zmq to {connect_to}')

    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)
    
    logging.debug('successfully bound to zeroMQ receiver socket as publisher')

    # open socket
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:
        logging.fatal('failed to open udp socket: {e}')
        sys.exit(-1)

    logging.debug(f'creating wifi udp socket: {config["udp_address"]}:{config["udp_port"]}')
    wifi_target = (config["udp_address"], config["udp_port"])

    logging.debug(f'binding to socket')
    udp_socket.bind(wifi_target)

    logging.debug(f'entering endless loop')

    while True:

        # read data from udp socket

        try:
            data, (ip, port) = udp_socket.recvfrom(1024)
        except Exception as e:
            logging.error(f'failed to receive from {wifi_target}: {e}')
            continue

        data = pickle.loads(data)
        
        zmq_socket.send_multipart(
            [
                data['id'].encode('utf-8'),
                pickle.dumps(data['payload'])
            ]
        )

        if config['print']:
            print(f'{ip}:{port} {data}')
    
        # maybe implement tcp? any pros? any cons?

if __name__ == '__main__':
    main()
