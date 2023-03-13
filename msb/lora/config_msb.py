from socket import gethostname

lora_hat_config = {
    "module_address": int(gethostname()[4:8]),
    "target_address": 0xFFFF,
}

msb_config = {
    # this assumes that all 4 senders have subsequent id's
    # if this is not the case set the sender time slot here manually
    # to one 0, 1, 2 or 3
    "sender_time_slot": lora_hat_config["module_address"] % 4,
}