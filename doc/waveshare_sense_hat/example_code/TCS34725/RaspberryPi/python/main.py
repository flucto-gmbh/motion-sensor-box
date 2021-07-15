#!/usr/bin/python
import time
import RPi.GPIO as GPIO
from TCS34725 import TCS34725


try:
    Light=TCS34725(0X29, debug=False)
    if(Light.TCS34725_init() == 1):
        print("TCS34725 initialization error!!")
    else:
        print("TCS34725 initialization success!!")
    time.sleep(2)
    while True:
     
        Light.Get_RGBData()
        Light.GetRGB888()
        Light.GetRGB565()
        print("R: %d "%Light.RGB888_R), 
        print("G: %d "%Light.RGB888_G), 
        print("B: %d "%Light.RGB888_B), 
        print("C: %#x "%Light.C),
        print("RGB565: %#x "%Light.RG565),
        print("RGB888: %#x "%Light.RGB888),    
        print("LUX: %d "%Light.Get_Lux()),
        print("CT: %dK "%Light.Get_ColorTemp())
       
except:
    GPIO.cleanup()
    print "\nProgram end"
    exit()
