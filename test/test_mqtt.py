import pytest
import paho.mqtt.client as mqtt_client
import time
import ssl

from msb.mqtt.msb_mqtt import MQTTConfig, MQTT_Base


def packer_func(data):
    now = int(time.time_ns())
    msg = f"turbine turbine={data['data']} {now}"
    return msg


def setup_config():
    config = MQTTConfig(broker="localhost", user="user", password="pw", port=1883, qos=0, ssl=False)
    return config


def get_client(config):
    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"MQTT node connected to {config.broker}:{config.port}")
        else:
            print("Connection failed!")
            assert False

    client = mqtt_client.Client()
    client.username_pw_set(config.user, config.password)
    client.on_connect = on_connect

    if config.ssl:
        # By default, on Python 2.7.9+ or 3.4+,
        # the default certification authority of the system is used.
        client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt", cert_reqs=ssl.CERT_REQUIRED)
        print("using ssl")
    else:
        print("not using ssl")

    client.connect(config.broker, config.port)
    time.sleep(1)

    return client


@pytest.mark.skip
def test_mqtt_node():
    from msb.mqtt.msb_mqtt import MQTT_Base
    mqtt = MQTT_Base(setup_config())

    for x in range(10):
        mqtt.send("mqtttest", {"data": x})
        time.sleep(0.1)


def test_zmq_to_mqtt_loop():
    from msb.mqtt.msb_mqtt import MQTT_Publisher
    from msb.zmq_base import get_default_subscriber
    config = setup_config()
    config.packstyle = "default"

    zmq_sub = get_default_subscriber(b"")

    pub = MQTT_Publisher(config, zmq_sub)

    for x in range(10):
        pub._zmq_to_mqtt()



@pytest.mark.skip
def test_mqtt_server_connection():
    config = setup_config()
    mqtt_node = MQTT_Base(config)
    mqtt_node.pack = packer_func
    # client = get_client(config)
    print(f"connected to {config.broker}:{config.port}")
    time.sleep(1)

    for x in range(10):
        mqtt_node.send("mqtttest", {"data": x})
        # payload = f"turbine test/test={float(x)} {time.time_ns()}"
        # client.publish(topic="mqtttest", payload=payload, qos=1)

        # print(f"t = mqtttest m = {payload} to {config.broker}:{config.port}")
        # time.sleep(1)


if __name__ == "__main__":
    test_mqtt_server_connection()
