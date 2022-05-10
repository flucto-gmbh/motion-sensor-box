import logging
import zmq
import sys
import time
import uptime
import pickle
from datetime import datetime

from os import path

try:
    from gps_config import (init, GPS_TOPIC)
except ImportError:
    raise Exception('failed to import init method')
    sys.exit(-1)

def gen_gps_message():
    return [ 
        time.time(),
        uptime.uptime(),
        {
          "class": "TPV",
          "device": "/dev/ttyACM0",
          "mode": 1,
          "timestamp" : time.time(),
          "leapseconds": 18,
          "lat" : 8.66645,
          "lon" : 53.5555,
          "alt" : 6.5546,
        }
    ]


def main():
    config = init()

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal('failed to connect to zeroMQ socket for IPC')
        sys.exit(-1)

    logging.debug(f'connected to zeroMQ IPC socket')

    logging.debug(f'entering endless loop')

    try:
        while True:
            # Do stuff
            data = gen_gps_message()
            if config['print']: print(f'gps: {data}')
            
            zmq_socket.send_multipart(
                [
                    GPS_TOPIC,
                    pickle.dumps(
                        data
                    )
                ]
            )

            time.sleep(1)
            # zmq_socket.send_pyobj(data)

    except StopIteration:
        logging.fatal("GPSD has terminated")

    except KeyboardInterrupt:
        logging.info('goodbye')
        sys.exit(0)


if __name__ == '__main__':
    main()

