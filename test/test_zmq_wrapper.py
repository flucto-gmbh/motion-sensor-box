import pytest
from time import sleep
from datetime import datetime
import zmq
from dataclasses import dataclass

from msb.zmq_base.Publisher import Publisher
from msb.zmq_base.Subscriber import Subscriber
from msb.zmq_base.Config import PublisherConfig, SubscriberConfig


SLEEPTIME = 0.01


@pytest.fixture
def get_zmq_config():
    @dataclass
    class Config:
        protocol: str = "tcp"
        address: str = "127.0.SLEEPTIME"
        port = "5555"

        @property
        def connect_to(self):
            return f"{self.protocol}://{self.address}:{self.port}"

    return Config()


@pytest.fixture
def setup_zmq_subscriber(get_zmq_config):
    config = get_zmq_config
    test_topic = b"test"

    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.SUB)
    socket.bind(config.connect_to)
    socket.setsockopt(zmq.SUBSCRIBE, test_topic)
    sleep(SLEEPTIME)

    return socket


@pytest.fixture
def setup_zmq_publisher(get_zmq_config):
    config = get_zmq_config

    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.PUB)
    socket.bind(config.connect_to)
    sleep(SLEEPTIME)

    return socket


def test_publisher(setup_zmq_subscriber):
    sub = setup_zmq_subscriber
    test_topic = b"test"

    publisher_config = PublisherConfig()
    pub = Publisher(publisher_config)
    pub.send(test_topic, "hello from pub")
    sleep(SLEEPTIME)

    _, return_data = sub.recv_multipart().decode()
    assert return_data == "hello from pub"


def test_subscriber(setup_zmq_publisher):
    pub = setup_zmq_publisher
    test_topic = b"test"

    subscriber_config = SubscriberConfig()
    sub = Subscriber(subscriber_config)
    sleep(SLEEPTIME)
    pub.send(test_topic, "hello from pub")
    sleep(SLEEPTIME)

    _, return_data = sub.recv_multipart().decode()
    assert return_data == "hello from pub"


@pytest.fixture
def setup_publisher_and_subscriber():
    publisher_config = PublisherConfig()
    pub = Publisher(publisher_config)

    subscriber_config = SubscriberConfig()
    topic = subscriber_config.topic
    sub = Subscriber(topic, subscriber_config)
    sleep(SLEEPTIME)

    return pub, sub, topic


def correct_transport(pub, sub, topic, message):
    pub.send(topic, message)
    sleep(SLEEPTIME)

    _, return_data = sub.recv_multipart().decode()
    assert return_data == message


@pytest.mark.skip(reason="not implemented yet")
def test_send_complex_data(setup_publisher_and_subscriber):
    pub, sub, topic = setup_publisher_and_subscriber

    format = "%Y-%m-%d %H:%M:%S.%f"

    data = {
        "name": "test",
        "timeformat": format,
        "timestamp": datetime.strftime(datetime.now(), format),
        "uptime": 1234,
        "from": "test_location",
        "accx": 1.0,
        "acc_y": 2.0,
        "mag_acc_x": 1e-5,
    }

    pub.send(topic, data)
    sleep(SLEEPTIME)

    _, incoming_data = sub.receive()

    print(incoming_data)
    assert incoming_data == data


@pytest.mark.skip(reason="not implemented yet")
def test_send_dict_via_broker(run_broker, setup_publisher_and_subscriber):
    pub, sub, topic = setup_publisher_and_subscriber
    data = {"testkey": "testvalue"}
    pub.send(topic, data)
    print("data sent")
    sleep(SLEEPTIME)

    _, incoming_data = sub.receive()
    print("data received")

    assert incoming_data == data
