#!/bin/bash

echo "stopping all services"

for service in /etc/systemd/system/multi-user.target.wants/msb-*.service
do
        echo -n "stopping $service "
        sudo systemctl stop $service
        echo "done"
done

