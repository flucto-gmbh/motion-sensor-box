#!/usr/bin/env bash

set +x
set +e

export MSB_HOME=$(pwd)

SYSTEMD_DIR=/etc/systemd/system

echo "Bootstrapping Motion Sensor Box"

# - copy wpa_supplicant (in case of update or non-network installation)
# - cp hosts and hostname to /etc
# - copy config.txt to /boot/
# - install packages via apt
# - install packages via pip
# - setup remote ssh tunnel
# - compile and install gpsd
# - copy, enable and start other systemd services

