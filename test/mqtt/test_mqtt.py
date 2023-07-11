from unittest.mock import MagicMock


def test_mqtt_publisher(mocker):
    from msb.network.mqtt.publisher import MQTT_Publisher
    from msb.network.mqtt.config import MQTTConf
    import json

    # Create a mock instance of the MQTT client
    mock_paho_mqtt = MagicMock()

    # Patch the paho-mqtt client module and return the mock instance
    mocker.patch("msb.network.mqtt.mqtt_base.mqtt_client", return_value=mock_paho_mqtt)

    # Call the function that uses paho-mqtt client

    conf = MQTTConf(broker="localhost", port=1)
    pub = MQTT_Publisher(conf)

    pub.send("test", {"epoch": 1})

    # Assert that the connect() function was called with the expected arguments
    mock_paho_mqtt.connect.assert_called_once_with("localhost", 1)
    mock_paho_mqtt.publish.assert_called_once_with("test", json.dumps({"epoch": 1}), qos=0, retain=False)


def test_mqtt_subscriber(mocker):
    from msb.network.mqtt.subscriber import MQTT_Subscriber
    from msb.network.mqtt.config import MQTTConf

    # Create a mock instance of the MQTT client
    mock_paho_mqtt = MagicMock()

    mocker.patch("msb.network.mqtt.mqtt_base.mqtt_client", return_value=mock_paho_mqtt)

    conf = MQTTConf(broker="localhost", port=1)
    sub = MQTT_Subscriber("test", conf)

    mock_paho_mqtt.subscribe.assert_called_once_with("test", 0)

    sub.subscribe(["test1", "test2"])
    mock_paho_mqtt.subscribe.assert_called_with([("test1", 0), ("test2", 0)])

