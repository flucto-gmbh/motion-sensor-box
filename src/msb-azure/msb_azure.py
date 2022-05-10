# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient
import json
import os
from socket import gethostname
import sys
import time
import uuid

messages_to_send = 10

def create_client(verbose=False) -> IoTHubDeviceClient:
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    if not conn_str:
        print(f'empty connection string environment variable! please make sure, the correct environment variable containing the connecition string has been set')
        sys.exit()
    # The client object is used to interact with your Azure IoT hub.
    # if the websockets flag is set to True, MGTT via websockets will be used
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str, websockets=True)
    # Connect the client.
    # this can time out, so a time out exception must be catched. 
    device_client.connect()
    return device_client

def send_message(data : str, device_client : IoTHubDeviceClient, verbose=False):
    msg = Message()
    msg.data = data
    msg.message_id = uuid.uuid4()
    msg.correlation_id = ""
    msg.custom_properties["msb-sn"] = f"{gethostname()}"
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    device_client.send_message(msg)

def main():
    device_client = create_client()

    while True:
        send_message(json.dumps({"a" : "b"}), device_client)
        time.sleep(1)

    # Finally, shut down the client
    device_client.shutdown()


if __name__ == "__main__":
    main()

    # If using Python 3.6 use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
