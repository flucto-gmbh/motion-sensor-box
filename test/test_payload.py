from msb.zmq_base.Payload import Payload, unpacker
import msb.zmq_base.payload_extender

import json

def test_payload():
    pl = Payload()
    compr = pl.to_json()


    # obj = unpacker.unpack("dataclass", compr)
    # obj = unpacker.unpack("json", compr)

    # print(obj)
    print(unpacker.unpack("list", compr))
    print(unpacker.unpack("obj", compr))

    # print(json.loads(compr))

    # assert obj.data == pl.data


if __name__ == "__main__":
    test_payload()

