#!/bin/bash

echo "starting all services"

for service_path in /etc/systemd/system/multi-user.target.wants/msb*service
do
	service=$(basename $service_path)
        echo -n "enabling $service... "
        sudo systemctl enable $service
        echo "done"
done

