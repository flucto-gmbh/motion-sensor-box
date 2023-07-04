from __future__ import annotations
from time import timezone
import serial
from serial import Serial
import datetime

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
# str(localtime), mm/min, mm/min, deg, deg, deg, m
# 1 Hz downsample
# 1685854601.000000,0.010,0.020,0.100,0.010,0.004,1.200
def serial_packer(input_dict) -> bytes:
    ts = input_dict["epoch"]
    ap = input_dict["velocity_x"]
    rp = input_dict["distance_x"]
    roll = input_dict["roll"]
    pitch = input_dict["pitch"]
    yaw = input_dict["yaw"]
    dist = input_dict["sum_distance_x"]

    ts = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y%m%dT%H%M%SZ+08:00")

    return f"{ts},{ap},{rp},{roll},{pitch},{yaw},{dist}\n"
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
