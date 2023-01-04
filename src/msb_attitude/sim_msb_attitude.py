import zmq
import logging
import sys
from os import path
import time
from datetime import datetime
import pickle
import numpy as np

# add ahrs directory to PYTHONPATH

try:
    from attitude_config import (init, ATTITUDE_TOPIC, IMU_TOPIC)
except ImportError as e:
    print(f'failed to import: {e} - exit')
    sys.exit(-1)

def main():

    config = init()

    logging.debug('msb_attitude.py starting up')
    
    broker_xsub = f'{config["ipc_protocol"]}:{config["broker_xsub"]}'

    ctx = zmq.Context()
    socket_broker_xsub = ctx.socket(zmq.PUB)
    logging.debug(f'trying to connect to {broker_xsub}')
    try:
        socket_broker_xsub.connect(broker_xsub)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket {broker_xsub}: {e}')
        sys.exit(-1)
    logging.debug(f'successfully connected to broker XSUB socket as a publisher')

    while True:

        ts = time.time()

        data = np.empty(5)
        data[0] = ts
        data[1:] = np.random.random_sample(size=4)

        if config['print']:
            print(f'att: {data}')
        # save for next step
        socket_broker_xsub.send_multipart(
            [
                ATTITUDE_TOPIC,    # topic
                pickle.dumps( # serialize the payload
                    data.tolist()
                )
            ]
        )

        time.sleep(0.05)

        # recv = zmq_socket_sub.recv_pyobj()
        # [topic, data] = zmq_socket_sub.recv_multipart()
        # topic = topic.decode('utf-8')

        # if config['print']: 
        #     print(f'{pickle.loads(data)}')
       
if __name__ == '__main__':
    main()
