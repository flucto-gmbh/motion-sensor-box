import pytest

def test_mqtt_import():
    from msb.mqtt.MQTTnode import MQTTnode
    from msb.mqtt.MQTTnode import MQTTConfig

def test_broker_import():
    import msb.broker.msb_broker
    from msb.broker.config import BrokerConf

def test_attitude_import():
    import msb.attitude.msb_attitude
    import msb.attitude.msb_attitude

def test_config_import():
    import msb.config.MSBConfig
    import msb.config.parse
    import msb.config.zeromq

def test_fusionlog_import():
    import msb.fusionlog.FusionlogConfig
    import msb.fusionlog.TimeSeriesLogger
    import msb.fusionlog.msb_fusionlog

def test_imu_import():
    import msb.imu.config
    # with pytest.raises(RuntimeError):
    #     import msb.imu.imu_standalone
