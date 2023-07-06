from msb.mqtt import get_mqtt_subscriber
import time
import uptime
from msb.mqtt.config import MQTTconf
from msb.serial.config import FugroSerialConfig
from msb.serial.publisher import SerialPublisher
from msb.serial.publisher import SerialForwarder
from msb.config import load_config


mock_opt_dict = {
    "epoch": time.time(),
    "uptime": uptime.uptime(),
    "distance_x": 0.005,
    "distance_y": 0.000018,
    "sum_distance_x": 40.318,
    "sum_distance_y": 0.001,
    "velocity_x": 0.0001,
    "velocity_y": 0.00000,
}

mock_rpy_dict = {
    "epoch": time.time(),
    "uptime": uptime.uptime(),
    "acc_x_f": 0.0001,
    "acc_y_f": 0.0381,
    "acc_z_f": 0.1337,
    "roll": 0.081,
    "pitch": 0.1337,
    "yaw": 0.70701,
}


def update_timestamp(data_dict: dict) -> dict:
    data_dict["epoch"] = time.time()
    return data_dict


class MockMQTTSubscriber:
    def __init__(self, config, mock_data={}):
        self.config = config
        self.mock_data = mock_data

    def receive(self):
        time.sleep(1)
        self.mock_data = update_timestamp(self.mock_data)
        return (self.config.topics, self.mock_data)


def main():
    # subscriber_opt = get_mqtt_subscriber("/+/opt")
    # subscriber_rpy = get_mqtt_subscriber("/+/rpy")
    subscriber_opt = MockMQTTSubscriber(MQTTconf(topics="/msb-mock/opt"), mock_opt_dict)
    subscriber_rpy = MockMQTTSubscriber(MQTTconf(topics="/msb-mock/rpy"), mock_rpy_dict)
    serial_config = load_config(
        FugroSerialConfig(), "fugro-config", read_commandline=False
    )
    publisher = SerialPublisher(serial_config)

    forwarder = SerialForwarder([subscriber_opt, subscriber_rpy], publisher)
    forwarder.sub_pub_loop()


if __name__ == "__main__":
    main()
