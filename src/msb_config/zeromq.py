

def get_zmq_xpub_socketstring(msb_config : dict) -> str:
    zmq_config = msb_config['zeromq']
    return f"{zmq_config['protocol']}://{zmq_config['address']}:{zmq_config['xpub_port']}"

def get_zmq_xsub_socketstring(msb_config : dict) -> str:
    zmq_config = msb_config['zeromq']
    return f"{zmq_config['protocol']}://{zmq_config['address']}:{zmq_config['xsub_port']}"


