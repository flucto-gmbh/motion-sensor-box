import pytest
from time import sleep
from datetime import datetime

import zmq
import json

from msb.zmq_base.Publisher import Publisher, get_default_publisher
from msb.zmq_base.Subscriber import Subscriber, get_default_subscriber
from msb.zmq_base.config import PublisherSubscriberConf

SLEEPTIME = 0.1


def wait():
    sleep(SLEEPTIME)

@pytest.mark.parametrize(
    "test_data",
    [
        "hello world",  # string
        1234,  # number
        [1, 2, 3, 4],  # list
        {"hello": "world"},  # simple dict
        {
            "name": "test",  # complex dict
            "timeformat": "%Y-%m-%d %H:%M:%S.%f",
            "timestamp": datetime.strftime(datetime.now(),
                                           "%Y-%m-%d %H:%M:%S.%f"),
            "uptime": 1234,
            "from": "test_location",
            "accx": 1.0,
            "acc_y": 2.0,
            "mag_acc_x": 1e-5,
        }
        # ("a", "b"), this doesn't work, returns ["a", "b"]
        # b"hello world", this doesn't work either
    ],
)
def test_publisher_subscriber_via_mock_broker(test_data):
    """
    Test the transport via mock broker.
    Tests sending different data
    """
    topic = b"tst"
    # create the pub-sub pair and connect to the mock broker
    pub = get_default_publisher()
    sub = get_default_subscriber(topic)
    wait()

    # send a message to the mock broker
    pub.send(topic, test_data)
    _, received_message = sub.receive()
    assert received_message == test_data


def test_subscribe_multiple_topics():
    topics = [b"apples", b"pears", b"carrots"]

    pub = get_default_publisher()
    sub = get_default_subscriber(topics)
    wait()

    for topic in topics:
        message = f"hello from {topic.decode()}"
        pub.send(topic, message)
        rec_topic, received_message = sub.receive()
        assert rec_topic == topic
        assert received_message == message


def test_subscriber_without_broker():
    """
    Test the subscriber class directly,
    without using the mock broker.
    This approach does not work for the publisher class,
    due to the bind / connect strategy
    """
    test_topic = b"tst"
    port = 7755

    ctx = zmq.Context.instance()
    pub = ctx.socket(zmq.PUB)
    pub.bind(f"tcp://*:{port}")
    subscriber_config = PublisherSubscriberConf(subscriber_port=port)
    sub = Subscriber(test_topic, subscriber_config)
    wait()

    pub.send_multipart([test_topic, json.dumps("hello from pub").encode()])

    _, return_data = sub.receive()
    assert return_data == "hello from pub"
