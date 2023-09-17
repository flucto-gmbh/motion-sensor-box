from __future__ import annotations
from types import FunctionType
import serial
from msb.network.pubsub.types import Subscriber
from .config import SerialConf


class SerialSubscriber(Subscriber):
    """
    Subscriber for serial devices. Connects to a serial port and reads from it.

    Parameters
    ----------
    :param topics:
        Placeholder for topic. Not used.

    :param config: SerialConf
        Configuration class for the serial connection.

    :param unpack_func: FunctionType
        Function to translate from a serialized string to a dict.
    """

    def __init__(self, topics, config: SerialConf, unpack_func: FunctionType = None):
        self.config = config
        self.unpack = unpack_func if unpack_func else lambda x: x
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

    def receive(self) -> dict:
        """
        Wait for data to arrive on the serial port and return it.

        Returns
        -------
        :return: (topic, payload)
            topic is a placeholder to adhere to the Subscriber interface
            payload is a dictionary containing the data from the serial port
        """
        # message is a string
        message = next(self.read_serial_port())
        # payload is a dictionary
        payload = self.unpack(message)
        # port is a placeholder for topic
        return self.config.port, payload

    def read_serial_port(self) -> str:
        buffer = ""
        while True:
            try:
                buffer = self.serial.readline().decode()
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
    config = SerialConf()
    serial_reader = SerialSubscriber(config)
    for message in serial_reader.receive():
        print(message)
