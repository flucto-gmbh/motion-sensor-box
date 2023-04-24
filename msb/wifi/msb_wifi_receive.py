import zmq
import logging
import socket
import json
import sys
import pickle

def main():
    zmq_xsub_socketstring = f'tcp://127.0.0.1:5555'
    udp_socket_tuple = ("0.0.0.0", 9870)
    print(f'trying to bind zmq to {zmq_xsub_socketstring}')
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)
    try:
        zmq_socket.connect(zmq_xsub_socketstring)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)
    print('successfully bound to zeroMQ receiver socket as publisher')
    # open socket
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:
        logging.fatal('failed to open udp socket: {e}')
        sys.exit(-1)
    print(f'creating wifi udp socket: :{udp_socket_tuple}')
    print(f'binding to socket')
    udp_socket.bind(udp_socket_tuple)
    print('entering endless loop')
    while True:
        try:
            data, (ip, port) = udp_socket.recvfrom(1024)
        except Exception as e:
            print(f'failed to receive from {wifi_target}: {e}')
            continue
        data = pickle.loads(data)
        zmq_socket.send_multipart(
            [
                data['msb-sn'].encode('utf-8'),
                pickle.dumps(data['payload'])
            ]
        )
        print(f'{ip}:{port} {data}')

if __name__ == '__main__':
    main()
