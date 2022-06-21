#!/bin/bash

function test () { 
  counter=0
  while true
  do 
    sleep 1
    counter=$((counter+1))
    echo $counter >> /tmp/t
  done
}

test
