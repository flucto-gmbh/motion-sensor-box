from __future__ import annotations
from types import FunctionType
import serial

from .config import SerialConf
from msb.network.pubsub.types import Publisher
from msb.network.packer import get_packer


class SerialPublisher(Publisher):
    """
    Publisher for serial devices.
    Can be used everywhere that a flucto style publishing connection is required.

    Parameters
    ----------
    config : SerialConf
        Configuration for the serial connection.
    pack_func : FunctionType
        Function to translate from a dict to a serialized string.
    """

    def __init__(self, config: SerialConf, pack_func: FunctionType = None):
        self.config = config
        self.packer = pack_func if pack_func else get_packer("serial")
        self._connect()

    def _connect(self):
        self.serial: serial.Serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        print(f"Successfully connected to serial device at port {self.config.port}")

    def send(self, message: object):
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Please note that this does not adhere to the interface, as there is no topic.

        Parameters
        ----------
        message : object
            object to be serialized and sent via the serial connection. Usually a dict.
        """
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
