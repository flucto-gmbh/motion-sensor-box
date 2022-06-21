#!/bin/bash

RUN_TIME="1s"
OUTPUT_DIR="$HOME/imu_tests"
OUTPUT_DIV=13

function _usage () {
  cat<<EOF

filters.sh

test script for testing msb_imu.py

EOF
exit
}

function _error () {
  echo "ERROR: $1"
  _usage
}

if ! [[ -d $OUTPUT_DIR ]]
then
  echo "creating output directory"
  mkdir -p $OUTPUT_DIR
fi


function run_imu () {
  if [[ -z $1 ]] ; then _error "missing first argument: acc filter number" ; fi
  if [[ -z $2 ]] ; then _error "missing second argument: gyr filter number" ; fi
  acc_filter=$1
  gyr_filter=$2
  echo "running msb_imu with acc_filter $acc_filter and gyr_filter $gyr_filter"

}

function filter_test () {
  for acc_filter in {0..1}
  do
    for gyr_filter in {0..1}
    do
      output_filepath="$OUTPUT_DIR/imu-test_acc-filter_${acc_filter}_gyr-filter_${gyr_filter}_run-time_${RUN_TIME}.csv"
      # python ../msb_imu.py --acc-filter $acc_filter --gyr-filter $gyr_filter --sample-rate-div 13 --print-stdout > output_filepath & 
      #timeout --foreground $RUN_TIME cat <(python ../msb_imu.py --acc-filter $acc_filter --gyr-filter $gyr_filter --sample-rate-div 13 --print-stdout) > output_filepath
    done
  done
}

filter_test
