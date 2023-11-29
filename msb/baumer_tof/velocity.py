#!/bin/python3
import time
import json
from os import path
import signal
import sys
from msb.network.zmq.subscriber import get_default_subscriber
from msb.network.zmq.publisher import get_default_publisher

class Velocity:
    def __init__(self):
        self.pub = get_default_publisher()
        self.sub = get_default_subscriber("baumer_tof")
        self.data_dic = {"timestamp":[], "distance": []}
        self.topic,self.payload = self.sub.receive()
        self.topic = b"tof_velocity"
        self.initial_timestamp = self.payload["epoch"]
        self.initial_distance = self.payload["distance"] 
        self.set_up()
        self.run()

    def run(self):
        while True:
            data = self.calc_velocity()
            if data is not None:
                self.pub.send(self.topic, data)

    def set_up(self):
        for key in self.data_dic:
            if key == "timestamp":
                self.data_dic[key].append(self.initial_timestamp)
            if key == "distance":
                self.data_dic[key].append(self.initial_distance)
        return "Set up"

    def add_data(self,timestamp,distance):
        for key in self.data_dic:
            if key == "timestamp":
                self.data_dic[key].append(timestamp)
            if key == "distance":
                self.data_dic[key].append(distance)

    def calc(self):
        delta_time = self.data_dic["timestamp"][1] - self.data_dic["timestamp"][0]
        delta_distance = self.data_dic["distance"][1] - self.data_dic ["distance"][0]
        velocity = delta_distance / delta_time
        return velocity

    def reorder_list(self):
        for key in self.data_dic:
            del self.data_dic[key][0]

    def calc_velocity(self):
        try:
            topic,payload = self.sub.receive()
            timestamp = payload["epoch"]
            distance = payload["distance"]
            self.add_data(timestamp,distance)
            velocity = self.calc()
            epoch = time.time()
            self.reorder_list()
            return {"epoch": epoch, "velocity": velocity}
            
        except KeyboardInterrupt:
            print("msbpipe.py exit")
            sys.exit(0)


def main():
    velocity = Velocity()
