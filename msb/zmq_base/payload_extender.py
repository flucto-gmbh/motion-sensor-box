from msb.zmq_base.Payload import unpacker


def unpack_to_list(data_dict):
    return list(data_dict.values())


unpacker.register("list", unpack_to_list)
