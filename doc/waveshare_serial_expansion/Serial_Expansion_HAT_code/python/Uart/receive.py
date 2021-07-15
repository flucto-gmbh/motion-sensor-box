# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time

dev = 1 #use ttySC0  => dev = 0, use ttySC1 => dev = 1
if dev == 0:
    ser = serial.Serial("/dev/ttySC0",115200,timeout=1)
else:
    ser = serial.Serial("/dev/ttySC1",115200,timeout=1)
time.sleep(1)
ser.flushInput()

data = ""
while 1: 
    while ser.inWaiting() > 0:
        data += ser.read(ser.inWaiting())
    if data != "":
        for i in range(len(data)):
            print data[i],
        print ""
        data = ""
