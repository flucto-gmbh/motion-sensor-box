import time

from msb.config import load_config
from msb.env.config import ENVConf
from msb.zmq_base.Publisher import Publisher, get_default_publisher
from msb.env.env import (
    sht, #temperature / humidity sensor
    lps #pressure sensor
)
from uptime import uptime
import math

class ENVService:
    def __init__(self, config: ENVConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher

        if self.config.verbose:
            print(self.config)

    def get_data(self) -> dict:
        data = {}
        data["epoch"] = time.time()
        data["uptime"] = uptime()
        data["temperature"] = sht()["temperature"] #°C
        data["relative_humidity"] = sht()["relative_humidity"] #%
        data["pressure"] = lps()["pressure"] #hPa
        return data

    def run(self):
        # timing adapted from https://stackoverflow.com/a/25251804
        delta_t = 1 # 1Hz - update frequency
        start_time = time.time()
        while True:
            data = self.get_data()
            self.publisher.send(self.config.topic, data)
            if self.config.print_stdout:
                print(data)
            time.sleep(delta_t - ((time.time() - start_time) % delta_t))

    def dew_point(self): # still in development -- source:  https://www.wetterochs.de/wetter/feuchte.html
        a = 7.5
        b = 235
        relative_humidity = 75
        T = 20
        dew_point = math.log(((relative_humidity/100)*(6.1078*10**((a*T)/(b+T))))/6.1078,10)
        print(dew_point)

def main():
     env_config = load_config(ENVConf(), "env")
     publisher = get_default_publisher()
     status_service = ENVService(env_config, publisher)
     status_service.run()
    # status_service.dew_point()
