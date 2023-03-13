import logging
import zmq
import sys
import uptime
import pickle
import time

from os import path

# add /usr/local/lib/python3/dist-packages to the system path
GPS_DIR = '/usr/local/lib/python3/dist-packages/'

if not path.isdir(path.join(GPS_DIR, 'gps')):
    raise Exception(f'no such file or directory: {GPS_DIR/gps}')

sys.path.append(path.dirname(GPS_DIR))

try:
    import gps
except ImportError as e:
    raise Exception('failed to import gps module')
    sys.exit(-1)

try:
    from gps_config import (init, GPS_TOPIC)
except ImportError:
    raise Exception('failed to import init method')

def main():
    config = init()

    logging.debug(f'connceting to gpsd socket')
    try:
        gpsd_socket = gps.gps(mode=gps.WATCH_ENABLE)
    except Exception as e:
        logging.fatal('failed to connect to gpsd')
        sys.exit(-1)
    logging.debug(f'connected to gpsd socket')

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'
    logging.debug(f'binding to {connect_to} for zeroMQ IPC')
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal('failed to connect to zeroMQ socket for IPC')
        sys.exit(-1)

    logging.debug(f'connected to zeroMQ IPC socket')

    logging.debug(f'entering endless loop')

    try:
        while True:
            # Do stuff
            report = gpsd_socket.next().__dict__
            if report['class'] == 'TPV':

                if not 'lat' in report:
                    logging.warning('no gps fix available')
                    report['lat'] = report['lon'] = report['alt'] = 0

                data = [time.time(), uptime.uptime(), report]          

                if config['print']: print(f'{data}')
                
                zmq_socket.send_multipart(
                    [
                        GPS_TOPIC,
                        pickle.dumps(
                            data
                        )
                    ]
                )
                # zmq_socket.send_pyobj(data)

    except StopIteration:
        logging.fatal("GPSD has terminated")

    except KeyboardInterrupt:
        logging.info('goodbye')
        sys.exit(0)


if __name__ == '__main__':
    main()

