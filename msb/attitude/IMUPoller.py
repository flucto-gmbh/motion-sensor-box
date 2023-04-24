from threading import Thread
import logging
import pickle
import zmq


class IMUPoller(Thread):

    def __init__(self, topic : str, config : dict, context : zmq.Context):
        super().__init__()
        
        self.new_data = False
        
        #    time, uptime, acc_x, acc_y, acc_z, rot_x, rot_y, rot_z, mag_x, mag_y, mag_z, temp
        self._data = [0] * 12
        self._loop = False
        self._topic = topic
        self._config = config

        # connect to xpub socket from broker here
        # set the context 

        self._zmq_ctx = context
        self._connect_to = f'{self._config["ipc_protocol"]}:{self._config["broker_xpub"]}'
        self._zmq_socket = self._zmq_ctx.socket(zmq.SUB)

        try:
            self._zmq_socket.connect(self._connect_to)
        except Exception as e:
            logging.fatal(f'failed to connect to broker XPUB socket {self._zmq_socket}: {e}')

        logging.debug(f'connected to broker XPUB socket: {self._connect_to}')

        self._zmq_socket.setsockopt_string(zmq.SUBSCRIBE, self._topic)

    def __del__(self):
        try:
            self._zmq_socket.close()
        except Exception as e:
            logging.error(f'failed to close broker XPUB socket: {e}')


    def run(self):
        self._loop = True
        while self._loop:
            [topic, data] = self._zmq_socket.recv_multipart()
            self.new_data = True
            self._data = pickle.loads(data)
            
            # if self._config['print']:
            #     print(f'{topic}: {self._data}')

    def get_data(self):
        self.new_data = False
        return self._data
        
        
    def stop(self):
        self._loop = False
