import argparse
import json
import sys
import signal
import logging

from datetime import datetime

ATTITUDE_TOPIC = "att".encode('utf-8')
IMU_TOPIC = "imu".encode('utf-8')
DELTAT = 0.1
TIME_STEP = 0.1

def signal_handler_exit(sig, frame):
    logging.info('* msb_attitude.py: bye')

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
        logging.error(f'failed to open config file: {e}')
        sys.exit(-1)

    config_file_args = json.load(config_file_handler)

    for key, value in config_file_args.items():
        if key == 'config_file':
            continue

        if key in config:

            logging.debug(f'parsing {key} : {value}')
            config[key] = value
        else:
            logging.debug(f'key not found: {key} omitting')

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
        default=''
    )

    arg_parser.add_argument(
        '--imu-output-div',
        help='sensor output data rate. calculated by 1100/(1+output_data_div). default 21 (100 Hz)',
        default=21,
        type=int
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
        '--broker-xsub',
        help='IPC port used by msb_broker to agglomerate data from primary producers',
        default=5555,
        type=int
    )

    arg_parser.add_argument(
        '--broker-xpub',
        help='IPC port used by msb_broker to broadcast data from primary producers',
        default=5556,
        type=int
    )

    arg_parser.add_argument(
        '--ipc-protocol',
        help='the protocol used for IPC with zeroMQ',
        default='tcp://127.0.0.1',
        type=str,
    )

    arg_parser.add_argument(
        '--sample-rate',
        help='sample rate of the imu data',
        default=10,
        type=int
    )

    arg_parser.add_argument(
        '--profile',
        help='profile flag',
        default=False,
        action='store_true'
    )

    return arg_parser.parse_args().__dict__

def init() -> dict:

    # register the signal hanlder function to be called upon when exiting
    signal.signal(signal.SIGINT, signal_handler_exit)

    # parse arguments from the command line
    config = parse_arguments()

    # create a logging file based on the command line
    logging.basicConfig(
        filename=config['logfile'],
        level=logging.DEBUG if config['verbose'] else logging.WARNING,
        format='%(levelname)s: %(asctime)s %(message)s',
        datefmt='%Y%m%dT%H%M%S%z',
    )

    logging.debug('msb_fusionlog.py commandline arguments parsed done')

    # if a config file was specified by the user, read it in and overwrite / extend
    # the config provided via command line arguments
    if config['config_file']:
        logging.debug('parsing config file')
        config = read_parse_config_file(config)
        logging.debug(f'updated config: {config}')

    # if the user requested to dump the config file, do it here
    if config['dump_config_file']:
        logging.debug(f'dumping config file to {config["dump_config_file"]}')
        dump_config_file(config)

    # return the configuration         
    return config
    
