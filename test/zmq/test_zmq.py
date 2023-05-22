from msb.zmq_base import get_default_subscriber


def test_sub_single_string_topic():
    get_default_subscriber("test")


def test_sub_single_string_bytes():
    get_default_subscriber(b"test")


def test_multiple_strings():
    get_default_subscriber(["test1", "test2"])


def test_multiples_bytes():
    get_default_subscriber([b"test1", b"test2"])


def test_ridiculous_fringe_case():
    get_default_subscriber([b"test1", "test2"])
