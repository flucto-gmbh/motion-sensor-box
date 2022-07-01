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
    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port_pubx"]}'
    logging.debug(f'trying to bind zmq to {connect_to}')

    hostname = socket.gethostname()
    logging.debug(f'hostname is: {hostname}')

    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.SUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)

    # let fusionlog subscribe to all available data
    zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
    
    logging.debug('successfully bound to zeroMQ receiver socket as subscriber')

    # open socket
    logging.debug('creating UDP socket')
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:
        logging.fatal('failed to open udp socket: {e}')
        sys.exit(-1)

    wifi_target = (config["udp_address"], config["udp_port"])
    logging.debug(f'udp sicket target: {wifi_target}')

    logging.debug(f'entering endless loop')

    while True:

        # get data from zmq_socket
        try:
            [topic, data] = zmq_socket.recv_multipart()
        except Exception as e:
            logging.error(f'failed to receive data: {e}')
            continue
        
        # decode the topic as it is encoded as a bytestream (utf-8)
        try:
            topic = topic.decode('utf-8')
        except Exception as e:
            logging.error(f'failed to decode topic: {e}')
            continue
    
        # try to unpickle the data
        try:
            data = pickle.loads(data)
        except Exception as e:
            logging.error(f'failed to load pickle: {e}')
            continue
        
        # if the print flag has been set, print to stdout
        if config['print']: 
            print(f'{topic}: {data}')
        
        # try to send data to the specified ip via udp
        try:
            udp_socket.sendto(
                pickle.dumps( { "id" : hostname, "payload" : {topic : data}}), 
                wifi_target
            )
        except Exception as e:
            logging.error(f'failed to send to {wifi_target}: {e}')
            continue

        # maybe implement tcp? any pros? any cons?

if __name__ == '__main__':
    main()
