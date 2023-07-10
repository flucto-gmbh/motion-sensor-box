import pytest


def test_import_zmq_config():
    from msb.network.config import ZMQConf

    conf = ZMQConf()
    assert conf.protocol == "tcp"


def test_import_mqtt_config():
    from msb.network.config import MQTTConf

    conf = MQTTConf()
    assert conf.broker == "localhost"


def test_publisher_factory_zmq():
    from msb.network import get_publisher
    from msb.network.pubsub.types import Publisher

    pub = get_publisher("zmq")

    assert isinstance(pub, Publisher)


def test_subscriber_factory_zmq():
    from msb.network import get_subscriber
    from msb.network.pubsub.types import Subscriber

    sub = get_subscriber("zmq", "testtopic")

    assert isinstance(sub, Subscriber)


def test_publisher_factory_mqtt():
    from msb.network import get_publisher
    from msb.network.pubsub.types import Publisher

    pub = get_publisher("mqtt")

    assert isinstance(pub, Publisher)


def test_subscriber_factory_mqtt():
    from msb.network import get_subscriber
    from msb.network.pubsub.types import Subscriber

    sub = get_subscriber("mqtt", "testtopic")

    assert isinstance(sub, Subscriber)


@pytest.mark.parametrize(
    "sub_name",
    [
        "zmq",
        "mqtt",
    ],
)
def test_subscriber_factory_multiple_topics(sub_name):
    from msb.network import get_subscriber
    from msb.network.pubsub.types import Subscriber

    sub = get_subscriber(sub_name, ["topic1", "topic2"])

    assert isinstance(sub, Subscriber)


# For debugging
if __name__ == "__main__":
    pytest.main()
