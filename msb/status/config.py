from msb.config import MSBConf


class StatusConf(MSBConf):
    topic: bytes = b"status"
    seconds_between_updates: float = 10.0

    get_uptime: bool = True
    get_disk_usage: bool = True
    get_system_load: bool = True
    get_ram_usage: bool = True
    get_temperature: bool = True
    get_msb_services_status: bool = True
    get_network_status: bool = True
