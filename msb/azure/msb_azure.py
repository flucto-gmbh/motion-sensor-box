# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient
from collections import deque
import json
import os
import pickle
from socket import gethostname
import sys
import threading
import time
import uuid
import zmq

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.parse import get_msb_config_filepath, parse_msb_config
from msb_config.zeromq import get_zmq_xpub_socketstring

messages_to_send = 10

imu_buffer = deque(maxlen=1)

def read_from_zeromq(socket):
    global imu_buffer
    try:
        while True:
            topic_bin, data_bin = socket.recv_multipart()
            imu_buffer.append(data_bin)

    except Exception as e:
        print(f"failed: {e}")
        sys.exit(-1)

async def create_client(verbose=False) -> IoTHubDeviceClient:
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = os.getenv("ACS")
    if not conn_str:
        print(f'empty connection string environment variable! please make sure, the correct environment variable containing the connecition string has been set')
        sys.exit()
    # The client object is used to interact with your Azure IoT hub.
    # if the websockets flag is set to True, MQTT via websockets will be used
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str, websockets=True)
    # Connect the client.
    # this can time out, so a time out exception must be catched. 
    await device_client.connect()
    return device_client

async def send_message(data : str, device_client : IoTHubDeviceClient, config : str, verbose=False):
    msg = Message(data)
    msg.message_id = uuid.uuid4()
    msg.correlation_id = ""
    msg.custom_properties["msb-sn"] = config['serialnumber']
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    await device_client.send_message(msg)

async def msb_azure():
    config = parse_msb_config(get_msb_config_filepath())
    connect_to = get_zmq_xpub_socketstring(config)
    print(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    s = ctx.socket(zmq.SUB)
    s.connect(connect_to)
    print(f'connected to zeroMQ IPC socket')
    s.setsockopt(zmq.SUBSCRIBE, b'imu')

    threading.Thread(target=read_from_zeromq, daemon=True, args=[s]).start()

    device_client = await create_client()
    while True:
        if len(imu_buffer) == 0:
            print(f'no imu data in buffer')
            time.sleep(0.01)
        else:
            data = pickle.loads(
                imu_buffer.pop()
            )
            await send_message(json.dumps(data), device_client, config)
            time.sleep(0.01)

    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(msb_azure())
