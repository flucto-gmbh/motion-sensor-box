#!/bin/bash

echo "starting all services"

for service_path in /etc/systemd/system/multi-user.target.wants/msb*service
do
	service=$(basename $service_path)
        echo -n "restarting $service... "
        sudo systemctl restart $service
        echo "done"
done

