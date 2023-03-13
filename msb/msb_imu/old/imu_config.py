import argparse
import json
import sys
import signal
import logging

from datetime import datetime
from os import path

IMU_TOPIC = "imu".encode('utf-8')

def signal_handler_exit(sig, frame):
    print('* msb_imu: bye')
    sys.exit(0)

def dump_config_file(config : dict):
    with open(config['dump_config_file'], 'w') as config_file_handle:
        config_file_handle.writelines(
            json.dumps(
                config,
                indent=4
            )
        )

def read_parse_config_file(config : dict) -> dict:

    try:
        config_file_handler = open(config['config_file'], 'r')
    except Exception as e:
        print(f'failed to open config file: {e}')
        sys.exit(-1)

    config_file_args = json.load(config_file_handler)

    for key, value in config_file_args.items():
        if key == 'config_file':
            continue

        if key in config:

            print(f'parsing {key} : {value}')
            config[key] = value
        else:
            print(f'key not found: {key} omitting')

    return config    
    # 1. read config file
    # 2. convert from json to dict
    # 3. iterate over entries in dictionary and override parsed arguments

# build a config named tuple

def parse_arguments() -> dict:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '--verbose',
        action='store_true',
        help='for debugging purposes'
    )

    arg_parser.add_argument(
        '--print',
        action='store_true',
        help='use this flag to print data to stdout'
    )

    arg_parser.add_argument(
        '--logfile',
        help='path to logfile',
        type=str,
        # default=f'/tmp/msb_imu_{datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")}.log',
        default="",
    )

    arg_parser.add_argument(
        '--imu-output-div',
        help='sensor output data rate. calculated by 1100/(1+output_data_div). default 54 (20 Hz)',
        default=54,
        type=int
    )

    arg_parser.add_argument(
        '--sample-rate',
        help='polling frequency with which data is retrieved from the sensor. must be >= ODR',
        default=20,
        type=int,
    )

    arg_parser.add_argument(
        '--acc-range',
        help=' ',
        default='2g',
        type=str,
    )

    arg_parser.add_argument(
        '--acc-filter',
        help='low pass filter to be applied to the raw data coming from the sensor. options are 1 - 6',
        default=1,
        type=int,
    )

    arg_parser.add_argument(
        '--gyro-range',
        help=' ',
        default='500dps',
        type=str,
    )

    arg_parser.add_argument(
        '--gyro-filter',
        help='low pass filter to be applied to the raw data coming from the gyro. options are 1 - 6',
        default=1,
        type=int,
    )

    arg_parser.add_argument(
        '--config-file',
        help='configuration file: overwrite all commandline options!',
        default='',
        type=str,
    )

    arg_parser.add_argument(
        '--dump-config-file',
        help='dumps the default config values into a file',
        default='',
    )

    arg_parser.add_argument(
        '--ipc-port',
        help='IPC port used to send data to msb_broker.service. Default is 5555',
        default=5555,
        type=int
    )

    arg_parser.add_argument(
        '--ipc-protocol',
        help='the protocol used for IPC with zeroMQ. Default is tcp://127.0.0.1',
        default='tcp://127.0.0.1',
        type=str,
    )

    arg_parser.add_argument(
        '--udp-address',
        help='Address to create an udp socket to allow streaming in of data from external sensors',
        default=None,
        type=str
    )

    arg_parser.add_argument(
        '--udp-port',
        help='port for local udp socket. Default is 5670',
        default=6666,
        type=int
    )

    arg_parser.add_argument(
        '--profile',
        help='profile flag',
        default=False,
        action='store_true'
    )

    arg_parser.add_argument(
        '--id',
        help='id to identify the imu by',
        default='imu',
        type=str
    )

    return arg_parser.parse_args().__dict__

def init() -> dict:

    signal.signal(signal.SIGINT, signal_handler_exit)

    config = parse_arguments()

    logging.basicConfig(
        filename=config['logfile'],
        level=logging.DEBUG if config['verbose'] else logging.WARNING,
        format='%(levelname)s: %(asctime)s %(message)s',
        datefmt='%Y%m%dT%H%M%S%z',
    )

    logging.debug('msb_imu.py parsing of configuration done')

    if config['config_file']:
        logging.debug('parsing config file')
        config = read_parse_config_file(config)
        logging.debug(f'updated config file: {config}')

    if config['dump_config_file']:
        logging.debug(f'dumping config file to {config["dump_config_file"]}')
        dump_config_file(config)

    return config
    
