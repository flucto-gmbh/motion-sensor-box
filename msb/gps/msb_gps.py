from datetime import datetime, timezone
import logging
import os
import pickle
import sys
import time
import uptime
import zmq
# add /usr/local/lib/python3/dist-packages to the system path
GPS_DIR = '/usr/local/lib/python3/dist-packages/'
if not os.path.isdir(os.path.join(GPS_DIR, 'gps')):
    raise Exception(f'no such file or directory: {GPS_DIR/gps}')
sys.path.append(os.path.dirname(GPS_DIR))
try:
    import gps
except ImportError as e:
    raise Exception('failed to import gps module')
    sys.exit(-1)
# local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from msb_config.zeromq import open_zmq_pub_socket
from GPSConfig import GPSConfig, GPS_TOPIC

zero_timestamp = datetime.fromtimestamp(0, tz=timezone.utc)

def open_gpsd_socket(gps_config : GPSConfig):
    if gps_config.verbose:
        print(f'connecting to gpsd socket')
    try:
        gpsd_socket = gps.gps(mode=gps.WATCH_ENABLE)
    except Exception as e:
        print('failed to connect to gpsd')
        sys.exit(-1)
    if gps_config.verbose:
        print(f'connected to gpsd socket')

    return gpsd_socket

def assemble_data(report):
    return [
        datetime.fromtimestamp(ts := time.time(), tz=timezone.utc), 
        ts,
        uptime.uptime(),
        report["mode"] if "mode" in report else 0,
        report["time"] if "time" in report else zero_timestamp,
        report["lat"] if "lat" in report else 0,
        report["lon"] if "lon" in report else 0,
        report["altHAE"] if "altHAE" in report else 0,
        report["altMSL"] if "altMSL" in report else 0,
        report["track"] if "track" in report else 0,
        report["magtrack"] if "magtrack" in report else 0,
        report["magvar"] if "magvar" in report else 0,
        report["speed"] if "speed" in report else 0,
    ]          

def consume_send_gps_data(gps_config : GPSConfig, zmq_socket, gpsd_socket):
    try:
        while True:
            report = gpsd_socket.next().__dict__
            if report["class"] == "TPV":
                if gps_config.verbose:
                    print(f"received TPV report {report}")
                if report["mode"] == 0 and gps_config.verbose:
                    print('no gps fix available')
                zmq_socket.send_multipart(
                    [
                        GPS_TOPIC,
                        pickle.dumps(
                            (data := assemble_data(report))
                        )
                    ]
                )
                if gps_config.print_stdout:
                    print(f','.join(map(str, data)))
    except StopIteration:
        logging.fatal("GPSD has terminated")
    except KeyboardInterrupt:
        logging.info('goodbye')
        sys.exit(0)

def msb_gps(gps_config : GPSConfig):
    zmq_pub_socket = open_zmq_pub_socket(gps_config.zmq["xsub_connect_string"])
    gpsd_socket = open_gpsd_socket(gps_config)
    consume_send_gps_data(gps_config, zmq_pub_socket, gpsd_socket)

if __name__ == '__main__':
    gps_config = GPSConfig()
    msb_gps(gps_config)
