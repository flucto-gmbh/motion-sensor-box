#!/bin/bash

echo "stopping all services"

for service_path in /etc/systemd/system/multi-user.target.wants/msb*service
do
	service=$(basename $service_path)
        echo -n "stopping $service "
        sudo systemctl stop $service
        echo "done"
done

