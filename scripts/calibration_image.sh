#!/bin/bash
echo "Enter filename without filetype"
read filename

libcamera-still -o "/home/msb/"$filename".jpg" -t 3000 --width 1920 --height 1080 --autofocus-mode manual --lens-position 0.0


