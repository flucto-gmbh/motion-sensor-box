import zmq
import sys
import logging
import uptime
import time
import json
import pickle
import socket
from datetime import datetime, timezone
from math import sin, cos, pi

try:
    from IPhonePoller import IPhonePoller
except Exception as e:
    print(f'failed to import IPhonePoller')
    sys.exit(-1)

# needs python 3.10
# from dataclass import dataclass

try:
    from imu_config import (init, IMU_TOPIC)
except ImportError as e:
    print(f'failed to import init function from config.py: {e}')
    sys.exit(-1)

class IMU():

    """ ICM-20948

        : param address: I2C address to use for the motion sensor.
                         The sensor has two different possible addresses (0x68 and 0x69)
                         depending on wether AD0 is high (0x69) or low (0x68)
        : param i2c_bus: if an I2C bus has already been initiated somewehere else,
                         use this parameter to pass the bus object to the object.
        : return:        ICM20938 object
        : rtype:         Object
    """

    device_name = "ICM20948_SIM"
    _data_generator_process = None
    _delta_t = 0.2

    _acceleration_x_raw = _acceleration_y_raw = _acceleration_z_raw = 0
    _gyroscope_x_raw = _gyroscope_y_raw = _gyroscope_z_raw = 0
    _mag_x_raw = _mag_y_raw = _mag_z_raw = _mag_stat_1 = _mag_stat_2 = 0
    _temp_raw = 0
    _time = 0            # holds the time stamp at which the last sensor data was retrieved
    _uptime = 0     # holds the uptime at which the last sensor data was retrieved since boot
    _verbose = False

    def __init__(self):
        pass

    def __del__(self):
        pass

    def _update_data(self):

        """
        this funciton is regularly called by the data_generator_process to
        provide updated values of the simulated sensor
        """

        # logging.debug("updating data")
        self._time = time.time()
        self._uptime = uptime.uptime()
        self._acceleration_x_raw = self._acceleration_y_raw = self._acceleration_z_raw = sin(self._time*2*pi)
        self._gyroscope_x_raw = self._gyroscope_y_raw = self._gyroscope_z_raw = cos(self._time*2*pi)
        self._mag_x_raw = self._mag_y_raw = self._mag_z_raw = -1 * sin(self._time*2*pi)
        self._temp_raw = -1 * cos(self._time*2*pi*0.0001)

    def begin(self):
        pass
    
    @property
    def data(self):
        self._update_data()

        return [
            datetime.fromtimestamp(self._time, tz=timezone.utc),
            self._time,
            self._uptime,

            self._acceleration_x_raw,
            self._acceleration_y_raw,
            self._acceleration_z_raw,

            self._gyroscope_x_raw,
            self._gyroscope_y_raw,
            self._gyroscope_z_raw,

            self._mag_x_raw,
            self._mag_y_raw,
            self._mag_z_raw,

            self._temp_raw,
        ]

def setup_socket(config : dict):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((config['udp_address'], config['udp_port']))
    except Exception as e:
        logging.fatal(f'failed to bind to socket: {config["udp_address"], config["udp_port"]}')
        sys.exit(-1)
    return s
    
def read_from_socket(s : socket.socket):
    data = s.recv(4192)             # read data from socket
    data = data.decode('utf-8')     # decode from byte to string
    data = data.rstrip()            # remove trailing newline
    data = data.split(',')          # split into list
    data = list(map(float, data))   # convert all strings in the list to floats

    # [time, uptime, uptime_acc, acc_x, acc_y, acc_z, uptime_rot, rot_x, rot_y, rot_z, uptime_mag, mag_x, mag_y, mag_z]
    return [
        data[0],
        data[1],
        data[3],
        data[4],
        data[5],
        data[7],
        data[8],
        data[9],
        data[11],
        data[12],
        data[13],
        30.0,
    ]
 

def main():

    config = init()

    dt_sleep = 1/config['sample_rate']
    logging.debug(f'sample rate set to {config["sample_rate"]}, sleeping for {dt_sleep} s')

    logging.debug('inititating sensor..')
    imu = IMU()
    logging.debug('.. sensor init done')

    imu.begin()

    # connect_to = "tcp://127.0.0.1:5555"
    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    s.connect(connect_to)
    logging.debug('connected to zeroMQ IPC socket')

    # setting up udp socket if necessary
    if config['udp_address']:
        udp_socket = setup_socket(config)

    # logging.debug('creating iphone data poller')
    # iphone_poller = IPhonePoller(config)
    # iphone_poller.start()
    # logging.debug('successfully started iphone data poller')

    logging.debug('entering endless loop')
    try:
        while True:
            #data = {config['id'] : imu.get_data()}
            if config['udp_address']:
                data = read_from_socket(udp_socket)

                if not data:
                    logging.debug('failed to retrieve data from udp socket')
                    continue

            else:
                data = imu.data

            if config['print']:
                print(data)

            # s.send_pyobj(data)
            s.send_multipart(
                [
                    IMU_TOPIC,    # topic
                    pickle.dumps( # serialize the payload
                        data
                    )
                ]
            )

            time.sleep(0.05)
    except KeyboardInterrupt:
        logging.info('msb_imu bye')
        sys.exit(0)
    except Exception as e:
        logging.fata(f'caught an Exception: {e}')
        sys.exit(-1)
        

if __name__ == '__main__':
    main()

