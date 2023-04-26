import os
import sys
import warnings
import yaml

from typing import TypeVar

from msb.config import MSBConf

ConfigType = TypeVar("ConfigType", bound=MSBConf)


def get_msb_config_filepath(config_filename : str = "msb.conf") -> str:
    config_subpath = os.path.join("msb/conf.d/", config_filename)
    try:
        config_filepath = os.path.join(os.environ['MSB_CONFIG_DIR'], config_subpath)
    except Exception as e:
        print(f"could no get MSB_CONFIG from PATH: {e}")
        sys.exit() # TODO use 1 or the error str as exit value
    if not os.path.isfile(config_filepath):
        print('not a file: {config_filepath}!')
        sys.exit()
    return config_filepath


def read_yaml_config_file(config_fpath : str) -> dict:
    with open(config_fpath, 'r') as config_filehandle:
        return yaml.safe_load(config_filehandle)


def update_config(config: ConfigType, config_dict : dict) -> ConfigType:
    for config_key, config_value in config_dict.items():
        # get expected type of element from config_object:
        if not hasattr(config, config_key):
            warnings.warn(f"no such configuration parameter: {config_key}, skipping")
            continue
        cast_func = type(config[config_key])
        try:
            config[config_key] = cast_func(config_value)
        except Exception as e:
            print(f'failed to cast {config_value} to {type(config[config_key])}: {e}. skipping')
            continue
    return config
