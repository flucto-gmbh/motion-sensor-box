#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import zmq
import time
from threading import Thread


class Poller(Thread):

    def __init__(self, id, topic):
        super().__init__()
        self.id = id
        self.topic = topic

    def run(self):
        print('start poller {}'.format(self.id))
        subscriber = context.socket(zmq.SUB)
        subscriber.connect("tcp://127.0.0.1:5559")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.loop = True
        while self.loop:
            message = subscriber.recv()
            print('poller {}: {}'.format(self.id, message))

    def stop(self):
        self.loop = False


context = zmq.Context()

poller1 = Poller(1, 'NASDA')
poller1.start()

poller2 = Poller(2, 'NASDAQ')
poller2.start()


socket = context.socket(zmq.PUB)
socket.connect("tcp://127.0.0.1:5560")

for index in range(3):
    time.sleep(2)
    socket.send_string('NASDA:' + time.strftime('%H:%M:%S'))
    time.sleep(2)
    socket.send_string('NASDAQ:' + time.strftime('%H:%M:%S'))


poller1.stop()
poller2.stop()
socket.send_string('NASDAQ:STOP')

sys.exit(0)
