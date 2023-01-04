import json
import os
import sys
import yaml

class MSBConfig(object):

    def __init__(self, subconf : str = "general"):
        self._conf_fname = "msb.conf"
        self._env_varname = "MSB_CONFIG_DIR"
        if not self._env_varname in os.environ:
            raise Exception("please set the $MSB_CONFIG_DIR environment variable")
        self._conf_fpath = os.path.join(os.environ[self._env_varname], self._conf_fname)
        self._load_conf(subconf=subconf)
        self._construct_zmq_socketstrings()

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def _load_conf(self, subconf : str):
        try:
            with open(self._conf_fpath, 'r') as conf_fhandle:
                for att_name, att_value in yaml.safe_load(conf_fhandle)[subconf].items():
                    setattr(self, att_name, att_value)
        except Exception as e:
            print(f"failed to open and parse config file: {e}")
            sys.exit()

    def _print_verbose(self, msg : str):
        if self._cmdline_conf['verbose'] or self.verbose:
            print(msg)

    # return f"{zmq_config['protocol']}://{zmq_config['address']}:{zmq_config['xpub_port']}"
    def _construct_zmq_socketstrings(self):
        if not hasattr(self, 'zmq'):
            raise Exception("Missing zmq config")
        self.zmq['xsub_connect_string'] = f"{self.zmq['protocol']}://{self.zmq['address']}:{self.zmq['xsub_port']}"
        self.zmq['xpub_connect_string'] = f"{self.zmq['protocol']}://{self.zmq['address']}:{self.zmq['xpub_port']}"
    
    @property
    def xsub_socketstring(self) -> str:
        return f"{self.zmq['xsub_connect_string']}"
    
    @property
    def xpub_socketstring(self) -> str:
        return f"{self.zmq['xpub_connect_string']}"

if __name__ == "__main__":
    msb_conf = MSBConfig()
    print(msb_conf)
