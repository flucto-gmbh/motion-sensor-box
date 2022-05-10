import zmq
import logging
import sys
from os import path
import pickle
import numpy as np
import time
import threading
from collections import deque
import math


try:
    from attitude_config import (init, ATTITUDE_TOPIC, IMU_TOPIC, TIME_STEP)
except ImportError as e:
    print(f'failed to import: {e} - exit')
    sys.exit(-1)

imu_buffer = deque(maxlen=1)

def read_from_zeromq(socket):
    logging.debug(f'in consumer thread')
    global imu_buffer
    try:
        while True:
            topic_bin, data_bin = socket.recv_multipart()
            logging.debug(f'received {topic_bin}')
            imu_buffer.append(data_bin)

    except Exception as e:
        logging.critical(f"failed: {e}")
        sys.exit(-1)


def main():

    config = init()

    logging.debug('msb_attitude.py starting up')
    
    broker_xsub = f'{config["ipc_protocol"]}:{config["broker_xsub"]}'
    broker_xpub = f'{config["ipc_protocol"]}:{config["broker_xpub"]}'

    ctx = zmq.Context()
    socket_broker_xsub = ctx.socket(zmq.PUB)
    logging.debug(f'trying to connect to {broker_xsub}')
    try:
        socket_broker_xsub.connect(broker_xsub)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket {broker_xsub}: {e}')
        sys.exit(-1)
    logging.debug(f'successfully connected to broker XSUB socket as a publisher')

    socket_broker_xpub = ctx.socket(zmq.SUB)
    logging.debug(f'trying to connect to {broker_xpub}')
    try:
        socket_broker_xpub.connect(broker_xpub)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket {broker_xpub}: {e}')
        sys.exit(-1)
    logging.debug(f'successfully connected to broker XPUB socket as a subscriber')

    socket_broker_xpub.setsockopt(zmq.SUBSCRIBE, IMU_TOPIC)

    logging.debug(f'starting imu consumer thread')
    threading.Thread(target=read_from_zeromq, daemon=True, args=[socket_broker_xpub]).start()

    t_old = time.time()
    t_cur = time.time()
    t_int_old = time.time()
    t_int_cur = time.time()
    dt_int = 0.1
    dt_sleep = 0.001
    pitch = 0
    pitch_corr = 0
    roll = 0
    roll_corr = 0

    try:
        while True:

            # check if data is available in the deque
            if len(imu_buffer) == 0:
                logging.debug(f'no imu data in buffer')
                time.sleep(0.001)
                continue
            
            # calculate dt
            t_cur = time.time()
            dt = t_cur - t_old           

            data = pickle.loads(
                imu_buffer.pop()
            )

            imu_time = data[0]
            acc = data[2:5]
            gyr = data[5:8]
            mag = data[8:11]

            t_int_cur = imu_time
            dt_int = t_int_cur - t_int_old
            t_int_old = t_int_cur

            if config['print']:
                print(f'time : {imu_time} acc : {acc} gyr : {gyr} mag : {mag}')

            # remove constant offset from gyro data
            # low pass filter gyro data

            # temporally integrate rotation
            pitch += gyr[0]*dt_int
            roll += gyr[1]*dt_int

            # Only use accelerometer when it's steady (magnitude is near 1g)
            force_magnitude = math.sqrt(acc[0]**2 + acc[1]**2 + acc[2]**2)
            if force_magnitude > 0.95 and force_magnitude < 1.05:
                logging.debug(f'correcting angles: {force_magnitude}')
                
                pitch_corr = math.atan2(-1*acc[1], -1*acc[2])*(180/math.pi)
                logging.debug(f'pitch acc: {pitch_corr}')
                pitch = (pitch * 0.9) + (pitch_corr * 0.1)
                
                roll_corr = math.atan2(acc[0], -1*acc[2])*(180/math.pi)
                logging.debug(f'roll acc: {roll_corr}')
                roll = (roll * 0.9) + (roll_corr * 0.1)

            else:
                logging.debug(f'exceeding acceleration magnitude: {force_magnitude}')

            p = (pitch*180/math.pi)
            r = (roll*180/math.pi)
            if config['print']:
                print(f'pitch: {p} roll: {r}')

            # print received data if --print flag was set
            # if config['print']:
            #     print(f'imu: {data}')

            # save for next step
            socket_broker_xsub.send_multipart(
                [
                    ATTITUDE_TOPIC,    # topic
                    pickle.dumps( # serialize the payload
                        [imu_time, pitch, roll, pitch_corr, roll_corr]
                    )
                ]
            )

            dt_sleep = (t_cur + TIME_STEP) - time.time()
            if dt_sleep > 0:
                logging.debug(f'sleeping for {dt_sleep} s')
                time.sleep(dt_sleep)
            
            #while (tt := time.time() - t_cur) < TIME_STEP:
            #    logging.debug(f'sleeping {tt}')
            #    time.sleep(0.001)

            t_old = t_cur


    except Exception as e:
        logging.fatal(f'received Exception: {e}')
        logging.fatal('cleaning up')

        socket_broker_xpub.close()
        socket_broker_xsub.close()
        ctx.terminate()

       
if __name__ == '__main__':
    main()
