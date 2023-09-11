import serial
from msb.network import Subscriber
from serial import Serial
from config import SerialConfig


class SerialSubscriber(Subscriber):
    def __init__(self, config: SerialConfig, unpack_func=None):
        self.config = config
        self.unpack = unpack_func if unpack_func else lambda x: x
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

    def receive(self) -> dict:
        # message is a string
        message = next(self.read_serial_port())
        # payload is a dictionary
        payload = self.unpack(message)
        return payload

    def read_serial_port(self) -> str:
        buffer = ""
        while True:
            try:
                buffer = self.serial.readline().decode().rstrip("\r\n")
                yield buffer
            except UnicodeError as e:
                if self.config.verbose:
                    print(f"Could not decode: {message}")
                    print(e)
                continue

    def __del__(self):
        if not hasattr(self, "serial"):
            return
        if not self.serial.is_open:
            return
        self.serial.flush()
        self.serial.close()


if __name__ == "__main__":
    config = SerialConfig()
    serial_reader = SerialSubscriber(config)
    for message in serial_reader.receive():
        print(message)
