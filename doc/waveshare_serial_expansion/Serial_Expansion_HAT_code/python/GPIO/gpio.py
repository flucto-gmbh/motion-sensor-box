from ctypes import *
import time

gpio = CDLL('./SC16IS752GPIO.so')
OUT = 1
IN  = 0

# Initialize 8 pin GPIO:0-7
gpio.SC16IS752GPIO_Init()

# SC16IS752GPIO_Mode(int Pin, int Mode)
# Pin: 0~7
# Mode:0 = intput, 1 = output
gpio.SC16IS752GPIO_Mode(0, OUT)
gpio.SC16IS752GPIO_Mode(1, IN)

# Write Pin
# SC16IS752GPIO_Write(int Pin, int value)
# Pin: 0~7
# value:0 = Low level, 1 = High level
i = 0
for i in range(0, 10):
    gpio.SC16IS752GPIO_Write(0, i % 2)
    time.sleep(1)
    
# Read Pin
# SC16IS752GPIO_Read(int Pin)
# Pin: 0~7
gpio.SC16IS752GPIO_Read(1)
print("GPIO 1 = "),gpio.SC16IS752GPIO_Read(1)

# gpio.SC16IS752GPIO_Exit()
