import time

from serial import Serial


class TF02Pro:
    def __init__(self):
        self.serial = Serial("/dev/ttyAMA0", 115200)
        if not self.serial.is_open:
            self.serial.open()
        self.buffer = bytearray(9)

    def get_data(self):
        while True:
            self.serial.readinto(self.buffer)
            checksum = self.buffer[8]
            if checksum != sum(self.buffer[:-1]) & 0xFF:
                print("Incorrect checksum. Skipping")
                continue
            epoch = time.time()
            if not (self.buffer[0] == 0x59 and self.buffer[1] == 0x59):
                # not a correct header, discard
                continue
            distance_raw = self.buffer[2] + (self.buffer[3] << 8)
            strength_raw = self.buffer[4] + (self.buffer[5] << 8)
            temperature_raw = self.buffer[6] + (self.buffer[7] << 8)

            distance = distance_raw / 100  # convert distance to meter
            strength = strength_raw / 65535  # convert to value between 0-1
            temperature = temperature_raw / 8 - 256  # convert to celcius

            return epoch, distance, strength, temperature
