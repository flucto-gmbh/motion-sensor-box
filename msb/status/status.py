import shutil

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
    return {}


def ram_usage() -> dict:
    return {}


def temperature() -> dict:
    return {}


def msb_services() -> dict:
    return {}