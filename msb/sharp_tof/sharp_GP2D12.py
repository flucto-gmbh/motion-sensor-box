import serial
import time

class GP2D12:
    def __init__(self):
        """
        Initialize the serial connection.
        :param port: Serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0').
        :param baud_rate: Baud rate for the serial communication.
        :param timeout: Read timeout in seconds.
        """
        self.ser = serial.Serial("/dev/ttyACM0", 9200)

    def get_data(self):
        """
        Read a message from the serial input.
        :return: The message read from the serial input.
        """
       	distance = self.ser.readline()
        if distance == None:
                return None
        distance = distance.decode('utf-8').strip()
        epoch = time.time()
       	distance = float(distance.split()[0]) * 10

       	return epoch,distance
