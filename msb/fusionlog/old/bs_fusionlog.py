import zmq
import logging
import socket
import json
import sys
import pickle
import logging
from logging.handlers import RotatingFileHandler
from os import path
from os import makedirs
from datetime import datetime
# from logging.handlers import RotatingFileHandler

try:
    from fusionlog_config import init
except Exception as e:
    print(f'failed to load init from config: {e}')
    sys.exit(-1)

try:
    from interval_logger import (calc_interval_from_timestamp, get_interval_file_handle, update_interval_file_handle)
except Exception as e:
    print(f'failed to import from interval_logger: {e}')
    sys.exit(-1)

data_files = dict() # should contain file_handle, current_interval, log_dir

def main():

    config = init()

    print('msb_fusionlog.py starting up')

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'

    print(f'trying to bind zmq to {connect_to}')

    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.SUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)

    # let fusionlog subscribe to all available data
    zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
    
    print('successfully bound to zeroMQ receiver socket as subscriber')

    # create new logger instance
    data_dir = config['base_data_dir']
    # data_file_prefix = f'{socket.gethostname()}'

    if not path.exists(data_dir):
        try:
            makedirs(data_dir, exist_ok=True)
        except Exception as e:
            logging.fatal(f'failed to create log file dir: {data_dir}: {e}')
            sys.exit(-1)

    print(f'saving data to {data_dir}')
    
    print(f'entering endless loop')

    while True:

        # recv = zmq_socket.recv_pyobj()
        # [topic, data] = socket.recv_multipart()
        try:
            (id, payload) = zmq_socket.recv_multipart()
        except Exception as e:
            print(f'failed to receive message: {e}')
            continue

        id = id.decode('utf-8')

        try:
            payload = pickle.loads(payload)
        except Exception as e:
            print(f'failed to load pickle message, skipping: {e}')
            continue

        topic, data = [(t, d) for (t, d) in payload.items()][0]

        # check if a file handle exists for the given id
        if id not in data_files:

            print(f'{id} not in data_files, creating...')

            # create empty dict
            data_files[id] = dict()

            data_files[id]['log_dir'] = path.join(config['base_data_dir'], id)
            
            if not path.exists(data_files[id]['log_dir']):
                try:
                    makedirs(data_files[id]['log_dir'], exist_ok=True)
                except Exception as e:
                    print(f'failed to create log file dir: {data_files[id]["log_dir"]}: {e}')
                    sys.exit(-1)
            
            data_files[id]['current_interval'] = calc_interval_from_timestamp(
                data[0],
                dt_interval=config['logfile_interval']
            )

            data_files[id]['file_handle'] = get_interval_file_handle(
                interval = data_files[id]['current_interval'],
                log_file_prefix = id,
                log_dir = data_files[id]['log_dir'],
            )

            print(f'created data_file for {id}: {data_files[id]}')

        if data[0] >= data_files[id]['current_interval']:

            data_files[id]['current_interval'], data_files[id]['file_handle'] = update_interval_file_handle(
                current_interval = data_files[id]['current_interval'],
                current_file_handle = data_files[id]['file_handle'],
                log_file_prefix = id,
                log_dir = data_files[id]['log_dir']
            )
        
        data_files[id]['file_handle'].write(f'{json.dumps({topic : data})}\n')        

        # id is the motion sensor box id
        # data is a dictionary where the key denotes the type of data and 

        if config['print']: 
            print(f'{id} : {topic} : {data}')
               
if __name__ == '__main__':
    main()
