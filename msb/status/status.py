import shutil
import socket

import psutil
from gpiozero import CPUTemperature

from msb.status._systemd import SystemdStatusParser


def disk_usage() -> dict:
    usage = shutil.disk_usage("/")
    byte_to_gib = 1024**3
    usage_gib = {
        "total": usage.total / byte_to_gib,
        "used": usage.used / byte_to_gib,
        "free": usage.free / byte_to_gib,
    }
    return usage_gib


def network_status() -> dict:
    net_if_addrs = psutil.net_if_addrs()
    status = {}
    for network_interface in net_if_addrs:
        addrs = {}
        for address in net_if_addrs[network_interface]:
            if address.family == socket.AF_INET:
                ipv_key = "IPv4"
            elif address.family == socket.AF_INET6:
                ipv_key = "IPv6"
            else:
                continue
            addrs[ipv_key] = {"address": address.address, "netmask": address.netmask}
        status[network_interface] = addrs
    return status


def system_load() -> dict:
    n_cores = psutil.cpu_count(logical=True)
    averages = psutil.getloadavg()
    return {
        "n_cores": n_cores,
        "average_1min": averages[0],
        "average_5min": averages[1],
        "average_15min": averages[2],
    }


def ram_usage() -> dict:
    byte_to_Mib = 1024**2
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram": {
            "total": ram.total / byte_to_Mib,
            "available": ram.available / byte_to_Mib,
            "percent": ram.percent,
        },
        "swap": {
            "total": swap.total / byte_to_Mib,
            "free": swap.free / byte_to_Mib,
            "percent": swap.percent,
        },
    }


def temperature() -> dict:
    # https://raspberrypi.stackexchange.com/a/93286
    cpu = CPUTemperature()
    return {"cpu": cpu.temperature}


msb_services = SystemdStatusParser()
