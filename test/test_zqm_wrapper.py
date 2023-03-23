import pytest 
import threading
from time import sleep
from os import environ as env, getcwd

from msb.zmq_base.Publisher import Publisher
from msb.zmq_base.Subscriber import Subscriber
from msb.zmq_base.Broker import Broker
from msb.broker.BrokerConfig import BrokerConfig


@pytest.fixture
def run_broker():
    def setup_broker():
        env["MSB_CONFIG_DIR"] = f"{getcwd()}/config"
        config = BrokerConfig()
        broker = Broker(config)
    threading.Thread(target=setup_broker, daemon=True, args=[]).start()
    sleep(0.1)




def test_send_dict_via_broker(run_broker):
    protocol = "tcp"
    address = "127.0.0.1"
    xsub_port = "5555"
    pub = Publisher(protocol, address, xsub_port)

    topic = b"testtopic"
    xpub_port = "5556"
    sub = Subscriber(topic, protocol, address, xpub_port)
    sleep(0.1)

    data = {"testkey": "testvalue"}
    pub.send(topic, data)
    sleep(0.1)

    inc_topic, incoming_data = sub.receive()

    print(incoming_data)

    assert incoming_data == data

    
