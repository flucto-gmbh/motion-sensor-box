import pickle
import pprint
import queue
import sys
import threading
import zmq

import logging.config

from driver import LoRaHatDriver
from config_lora import lora_hat_config, logging_config_dict
from message import TimeAttGPSMessage, DeserializeError

logging.config.dictConfig(logging_config_dict)

# overwrite basestation specifics in lora hat config
try:
    import config_basestation

    lora_hat_config.update(config_basestation.lora_hat_config)
except ImportError:
    pass


socket_name = "tcp://127.0.0.1:5555"

q = queue.Queue(maxsize=3)


def write_to_zeromq(socket_name):
    logging.info(f"binding to {socket_name} for zeroMQ IPC")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    with socket.connect(socket_name):
        logging.info("connected to zeroMQ IPC socket")

        while True:
            data_bin = q.get()
            try:
                message = TimeAttGPSMessage.from_bytes(data_bin)
            except DeserializeError as e:
                logging.error(e)
                continue
            logging.debug(str(message))
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
                ["lor".encode("utf-8"), pickle.dumps(data_dict), ]
            )


threading.Thread(target=write_to_zeromq, daemon=True, args=[socket_name]).start()

with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(f"LoRa hat config: {pprint.pformat(lora_hat.config)}")
    while True:
        q.put(lora_hat.receive(), block=False)
