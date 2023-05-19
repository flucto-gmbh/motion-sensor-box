import re
import shutil
import socket
import subprocess

import psutil
from gpiozero import CPUTemperature


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
    current = psutil.cpu_percent()
    averages = psutil.getloadavg()
    return {
        "current": current,
        "average_1min": averages[0],
        "average_5min": averages[1],
        "averages_15min": averages[2],
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


_name_desc_pattern = re.compile(r"^(msb-\w*\.service)\s-\s([\w\s]*)")
_loaded_enabled_pattern = re.compile(
    r"^Loaded:\s(loaded)\s\(/etc/systemd/system/msb-\w+\.service;\s(\w*);"
)
_active_pattern = re.compile(r"^Active:\s(\w*\s\(\w*\))")


def msb_services() -> dict:
    completed_process = subprocess.run(
        ["systemctl", "status", "msb-*"], capture_output=True, encoding="utf-8"
    )
    answer = completed_process.stdout
    service_strs = [s.strip() for s in answer.split("●") if s.strip()]
    service_status = {}
    for service_str in service_strs:
        service_lines = [l.strip() for l in service_str.split("\n") if l.strip()]

        if m := _name_desc_pattern.match(service_lines[0]):
            name, desc = m.groups()
        else:
            print("Could not parse service status name and description.")
            continue
        if m := _loaded_enabled_pattern.match(service_lines[1]):
            loaded, enabled = m.groups()
        else:
            print("Could not parse service status loaded and enabled.")
            continue
        if m := _active_pattern.match(service_lines[2]):
            (active,) = m.groups()
        else:
            print("Could not parse service status active.")
            continue

        service_status[name] = {
            "description": desc,
            "loaded": loaded,
            "enabled": enabled,
            "active": active,
        }
    return service_status
