import time

from msb.config import load_config
from msb.status.config import StatusConf
from msb.zmq_base.Publisher import Publisher, get_default_publisher
from msb.status.status import (
    disk_usage,
    msb_services,
    ram_usage,
    temperature,
    system_load,
    network_status,
)
from uptime import uptime


class StatusService:
    def __init__(self, config: StatusConf, publisher: Publisher):
        self.config = config
        self.publisher = publisher

        if self.config.verbose:
            print(self.config)

    def get_data(self) -> dict:
        data = {}
        if self.config.get_uptime:
            data["uptime"] = uptime()
        if self.config.get_disk_usage:
            data["disk_usage"] = disk_usage()
        if self.config.get_msb_services_status:
            data["msb_services_status"] = msb_services()
        if self.config.get_temperature:
            data["temperature"] = temperature()
        if self.config.get_ram_usage:
            data["ram_usage"] = ram_usage()
        if self.config.get_system_load:
            data["system_load"] = system_load()
        if self.config.get_network_status:
            data["network_status"] = network_status()

        data["epoch"] = time.time()
        return data

    def run(self):
        # timing adapted from https://stackoverflow.com/a/25251804
        delta_t = self.config.seconds_between_updates
        start_time = time.time()
        while True:
            data = self.get_data()
            self.publisher.send(self.config.topic, data)
            time.sleep(delta_t - ((time.time() - start_time) % delta_t))


def main():
    status_config = load_config(StatusConf(), "status")
    publisher = get_default_publisher()
    status_service = StatusService(status_config, publisher)
    status_service.run()
