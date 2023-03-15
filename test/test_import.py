import pytest

def test_mqtt_import():
    from mqtt.MQTTnode import MQTTnode
    from mqtt.MQTTnode import MQTTConfig

def test_broker_import():
    import broker.msb_broker
    import broker.BrokerConfig

def test_attitude_import():
    import attitude.msb_attitude
    import attitude.msb_attitude

def test_config_import():
    import config.MSBConfig
    import config.parse
    import config.zeromq

def test_fusionlog_import():
    import uptime
    import fusionlog.FusionlogConfig
    import fusionlog.TimeSeriesLogger
    import fusionlog.msb_fusionlog

def test_imu_import():
    import imu.IMUConfig
    import imu.IPhonePoller
    with pytest.raises(RuntimeError):
        import imu.imu_standalone


