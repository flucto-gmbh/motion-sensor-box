import pytest


def test_load_config(pytestconfig):
    import os
    from msb.config import load_config
    from msb.zmq_base.config import PublisherSubscriberConf

    root_dir = pytestconfig.rootdir
    conf_dir = os.path.join(root_dir, "config")
    os.environ["MSB_CONFIG_DIR"] = conf_dir
    config = load_config(PublisherSubscriberConf(), "zmq", read_commandline=False)

    assert config.subscriber_port == 5556
    assert config.publisher_port == 5555
    assert config.protocol == "tcp"
