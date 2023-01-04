import time
import sys
import zmq
import logging
import pickle
import numpy as np

from ICM20948 import ICM20948

# TODO:
# - no ipc flag einbauen fuer testing

try:
    from imu_config import (init, IMU_TOPIC)
except ImportError:
    print('faild to import init function from config.py')
    sys.exit(-1)

try:
    from ICM20948 import ICM20948 as IMU
except ImportError:
    print('failed to import ICM20948 module')
    sys.exit(-1)

offsets = {
    'gyr_x' : 0,
    'gyr_y' : 0,
    'gyr_z' : 0,
}

def round_floats(o, precision=6):
    if isinstance(o, float):
        return round(o, precision)
    if isinstance(o, dict):
        return {k: round_floats(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [round_floats(x) for x in o]
    return o

def estimate_offsets(imu : ICM20948):
    global offsets

    data = list()

    for _ in range(500):
        t = imu.get_data()
        data.append(t)

    data = np.array(data)

    offsets['gyr_x'] = np.mean(data[:,5])
    offsets['gyr_y'] = np.mean(data[:,6])
    offsets['gyr_z'] = np.mean(data[:,7])

def main():

    config = init()

    dt_sleep = 1/config['sample_rate']
    logging.debug(f'sample rate set to {config["sample_rate"]}, sleeping for {dt_sleep} s')

    logging.debug('inititating sensor..')

    imu = IMU.ICM20948(
        verbose=config['verbose'],
        output_data_div=config['imu_output_div'],
        accelerometer_sensitivity=config['acc_range'],
        gyroscope_sensitivity=config['gyro_range'],
    )

    logging.debug('.. sensor init done')

    imu.begin()

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUB)
    s.connect(connect_to)
    logging.debug(f'connected to zeroMQ IPC socket')

    logging.debug(f'estimating offsets for gyroscope')
    estimate_offsets(imu=imu)
    logging.debug(f'offets: {offsets}')

    #sync(connect_to)

    logging.debug('entering endless loop')

    t_old = time.time()
    t_cur = time.time()
    
    try:
        while True:

            t_cur = time.time()

            # data = {config['id'] : imu.get_data()}
            data = imu.get_data()
            logging.debug(f'before offset correction: {data}')
            data[2] *= -1
            data[3] *= -1
            data[4] *= -1
            data[5] -= offsets['gyr_x']
            data[6] -= offsets['gyr_y']
            data[7] -= offsets['gyr_z']
            logging.debug(f'after offset correction: {data}')

            if config['print']:
                print(data)
            # send multipart message:

            s.send_multipart(
                [
                    IMU_TOPIC,    # topic
                    pickle.dumps( # serialize the payload
                        round_floats(
                            data
                        )
                    )
                ]
            )

            dt_sleep = (t_cur + (1/config['sample_rate'])) - time.time()

            if dt_sleep > 0:
                logging.debug(f'sleeping for {dt_sleep} s')
                time.sleep(dt_sleep)

            #while (time.time() - t_cur) < 1/config['sample_rate']:
            #    time.sleep(0.001)

            #time.sleep(1/config['sample_rate'])
    except KeyboardInterrupt:
        logging.info('msb_imu bye')
        sys.exit(0)

if __name__ == '__main__':
    main()
