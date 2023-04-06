from dataclasses import dataclass
import json
import os
import sys
import warnings
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

def read_yaml_config_file(config_fpath : str) -> dict:
    with open(config_fpath, 'r') as config_filehandle:
        return yaml.safe_load(config_filehandle)

def update_config(config_object, config_conffile : dict):
    for config_key, config_value in config_conffile.items():
        # get expected type of element from config_object:
        if not hasattr(config_object, config_key):
            warnings.warn(f"no such configuration parameter: {config_key}, skipping")
            continue
        cast_func = type(config_object[config_key])
        try:
            config_object[config_key] = cast_func(config_value)
        except Exception as e:
            print(f'failed to cast {config_value} to {type(config_object[config_key])}: {e}. skipping')
            continue

