The motion sensor boxes are based on a raspberry pi zero WH running raspberry os. The following packages are needed to successfully set up a yasb device:

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

On older versions of Raspberry OS, the default python version is 2.7.16 However, the motion sensor box requires python3 system wide. In order to configure this, please run 

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

To ensure the raspberry pi does not run out of memory, the swap space needs to be configured. Open the file `/etc/dphys-swapfile`, comment out the current settings and add 
``
CONF_SWAPFACTOR=2
CONF_MAXSWAP=2048

``

## system packages

A number of packages are needed in order for the software stack to function properly.
To install the packages, we first need to add some sources (for the camera)
```bash
curl https://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -
echo "deb https://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" | sudo tee /etc/apt/sources.list.d/uv4l.list
sudo apt-get update
```

Now we can install system packages

```bash
sudo apt -y install git python3 python3-dev python3-pip i2c-tools spi-tools \
                    python3-spidev python3-smbus screen asciidoctor python3-matplotlib \
                    libncurses5-dev python3-dev pps-tools build-essential manpages-dev \
                    pkg-config python3-cairo-dev libgtk-3-dev python3-serial libdbus-1-dev \
                    autossh mosh python3-numpy scons rsync vim uv4l uv4l-raspicam \
                    uv4l-raspicam-extras uv4l-server uv4l-uvc uv4l-xscreen uv4l-mjpegstream \
                    uv4l-dummy uv4l-raspidisp uv4l-webrtc-armv6 uv4l-raspidisp-extras \
                    gstreamer1.0-tools gstreamer1.0-plugins-bad gstreamer1.0-plugins-good \
                    gstreamer1.0-libav python3-picamera cmake pkg-config libjpeg-dev \
                    libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev \
                    libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev \
                    libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev \
                    libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev \
                    libhdf5-103 python3-pyqt5 python3-dev python3-opencv chrony python3-pandas
```

Some packages need to be installed via pip:

```bash
python -m pip install -r requirements.txt --user
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

The motion sensor box relies on [gpsd](https://gpsd.io/) and chronyd to generate an accurate time stamp for all it's measurements. Therefore a Navilock NL-852ETLL GNSS receiver is attached to the serial port /dev/ttySC0. 
Apart from the standard NMEA sentence transmitted via serial port, a second signal (1 pulse per second, PPS) is generated by the receiver. This line is attached to GPIO Pin 13 (see [yasb pinout](../YASB_pinout.png)).

Because the gpsd package provided by raspberry pi OS is quite old, the upstream gpsd code must first be pulled, compiled and installed, following the [official guide](https://gitlab.com/gpsd/gpsd/-/blob/master/build.adoc) and more specifically [this](https://gpsd.io/installation.html#_other_raspberry_pi_tips).
 
The configuration of chronyd follows largely [this](https://www.slsmk.com/how-to-setup-a-gps-pps-ntp-time-server-on-raspberry-pi/) instruction. 

#### Installation of gpsd

1. change into the source folder lib/gpsd. gpsd is a submodule in the yasb repository.
2. build gpsd by running:

```bash
scons -config=force
```

3. check the build by running

```bash
scons check
```

4. install udev rules by running

```bash
cp gpsd.rules.in gpsd-3.23.2~dev/gpsd.rules
sudo scons udev-install
```

After compilation, the gps python package is located under `/usr/local/lib/python3/dist-packages/`. This is hard coded in `msb_gps.py`. 

#### Running gpsd

gpsd is now installed and can be tested by running the commands below which will run gpsd in the background. To stop gpsd again, press `CTRL+C`.

```bash
sudo gpsd -N -n /dev/ttyACM0 &
gpsmon -n
```

#### Configuration

##### gpsd config file

A configuration file containing all necessary info for gpsd to run properly needs to be placed in `/etc/default/gpsd`. The config file can be found in the `cfg` folder. Copy it with the following command:

```bash
sudo cp cfg/gpsd.conf /etc/default/gpsd
```

##### systemd

per default, gpsd installs `gpsd.service` and `gpsd.socket` at `/usr/lib/systemd/system/`

You can start gpsd by typing `sudo systemctl start gpsd`

You can check gpsd's status by typing `sudo systemctl status gpsd`.

The following lists the systemd service and socket file.

gpsd.service

```bash
[Unit]
Description=GPS (Global Positioning System) Daemon
Requires=gpsd.socket
# Needed with chrony SOCK refclock
After=chronyd.service

[Service]
Type=forking
EnvironmentFile=-/etc/default/gpsd
EnvironmentFile=-/etc/sysconfig/gpsd
ExecStart=/usr/local/sbin/gpsd $GPSD_OPTIONS $OPTIONS $DEVICES

[Install]
WantedBy=multi-user.target
Also=gpsd.socket
```

gpsd.socket

```bash
[Unit]
Description=GPS (Global Positioning System) Daemon Sockets

[Socket]
ListenStream=/run/gpsd.sock
ListenStream=[::1]:2947
ListenStream=127.0.0.1:2947
# To allow gpsd remote access, start gpsd with the -G option and
# uncomment the next two lines:
# ListenStream=[::]:2947
# ListenStream=0.0.0.0:2947
SocketMode=0600
BindIPv6Only=yes

[Install]
WantedBy=sockets.target
```

#### Interfacing gpsd with client applications

Official documentation [here](https://gpsd.gitlab.io/gpsd/client-howto.html)

High accuracy time stamps are provided by synchronizing the system time using the GNSS receiver. Further documentation as to how to connect the gnss receiver, compile gpsd and configure gpsd can be found [here](./gpsd/gpsd.md)

### chronyd

As a ntp server, chrony is used. For successful configuration of chrony, please continue [here](./chrony/time-synchronisation.md)

### StromPi3

Power is managed by the [strompi3](https://strompi.joy-it.net/strompi-family), an embedded USV. The strompi3 needs to be put into "serialless mode" to prevent
serial communication breakdown of the pi with the LoRa board. To do so, use the config script: `scripts/strompi3/strompi_config.py`

Upon first boot, configure the strompi3 such that all options except the serialless mode are disabled. Reboot.

Then, on every boot, first start the serialless mode via the script `scripts/strompi3/start_serialless.py`. Afterwards, the serial connection can be used by the lora board.

To power off, first stop the lora service (e.g. `sudo systemctl stop msb-lora.service`), disable serialless mode via `scripts/strompi3/stop_serialless.py` and then power off via `scripts/strompi3/poweroff.py`. 

The Serialless jumper on the strompi only controls whether signals will be put through to pin 21 on the pi, needed for communication with the strompi with serialless mode active. It needs to be put in the "on" position.
