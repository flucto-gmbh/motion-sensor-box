import time

from msb.config import load_config
from msb.dew.config import DewConf
from msb.dew.dew import air_pressure, estimate_dew_point, temperature_and_rel_humidity
from msb.network import Publisher, get_publisher
from uptime import uptime


class DewPointService:
    def __init__(self, config: DewConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher

        if self.config.verbose:
            print(self.config)

    @staticmethod
    def get_data() -> dict:
        temp_rel_hum = temperature_and_rel_humidity()
        temp, rel_hum = temp_rel_hum["temperature"], temp_rel_hum["relative_humidity"]
        air_pres = air_pressure()["air_pressure"]

        data = {
            "epoch": time.time(),
            "uptime": uptime(),
            "temperature": temp,
            "relative_humidity": rel_hum,
            "air_pressure": air_pres,
            "dew_point": estimate_dew_point(temp, rel_hum),
        }
        return data

    def run(self):
        # timing adapted from https://stackoverflow.com/a/25251804
        delta_t = self.config.seconds_between_updates
        start_time = time.time()
        while True:
            data = self.get_data()
            self.publisher.send(self.config.topic, data)
            if self.config.print_stdout:
                print(data)
            time.sleep(delta_t - ((time.time() - start_time) % delta_t))


def main():
    dew_config = load_config(DewConf(), "dew")
    publisher = get_publisher("zmq")
    dew_service = DewPointService(dew_config, publisher)
    dew_service.run()
