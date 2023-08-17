#!/bin/bash

libcamera-still -o "/home/msb/"$1".jpg" -t 3000 --width 1920 --height 1080 --autofocus-mode manual --lens-position 0.0

