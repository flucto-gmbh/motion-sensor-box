#!/bin/bash

# set -x
set -e

CWD=$(pwd)
SCRIPT_DIR=$(dirname $0)
CONFIG_DIR="${PWD}/${SCRIPT_DIR}/../config/services/"
SYSTEMD_DIR="/etc/systemd/system/"

# iterate over service files
for service_file in ${CONFIG_DIR}/*.service
do
	echo $service_file
	service_file_name=$(basename $service_file)

	if [[ $service_file_name == "rtunnel.service" ]]
	then
		echo "skipping $service_file_name"
		continue
	fi

	echo "copying $service_file_name to $SYSTEMD_DIR"
	sudo cp $service_file $SYSTEMD_DIR

done

sudo systemctl daemon-reload

sudo systemctl enable gpsd.service
sudo systemctl enable rtunnel.service
sudo systemctl enable msb-imu.service
sudo systemctl enable msb-gps.service
sudo systemctl enable msb-fusionlog.service
sudo systemctl enable msb-broker.service
sudo systemctl enable msb-attitude.service
sudo systemctl enable msb-lora.service
sudo systemctl enable msb-serialless-on.service
sudo systemctl enable msb-wifi.service
sudo systemctl enable msb-mqtt.service
