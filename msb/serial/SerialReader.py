import re
import serial
from serial.serialutil import SerialException
import sys

from msb.serial.config import SerialConf
from msb.config import load_config
from msb.zmq_base import get_default_publisher


class SerialReader:
    def __init__(self, config, publisher):
        self.config = config
        self.publisher = publisher
        self.measurement_keys = ["pow", "gen", "rtr", "wnd", "pit"]
        self.topic = self.config.topic
        self.pattern = re.compile(self.config.regex)

        # make sure that topic is a byte string
        if isinstance(self.topic, str):
            self.topic = self.topic.encode()

    def create_payload(self, data_values):
        payload = {k: v for k, v in zip(self.measurement_keys, data_values)}
        return payload

    def read_a_message_and_publish(self, message):
        data_values = self.extractFloats(message)
        payload = self.create_payload(data_values)
        self.publisher.send(self.topic, payload)

    def start_loop(self):
        for message in self.read_message():
            self.read_a_message_and_publish(message)

    def extractFloats(self, text) -> str:
        # Match regex, return a tuple
        try:
            matching_tuple = re.findall(self.pattern, text)
            return matching_tuple[0]
        except Exception as e:
            print(f"Could not find match on {text}")
            return ""

    def read_message(self):
        with serial.Serial(
            port=self.config.device,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
        ) as serial_reader:
            # Set RTS to low and DTR to high
            # Required for a read-only connection to Vestas controller
            serial_reader.rts = False
            serial_reader.dtr = True

            buffer = ""

            while True:
                if serial_reader.in_waiting > 0:
                    try:
                        buffer = buffer + serial_reader.read(serial_reader.in_waiting).decode()
                        if "1:OVERVIEW" in buffer:
                            message = buffer
                            buffer = ""
                            yield message
                    except UnicodeError as e:
                        # print(f"Could not decode: {message}")
                        # print(e)
                        continue


if __name__ == "__main__":
    config = load_config(SerialConf(), "serial", read_commandline=False)
    publisher = get_default_publisher()
    reader = SerialReader(config, publisher)
    reader.start_loop()
