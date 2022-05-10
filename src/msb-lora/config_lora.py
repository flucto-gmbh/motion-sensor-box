import logging
import logging.config
import os

from driver import (
    BaudRate,
    ParityBit,
    AirSpeed,
    PacketLen,
    TransmitPower,
    WORMode,
    WORPeriod,
)

# %% logging config
log_config = {
    "log_level": "DEBUG",
    "log_file": "/tmp/msb_lora}.log",
    "log_to_console": True,
}

_log_handlers = []
if log_config.get("log_to_console", False):
    _log_handlers.append("console")
if log_config.get("log_file", ""):
    _log_handlers.append("file_handler")

logging_config_dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "loggers": {
        "": {
            "handlers": _log_handlers,
            "level": log_config.get("log_level", "WARNING"),
            "propagate": True,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_config.get("log_level", "WARNING"),
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "level": log_config.get("log_level", "WARNING"),
            "formatter": "standard",
            "filename": log_config.get("log_file", ""),
        },
    },
    "formatters": {
        "standard": {
            "format": "%(levelname)s: %(asctime)s %(message)s",
            "datefmt": "%Y%m%dT%H%M%S%z",
        },
    },
}
logging.config.dictConfig(logging_config_dict)

# %% lora hat config
lora_hat_default = {
    "module_address": 0,
    "net_id": 0,
    "baud_rate": BaudRate.BR_9600,
    "parity_bit": ParityBit.PB_8N1,
    "air_speed": AirSpeed.AS_2_4K,
    "packet_len": PacketLen.PL_240B,
    "enable_ambient_noise": False,
    "transmit_power": TransmitPower.TP_22dBm,
    "channel": 18,  # 18 default for SX1262, 23 default for SX1268
    "enable_RSSI_byte": False,
    "enable_point_to_point_mode": False,
    "enable_relay_function": False,
    "enable_LBT": False,
    "WOR_mode": WORMode.WOR_transmit,
    "WOR_period": WORPeriod.WP_500ms,
    "key": 0,
}

lora_hat_config = lora_hat_default.copy()
lora_hat_config["enable_point_to_point_mode"] = True
lora_hat_config["channel"] = 73  # ^= 923.125MHz
lora_hat_config["air_speed"] = AirSpeed.AS_1_2K


try:
    lora_hat_config["key"] = int(os.environ["MSB_LORA_HAT_KEY"])
except KeyError:  # Environment variable not set
    pass

if lora_hat_config["key"] == 0:
    logging.warning("No secret key set.")
