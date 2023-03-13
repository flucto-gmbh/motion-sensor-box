import logging
import logging.config
import pprint
import queue
import threading
import sys

from config_lora import lora_hat_config
from config_lora import logging_config_dict
from driver import LoRaHatDriver
from message import TextMessage

logging.config.dictConfig(logging_config_dict)

q = queue.SimpleQueue()


def print_received_data():
    while True:
        message = TextMessage.from_bytes(q.get())
        print(f"{message.topic.name}: {message.content}")


threading.Thread(target=print_received_data, daemon=True).start()

with LoRaHatDriver(lora_hat_config) as lora_hat:
    logging.debug(pprint.pformat(lora_hat.config))
    print("Press \033[1;32mCtrl+C\033[0m to exit")
    while True:
        q.put(lora_hat.receive())
