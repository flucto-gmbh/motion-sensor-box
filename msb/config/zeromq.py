import sys
import zmq

def open_zmq_sub_socket(connect_to : str, topic = b''):
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.SUB)
    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        print(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)
    zmq_socket.setsockopt(zmq.SUBSCRIBE, topic)
    return zmq_socket

def open_zmq_pub_socket(connect_to : str):
    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.PUB)
    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        print(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)
    return zmq_socket
 
def get_zmq_xpub_socketstring(msb_config : dict) -> str:
    zmq_config = msb_config['zeromq']
    return f"{zmq_config['protocol']}://{zmq_config['address']}:{zmq_config['xpub_port']}"

def get_zmq_xsub_socketstring(msb_config : dict) -> str:
    zmq_config = msb_config['zeromq']
    return f"{zmq_config['protocol']}://{zmq_config['address']}:{zmq_config['xsub_port']}"


