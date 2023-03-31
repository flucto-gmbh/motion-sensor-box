import pytest 
import threading
from time import sleep
from os import environ as env, getcwd
from datetime import datetime

from msb.zmq_base.Publisher import Publisher
from msb.zmq_base.Subscriber import Subscriber
from msb.zmq_base.Broker import Broker
from msb.broker.BrokerConfig import BrokerConfig
from msb.zmq_base.Config import PublisherConfig, SubscriberConfig


@pytest.fixture
def run_broker():
    def setup_broker():
        env["MSB_CONFIG_DIR"] = f"{getcwd()}/config"
        config = BrokerConfig()
        broker = Broker(config)
    threading.Thread(target=setup_broker, daemon=True, args=[]).start()
    sleep(0.1)
    return threading.Thread(target=setup_broker, daemon=True, args=[])


@pytest.fixture
def setup_publisher_and_subscriber():
    publisher_config = PublisherConfig()
    pub = Publisher(publisher_config)

    subscriber_config = SubscriberConfig()
    topic = subscriber_config.topic
    sub = Subscriber(topic, subscriber_config)
    sleep(0.1)

    return pub, sub, topic


# @pytest.mark.skip(reason="not implemented yet")
def test_send_complex_data(run_broker, setup_publisher_and_subscriber):
    pub, sub, topic = setup_publisher_and_subscriber

    format = "%Y-%m-%d %H:%M:%S.%f"

    data = {"name" : "test",
            "timeformat" : format,
            "timestamp" : datetime.strftime(datetime.now(), format),
            "uptime" : 1234,
            "from" : "test_location",
            "accx" : 1.0,
            "acc_y" : 2.0,
            "mag_acc_x" : 1e-5,
            }

    pub.send(topic, data)
    sleep(0.1)

    _, incoming_data = sub.receive()

    print(incoming_data)
    assert incoming_data == data
    

# @pytest.mark.skip(reason="not implemented yet")
def test_send_dict_via_broker(run_broker, setup_publisher_and_subscriber):
    pub, sub, topic = setup_publisher_and_subscriber
    data = {"testkey": "testvalue"}
    pub.send(topic, data)
    print("data sent")
    sleep(0.1)

    _, incoming_data = sub.receive()
    print("data received")

    assert incoming_data == data

