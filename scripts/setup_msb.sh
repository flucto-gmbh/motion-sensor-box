#!/bin/bash

set -e  # exit if an error occurs
set -x  # print each executed command to stdout

CWD=$(pwd)
SCRIPT_DIR=$(dirname $0)
MSB_BASE_DIR="${PWD}/${SCRIPT_DIR}/.."
MSB_CONFIG_DIR="${PWD}/${SCRIPT_DIR}/../config"
MSB_TARGET_CONFIG_DIR="${HOME}/.config"
MSB_SRC_DIR="${PWD}/${SCRIPT_DIR}/../src"
MSB_SSH_KEY="${HOME}/.ssh/msb_key"

if ! [[ -f "${MSB_SSH_KEY}" ]]
then
  echo "could not find ssh key at ${MSB_SSH_KEY}"
  exit
fi

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

function copy_config () {
  mkdir -p "${MSB_TARGET_CONFIG_DIR}"
  sudo cp "${MSB_CONFIG_DIR}"/config.txt /boot/
  sudo cp "${MSB_CONFIG_DIR}"/cmdline.txt /boot/
  sudo cp "${MSB_CONFIG_DIR}"/wpa_supplicant.conf /etc/wpa_supplicant
  sudo cp "${MSB_CONFIG_DIR}"/gpsd /etc/default
  cp "${MSB_CONFIG_DIR}"/msb.conf "${MSB_TARGET_CONFIG_DIR}"
  cp "${MSB_CONFIG_DIR}"/msb_env.sh "${MSB_TARGET_CONFIG_DIR}"
}

function copy_services () {
  sudo cp "${MSB_CONFIG_DIR}"/services/*.service /etc/systemd/system/ 
}

function add_configpath_profile () {
  echo ". ${MSB_TARGET_CONFIG_DIR}/msb_env.sh" >> "${HOME}/.profile"
}

function get_port_from_hostname () {
  serialnumber=$(hostname | cut -d "-" -f2 | tr "0" " ") 
  port=$(python -c "port=65000+${serialnumber}; print(f'{port}')")
  echo "${port}"
}

function insert_port () {
  port=$(get_port_from_hostname)
  sudo sed -i "s/\[REMOTE_PORT\]/${port}/" /etc/systemd/system/rtunnel.service 
}

function check_ssh () {
  server_response=$(ssh \
    -i "${MSB_SSH_KEY}"\
    -o "StrictHostKeyChecking no"\
    -p $(get_port_from_hostname)\
    -l msb\
    flucto.tech \
    "hostname")
  local_hostname=$(hostname)
  if ! [[ $server_response -eq $(hostname) ]]
  then
    echo "hostnames do not match! ${server_response} != ${local_hostname}"
  fi
}

function setup_rtunnel () {
  insert_port
  check_ssh
  sudo systemctl enable rtunnel.service
  sudo systemctl start rtunnel.service
}

update_software
install_dependencies
install_python_requirements
copy_services
setup_rtunnel
copy_config
add_path_profile

