import json
from datetime import datetime


class Payload:
    def __init__(self):
        self.data = "hello world"
        self.name = "payload"
        self.owner = "msb"
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Packer:
    def __init__(self):
        self.packers = {}

    def register(self, name, func):
        self.packers[name] = func

    def pack(self, pack_type, data):
        return self.packers[pack_type](data)


class Unpacker:
    def __init__(self):
        self.unpackers = {}

    def register(self, name, func):
        self.unpackers[name] = func

    def unpack(self, unpack_type, data):
        data_dict = json.loads(data)
        return self.unpackers[unpack_type](data_dict)


def unpack_to_dataclass(data_dict):
    class dc:
        def __init__(self, data_dict):
            for key, value in data_dict.items():
                setattr(self, key, value)

    return dc(data_dict)


def unpack_to_dict(data):
    return data


packer = Packer()
packer.register(
    "json",
    lambda x: json.dumps(x, default=lambda o: o.__dict__, sort_keys=True, indent=4),
)

unpacker = Unpacker()
unpacker.register("dataclass", unpack_to_dataclass)
unpacker.register("json", unpack_to_dict)
