import time

import automationhat


class Baumer:
    def __init__(self):
        self.inital = True

    def get_data(self):
        start1 = 0.08  # minimum voltage
        stop1 = 10.03  # maximum voltage
        start2 = 100  # minimum distance
        stop2 = 600  # maximum distance
        voltage = automationhat.analog.one.read()

        distance = start2 + (voltage - start1) * (stop2 - start2) / (stop1 - start1)
        epoch = time.time()

        return epoch, distance
