import time
import board
import adafruit_shtc3 #temperature / humidity sensor;  I2C adress: 0x70
import adafruit_lps2x #pressure sensor; I2C adress: 0x5C: Make sure that you change the adress 0x5D to 0x5C in the library adafruit_lps2x 
 
def sht() -> dict: #temperature / humidity sensor
    i2c = board.I2C()
    sht = adafruit_shtc3.SHTC3(i2c)
    temperature, relative_humidity = sht.measurements
    sht = {
        "temperature" : temperature,
        "relative_humidity": relative_humidity
    }
    return sht

def lps() -> dict: #pressure sensor
    i2c = board.I2C()
    lps = adafruit_lps2x.LPS22(i2c)
    lps = {
        "pressure": lps.pressure
    }
    return lps










