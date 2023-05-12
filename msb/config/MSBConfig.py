from dataclasses import dataclass
import json
import os
import sys
import warnings
import yaml
import socket

@dataclass
class MSBConf():
    """
    default configuration class for generic configuration info
    """
    verbose: bool = False
    print_stdout: bool = False

    def __setitem__(self, key, value):
        if hasattr(self, key):
            self.__setattr__(key, value)
        else:
            warnings.warn(UserWarning(f"no such class member: {key}"))

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            warnings.warn(UserWarning(f"no such class member: {key}"))

    def to_json(self):
        return json.dumps({key : self[key] for key in vars(self)}, indent=4)

    @property
    def serial_number(self):
        return socket.gethostname().upper()

if __name__ == "__main__":
    msb_conf = MSBConfig()
    print(msb_conf)
