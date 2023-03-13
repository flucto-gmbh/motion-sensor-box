import argparse
import json
import sys
import signal
import os

from os import path
from socket import gethostname

def signal_handler_exit(sig, frame):
    print('* msb_fusionlog: bye')
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
        help='prints the incoming data',
        default=False
    )

    arg_parser.add_argument(
        '--logfile',
        help='path to logfile',
        type=str,
        # default=f'/tmp/msb_fusionlog_{datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")}.log',
        default='',
    )

    arg_parser.add_argument(
        '--base-data-dir',
        help='directory to consistently store recorded data. Defaults to $HOME/msb_data',
        default=path.join(os.environ['HOME'], 'msb_data'),
        type=str,
    )

    arg_parser.add_argument(
        '--custom-data-dir',
        help='directory to consistently store recorded data',
        default=f'{gethostname()}',
        type=str,
    )

    arg_parser.add_argument(
        '--logfile-interval',
        help='length of each logfile in seconds',
        default=600,  
        type=int,
    )

    arg_parser.add_argument(
        '--max-number-data-files',
        help='maximum number of data files before roll over. Default is 5.',
        default=5,
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
    )

    arg_parser.add_argument(
        '--ipc-port',
        help='IPC port used by zeroMQ',
        default=5556,
        type=int
    )

    arg_parser.add_argument(
        '--ipc-protocol',
        help='the protocol used for IPC with zeroMQ',
        default='tcp://127.0.0.1',
        type=str,
    )

    return arg_parser.parse_args().__dict__

def init() -> dict:

    signal.signal(signal.SIGINT, signal_handler_exit)

    config = parse_arguments()

    print('msb_fusionlog.py parsing of configuration done')

    if config['config_file']:
        print('parsing config file')
        config = read_parse_config_file(config)
        print(f'updated config file: {config}')

    if config['dump_config_file']:
        print(f'dumping config file to {config["dump_config_file"]}')
        dump_config_file(config)
        
    return config
    
