#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt -y install git python3 python3-dev python3-pip i2c-tools spi-tools python3-spidev \
	python3-smbus screen asciidoctor python3-matplotlib libncurses5-dev python3-dev \
	pps-tools build-essential manpages-dev pkg-config python3-cairo-dev libgtk-3-dev \
	python3-serial libdbus-1-dev autossh mosh python3-numpy scons

git clone https://github.com/flucto-gmbh/motion-sensor-box --recursive

mkdir .ssh

cd motion-sensor-box

# install python requirements
python -m pip install -r requirements.txt --user

# build gpsd
cd lib/gpsd
scons config=force
sudo scons udev-install

# cp gpsd config
cd ../../
sudo cp cfg/gpsd.conf /etc/default/gpsd

# cp rtunnel service file
sudo cp cfg/rtunnel.service /etc/systemd/system/
sn=$(hostname | cut -d '-' -f 2)
port=$(echo "$sn + 65000" | bc)

# insert the correct port based on the serial number (hostname)
sudo sed -i -e "s/\[REMOTE PORT\]/$port/" /etc/systemd/system/rtunnel.service

# install services
./scripts/install_services.sh

