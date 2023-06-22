import serial

from msb.serial.config import FugroSerialConfig


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

    return f + "." + b


# timestamp,abs_pile_velocity,rel_pile_velocity,vessel_roll,vessel_pitch,vessel_yaw,pile_distance_travelled
# 1685854601.000000,0.010,0.020,0.100,0.010,0.004,1.200
def serial_packer(input_dict) -> bytes:
    ts = pad(10, 6, input_dict["timestamp"])
    ap = pad(1, 3, input_dict["abs_pile_velocity"])
    rp = pad(1, 3, input_dict["rel_pile_velocity"])
    roll = pad(1, 3, input_dict["vessel_roll"])
    pitch = pad(1, 3, input_dict["vessel_pitch"])
    yaw = pad(1, 3, input_dict["vessel_yaw"])
    dist = pad(1, 3, input_dict["pile_distance_travelled"])

    return f"{ts},{ap},{rp},{roll},{pitch},{yaw},{dist}"


class SerialPublisher:
    def __init__(self, config: FugroSerialConfig):
        self.config = config
        self.packer = serial_packer
        self.connect()

    def connect(self):
        self.serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bitesize=self.config.bytesize,
        )

    def send(self, topic, message):
        payload = self.packer(message)
        self.serial.write(payload)
        self.serial.flush()

    def __del__(self):
        if not self.serial_is_open():
            return
        self.serial.flush()
        self.serial.close()


class SerialForwarder:
    def __init__(self, subscriber, publisher):
        pass
