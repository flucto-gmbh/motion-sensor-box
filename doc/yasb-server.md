# YASB Server Setup Documentation

## Preface

This document describes in a step-by-step manner how to set up a raspberry pi running debian (raspbian) as a yasb server.
The yasb server runs a wifi network for other yasb clients to connect to. Additionally, other interfaces, such as LoRaWAN, wifi-send or bluetooth are also served. 

## Access point configuration

### Raspberry Pi

In order to enable this functionality, a number of services (e.g. software demons) need to be running on the yasb server. These include:

- DHCP
- HOSTAPD
- DNS

IP-tables will be used to route incoming traffic. 

The setup is loosely based on the tutorial by the raspbian os tutorial, which can be found [here](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md)

The main deviation from the above tutorial is, that instead of the onboard wifi chip, a TP-Link TL-WN722N is used. The interface thus can be found at wlan1

### Fedora workstation

To configure a hotspot using network manager, create a new connection (either via graphical user interface) or by creating a config file under `/etc/sysconfig/network-scripts`. An exemplay configuration file is listed here:

```
HWADDR=6C:88:14:72:8B:80    # your wifi chips MAC address
ESSID=yasb                  # name of the network
MODE=Ap
KEY_MGMT=WPA-PSK
MAC_ADDRESS_RANDOMIZATION=default
TYPE=Wireless
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=shared
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=shared
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_PRIVACY=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=yasbAP
UUID=c66964be-490e-45d4-b91a-20b151771777
DEVICE=wlp3s0               # your device name
ONBOOT=yes
```
Please note, that on fedora firewalld might interfere with udp network traffic. To disable the firewall daemon, run:

```
sudo systemctl stop firewalld.service
```





