from typing import TypeVar

from msb.config.MSBConfig import MSBConf
from msb.config.parse import get_msb_config_filepath, read_yaml_config_file, update_config
from msb.config.cmdline import get_cmdline


__all__ = ["load_config", "MSBConf"]

ConfigType = TypeVar("ConfigType", bound=MSBConf)  # https://stackoverflow.com/a/46227137 , https://docs.python.org/3/library/typing.html#typing.TypeVar


def load_config(config: ConfigType, config_filename: str, read_commandline: bool = True) -> ConfigType:
    """Load the config file and update the config object.

    Parameters
    ----------
    config : MSBConf
        The config object to fill with values.
    config_filename : str
        The name of the config file in $MSB_CONF/msb/conf.d/.
        If the file does not have an extension the default extension .yaml is appended.
    read_commandline : bool
        Whether to read arguments from the command line. Optional. Defaults to True.
    """
    config_filename = config_filename if "." in config_filename else config_filename + ".yaml"
    config_filepath = get_msb_config_filepath(config_filename)
    config_dict = read_yaml_config_file(config_filepath)
    print(config)
    print(config_dict)
    config = update_config(config, config_dict)
    print(config)

    if not read_commandline:
        return config

    config_dict = get_cmdline()
    config = update_config(config, config_dict)
    return config


