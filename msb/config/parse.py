from dataclasses import dataclass
import json
import os
import sys
import yaml

def get_msb_config_filepath(config_filename : str = "msb.conf") -> str:
    try:
        config_filepath = os.path.join(os.environ['MSB_CONFIG'], config_filename)
    except Exception as e:
        print(f"could no get MSB_CONFIG from PATH: {e}")
        sys.exit()
    if not os.path.isfile(config_filepath):
        print('not a file: {config_filepath}!')
        sys.exit()
    return config_filepath

def parse_msb_config(msb_config_filepath : str) -> dict:
   with open(msb_config_filepath, 'r') as msb_config_filehandle:
        msb_config = yaml.safe_load(msb_config_filehandle)
        return msb_config

def read_yaml_config_file(config_fpath : str) -> dict:
    with open(config_fpath, 'r') as config_filehandle:
        return yaml.safe_load(config_filehandle)

def update_config(config_object, config_conffile : dict):
    for config_key, config_value in config_conffile.items():
        config_object[config_key] = config_value

if __name__ == "__main__":
    msb_config = parse_msb_config(get_msb_config_filepath())
    print(json.dumps(msb_config, indent=4))
