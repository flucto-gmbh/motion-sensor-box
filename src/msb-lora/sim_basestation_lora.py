import itertools
import time
import pickle

import zmq
import numpy as np

import logging.config

from config_lora import logging_config_dict
from message import TimeAttGPSMessage, Topic

logging.config.dictConfig(logging_config_dict)


socket_name = "tcp://127.0.0.1:5555"

logging.info(f"binding to {socket_name} for zeroMQ IPC")
context = zmq.Context()
socket = context.socket(zmq.PUB)
with socket.connect(socket_name):
    logging.info("connected to zeroMQ IPC socket")
    sender_iter = itertools.cycle([150, 151, 153])
    while True:
        data = {
            "timestamp": np.array(
                [time.time()], dtype=TimeAttGPSMessage.timestamp_dtype
            ),
            "attitude": np.random.standard_normal(4).astype(
                TimeAttGPSMessage.attitude_dtype
            ),
            "gps": np.random.standard_normal(3).astype(
                TimeAttGPSMessage.attitude_dtype
            ),
        }
        sender = next(sender_iter)
        message = TimeAttGPSMessage(data, sender, topic=Topic.ATTITUDE_AND_GPS)
        data_dict = {
            "time": message.timestamp[0],
            "msb_serial_number": message.sender,
            "topic": "att_gps",
            "quat1": message.attitude[0],
            "quat2": message.attitude[1],
            "quat3": message.attitude[2],
            "quat4": message.attitude[3],
            "lat": message.gps[0],
            "lon": message.gps[1],
            "alt": message.gps[2],
        }
        socket.send_multipart(
            ["lor".encode("utf-8"), pickle.dumps(data_dict),]
        )
        time.sleep(0.3)
