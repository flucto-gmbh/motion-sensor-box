# Waveshare serial expansion board

## Configuration

add the following to /boot/config.txt

```
dtoverlay=sc16is752-i2c,int_pin=24,addr=0x49
```

Because the default I2C address of the serial expansion board collides with the ICM-20948's I2C address, the serial expansion boards address needs to be changed by removing one of the smd resistors (see images).

