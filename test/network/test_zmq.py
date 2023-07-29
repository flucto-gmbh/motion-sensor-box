import pytest
from unittest.mock import Mock, patch

import msb.network
from msb.network import get_publisher
from msb.network.zmq import ZMQConf, ZMQ_Publisher
from msb.config import load_config

import requests


def myfunc(x):
    return x * x


def test_key_error(mocker):
    mocker.patch(
        "msb.network.pubsub.factories._registered_publishers", {"serial": None}
    )

    with pytest.raises(KeyError):
        get_publisher("zmq")


def test_type_error(mocker):
    mocker.patch("msb.network.pubsub.factories._registered_publishers", {"zmq": None})

    with pytest.raises(TypeError):
        get_publisher("zmq")

@patch("msb.network.zmq.ZMQ_Publisher.zmq.context.socket.send_multipart")
def test_zmq_publisher_send_with_mock(mock_send_multipart):
    zmq_pub = get_publisher("zmq")
    assert zmq_pub.send("test", {"data": "tried"}) == True



# @patch("msb.network.publisher_factory")
# def test_returns_config(mock_factory):
#     mock_factory.return_value = 1
#     assert type(publisher_factory("zmq")) == ZMQ_Publisher


@patch("msb.network.mypackage.half")
def test_double(mock_func):
    mock_func.return_value = 4
    assert double(5) == 16


@patch("msb.network.pubsub.factories.load_config")
def test_load_config(mock_load_config):
    zmq_pub = get_publisher("zmq")
    assert zmq_pub.config.protocol == "udp"


@patch("")

# def test_mock_double(mocker):
#     mocker.patch("msb.network.mypackage.double", return_value=100)
#     assert double(5) == 100

# @pytest.fixture
# def mock_config(mocker):
#     return mocker


# def test_load_config(mocker):
#     fake_return = ZMQConf(protocol="udp")
#     mocker.patch("msb.config.load_config", return_value=fake_return)
#     # config = mock_config.load_config(ZMQConf, "zmq")
#     config = load_config(ZMQConf(), "zmq", read_commandline=False)
#     assert config.protocol == "udp"


# @pytest.fixture
# def mock_get(mocker: Mock):
#     mock = Mock()
#     mock.patch("requests.get", return_value=mock)
#     mock.return_value.status_code = 200
#     mock.return_value.json.return_value = {"key": "value"}
#     return mock


# def test_get_request(mock_get):
#     response = requests.get("http://example.com")
#     assert response.status_code == 200
#     # assert response.json() == {"key": "value"}
