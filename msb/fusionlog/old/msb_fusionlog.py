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
    data_dir = path.join(config['base_data_dir'], config['custom_data_dir'] )
    data_file_prefix = f'{socket.gethostname()}'

    if not path.exists(data_dir):
        try:
            makedirs(data_dir, exist_ok=True)
        except Exception as e:
            logging.fatal(f'failed to create log file dir: {data_dir}: {e}')
            sys.exit(-1)

    print(f'saving data to {data_dir} with {data_file_prefix} as prefix')

    # waiting for first data to arrive
    while True:
        try:
            (topic, data) = zmq_socket.recv_multipart()
            data = pickle.loads(data)
            print(f'received first data: {data}')
            break
        except Exception as e:
            print(f'failed to receive message: {e} ({topic} : {data})')
            continue

    # now we have first data
    # the first field is always unix epoch
    current_interval = calc_interval_from_timestamp(
        data[0],
        dt_interval=config['logfile_interval']
    )

    print(f'current interval is: {current_interval}')

    data_file_handle = get_interval_file_handle(
        interval=current_interval,
        log_file_prefix=data_file_prefix,
        log_dir=data_dir,
    )

    print(f'created file handle: {data_file_handle}')
    
    print(f'entering endless loop')

    while True:

        # recv = zmq_socket.recv_pyobj()
        # [topic, data] = socket.recv_multipart()
        try:
            (topic, data) = zmq_socket.recv_multipart()
        except Exception as e:
            print(f'failed to receive message: {e}')
            continue

        topic = topic.decode('utf-8')

        try:
            data = pickle.loads(data)
        except Exception as e:
            print(f'failed to load pickle message, skipping: {e}')
            continue

        # log to data file
        # update file handle and interval if the time stamp overflows the current interval
        if data[0] >= current_interval:
            print(f'updating file handle and current interval')
            current_interval, data_file_handle = update_interval_file_handle(
                current_interval=current_interval,
                current_file_handle=data_file_handle,
                log_file_prefix=data_file_prefix,
                log_dir=data_dir,
                dt_interval=config['logfile_interval']
            )
            print(f'new interval: {current_interval}, new file handle: {data_file_handle}')

        # write out data 
        data_file_handle.write(f'{json.dumps({topic : data})}\n')

        if config['print']: 
            print(f'{topic}: {data}')
               
if __name__ == '__main__':
    main()
