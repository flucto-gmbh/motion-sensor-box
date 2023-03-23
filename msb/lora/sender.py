import socket
import time
from config_lora import lora_hat_config
from config_lora import logging_config_dict
from driver import LoRaHatDriver
import logging
import logging.config
import pprint
import sys
from message import TextMessage

logging.config.dictConfig(logging_config_dict)


hostname = socket.gethostname()
with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(pprint.pformat(lora_hat.config))
    print("Press \033[1;32mCtrl+C\033[0m to exit")
    while True:
        text = f"{hostname} local time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\r\n"
        lora_hat.send(TextMessage(text).serialize())
        time.sleep(2)
