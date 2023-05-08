import shutil
from gpiozero import CPUTemperature
import psutil
from pystemd.systemd1 import Manager
import os


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
    return {}


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


def msb_services() -> dict:
    with Manager() as manager:
        msb_units = (u for u in manager.ListUnits() if b"msb-" in u[0])
        enabled = {
            os.path.basename(uf.decode("utf-8")): s.decode("utf-8")
            for uf, s in manager.Manager.ListUnitFiles()
            if b"msb-" in uf
        }
        services = {}
        for unit in msb_units:
            name = unit[0].decode("utf-8")
            status = {
                "description": unit[1].decode("utf-8"),
                "loaded": unit[2].decode("utf-8"),
                "active": unit[3].decode("utf-8") + f" ({unit[4].decode('utf-8')})",
                "enabled": enabled[name],
            }
            services[name] = status

    return services
