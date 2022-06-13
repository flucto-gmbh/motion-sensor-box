#!/bin/bash

set -e  # exit if an error occurs
set -x  # print each executed command to stdout

CWD=$(pwd)
SCRIPT_DIR=$(dirname $0)
MSB_BASE_DIR="${PWD}/${SCRIPT_DIR}/.."
MSB_CONFIG_DIR="${PWD}/${SCRIPT_DIR}/../config"
MSB_SRC_DIR="${PWD}/${SCRIPT_DIR}/../src"

function update_software() {
  sudo apt update && sudo apt upgrade -y
}

function install_dependencies () {
  sudo apt -y install git python3 python3-dev python3-pip i2c-tools spi-tools\
      python3-spidev python3-smbus screen asciidoctor python3-matplotlib\
      libncurses5-dev python3-dev pps-tools build-essential manpages-dev\
      pkg-config python3-cairo-dev libgtk-3-dev python3-serial libdbus-1-dev\
      autossh mosh python3-numpy scons rsync vim
}

function install_python_requirements () {
  python -m pip install pip --upgrade
  python -m pip install -r "${MSB_BASE_DIR}/requirements.txt"
}

function copy_raspiconfig () {
  sudo cp "${MSB_CONFIG_DIR}/config.txt" /boot/
  sudo cp "${MSB_CONFIG_DIR}/cmdline.txt" /boot/
}

function insert_port () {
  serial=$(hostname | cut -d "-" -f2 | tr "0" " ") 
  port=$(python -c "port=65000+${serial}; print(f'{port}')")
  sudo sed -i "s/\[REMOTE_PORT\]/${port}/" /etc/systemd/system/rtunnel.service 
}

function setup_services () {
  sudo cp "${MSB_CONFIG_DIR}/services/*.service" /etc/systemd/system/
  insert_port
}


function main () {
  #update_software
  #install_dependencies
  #install_python_requirements
  setup_services
  #copy_raspiconfig
}

main
