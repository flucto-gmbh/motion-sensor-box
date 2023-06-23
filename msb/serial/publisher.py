from __future__ import annotations
import serial
from serial import Serial

from msb.serial.config import FugroSerialConfig
from msb.mqtt.subscriber import MQTT_Subscriber
from msb.mqtt.subscriber import get_default_subscriber as get_mqtt_subscriber
from msb.zmq_base.Subscriber import Subscriber as ZMQ_Subscriber
from msb.zmq_base.Subscriber import get_default_subscriber as get_zmq_subscriber
from msb.config import load_config


def pad(n_pre, n_post, string):
    if not isinstance(string, str):
        string = str(string)

    if "." in string:
        front, back = string.split(".")
    else:
        front = string
        back = ""

    f = front.rjust(n_pre, "0")
    b = back.ljust(n_post, "0")
    if len(b) > n_post:
        b = b[:n_post]

    return f + "." + b


# timestamp,abs_pile_velocity,rel_pile_velocity,vessel_roll,vessel_pitch,vessel_yaw,pile_distance_travelled
# 1685854601.000000,0.010,0.020,0.100,0.010,0.004,1.200
def serial_packer(input_dict) -> bytes:
    ts = pad(10, 6, input_dict["epoch"])
    ap = pad(1, 3, input_dict["velocity_x"] * 6e4)
    rp = pad(1, 3, input_dict["distance_x"] * 6e4)
    roll = pad(1, 3, input_dict["roll"])
    pitch = pad(1, 3, input_dict["pitch"])
    yaw = pad(1, 3, input_dict["yaw"])
    dist = pad(1, 3, input_dict["sum_distance_x"])
    # ts = pad(10, 6, input_dict["epoch"])
    # ap = pad(1, 3, input_dict["abs_pile_velocity"])
    # rp = pad(1, 3, input_dict["rel_pile_velocity"])
    # roll = pad(1, 3, input_dict["vessel_roll"])
    # pitch = pad(1, 3, input_dict["vessel_pitch"])
    # yaw = pad(1, 3, input_dict["vessel_yaw"])
    # dist = pad(1, 3, input_dict["pile_distance_travelled"])

    return f"{ts},{ap},{rp},{roll},{pitch},{yaw},{dist}"
    # return f"{ts:10.6f},{ap:1.3f},{rp:1.3f},{roll:1.3f},{pitch:1.3f},{yaw:1.3f},{dist:1.3f}"


class SerialPublisher:

    def __init__(self, config: FugroSerialConfig):
        self.config = config
        self.packer = serial_packer
        self.connect()

    def connect(self):
        self.serial: Serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        print(f"Successfully connected to serial device at port {self.config.port}")

    def send(self, message):
        payload = self.packer(message)
        self.serial.write(payload.encode(self.config.encoding))
        self.serial.flush()
        if self.config.verbose:
            print(payload)

    def __del__(self):
        if not hasattr(self, "serial"):
            return
        if not self.serial.is_open:
            return
        self.serial.flush()
        self.serial.close()


class SerialForwarder:
    def __init__(
        self, subscriber: MQTT_Subscriber | ZMQ_Subscriber, publisher: SerialPublisher
    ):
        self.subs = subscriber
        self.pub = publisher

    """
    Wait for message and forward
    """
    def forward_message(self):
        collected = {}
        for sub in self.subs:
            topic, data = sub.receive()
            collected.update(data)

        self.pub.send(collected)
        # self.pub.send(data)

    """
    Enter loop and continuously forward messages
    """
    def sub_pub_loop(self):
        while True:
            self.forward_message()


def main():
    subscriber_opt = get_mqtt_subscriber("/+/opt")
    subscriber_rpy = get_mqtt_subscriber("/+/rpy")
    serial_config = load_config(
        FugroSerialConfig(), "fugro-config", read_commandline=False
    )
    publisher = SerialPublisher(serial_config)

    forwarder = SerialForwarder([subscriber_opt, subscriber_rpy], publisher)
    forwarder.sub_pub_loop()
