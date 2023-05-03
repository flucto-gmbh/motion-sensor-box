import json


def fluxpacker(data):
    time = data["timestamp"]  # convert to nanoseconds
    measurement = data["measurement"]
    return f"{measurement} {measurement}={data['data']}{time}"


def packer_factory(style):
    packstyles = {"json": json.dumps, "flux": fluxpacker, "default": json.dumps}
    if style in packstyles:
        return packstyles[style]
    else:
        return packstyles["default"]
