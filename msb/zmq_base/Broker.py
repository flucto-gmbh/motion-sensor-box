import signal
import zmq 
import sys

from msb.broker.BrokerConfig import BrokerConfig

class Broker:
    def __init__(self, broker_config : BrokerConfig):
        self.xpub_connect_string = broker_config.zmq["xpub_connect_string"]
        self.xsub_connect_string = broker_config.zmq["xsub_connect_string"]

        self.ctx = zmq.Context.instance()
        self._bind_to_xpub()
        self._bind_to_xsub()
        self._create_proxy()

    def _bind_to_xpub(self):
        self.xpub = self.ctx.socket(zmq.XPUB)
        self.xpub.bind(self.xpub_connect_string)

    def _bind_to_xsub(self):
        self.xsub = self.ctx.socket(zmq.XSUB)
        self.xsub.bind(self.xsub_connect_string)

    def _create_proxy(self):
        self.proxy = zmq.proxy(self.xpub, self.xsub)

def main():
    broker_config = BrokerConfig()
    broker = Broker(broker_config)
