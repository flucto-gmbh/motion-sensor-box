#!/bin/bash

# This script is intended for testing or small ad-hoc 
# measurements. It can be used to run the motion sensor box
# scripts directly without invoking systemd

set -x

CWD=$(pwd)
SCRIPT_DIR=$(dirname $0)
SRC_DIR="${PWD}/${SCRIPT_DIR}/../src"

# start broker
python $SRC_DIR/msb_broker/msb_broker.py & 

# start fusionlog
python $SRC_DIR/msb_fusionlog/msb_fusionlog.py & 

# start imu sim
python $SRC_DIR/msb_imu/msb_imu.py &

# start gps sim
python $SRC_DIR/msb_gps/msb_gps.py & 

# start wifi
#python $SRC_DIR/msb_wifi/msb_wifi.py & 

