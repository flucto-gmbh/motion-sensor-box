#!/bin/bash

set -x

CWD=$(pwd)
SCRIPT_DIR=$(dirname $0)
SRC_DIR="${PWD}/${SCRIPT_DIR}/../src"

# start broker
python $SRC_DIR/broker/src/msb_broker.py & 

# start imu sim
python $SRC_DIR/imu/src/sim_msb_imu.py & 

# start gps sim
python $SRC_DIR/gps/src/sim_msb_gps.py & 



