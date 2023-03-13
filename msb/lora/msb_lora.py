import pickle
import pprint
from collections import deque
from datetime import datetime
from socket import gethostname
import sys
import threading
import time
import zmq

import numpy as np

import logging.config

from driver import LoRaHatDriver
from config_lora import lora_hat_config, logging_config_dict
from config_msb import msb_config
from message import Topic, TimeAttGPSMessage

logging.config.dictConfig(logging_config_dict)

# overwrite msb specifics in lora hat config
try:
    import config_msb

    lora_hat_config.update(config_msb.lora_hat_config)
except ImportError:
    pass


socket_name = "tcp://127.0.0.1:5556"
seconds_between_messages = 1

# thread safe, according to:
# https://docs.python.org/3/library/collections.html#collections.deque
attitude_buffer = deque(maxlen=1)
gps_buffer = deque(maxlen=1)

ATTITUDE_TOPIC = "att".encode("utf-8")
GPS_TOPIC = "gps".encode("utf-8")


def read_from_zeromq(socket_name):
    global attitude_buffer
    global gps_buffer
    logging.debug(f"trying to bind zmq to {socket_name}")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    try:
        with socket.connect(socket_name) as connected_socket:
            # subscribe to att and gps
            socket.setsockopt(zmq.SUBSCRIBE, ATTITUDE_TOPIC)
            socket.setsockopt(zmq.SUBSCRIBE, GPS_TOPIC)
            logging.debug("successfully bound to zeroMQ receiver socket as subscriber")

            while True:
                topic_bin, data_bin = socket.recv_multipart()
                if topic_bin == ATTITUDE_TOPIC:
                    attitude_buffer.append(data_bin)
                elif topic_bin == GPS_TOPIC:
                    gps_buffer.append(data_bin)
                else:
                    assert False

    except Exception as e:
        logging.critical(f"failed to bind to zeromq socket: {e}")
        sys.exit(-1)


threading.Thread(target=read_from_zeromq, daemon=True, args=[socket_name]).start()


sender_time_slot = msb_config["sender_time_slot"]


with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(f"LoRa hat config: {pprint.pformat(lora_hat.config)}")
    sender = int(gethostname()[4:8])
    while True:
        # time.sleep(seconds_between_messages)
        now = time.time()
        part = now - int(now)
        if not (int(now) % 4 == sender_time_slot):
            time.sleep(0.1)
            continue
        try:
            gps_data_bin = gps_buffer.pop()
        except IndexError:
            logging.debug("No new gps data to send")
            time.sleep(1)
            continue
        try:
            attitude_data_bin = attitude_buffer.pop()
        except IndexError:
            logging.debug("No new attitude data to send")
            time.sleep(1)
            continue

        attitude_data = pickle.loads(attitude_data_bin)
        gps_data = pickle.loads(gps_data_bin)
        # we only care about the dict (3rd entry) in gps_data
        gps_data = gps_data[2]

        assert len(attitude_data) == 5

        data = {
            "timestamp": np.array(
                [attitude_data[0]], dtype=TimeAttGPSMessage.timestamp_dtype
            ),
            "attitude": np.array(
                attitude_data[1:5], dtype=TimeAttGPSMessage.attitude_dtype
            ),
            "gps": np.array(
                [gps_data["lat"], gps_data["lon"], gps_data["alt"]],
                dtype=TimeAttGPSMessage.gps_dtype,
            ),
        }

        message = TimeAttGPSMessage(data, sender, topic=Topic.ATTITUDE_AND_GPS)

        lora_hat.send(message.serialize())
        time.sleep(1)
