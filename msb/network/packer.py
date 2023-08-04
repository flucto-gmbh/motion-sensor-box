import json
import pickle


def get_packer(style):
    if style in _packstyles:
        return _packstyles[style]
    else:
        return _packstyles["default"]


def get_unpacker(style):
    if style in _unpackstyles:
        return _unpackstyles[style]
    else:
        return _unpackstyles["default"]


def serialpacker(data: dict):
    return ",".join([str(v) for v in data.values()])


_packstyles = {
    "json": json.dumps,
    "pickle": pickle.dumps,
    "serial": serialpacker,
    "default": json.dumps,
}

_unpackstyles = {
    "json": json.loads,
    "raw" : lambda x: x,
    "pickle": pickle.loads,
    "default": json.loads,
}
