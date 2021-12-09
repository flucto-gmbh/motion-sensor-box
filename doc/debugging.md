# Debugging a non-responsive motions sensor box

## Hardware

1. Connect the Cybercube to a power supply. 
    - Does the blue LED on the strom pi light up? If not, make sure, that the power cables are connected correctly, that there is actually power coming from the power source and that the jumpers on the strompi are set correctly
    - Does the green LED on the Raspberry Pi light up (flash)? While booting, activity of the raspberry pi zero is indicated by the green LED. If the LED on flashes shortly in the beginning and then ceases, there is probably something wrong with the CD-card.

2. If all of the above checks out, remove power from the raspberry pi, and then remove all HATs from the electronics stack and reconnect power to the strom pi. If the box now connects to the wifi, one of the shields may cause a short and thus prevent the raspberry pi from booting.

3. If the raspberry pi is still not connecting to the wifi, remove power from the strom pi and  use a microHDMI to HDMI adapter to connect the raspberry pi to a computer screen. Add a keyboard as well via a USB OTG cable enter commands at the command line. Reconnect power to the strom pi and watch the output from the boot process. Once the raspberry pi has successfully booted up, login via the keyboard and start software debugging.

4. If the raspberry does not boot, the culprit is most likely the SD-card. Remove the SD-card, get a copy of the latest stable version of raspberry pi os and flash it onto the SD-card. If the raspberry pi boots with the new SD card, proceed with a normal setup as described in the README of the motion sensor box repository.

## Software

1. Once you have logged into the raspberry pi, first check out the available network interfaces. Type `ifconfig` into the console to see what network interfaces are available. `lo` is the loopback interface, whereas `wlan0` should be the wifi adapter. The output from `ifconfig` should look something like this: 
```bash
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 234  bytes 39423 (38.4 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 234  bytes 39423 (38.4 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.98  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::8bba:c5bb:96f9:9d51  prefixlen 64  scopeid 0x20<link>
        inet6 2a02:8109:ebf:d2d4:aa43:7dac:3bb2:b5a  prefixlen 64  scopeid 0x0<global>
        ether b8:27:eb:f3:a6:2a  txqueuelen 1000  (Ethernet)
        RX packets 258781  bytes 13999084 (13.3 MiB)
        RX errors 0  dropped 4  overruns 0  frame 0
        TX packets 30878  bytes 3492336 (3.3 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

2. If the wifi adapter is not present, it might be deactivated via the rfkill command or because the country code has not been set yet (see for example [this question on stack overflow](https://raspberrypi.stackexchange.com/questions/123717/how-to-disable-wi-fi-is-currently-blocked-by-rfkill-message)).  To check whether the country code has been set successfully, open the file `/etc/wpa_supplicant/wpa_supplicant.conf`. The header of the file should include a line defining the country code, e.g. for Germany:

```bash
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=DE

network={
        ssid="flucto"
        psk="yasbyasbyasb"
        priority=1
}
```
if the country code is available, make sure, that the wifi you are trying to connect to is actually listed in the file. Note: a higher number corresponds to a higher priority of the wifi network if two competing networks are available.

3. If the network is present in `wpa_supplicant.conf` and the country code has been set as well, but the network adapter is not present in the output of `ifconfig`, type `rfkill` in the console to see if wifi is blocked manually. If this is the case, use `rfkill unblock wlan0`. Type `ifconfig` again and if the wifi adapter is still not listed, the wifi chip might actually be broke. Switch out the rasberry pi and proceed with a normal installation.

