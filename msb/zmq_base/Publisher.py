import zmq
import pickle
import sys

class Publisher:
    def __init__(self, protocol="tcp", ip="*", port="5555", connect_to = None):
        if not connect_to:
            connect_to = f"{protocol}://{ip}:{port}"
            print(f"binding to : {connect_to}")

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        try:
            self.socket.connect(connect_to)
            # self.socket.bind(connect_to)
        except Exception as e:
            print(f'failed to bind to zeromq socket: {e}')
            sys.exit(-1)


    def __del__(self):
        self.socket.close()
    #     self.context.term()
    

    def send(self, topic, payload):
        # data = payload.pack()
        data = pickle.dumps(payload)

        self.socket.send_multipart(
            [
                topic,
                data
            ]
        )
