# System setup

The YASB boxes are based on a raspberry pi zero WH running raspberry os. The following packages are needed to successfully set up a yasb device:

## system configuration

To install packages, internet connectivity is required!

using raspi-config, the following settings must be set.
Enter the configuration by typing `sudo raspi-config`
- inteface options:
  - activate i2c
  - activate spi
  - disable login shell on serial and enable the hardware serial port
- Performance options
  - set GPU memory split to 16 MB
- Advanced Options:
  - enable perdictable network interface names

Optional for wifi:

- System Options
  - Wireless LAN

To check for wifi connectivity, type `ifconfig` and check if you have been assigned an IP address under the wifi adaptor `wlan0` -> inet

Finish the configuration and reboot the system.

To enable the serial expansion hat and pps, the following lines need to be added to `/boot/config.txt`.

Edit the file by running

```bash
sudo nano /boot/config.txt
```

and add the following lines to the end of the file:

```bash
dtoverlay=pps-gpio,gpiopin=13
```

On Raspberry OS, the default python version is 2.7.16 However, the motion sensor box requires python3 system wide. In order to configure this, please run 

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 2
```

This makes python 3.9 the default version on the system (highest priority number wins). To list all available python alternatives and configure them, type:

```bash
update-alternatives --config python
```

TODO: add description
Additionally, cmdline.txt and config.txt both on the boot partition need to be modified to:

- disable LED
- disable graphic stack

This nifty configuration trick was copied from [linuxconfig](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux)

## system packages

The following packages need to be installed via the package manager `apt`.

- git
- python3
- python3-dev
- python3-pip
- i2c-tools
- spi-tools
- python3-spidev
- python3-smbus
- python3-uptime
- nmcli
- screen
- scons
- libncurses5-dev
- python-dev
- pps-tools
- build-essential 
- manpages-dev
- pkg-config
- python3-cairo-dev
- libgtk-3-dev
- python3-serial
- libdbus-1-dev
- autossh

To install the packages, type the following:

```bash
sudo apt -y install git python3 python3-dev python3-pip i2c-tools spi-tools python3-spidev python3-smbus screen asciidoctor python3-matplotlib scons libncurses5-dev python3-dev pps-tools build-essential manpages-dev pkg-config python3-cairo-dev libgtk-3-dev python3-serial libdbus-1-dev autossh
```

Some packages need to be installed via pip:

```bash
pip3 install -r requirements.txt --user
```

### autossh

All motion-sensor-boxes will create a reverse ssh tunnel to the `flucto.tech` server for maintenance reasons. To enable this, an systemd service has to be set up.

The [rtunnel.service](../cfg/rtunnel.service) file contains the following configuration:

```bash
[Unit]
Description = reverse SSH tunnel
After =  network-online.target 
#Requires

[Service]
User = root
#Type = forking
Environment=AUTOSSH_GATETIME=0
ExecStart = /usr/bin/autossh -M 0 -q -N -o "PubKeyAuthentication=yes" -o "PasswordAuthentication=no" -o "ExitOnForwardFailure=yes" -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3"  -i /home/pi/.ssh/id_rsa -R [REMOTE PORT]:localhost:22 -l msb flucto.tech
ExecStop= /usr/bin/killall autossh
RestartSec=5
Restart=always

[Install]
WantedBy = multi-user.target
```

NOTE: you have to change PORT to a port that is still available.

Copy the pre-configured service file to `/etc/systemd/system/` and add the reverse ssh tunnel service to systemd:

```bash
sudo cp doc/rtunnel.service /etc/systemd/systemd/

sudo systemctl daemon-reload
sudo systemctl start rtunnel
sudo systemctl enable rtunnel
```

### gpsd

High accuracy time stamps are provided by synchronizing the system time using the GNSS receiver. Further documentation as to how to connect the gnss receiver, compile gpsd and configure gpsd can be found [here](./gpsd/gpsd.md)

### chronyd

As a ntp server, chrony is used. For successful configuration of chrony, please continue [here](./chrony/time-synchronisation.md)

## python

YASB requires a number of python3 modules to be present on the system. For each python script that makes up the yasb system, a requirements.txt file can be found in the respective folder. As an example, before running yasb_imul.py, install all dependencies by running:

```bash
python3 -m pip install -r yasb_imu/requirements.txt --user
```
