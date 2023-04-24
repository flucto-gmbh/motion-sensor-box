import socket
import logging
import sys
import json
import numpy as np
import time
import uptime
from threading import (Thread, Lock)

class IPhonePoller(Thread):

    def __init__(self, config : dict):
        super().__init__()

        self.port = config['udp_port']
        self.address = config['udp_address']
        self.new_data = False

        self._lock = Lock()
        self._loop = False
        self._data = {
            'accelerometerAccelerationX' : 0,
            'accelerometerAccelerationY' : 0,
            'accelerometerAccelerationZ' : 0,
            'gyroRotationX' : 0,
            'gyroRotationY' : 0,
            'gyroRotationZ' : 0,
            'magnetometerX' : 0,
            'magnetometerY' : 0,
            'magnetometerZ' : 0,
        }


        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            logging.fatal(f'failed to create UDP socket: {e}')
            sys.exit(-1)

        try:
            self._socket.bind((self.address, self.port))
        except Exception as e:
            logging.fatal(f'failed to bind to socket: {self.address, self.port}: {e}')
            sys.exit(-1)

    def __del__(self):
        try:
            self._socket.close()
        except Exception as e:
            logging.fatal(f'failed to close udp socket: {e}')
            sys.exit(-1)
        pass

    def run(self):
        self._loop = True

        while self._loop:
            # lock thread
            data, _ = self._socket.recvfrom(8192)
            data = data.decode('utf-8')
            print(f'{data}')
            try:
                self._data = json.loads(data)
            except Exception as e:
                logging.error(f'failed to load json: {e}')
                continue
            
            self.new_data = True

    def stop(self):
        self._loop = False
    
    def get_data(self, json=False) -> np.array:
        self.new_data = False
        if json:
            return self._data
        else:
            return [
                time.time(),
                uptime.uptime(),
                float(self._data['accelerometerAccelerationX']),
                float(self._data['accelerometerAccelerationY']),
                float(self._data['accelerometerAccelerationZ']),
                float(self._data['gyroRotationX']),
                float(self._data['gyroRotationY']),
                float(self._data['gyroRotationZ']),
                float(self._data['magnetometerX']),
                float(self._data['magnetometerY']),
                float(self._data['magnetometerZ']),
                30.0,
            ]
