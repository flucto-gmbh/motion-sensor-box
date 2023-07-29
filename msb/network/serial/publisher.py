from __future__ import annotations
import serial

from .config import SerialConf
from msb.network.types import Publisher


def serial_packer(input_dict) -> bytes:
    return ",".join(input_dict.values())


class SerialPublisher(Publisher):
    def __init__(self, config: SerialConf):
        self.config = config
        self.packer = serial_packer
        self.connect()

    def connect(self):
        self.serial: serial.Serial = serial.Serial(
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


