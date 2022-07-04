#!/bin/env python
from multiprocessing import Process
import os
import pickle
import socket
import sys
import signal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.zeromq import open_zmq_sub_socket
from WifiConfig import WifiConfig

wifi_processes = dict()

def signal_handler(sig, frame):
    global wifi_processes
    for target, process in wifi_processes.items():
        print(f"stopping process {target} : {process}")
        process.kill()
    print('msb_wifi.py exit')
    sys.exit(0)

def construct_udp_socketstring(target : dict) -> str:
    pass

def get_data_zmqxpub(zmq_socket):
    while True:
        try:
            (topic, data) = zmq_socket.recv_multipart()
        except Exception as e:
            print(f'failed to receive message: {e}')
            continue
        topic = topic.decode('utf-8')
        try:
            data = pickle.loads(data)
        except Exception as e:
            print(f'failed to load pickle message, skipping: {e}')
            continue
        yield (topic, data)

def consume_send_msbdata(target : str, wifi_config : WifiConfig):
    # open udp socket to send msb data to
    # enter endless loop consuming msb data and sending data to udp target
    try:
        zmq_sub_socket = open_zmq_sub_socket(wifi_config.xpub_socketstring)
    except Exception as e:
        print(f"failed to connect to xpub zermoq socket: {e}")
        sys.exit(-1)
    if wifi_config.verbose:
        print('creating UDP socket')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        for topic, data in get_data_zmqxpub(zmq_sub_socket):
            if wifi_config.verbose:
                print(f"target {target}: received {topic} : {data}")
            try:
                udp_socket.sendto(
                    pickle.dumps({"msb-sn" : wifi_config.serialnumber, "payload" : {topic : data}}), 
                    (wifi_config.targets[target]["target_address"], wifi_config.targets[target]["target_port"])
                )
            except Exception as e:
                if wifi_config.verbose:
                    print(f"""failed to send data for target {target} \
{wifi_config.targets[target]['target_address']}:\
{wifi_config.targets[target]['target_port']}: {e}""")
                continue

def msb_wifi(wifi_config : WifiConfig):
    global wifi_processes
    for target, _ in wifi_config.targets.items():
        if wifi_config.verbose:
            print(f"setting up consumer process for target {target}")
        wifi_processes[target] = Process(target=consume_send_msbdata, args=(target, wifi_config,))
        wifi_processes[target].start()
    signal.pause()
        

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    wifi_config = WifiConfig()
    msb_wifi(wifi_config)

